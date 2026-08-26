<!-- GENERATED — DO NOT EDIT -->
# Use Work Management operations

Define the bounded Work Management operations and their implementation surfaces.

Choose the operation that matches the intended lifecycle action; mutation authority is bounded by the command plane.

## Capture Work

Capture one bounded source record into Work without duplicating source identity.

Implementation surface: `project_management_reconcile`. Effect: `external_or_local_change`.

## Create Work

Create or reconcile one new Work record through the configured provider boundary.

Implementation surface: `project_management_reconcile`. Effect: `external_or_local_change`.

## Take Next Work

Select the next eligible Ready item and establish its execution claim.

Implementation surface: `project_management_take_next_work`. Effect: `external_or_local_change`.

## Claim Work

Establish one execution owner after revision and state guards pass.

Implementation surface: `project_management_claim_work`. Effect: `external_or_local_change`.

## Release Work

Clear an execution claim through the bounded command plane.

Implementation surface: `project_management_release_work`. Effect: `external_or_local_change`.

## Hold Work

Move work to On Hold only with the required review trigger.

Implementation surface: `project_management_hold_work`. Effect: `external_or_local_change`.

## Defer Work

Move work to Deferred only with the required review trigger.

Implementation surface: `project_management_defer_work`. Effect: `external_or_local_change`.

## Complete Work

Complete work only after configured completion and evidence guards pass.

Implementation surface: `project_management_complete_work`. Effect: `external_or_local_change`.

## Readiness

Evaluate deterministic queue eligibility and readiness evidence.

Implementation surface: `project_management_next_work`. Effect: `read_only`.

## Assignment Packet

Bind execution to a generation-specific work packet and reservation fence.

Implementation surface: `coordinator_work_packet`. Effect: `local_change`.

## Verification

Evaluate repository/source verification evidence for the exact delivery identity.

Implementation surface: `project_management_merge_readiness`. Effect: `read_only_or_external_evidence`.

## Commissioning

Track post-merge live verification separately from source verification.

Implementation surface: `issue_419_commissioning`. Effect: `external_or_local_change`.

## Authority Revision

Retain provider/Git revision evidence used for optimistic concurrency and traceability.

Implementation surface: `project_management_inventory`. Effect: `read_only`.

For operation contracts and typed errors, use the [Work Management Specification](../work-management-spec/001-specification.md).
