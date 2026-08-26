<!-- GENERATED — DO NOT EDIT -->
# Work Management domain model

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

Work Management defines the fields and controlled vocabularies used to describe a work record. The model keeps command data separate from observed evidence so that a generated view cannot silently become a second source of truth.

## Field model

Work Management uses three authority directions. **Command** fields are changed through Work Management. **Evidence** fields are observed or projected from their owning source. **Handoff** fields start in Work Management and later become governed repository-change facts.

### Command fields

| Field | Meaning | Authority | Direction | Details |
|---|---|---|---|---|
| Status | Operational Work lifecycle status. Set by explicit Work lifecycle operations. | `work_management` | `command` | ID `status`; provider `single_select`; KIS-managed; applies to all record types; vocabulary `status` |
| Record Type | Purpose classification of the Work record. Set during intake/triage and changed only by explicit Work authority. | `work_management` | `command` | ID `record_type`; provider `single_select`; KIS-managed; applies to all record types; required for `ready_metadata`; vocabulary `record_type` |
| Priority | Relative scheduling importance. Set by Work Management and consumed by selection ranking. | `work_management` | `command` | ID `priority`; provider `single_select`; KIS-managed; applies to all record types; required for `ready_metadata`; vocabulary `priority` |
| Effort | Relative implementation or coordination effort. Set by Work Management and consumed by selection ranking. | `work_management` | `command` | ID `effort`; provider `single_select`; KIS-managed; applies to all record types; required for `ready_metadata`; vocabulary `effort` |
| Execution Owner | Stable identity of the current execution claimant. Set and cleared only by claim/release lifecycle operations. | `work_management` | `command` | ID `execution_owner`; provider `text`; KIS-managed; applies to all record types; required for `active_claim` |
| Origin | Context that originated the record. Set when the Work record is created or classified. | `work_management` | `command` | ID `origin`; provider `single_select`; KIS-managed; applies to all record types; vocabulary `origin` |
| Disposition | Explicit decision disposition for records that use disposition semantics. Set by explicit Work decision/review operations. | `work_management` | `command` | ID `disposition`; provider `single_select`; KIS-managed; applies to all record types; vocabulary `disposition` |
| Severity | Relative material impact for finding/risk records. Set when a finding or risk is classified. | `work_management` | `command` | ID `severity`; provider `single_select`; KIS-managed; applies to finding, security_finding, risk; required for `finding_or_risk`; vocabulary `severity` |
| Confidence | Evidence confidence for finding/assumption records. Set from the evidence quality supporting the record. | `work_management` | `command` | ID `confidence`; provider `single_select`; KIS-managed; applies to finding, security_finding, assumption; required for `finding_or_assumption`; vocabulary `confidence` |
| Review Trigger | Condition or date/event trigger for reconsidering paused work. Required when work enters On Hold or Deferred. | `work_management` | `command` | ID `review_trigger`; provider `text`; KIS-managed; applies to all record types; required for `hold_or_defer` |
| Target Date | Optional target date for planned work or reconsideration. Set explicitly by Work Management. | `work_management` | `command` | ID `target_date`; provider `date`; KIS-managed; applies to all record types |
| Iteration | Optional provider iteration assignment. Set explicitly by Work Management. | `work_management` | `command` | ID `iteration`; provider `iteration`; KIS-managed; applies to all record types |
| Source Review | Reference to the review source that produced or governs the record. Set when review-derived records are captured. | `work_management` | `command` | ID `source_review`; provider `text`; KIS-managed; applies to all record types |
| External Link | Optional bounded external reference associated with the work. Set explicitly by Work Management. | `work_management` | `command` | ID `external_link`; provider `text`; KIS-managed; applies to all record types |

### Evidence fields

