<!-- GENERATED — DO NOT EDIT -->
# Troubleshoot work state

Use guards, authority, and typed errors instead of forcing a state transition.

## Guards

- `approval-before-active` → `approval_incomplete`: Reject activation when the record requires approval and approval is incomplete.
- `completion-no-active-claim` → `active_claim_present`: When configured, reject completion while an execution claim remains.
- `completion-documentation-due` → `documentation_reconciliation_due`: Required post-merge documentation reconciliation must be completed before Done.
- `completion-documentation-due-advisory` → `documentation_reconciliation_advisory_due`: Advisory post-merge documentation reconciliation may complete with an explicit advisory reason.
- `completion-documentation-unrecorded` → `documentation_reconciliation_unrecorded`: Required post-merge documentation milestone must be recorded before Done.
- `completion-documentation-unrecorded-advisory` → `documentation_reconciliation_advisory_incomplete`: Advisory documentation reconciliation may complete without a recorded post-merge milestone, with an explicit advisory reason.
- `completion-documentation-incomplete` → `documentation_incomplete`: Required documentation impact must be complete before Done.
- `completion-documentation-incomplete-advisory` → `documentation_advisory_incomplete`: Advisory documentation may complete while incomplete, with an explicit advisory reason.

## Provider boundary

Live Project evidence was observed; inventory is complete; the configured Project schema is ready with no field, option, type, or view drift in the captured evidence.

Typed errors:
- `provider_unavailable`
- `project_not_commissioned`
- `inventory_incomplete`
- `conflict`
- `invalid_transition`
- `not_found`
- `invalid_request`
- `internal`

Use the [Work Management Specification](../work-management-spec/001-specification.md) for exact field authority and recovery semantics.
