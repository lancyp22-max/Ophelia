# Project Espresso v0.1

Project Espresso is a lightweight local observability layer for agent coding work. It is designed to make the environment feel modular and alive enough that a human pilot can see **what agents are touching, what changed, what needs review, and what is safe to merge** without replaying the full chat.

It does not add a service, socket server, cloud dependency, telemetry sink, or background daemon. The first pass is file-and-git based: a script reads the current working tree, recent commits, and an Espresso capsule, then emits small artifacts that can be watched or pasted into the next turn.

## Goal

Give the pilot and future agents a fast answer to:

> What work is happening in this place right now, where is it happening, and what needs attention?

## Architecture

```text
Git status + recent commits + project capsule
        ↓
Project Espresso observer
        ↓
artifacts/project-espresso-state.json
artifacts/project-espresso-brief.md
        ↓
read-only UI panel / next prompt / PR review packet
```

## Espresso lanes

| Lane | Purpose | Source |
| --- | --- | --- |
| `active_changes` | Files currently modified, added, deleted, or untracked | `git status --porcelain=v1` |
| `recent_commits` | Latest visible work pulses on the branch | `git log --oneline` |
| `module_map` | Human-readable module buckets for changed paths | `data/context/project-espresso-capsule.v0.1.json` |
| `review_focus` | Things the next reviewer should inspect first | generated from change types |
| `safety_gates` | Checks and boundaries that must remain visible | capsule + Makefile targets |

## Real-time mode

For a terminal-side pulse, run:

```bash
make espresso-watch
```

This refreshes the generated brief every few seconds. It is not a daemon and it does not send data anywhere; stop it with `Ctrl+C`.

## Review packet mode

For a one-shot packet before commit or handoff, run:

```bash
make espresso
```

Outputs:

- `artifacts/project-espresso-state.json`
- `artifacts/project-espresso-brief.md`

## Safety rules

- Observe local git/file state only.
- Do not infer agent intent from file paths; show evidence, not mind-reading.
- Do not expose sealed/private content in public artifacts.
- Keep generated artifacts out of committed source unless explicitly needed.
- Human pilot remains the merge/publish authority.

## Next implementation steps

1. Add an optional read-only Flight Deck panel that loads `project-espresso-state.json` when served locally.
2. Let spawned/parallel agents write small sanitized pulse files under `artifacts/agent-pulses/`.
3. Merge pulse files into the Espresso brief with timestamps and claimed file scopes.
4. Add stale-pulse detection so frozen work is visible without guessing.
5. Keep all mutation behind explicit human approval.