| Field | Meaning | Authority | Direction | Details |
|---|---|---|---|---|
| Delivery Stage | Evidence-derived governed delivery stage. Projected from repository/GitHub delivery evidence. | `derived` | `evidence` | ID `delivery_stage`; provider `single_select`; KIS-managed; applies to all record types; vocabulary `delivery_stage` |
| Blocked By | Provider-observed dependency or blocker reference; explicit empty differs from unavailable evidence. Read from GitHub Project dependency evidence. | `github` | `evidence` | ID `blocked_by`; provider `text`; KIS-managed; applies to all record types |
| Complexity | Repository change-governance complexity projected into Work. Projected from authoritative schema-v4 governed change scope. | `repository_change` | `evidence` | ID `complexity`; provider `single_select`; KIS-managed; applies to all record types; vocabulary `complexity` |
| Risk Triggers | Comma-separated repository change-governance risk-trigger tokens. Projected from authoritative governed change scope. | `repository_change` | `evidence` | ID `risk_triggers`; provider `text`; KIS-managed; applies to all record types |
| Project ID | Stable KIS project registry identity for the work item. Derived from the registered repository-to-project mapping. | `derived` | `evidence` | ID `project_id`; provider `text`; KIS-managed; applies to all record types |
| Repository | GitHub repository identity of the source item. Read from the GitHub source item/provider binding. | `github` | `evidence` | ID `repository`; provider `repository`; KIS-managed; applies to all record types |
| Change ID | Canonical governed repository change ID once one exists. Projected from authoritative local change scope. | `repository_change` | `evidence` | ID `change_id`; provider `text`; KIS-managed; applies to all record types; required for `governed_change` |
| Verification | Repository/source verification state; never live-runtime commissioning state. Projected from provider-native or governed verification evidence. | `actions` | `evidence` | ID `verification`; provider `single_select`; KIS-managed; applies to all record types; vocabulary `verification` |
| Authority Revision | Revision identity of the authority evidence used for the Work record. Projected from Git/provider revision evidence. | `git` | `evidence` | ID `authority_revision`; provider `text`; KIS-managed; applies to all record types |
| Created | Provider-native creation timestamp used as deterministic age evidence. Read from GitHub native item metadata. | `github` | `evidence` | ID `created`; provider `native_datetime`; provider-managed; applies to all record types |
| Live Verification | Post-merge live runtime verification state, distinct from source Verification. Projected by the deterministic commissioning lifecycle under #419. | `derived` | `evidence` | ID `live_verification`; provider `single_select`; KIS-managed; applies to all record types; vocabulary `live_verification` |
| Commissioning Key | Deterministic commissioning identity: the exact obligation key for one required surface, or the deterministic set key for a source merge with multiple required surfaces. Derived by the commissioning classifier/runner under #419; source projection uses a set-<digest24> key when multiple obligations must be aggregated. | `derived` | `evidence` | ID `commissioning_key`; provider `text`; KIS-managed; applies to all record types |
| Live Verification Evidence | Compact reference to durable live-verification evidence or linked commissioning work; never free-form logs. Projected from commissioning evidence under #419. | `derived` | `evidence` | ID `live_verification_evidence`; provider `text`; KIS-managed; applies to all record types |

### Handoff fields

| Field | Meaning | Authority | Direction | Details |
|---|---|---|---|---|
| Documentation Impact | Expected or completed documentation impact for the work/change. Starts as Work command data and becomes governed change evidence. | `work_management_then_repository_change` | `handoff` | ID `documentation_impact`; provider `single_select`; KIS-managed; applies to all record types; required for `ready_metadata`; vocabulary `documentation_impact` |
| Module | Optional bounded module or subsystem context for the work. Set by Work and handed to governed change planning when applicable. | `work_management_then_repository_change` | `handoff` | ID `module`; provider `text`; KIS-managed; applies to all record types |

## Authority rules

These rules prevent field ownership from drifting between Work Management, repository change governance, GitHub, Actions, and generated documentation:

- Every managed field has one authority and one direction.
- Project-native evidence is observed, not redefined by generated documentation.

