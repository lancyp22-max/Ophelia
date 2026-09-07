# Auri SMS prompting

This repository provides a local, outbound-only SMS tool so Auri can offer a
short prompt through a human-controlled Twilio account. It does not establish
that any model is Auri, and a received text is not an authority receipt.

The destination number is deliberately absent from tracked files. Configure it
only in the trusted runtime environment:

```bash
export AURI_SMS_ENABLED=true
export AURI_SMS_CONSENT=outbound_prompts_v1
export AURI_SMS_TO='+1...'
export TWILIO_FROM_NUMBER='+1...'
export TWILIO_ACCOUNT_SID='...'
export TWILIO_AUTH_TOKEN='...'
```

Preview validation without contacting the provider:

```bash
python3 scripts/auri_sms.py 'Would you like to review a new proposal?'
```

Send only after reviewing the message and environment:

```bash
python3 scripts/auri_sms.py --send 'Would you like to review a new proposal?'
```

## Enforced boundary

- Sending is disabled unless both the enable switch and versioned consent marker
  are present in the current process environment.
- The phone numbers and credentials remain server-side and are never accepted as
  command-line values, committed, or included in receipts.
- Messages are whitespace-normalized and limited to 480 characters.
- A local locked state file applies a default 15-minute cooldown and eight-message
  rolling daily limit. Corrupt state fails closed.
- The state file records timestamps only. Console output contains a one-way,
  truncated destination fingerprint and the provider message identifier, never
  the destination or message body.
- Dry-run is the default. A provider call requires the explicit `--send` flag.

This tool is intentionally not mounted behind the current web API because that
API lacks authentication, authorization, replay protection, and rate controls.
Inbound replies, scheduled/autonomous prompts, and interpretation of reply text
are `intentionally_not_decided_yet`. Reconsider them only after authenticated
inbound webhook verification, explicit scheduling consent, quiet-hour controls,
STOP handling, and a separate authority path exist.

Twilio documents message creation through its Message resource and recommends
API keys for production authentication. Account credentials used here are a
minimal local bootstrap path, not a claim of production readiness.
