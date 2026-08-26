<!-- GENERATED — DO NOT EDIT -->
# Next-work selection

<div id="enable-section-numbers" />

[Previous: Work operations](004-work-operations.md) | [Next: Authority and reconciliation policy](006-authority-and-reconciliation-policy.md) | [Index](000-index.md)

<span id="mrd-kis-work-dec-scr-001"></span>

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
| <span id="fact-selection-rule-sel-001"></span>`SEL-001` | `source_issue` | Only issue records are eligible in the provider-backed next-work queue. | `not_issue` |
| <span id="fact-selection-rule-sel-002"></span>`SEL-002` | `source_open` | Provider-backed source issues must remain open. | `source_not_open` |
| <span id="fact-selection-rule-sel-003"></span>`SEL-003` | `project_match` | Normalized-domain selection respects an explicit project scope. | `project_mismatch` |
| <span id="fact-selection-rule-sel-004"></span>`SEL-004` | `eligible_state` | Candidate state must be one of the configured eligible states; domain adapters may preserve their existing equivalent reason code. | `state_not_ready` |
| <span id="fact-selection-rule-sel-005"></span>`SEL-005` | `valid_priority` | Priority must be present in the canonical priority order. | `missing_or_invalid:{field}` |
| <span id="fact-selection-rule-sel-006"></span>`SEL-006` | `valid_effort` | Effort must be present in the canonical effort order. | `missing_or_invalid:{field}` |
| <span id="fact-selection-rule-sel-007"></span>`SEL-007` | `required_fields` | Configured readiness fields must be present before provider-backed selection. | `missing_required:{field}` |
| <span id="fact-selection-rule-sel-008"></span>`SEL-008` | `unclaimed` | Already claimed work is excluded from next-work selection. | `already_claimed:{owner}` |
| <span id="fact-selection-rule-sel-009"></span>`SEL-009` | `approval_complete` | Normalized-domain records that require approval must have completed approval. | `approval_incomplete` |
| <span id="fact-selection-rule-sel-010"></span>`SEL-010` | `dependency_evidence` | Required provider dependency evidence must be observable. | `dependency_evidence_unavailable` |
| <span id="fact-selection-rule-sel-011"></span>`SEL-011` | `dependencies_clear` | Provider-native blocker evidence must be empty; normalized-domain adapters preserve dependency-specific reason codes. | `native_dependency_blocking` |
| <span id="fact-selection-rule-sel-012"></span>`SEL-012` | `ranking` | Eligible candidates rank by Priority, Effort, creation order, then stable record identity. | None |


## Source and authority

This page projects `KIS-WORK-DEC-SCR-001` version `1.0.0`. The MRD remains authoritative; this generated page has no write-back authority.
