<!-- GENERATED — DO NOT EDIT -->
# Complete governed work

Completion is evidence-gated; merge is not the same as Done.

A change can move through repository delivery, merge, documentation reconciliation, and commissioning before Work reaches Done.

## Delivery stages

`none` → `change_created` → `implementing` → `pr_open` → `review` → `ci_pending` → `ci_failed` → `ci_passed` → `merged` → `documentation` → `commissioning` → `complete`

## Completion checks

- Terminal Work state: `done`.
- Required post-merge documentation reconciliation must be complete when its guard applies.
- Source verification and live verification remain separate evidence domains.

See the [Work Management Specification](../work-management-spec/001-specification.md) for exact completion guards.