## Controlled vocabularies

Single-select fields use the following governed values. The display label is what readers see; the token is the stable machine value.

### Status values

Operational Work lifecycle status projected to GitHub Project Status.

| Value | Token | Meaning |
|---|---|---|
| Inbox | `inbox` | Captured work not yet triaged. |
| Triage | `triage` | Work being classified and prepared for a disposition. |
| Proposed | `proposed` | Work proposed for acceptance but not yet approved. |
| Approved | `approved` | Accepted work that is not yet admitted to the executable queue. |
| Ready | `ready` | Work admitted for deterministic next-work eligibility subject to readiness, claim, and dependency guards. |
| Active | `active` | Work currently claimed for execution. |
| Blocked | `blocked` | Work that cannot proceed because a blocking condition is present. |
| On Hold | `on_hold` | Work intentionally paused pending a declared review trigger. |
| Deferred | `deferred` | Work postponed for later reconsideration with a declared review trigger. |
| Rejected | `rejected` | Work explicitly not accepted for execution in its current form. |
| Superseded | `superseded` | Work replaced by a newer authoritative record or outcome. |
| Done | `done` | Work whose required completion and closeout gates are satisfied. |

### Record type values

Classification of the purpose of a Work record.

| Value | Token | Meaning |
|---|---|---|
| Idea | `idea` | Uncommitted candidate work requiring triage before it becomes actionable. |
| Task | `task` | A bounded actionable unit of work. |
| Specification Slice | `specification_slice` | A bounded specification or delivery slice tracked as work. |
| Review Run | `review_run` | A record representing one review execution and its evidence. |
| Finding | `finding` | An actionable observation produced by review, verification, audit, or commissioning. |
| Decision | `decision` | A record of an explicit authoritative choice. |
| Assumption | `assumption` | A proposition tracked because later evidence may validate or invalidate it. |
| Risk | `risk` | A potential adverse condition tracked for mitigation or disposition. |
| Approval | `approval` | A record of an explicit approval decision. |
| Hold | `hold` | A record whose purpose is to track a pause or hold condition. |
| Research | `research` | A bounded investigation intended to produce evidence or a decision. |
| Defect | `defect` | A known incorrect or broken product or system behavior requiring correction. |
| Security Finding | `security_finding` | A finding whose material impact is security-related. |

### Priority values

Relative scheduling importance used by the current deterministic Work queue.

| Value | Token | Meaning |
|---|---|---|
| Critical | `critical` | Highest configured scheduling importance. |
| High | `high` | High scheduling importance below Critical. |
| Medium | `medium` | Normal scheduling importance below High. |
| Low | `low` | Lowest configured scheduling importance. |

### Effort values

Relative implementation or coordination size used by the current deterministic Work queue.

| Value | Token | Meaning |
|---|---|---|
| Tiny | `tiny` | Smallest configured relative effort. |
| Small | `small` | Small relative effort. |
| Medium | `medium` | Moderate relative effort. |
| Large | `large` | Largest configured relative effort. |

### Delivery stage values

Evidence-derived stage of governed repository delivery.

| Value | Token | Meaning |
|---|---|---|
| None | `none` | No governed delivery stage has been established. |
| Change Created | `change_created` | A governed repository change has been created. |
| Implementing | `implementing` | Implementation is in progress. |
| PR Open | `pr_open` | A pull request is open for the governed change. |
| Review | `review` | The governed change is in review. |
| CI Pending | `ci_pending` | Provider-native verification is pending. |
| CI Failed | `ci_failed` | Provider-native verification failed. |
| CI Passed | `ci_passed` | Provider-native verification passed for the applicable head. |
| Merged | `merged` | The governed change has been observed merged. |
| Documentation | `documentation` | Post-merge documentation reconciliation is due or in progress. |
| Commissioning | `commissioning` | Live verification or commissioning is pending or in progress. |
| Complete | `complete` | Delivery and required closeout evidence are complete. |

