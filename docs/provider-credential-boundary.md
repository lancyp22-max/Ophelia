# Provider credential boundary

## Current state

The public web surface must contain no provider credential. The repository's
leak guard blocks common provider-token formats, tracked private-key material,
and secret-like values assigned to browser-public environment names.

This is defense in depth, not a credential vault. Pattern scanning cannot prove
that a repository contains no secret.

The existing `POST /api/seeds/authority/verify` route enforces a surfaced
confirmation invariant for its in-memory state operation. It does **not**
currently provide:

- user authentication;
- role or scope authorization;
- session or CSRF protection;
- provider API proxying;
- rate or concurrency limits;
- per-user quotas or budget circuit breakers;
- production secret storage;
- durable transaction storage.

Therefore, it must not be described as a secure token endpoint or used as the
gate for provider calls in its current form.

## Boundary required before a provider call exists

1. Keep credentials in a deployment secret store or server-only environment;
   never serialize them into HTML, JavaScript, responses, telemetry, or logs.
2. Authenticate the caller and authorize the requested provider capability.
3. Validate request size and schema; allowlist providers, models, and tools.
4. Apply per-user and global rate, concurrency, token, and monetary limits.
5. Use timeouts, bounded retries, idempotency where applicable, and an emergency
   disable switch.
6. Redact request/response logs and prohibit provider credentials in exception
   messages.
7. Return only the minimum response required by the client.
8. Test denial paths, budget exhaustion, provider failure, replay, and log
   redaction before public exposure.

Until those controls exist, provider integration is
`blocked_by_missing_safety_boundary`. That is a concrete security blocker, not
an intentionally undecided future.
