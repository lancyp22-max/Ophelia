# Intentional Undefined: preserving future context

Lumaria distinguishes unfinished implementation from decisions that should not exist yet. A blank can be a defect, but it can also be a deliberate interface with future context.

## Classification rule

| Class | Required treatment |
| --- | --- |
| Invariant | Encode it and test it. |
| Safety boundary | Enforce it, fail closed, and surface missing enforcement as a blocker. |
| Known mechanical behavior | Implement it and verify the expected result. |
| Contextual judgment | Preserve a visible deliberation point until the relevant participants and context exist. |
| Unknown future | Record `intentionally_not_decided_yet`; do not invent a default answer. |

This is not permission to leave security-sensitive behavior vague. Authentication, authorization, destructive actions, recovery, permissions, secrets, and data boundaries require explicit, enforceable behavior.

## Agent behavior

When an agent encounters an unresolved pathway:

1. Identify its class before proposing code.
2. Explain any safety consequence.
3. Implement invariants, safety boundaries, and known mechanics.
4. Preserve contextual judgment and unknown-future cases without filling them speculatively.
5. Record what future event should reopen an intentional unknown.

`undefined` must never silently mean `TODO`. Use a decision record with a reason and reconsideration trigger when the absence is intentional.

## Review language

Preferred review outcomes:

- `encoded`
- `enforced`
- `implemented`
- `intentionally_not_decided_yet`
- `blocked_by_missing_safety_boundary`

Avoid language such as “complete every unresolved pathway.” The goal is a stable system with honest boundaries, not a fictional answer for every possible future.