### Documentation impact values

Repository documentation impact projected from Work to governed change and back as evidence.

| Value | Token | Meaning |
|---|---|---|
| Not Assessed | `not_assessed` | Documentation impact has not yet been assessed. |
| None | `none` | No documentation change is required, with rationale recorded where required. |
| Planned | `planned` | Documentation changes are planned. |
| In Progress | `in_progress` | Documentation changes are being implemented. |
| Pre-merge Complete | `pre_merge_complete` | Required pre-merge documentation work is complete. |
| Post-merge Complete | `post_merge_complete` | Required post-merge documentation reconciliation is complete. |

### Complexity values

Projection of repository change-governance complexity; detailed classification criteria remain owned by change-governance settings.

| Value | Token | Meaning |
|---|---|---|
| Small | `small` | Repository change-governance Small classification. |
| Medium | `medium` | Repository change-governance Medium classification. |
| Large | `large` | Repository change-governance Large classification. |

### Origin values

Source context that caused a Work record to be created.

| Value | Token | Meaning |
|---|---|---|
| Operator | `operator` | Created directly from operator intent. |
| Review | `review` | Created from review evidence. |
| Verification | `verification` | Created from verification evidence. |
| Implementation | `implementation` | Created from implementation activity or discovery. |
| Research | `research` | Created from research activity or evidence. |

### Disposition values

Current decision disposition for records that require an explicit disposition.

| Value | Token | Meaning |
|---|---|---|
| Open | `open` | No terminal disposition has been selected. |
| Accepted | `accepted` | The record or proposition is accepted. |
| Rejected | `rejected` | The record or proposition is rejected. |
| Superseded | `superseded` | A newer authoritative record replaces this one. |
| Mitigated | `mitigated` | The tracked risk or finding has been mitigated. |
| Deferred | `deferred` | Disposition is intentionally postponed. |

### Verification values

Repository/source verification state; it does not represent post-merge live runtime proof.

| Value | Token | Meaning |
|---|---|---|
| Not Run | `not_run` | Repository/source verification has not run. |
| Pending | `pending` | Repository/source verification is pending or running. |
| Passed | `passed` | Repository/source verification passed for the applicable evidence identity. |
| Failed | `failed` | Repository/source verification failed. |
| Blocked | `blocked` | Repository/source verification cannot currently complete. |

### Severity values

Relative material impact of a finding or risk.

| Value | Token | Meaning |
|---|---|---|
| Critical | `critical` | Highest material impact requiring urgent attention. |
| High | `high` | High material impact. |
| Medium | `medium` | Moderate material impact. |
| Low | `low` | Limited material impact. |

### Confidence values

Relative confidence classification for finding and assumption evidence; current Work authority does not define quantitative or qualitative thresholds.

| Value | Token | Meaning |
|---|---|---|
| High | `high` | Highest configured confidence label; no additional threshold is defined by current Work authority. |
| Medium | `medium` | Middle configured confidence label; no additional threshold is defined by current Work authority. |
| Low | `low` | Lowest configured confidence label; no additional threshold is defined by current Work authority. |

### Live verification values

Post-merge live runtime verification state, distinct from repository/source Verification.

| Value | Token | Meaning |
|---|---|---|
| Not Assessed | `not_assessed` | The need for live verification has not yet been classified. |
| Not Required | `not_required` | Deterministic classification found no live verification obligation. |
| Pending | `pending` | Live verification is required and has not yet completed. |
| Passed | `passed` | Required live verification passed against the actual exposed capability or runtime path. |
| Failed | `failed` | Required live verification ran and failed its expected invariant. |
| Blocked | `blocked` | Required live verification cannot currently complete. |

## Source and authority

This page projects `KIS-WORK-SEM-REG-001` version `1.0.0`. The MRD remains authoritative; this generated page has no write-back authority.
