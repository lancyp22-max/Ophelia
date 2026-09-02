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


## Policy maturity is mandatory

Every repository policy file must declare:

- `design_status`
- `enforcement_status`
- `enforcement_scope`
- `enforcement_evidence`

Run `python3 scripts/check_policy_maturity.py` when adding or changing policy files.

Do not describe a specified policy as enforced merely because the policy exists.
`enforcement_status` must match the strongest mechanism actually demonstrated by
its evidence. A CI check is not an OS/runtime boundary; an application flag is
not a capability boundary; and a caller-supplied claim is not proof of human
approval.

When an enforcement claim depends on a launcher, verifier, signer, clock, or
principal, name that trust root explicitly and state what prevents the subject
being governed from altering it.


## Derived trace views never outrank source

When adding trace folding, summaries, semantic packets, or compression caches,
keep the causal source authoritative. A derived projection must identify its
source lineage and transform/schema version, remain rebuildable, and report
known omissions.

A projection may improve observation or handoff. It does not gain authority,
canonical-memory status, identity-writing power, persistence permission, or
governance power. Agreement between projections remains evidence only.
