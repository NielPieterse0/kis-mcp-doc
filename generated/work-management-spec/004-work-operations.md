<!-- GENERATED — DO NOT EDIT -->
# Work operations

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

Work Management exposes a bounded set of operations for intake, claiming, state changes, verification, and post-merge commissioning. Each operation has a defined effect and implementation surface so callers can distinguish reads from mutations and evidence collection.

## Mutation safety

External Project mutations require `apply=true` and an explicit idempotency key.

## Operations

| Operation | Purpose | Effect | Implementation surface |
|---|---|---|---|
| Capture work (`capture_work`) | Capture one bounded source record into Work without duplicating source identity. | `external_or_local_change` | `project_management_reconcile` |
| Create work (`create_work`) | Create or reconcile one new Work record through the configured provider boundary. | `external_or_local_change` | `project_management_reconcile` |
| Take next work (`take_next_work`) | Select the next eligible Ready item and establish its execution claim. | `external_or_local_change` | `project_management_take_next_work` |
| Claim work (`claim_work`) | Establish one execution owner after revision and state guards pass. | `external_or_local_change` | `project_management_claim_work` |
| Release work (`release_work`) | Clear an execution claim through the bounded command plane. | `external_or_local_change` | `project_management_release_work` |
| Hold work (`hold_work`) | Move work to On Hold only with the required review trigger. | `external_or_local_change` | `project_management_hold_work` |
| Defer work (`defer_work`) | Move work to Deferred only with the required review trigger. | `external_or_local_change` | `project_management_defer_work` |
| Complete work (`complete_work`) | Complete work only after configured completion and evidence guards pass. | `external_or_local_change` | `project_management_complete_work` |
| Readiness (`readiness`) | Evaluate deterministic queue eligibility and readiness evidence. | `read_only` | `project_management_next_work` |
| Assignment packet (`assignment_packet`) | Bind execution to a generation-specific work packet and reservation fence. | `local_change` | `coordinator_work_packet` |
| Verification (`verification`) | Evaluate repository/source verification evidence for the exact delivery identity. | `read_only_or_external_evidence` | `project_management_merge_readiness` |
| Commissioning (`commissioning`) | Track post-merge live verification separately from source verification. | `external_or_local_change` | `issue_419_commissioning` |
| Authority revision (`authority_revision`) | Retain provider/Git revision evidence used for optimistic concurrency and traceability. | `read_only` | `project_management_inventory` |

## Result envelope

Operation results use a common envelope so readers and tools can identify when the observation was made, what target was resolved, where the evidence came from, the operation result, and any valid next action.

- `observed_at`
- `resolved_target`
- `provenance`
- `result`
- `next_actions`

## Typed errors

Failures use bounded error categories rather than unstructured provider text:

- `provider_unavailable`
- `project_not_commissioned`
- `inventory_incomplete`
- `conflict`
- `invalid_transition`
- `not_found`
- `invalid_request`
- `internal`

## Verification domains

Source verification and live verification are separate evidence domains. A successful repository check does not by itself prove the post-merge runtime surface.

| Domain | Field | Meaning |
|---|---|---|
| `source_verification` | Verification | Repository/source verification evidence tied to the delivery identity. |
| `live_verification` | Live Verification | Post-merge runtime proof tied to the actual exposed capability or runtime path. |

## Source and authority

This page projects `KIS-WORK-WRK-WFL-001` version `1.0.0`. The MRD remains authoritative; this generated page has no write-back authority.
