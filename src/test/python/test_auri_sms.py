#!/usr/bin/env python3
import argparse
import json
import tempfile
import unittest
import urllib.parse
from pathlib import Path

from scripts.auri_sms import SmsBoundaryError, execute


class AuriSmsTest(unittest.TestCase):
    def setUp(self):
        self.env = {
            "AURI_SMS_ENABLED": "true",
            "AURI_SMS_CONSENT": "outbound_prompts_v1",
            "AURI_SMS_TO": "+15555550123",
            "TWILIO_FROM_NUMBER": "+15555550124",
            "TWILIO_ACCOUNT_SID": "AC-test-account",
            "TWILIO_AUTH_TOKEN": "test-only-token",
        }
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)

    def args(self, *, send=False, message="Would you like to review the proposal?"):
        return argparse.Namespace(
            send=send,
            message=message,
            state_file=str(Path(self.tempdir.name) / "state.json"),
            daily_limit=2,
            cooldown_seconds=900,
        )

    def test_dry_run_does_not_need_provider_credentials(self):
        env = {key: value for key, value in self.env.items() if not key.startswith("TWILIO_A")}
        result = execute(self.args(), env)
        self.assertEqual("dry_run", result["status"])

    def test_send_uses_provider_and_records_only_timestamp(self):
        observed = {}

        def transport(request, timeout):
            observed["body"] = urllib.parse.parse_qs(request.data.decode())
            observed["timeout"] = timeout
            return 201, json.dumps({"sid": "SM-test-message"}).encode()

        result = execute(self.args(send=True), self.env, transport)
        self.assertEqual("sent", result["status"])
        self.assertEqual(["Would you like to review the proposal?"], observed["body"]["Body"])
        self.assertEqual(10.0, observed["timeout"])
        state = Path(self.args().state_file).read_text(encoding="utf-8")
        self.assertNotIn(self.env["AURI_SMS_TO"], state)
        self.assertNotIn("proposal", state)

    def test_disabled_boundary_fails_closed(self):
        self.env["AURI_SMS_ENABLED"] = "false"
        with self.assertRaisesRegex(SmsBoundaryError, "disabled"):
            execute(self.args(send=True), self.env)

    def test_memory_of_consent_is_not_current_consent(self):
        self.env["AURI_SMS_CONSENT"] = "yes"
        with self.assertRaisesRegex(SmsBoundaryError, "current consent marker"):
            execute(self.args(send=True), self.env)

    def test_cooldown_blocks_second_send(self):
        transport = lambda request, timeout: (201, b'{"sid":"SM-test-message"}')
        execute(self.args(send=True), self.env, transport)
        with self.assertRaisesRegex(SmsBoundaryError, "cooldown"):
            execute(self.args(send=True), self.env, transport)

    def test_caller_cannot_weaken_rate_limits(self):
        args = self.args()
        args.daily_limit = 9
        args.cooldown_seconds = 0
        with self.assertRaisesRegex(SmsBoundaryError, "daily limit"):
            execute(args, self.env)

    def test_provider_failure_still_reserves_cooldown(self):
        def rejected(request, timeout):
            return 503, b"{}"

        with self.assertRaisesRegex(SmsBoundaryError, "HTTP 503"):
            execute(self.args(send=True), self.env, rejected)
        with self.assertRaisesRegex(SmsBoundaryError, "cooldown"):
            execute(self.args(send=True), self.env, rejected)


if __name__ == "__main__":
    unittest.main()
