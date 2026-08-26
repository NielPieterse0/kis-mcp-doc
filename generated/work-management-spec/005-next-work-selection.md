<!-- GENERATED — DO NOT EDIT -->
# Next-work selection

<div id="enable-section-numbers" />

[Previous: Work operations](004-work-operations.md) | [Next: Authority and reconciliation policy](006-authority-and-reconciliation-policy.md) | [Index](000-index.md)

Selection is deterministic. Work Management first applies the eligibility rules for the active profile, then ranks only the candidates that remain.

## Selection procedure

1. Keep only candidates whose state is `ready`.
2. Apply the active profile's rules in their declared order. These rules check source shape, open state, project scope, required metadata, claims, approval, dependency evidence, and blockers as applicable to that profile.
3. Exclude any candidate that fails a rule and return the rule's stable reason code.
4. Rank the remaining candidates by `priority`, `effort`, `created_order`, `record_id`.

Priority order is `critical`, `high`, `medium`, `low`. Effort order is `tiny`, `small`, `medium`, `large`. Dependency evidence is classified as `unavailable`, `partial`, `observed`.

## Selection inputs

| Input | Project field |
|---|---|
| Blocked by | Blocked By |
| Created | Created |
| Effort | Effort |
| Execution owner | Execution Owner |
| Priority | Priority |
| State | Status |

## Selection profiles

Profiles reuse the same rule catalog but apply different subsets and preserve profile-specific failure reasons where the source contract requires them.

| Profile | Rules in order | Reason overrides |
|---|---|---|
| Normalized domain | `project_match`, `eligible_state`, `unclaimed`, `approval_complete`, `dependencies_clear` | `dependencies_clear` maps to `dependency_incomplete:{dependency_id}`; `eligible_state` maps to `state_not_executable` |
| Provider project | `source_issue`, `source_open`, `eligible_state`, `valid_priority`, `valid_effort`, `required_fields`, `unclaimed`, `dependency_evidence`, `dependencies_clear` | `dependencies_clear` maps to `native_dependency_blocking`; `eligible_state` maps to `state_not_ready` |

## Rule catalog

| Rule | Kind | Requirement | Failure reason |
|---|---|---|---|
| `SEL-001` | `source_issue` | Only issue records are eligible in the provider-backed next-work queue. | `not_issue` |
| `SEL-002` | `source_open` | Provider-backed source issues must remain open. | `source_not_open` |
| `SEL-003` | `project_match` | Normalized-domain selection respects an explicit project scope. | `project_mismatch` |
| `SEL-004` | `eligible_state` | Candidate state must be one of the configured eligible states; domain adapters may preserve their existing equivalent reason code. | `state_not_ready` |
| `SEL-005` | `valid_priority` | Priority must be present in the canonical priority order. | `missing_or_invalid:{field}` |
| `SEL-006` | `valid_effort` | Effort must be present in the canonical effort order. | `missing_or_invalid:{field}` |
| `SEL-007` | `required_fields` | Configured readiness fields must be present before provider-backed selection. | `missing_required:{field}` |
| `SEL-008` | `unclaimed` | Already claimed work is excluded from next-work selection. | `already_claimed:{owner}` |
| `SEL-009` | `approval_complete` | Normalized-domain records that require approval must have completed approval. | `approval_incomplete` |
| `SEL-010` | `dependency_evidence` | Required provider dependency evidence must be observable. | `dependency_evidence_unavailable` |
| `SEL-011` | `dependencies_clear` | Provider-native blocker evidence must be empty; normalized-domain adapters preserve dependency-specific reason codes. | `native_dependency_blocking` |
| `SEL-012` | `ranking` | Eligible candidates rank by Priority, Effort, creation order, then stable record identity. | None |

## Source and authority

This page projects `KIS-WORK-DEC-SCR-001` version `1.0.0`. The MRD remains authoritative; this generated page has no write-back authority.
