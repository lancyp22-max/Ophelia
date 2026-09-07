# Task guidepost scanner

The task guidepost scanner interrupts tunnel vision before implementation. It
matches the current task against a small, curated registry of operational
failure patterns and hard boundaries, then emits checks to consider.

It is not an autonomous research agent and does not claim that a historical
failure applies merely because keywords matched. A match means **look here**, not
**this is what happened**.

## Usage

```bash
make task-guideposts TASK="automate coffee and flour supplier orders"
# artifacts/task-guideposts.json
# artifacts/task-guideposts.md

python3 scripts/task_guidepost_scan.py --task-file /path/to/task.txt
```

Run `make task-guidepost-check` to validate the curated registry without
generating artifacts.

## Why cases are curated

External business-failure stories can be useful guideposts, but search snippets,
retellings, and model summaries are not sufficient evidence. An external case is
admitted only with a primary-source HTTPS URL, verification date, and a list of
claims that source actually supports. Facts and architectural inferences remain
separate.

The initial external-case list is deliberately empty. No claim about a named
coffee-shop experiment is encoded until its primary source can be verified.

## Limits

- Keyword matching can miss relevant risks and can produce irrelevant matches.
- Multiple reviewers are not independent if they share the same source or blind
  spot.
- The scanner does not replace authentication, authorization, threat modeling,
  financial controls, food-safety review, or human judgment.
- A no-match result is not a safety result.
