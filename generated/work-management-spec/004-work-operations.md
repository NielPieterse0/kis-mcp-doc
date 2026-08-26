<!-- GENERATED — DO NOT EDIT -->
# Work operations

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

Define the bounded Work Management operations and their implementation surfaces.

## Mutation rule

External Project mutations require apply=true and an explicit idempotency key.

## Operations

### capture work

**Definition:** Capture one bounded source record into Work without duplicating source identity.

**Effect:** external_or_local_change

**Id:** capture_work

**Implementation surface:** project_management_reconcile

### create work

**Definition:** Create or reconcile one new Work record through the configured provider boundary.

**Effect:** external_or_local_change

**Id:** create_work

**Implementation surface:** project_management_reconcile

### take next work

**Definition:** Select the next eligible Ready item and establish its execution claim.

**Effect:** external_or_local_change

**Id:** take_next_work

**Implementation surface:** project_management_take_next_work

### claim work

**Definition:** Establish one execution owner after revision and state guards pass.

**Effect:** external_or_local_change

**Id:** claim_work

**Implementation surface:** project_management_claim_work

### release work

**Definition:** Clear an execution claim through the bounded command plane.

**Effect:** external_or_local_change

**Id:** release_work

**Implementation surface:** project_management_release_work

### hold work

**Definition:** Move work to On Hold only with the required review trigger.

**Effect:** external_or_local_change

**Id:** hold_work

**Implementation surface:** project_management_hold_work

### defer work

**Definition:** Move work to Deferred only with the required review trigger.

**Effect:** external_or_local_change

**Id:** defer_work

**Implementation surface:** project_management_defer_work

### complete work

**Definition:** Complete work only after configured completion and evidence guards pass.

**Effect:** external_or_local_change

**Id:** complete_work

**Implementation surface:** project_management_complete_work

### readiness

**Definition:** Evaluate deterministic queue eligibility and readiness evidence.

**Effect:** read_only

**Id:** readiness

**Implementation surface:** project_management_next_work

### assignment packet

**Definition:** Bind execution to a generation-specific work packet and reservation fence.

**Effect:** local_change

**Id:** assignment_packet

**Implementation surface:** coordinator_work_packet

### verification

**Definition:** Evaluate repository/source verification evidence for the exact delivery identity.

**Effect:** read_only_or_external_evidence

**Id:** verification

**Implementation surface:** project_management_merge_readiness

### commissioning

**Definition:** Track post-merge live verification separately from source verification.

**Effect:** external_or_local_change

**Id:** commissioning

**Implementation surface:** issue_419_commissioning

### authority revision

**Definition:** Retain provider/Git revision evidence used for optimistic concurrency and traceability.

**Effect:** read_only

**Id:** authority_revision

**Implementation surface:** project_management_inventory

## Result envelope

observed_at, resolved_target, provenance, result, next_actions

## Typed errors

provider_unavailable, project_not_commissioned, inventory_incomplete, conflict, invalid_transition, not_found, invalid_request, internal

## Verification domains

### source verification

**Definition:** Repository/source verification evidence tied to the delivery identity.

**Field:** Verification

**Id:** source_verification

### live verification

**Definition:** Post-merge runtime proof tied to the actual exposed capability or runtime path.

**Field:** Live Verification

**Id:** live_verification

## Source and authority

This page projects `KIS-WORK-WRK-WFL-001` version `1.0.0`. The MRD is authoritative; this generated page has no write-back authority.
