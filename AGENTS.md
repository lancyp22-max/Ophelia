# Lumaria agent instructions

## Preserve intentional open space

Do not interpret every blank, missing branch, unresolved pathway, or unspecified future behavior as technical debt.

Classify the gap before changing it:

1. **Invariant** — encode it and test it.
2. **Safety boundary** — enforce it and fail closed.
3. **Known mechanical behavior** — implement it.
4. **Contextual judgment** — preserve a deliberation point unless the current task supplies the missing context.
5. **Unknown future** — use `intentionally_not_decided_yet`; do not manufacture an answer merely because a field is blank.

Agents may flag intentional unknowns, but must not silently turn them into TODOs or speculative behavior. Revisit them only when their recorded trigger occurs or a human explicitly asks for a decision.

Authentication, authorization, destructive actions, recovery, permissions, security, and data boundaries are not philosophical unknowns. Treat gaps in those areas as blocking safety work and surface them clearly.

Run `make decision-boundary-check` when changing decision-boundary records or policy documentation.
