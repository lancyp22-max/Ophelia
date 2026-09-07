#!/usr/bin/env python3
"""Validate, encode, decode, and size-check experimental semantic packets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CODEBOOK_PATH = ROOT / "data" / "semantic-packets" / "lumaria-semantic-codebook.v0.1.json"
DELTA_PATH = ROOT / "data" / "semantic-packets" / "sample-state-delta.v0.1.json"
PACKET_PATH = ROOT / "data" / "semantic-packets" / "sample-state-packet.v0.1.json"


class PacketError(ValueError):
    """Raised when a packet cannot cross the semantic transport boundary."""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=False)


def inverse_unique(values: dict[str, str], label: str) -> dict[str, str]:
    inverse: dict[str, str] = {}
    for semantic, atom in values.items():
        if not semantic or not atom:
            raise PacketError(f"{label} entries must have non-empty names and atoms")
        if atom in inverse:
            raise PacketError(f"duplicate {label} atom: {atom!r}")
        inverse[atom] = semantic
    return inverse


def validate_codebook(codebook: dict[str, Any]) -> None:
    if codebook.get("version") != "0.1":
        raise PacketError("unsupported codebook version")
    inverse_unique(codebook.get("operators", {}), "operator")
    inverse_unique(codebook.get("paths", {}), "path")
    inverse_unique(codebook.get("values", {}), "value")
    forbidden = [item.casefold() for item in codebook["safety"]["forbidden_path_fragments"]]
    for path in codebook["paths"]:
        if any(fragment in path.casefold() for fragment in forbidden):
            raise PacketError(f"forbidden semantic path in codebook: {path}")
    if codebook["safety"].get("decoded_values_are") != "untrusted_context_data":
        raise PacketError("decoded packets must remain untrusted context data")


def validate_envelope(value: dict[str, Any], codebook: dict[str, Any]) -> None:
    if set(value) != {"v", "b", "n", "d"}:
        raise PacketError("packet envelope must contain only v, b, n, and d")
    if value["v"] != codebook["version"]:
        raise PacketError("codebook version mismatch")
    if not isinstance(value["b"], str) or not value["b"]:
        raise PacketError("base state reference is required")
    if not isinstance(value["n"], int) or value["n"] < 1:
        raise PacketError("positive sequence number is required")
    operations = value["d"]
    maximum = codebook["limits"]["maximum_operations"]
    if not isinstance(operations, list) or len(operations) > maximum:
        raise PacketError(f"operation list must contain at most {maximum} entries")


def encode(delta: dict[str, Any], codebook: dict[str, Any]) -> dict[str, Any]:
    expected_codebook = f"{codebook['protocol']}@{codebook['version']}"
    if delta.get("codebook") != expected_codebook:
        raise PacketError("delta codebook identifier mismatch")
    base_state = delta.get("base_state")
    sequence = delta.get("sequence")
    operations = delta.get("operations")
    if not isinstance(operations, list):
        raise PacketError("delta operations must be a list")

    encoded: list[list[Any]] = []
    for operation in operations:
        operator = codebook["operators"].get(operation.get("operator"))
        path = codebook["paths"].get(operation.get("path"))
        if operator is None or path is None:
            raise PacketError("delta contains an unknown operator or path")
        if operation.get("operator") == "remove":
            encoded.append([operator, path])
            continue
        value = codebook["values"].get(operation.get("value"))
        if value is None:
            raise PacketError("delta contains an unknown value; literals are disabled in v0.1")
        encoded.append([operator, path, value])

    packet = {"v": codebook["version"], "b": base_state, "n": sequence, "d": encoded}
    validate_envelope(packet, codebook)
    return packet


def decode(
    packet: dict[str, Any], codebook: dict[str, Any], prior_sequence: int | None = None
) -> dict[str, Any]:
    validate_envelope(packet, codebook)
    if prior_sequence is not None and packet["n"] <= prior_sequence:
        raise PacketError("packet sequence must advance beyond the prior sequence")
    operators = inverse_unique(codebook["operators"], "operator")
    paths = inverse_unique(codebook["paths"], "path")
    values = inverse_unique(codebook["values"], "value")
    decoded: list[dict[str, str]] = []
    for item in packet["d"]:
        if not isinstance(item, list) or len(item) not in (2, 3):
            raise PacketError("each operation must contain two or three atoms")
        if item[0] not in operators or item[1] not in paths:
            raise PacketError("packet contains an unknown operator or path atom")
        operator = operators[item[0]]
        operation = {"operator": operator, "path": paths[item[1]]}
        if operator == "set":
            if len(item) != 3 or item[2] not in values:
                raise PacketError("set operation requires a known value atom")
            operation["value"] = values[item[2]]
        elif len(item) != 2:
            raise PacketError("remove operation must not carry a value")
        decoded.append(operation)
    return {
        "codebook": f"{codebook['protocol']}@{codebook['version']}",
        "base_state": packet["b"],
        "sequence": packet["n"],
        "operations": decoded,
        "trust": "untrusted_context_data"
    }


def check() -> None:
    codebook = load_json(CODEBOOK_PATH)
    delta = load_json(DELTA_PATH)
    fixture = load_json(PACKET_PATH)
    validate_codebook(codebook)
    encoded = encode(delta, codebook)
    if encoded != fixture:
        raise PacketError("sample packet does not match deterministic encoding")
    decoded = decode(fixture, codebook)
    comparable = {key: decoded[key] for key in ("codebook", "base_state", "sequence", "operations")}
    if comparable != delta:
        raise PacketError("sample packet does not round-trip")

    bad_packet = dict(fixture)
    bad_packet["d"] = [["=", "unknown", "c"]]
    try:
        decode(bad_packet, codebook)
    except PacketError:
        pass
    else:
        raise PacketError("unknown atoms must fail closed")
    try:
        decode(fixture, codebook, prior_sequence=fixture["n"])
    except PacketError:
        pass
    else:
        raise PacketError("sequence replay or regression must fail closed")


def benchmark() -> None:
    delta = load_json(DELTA_PATH)
    packet = load_json(PACKET_PATH)
    verbose = compact(delta)
    packed = compact(packet)
    saved = len(verbose.encode()) - len(packed.encode())
    ratio = len(packed.encode()) / len(verbose.encode())
    print(f"verbose_utf8_bytes={len(verbose.encode())}")
    print(f"packet_utf8_bytes={len(packed.encode())}")
    print(f"byte_savings={saved}")
    print(f"packet_to_verbose_ratio={ratio:.3f}")
    print("provider_token_count=unavailable")
    print("note=Byte reduction is not proof of billed-token reduction; benchmark with the target provider tokenizer and include codebook/prompt overhead.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="validate fixtures and denial paths")
    mode.add_argument("--benchmark", action="store_true", help="report provider-neutral size metrics")
    mode.add_argument("--encode", type=Path, help="encode a semantic delta JSON file")
    mode.add_argument("--decode", type=Path, help="decode a semantic packet JSON file")
    parser.add_argument(
        "--prior-sequence",
        type=int,
        help="authoritative prior sequence used to reject replay/regression during decode",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.prior_sequence is not None and args.decode is None:
            raise PacketError("--prior-sequence is valid only with --decode")
        codebook = load_json(CODEBOOK_PATH)
        validate_codebook(codebook)
        if args.check:
            check()
            print("[semantic-packet] fixtures and denial paths passed")
        elif args.benchmark:
            benchmark()
        elif args.encode:
            print(compact(encode(load_json(args.encode), codebook)))
        elif args.decode:
            print(json.dumps(decode(load_json(args.decode), codebook, args.prior_sequence), indent=2))
    except (OSError, json.JSONDecodeError, PacketError) as error:
        print(f"[semantic-packet] ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
