# Token Context Workflow v0.1

Ophelia has enough history now that replaying the whole conversation wastes the budget that should go to coding. This workflow keeps future turns compact.

## Rule

Use a **context capsule**, not the full chat log.

Paste only:

1. the current small task,
2. the generated capsule from `make context-brief`, and
3. any new reference image/details that are truly required for that task.

Do not paste the full prior conversation unless debugging a specific regression.

## Why

The repo already carries the durable memory:

- `README.md` for public orientation,
- `docs/` for design laws and roadmaps,
- `data/visual-state/` for semantic visual state,
- `data/context/ophelia-context-capsule.v0.1.json` for the compact handoff,
- Git history for exact changed files and commits.

The chat should carry intent, not the entire archive.

## Small-prompt pattern

```text
Use the Ophelia context capsule. Do not replay old chat.
Task: improve only <district/object/system>.
Scope: <1-3 files if possible>.
Constraints: no new dependencies, no binary assets, public-shell safe.
Testing: run make ci-check and make public-shell-audit.
```

## Visual work slicing

For A1/Base Camp visuals, prefer one of these per prompt:

- one district: Market, Stables, Welcome Grove, South Gate,
- one object family: lanterns, grass, clouds, benches, signs,
- one rendering property: shadows, texture contrast, glow, camera,
- one mobile usability issue.

This keeps each wave easy to review and avoids turning every visual request into a full-project replay.

## Generated brief

Run:

```bash
make context-brief
```

This writes `artifacts/context-brief.md`, which is intended to be pasted into the next coding session instead of the whole conversation.
