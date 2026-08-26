<!-- GENERATED — DO NOT EDIT -->
# Next-work selection

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

Define deterministic eligibility and ranking for selecting executable work.

## Dependency evidence

unavailable, partial, observed

## Effort order

tiny, small, medium, large

## Eligible states

ready

## Fields

**Blocked by:** Blocked By

**Created:** Created

**Effort:** Effort

**Execution owner:** Execution Owner

**Priority:** Priority

**State:** Status

## Priority order

critical, high, medium, low

## Profiles

### Normalized domain

#### Reason overrides

**Dependencies clear:** dependency_incomplete:{dependency_id}

**Eligible state:** state_not_executable

**Rules:** project_match, eligible_state, unclaimed, approval_complete, dependencies_clear

### Provider project

#### Reason overrides

**Dependencies clear:** native_dependency_blocking

**Eligible state:** state_not_ready

**Rules:** source_issue, source_open, eligible_state, valid_priority, valid_effort, required_fields, unclaimed, dependency_evidence, dependencies_clear

## Ranking

priority, effort, created_order, record_id

## Rules

### SEL-001

**Definition:** Only issue records are eligible in the provider-backed next-work queue.

**Id:** SEL-001

**Kind:** source_issue

**Reason code:** not_issue

### SEL-002

**Definition:** Provider-backed source issues must remain open.

**Id:** SEL-002

**Kind:** source_open

**Reason code:** source_not_open

### SEL-003

**Definition:** Normalized-domain selection respects an explicit project scope.

**Id:** SEL-003

**Kind:** project_match

**Reason code:** project_mismatch

### SEL-004

**Definition:** Candidate state must be one of the configured eligible states; domain adapters may preserve their existing equivalent reason code.

**Id:** SEL-004

**Kind:** eligible_state

**Reason code:** state_not_ready

### SEL-005

**Definition:** Priority must be present in the canonical priority order.

**Id:** SEL-005

**Kind:** valid_priority

**Reason code:** missing_or_invalid:{field}

### SEL-006

**Definition:** Effort must be present in the canonical effort order.

**Id:** SEL-006

**Kind:** valid_effort

**Reason code:** missing_or_invalid:{field}

### SEL-007

**Definition:** Configured readiness fields must be present before provider-backed selection.

**Id:** SEL-007

**Kind:** required_fields

**Reason code:** missing_required:{field}

### SEL-008

**Definition:** Already claimed work is excluded from next-work selection.

**Id:** SEL-008

**Kind:** unclaimed

**Reason code:** already_claimed:{owner}

### SEL-009

**Definition:** Normalized-domain records that require approval must have completed approval.

**Id:** SEL-009

**Kind:** approval_complete

**Reason code:** approval_incomplete

### SEL-010

**Definition:** Required provider dependency evidence must be observable.

**Id:** SEL-010

**Kind:** dependency_evidence

**Reason code:** dependency_evidence_unavailable

### SEL-011

**Definition:** Provider-native blocker evidence must be empty; normalized-domain adapters preserve dependency-specific reason codes.

**Id:** SEL-011

**Kind:** dependencies_clear

**Reason code:** native_dependency_blocking

### SEL-012

**Definition:** Eligible candidates rank by Priority, Effort, creation order, then stable record identity.

**Id:** SEL-012

**Kind:** ranking

**Reason code:** None

## Source and authority

This page projects `KIS-WORK-DEC-SCR-001` version `1.0.0`. The MRD is authoritative; this generated page has no write-back authority.
