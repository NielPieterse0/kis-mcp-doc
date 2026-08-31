<!-- GENERATED — DO NOT EDIT -->
# Work field and vocabulary reference

<div id="enable-section-numbers" />

[Owning specification chapter: Work Management domain model](002-work-management-domain-model.md) | [Documentation index](000-index.md)

> **Output class:** `generated_reference`. This page is an exact lookup projection of canonical Work Management authority. It has no write-back authority.

Work Management defines the fields and controlled vocabularies used to describe a work record. The model keeps command data separate from observed evidence so that a generated view cannot silently become a second source of truth.

## Field model

Work Management uses three authority directions. **Command** fields are changed through Work Management. **Evidence** fields are observed or projected from their owning source. **Handoff** fields start in Work Management and later become governed repository-change facts.

### Command fields

| Field | Meaning | Authority | Direction | Details |
|---|---|---|---|---|
| <span id="fact-field-status"></span>Status | Operational Work lifecycle status. Set by explicit Work lifecycle operations. | `work_management` | `command` | ID `status`; provider `single_select`; KIS-managed; applies to all record types; vocabulary `status` |
| <span id="fact-field-record-type"></span>Record Type | Purpose classification of the Work record. Set during intake/triage and changed only by explicit Work authority. | `work_management` | `command` | ID `record_type`; provider `single_select`; KIS-managed; applies to all record types; required for `ready_metadata`; vocabulary `record_type` |
| <span id="fact-field-priority"></span>Priority | Relative scheduling importance. Set by Work Management and consumed by selection ranking. | `work_management` | `command` | ID `priority`; provider `single_select`; KIS-managed; applies to all record types; required for `ready_metadata`; vocabulary `priority` |
| <span id="fact-field-effort"></span>Effort | Relative implementation or coordination effort. Set by Work Management and consumed by selection ranking. | `work_management` | `command` | ID `effort`; provider `single_select`; KIS-managed; applies to all record types; required for `ready_metadata`; vocabulary `effort` |
| <span id="fact-field-execution-owner"></span>Execution Owner | Stable identity of the current execution claimant. Set and cleared only by claim/release lifecycle operations. | `work_management` | `command` | ID `execution_owner`; provider `text`; KIS-managed; applies to all record types; required for `active_claim` |
| <span id="fact-field-origin"></span>Origin | Context that originated the record. Set when the Work record is created or classified. | `work_management` | `command` | ID `origin`; provider `single_select`; KIS-managed; applies to all record types; vocabulary `origin` |
| <span id="fact-field-disposition"></span>Disposition | Explicit decision disposition for records that use disposition semantics. Set by explicit Work decision/review operations. | `work_management` | `command` | ID `disposition`; provider `single_select`; KIS-managed; applies to all record types; vocabulary `disposition` |
| <span id="fact-field-severity"></span>Severity | Relative material impact for finding/risk records. Set when a finding or risk is classified. | `work_management` | `command` | ID `severity`; provider `single_select`; KIS-managed; applies to finding, security_finding, risk; required for `finding_or_risk`; vocabulary `severity` |
| <span id="fact-field-confidence"></span>Confidence | Evidence confidence for finding/assumption records. Set from the evidence quality supporting the record. | `work_management` | `command` | ID `confidence`; provider `single_select`; KIS-managed; applies to finding, security_finding, assumption; required for `finding_or_assumption`; vocabulary `confidence` |
| <span id="fact-field-review-trigger"></span>Review Trigger | Condition or date/event trigger for reconsidering paused work. Required when work enters On Hold or Deferred. | `work_management` | `command` | ID `review_trigger`; provider `text`; KIS-managed; applies to all record types; required for `hold_or_defer` |
| <span id="fact-field-target-date"></span>Target Date | Optional target date for planned work or reconsideration. Set explicitly by Work Management. | `work_management` | `command` | ID `target_date`; provider `date`; KIS-managed; applies to all record types |
| <span id="fact-field-iteration"></span>Iteration | Optional provider iteration assignment. Set explicitly by Work Management. | `work_management` | `command` | ID `iteration`; provider `iteration`; KIS-managed; applies to all record types |
| <span id="fact-field-source-review"></span>Source Review | Reference to the review source that produced or governs the record. Set when review-derived records are captured. | `work_management` | `command` | ID `source_review`; provider `text`; KIS-managed; applies to all record types |
| <span id="fact-field-external-link"></span>External Link | Optional bounded external reference associated with the work. Set explicitly by Work Management. | `work_management` | `command` | ID `external_link`; provider `text`; KIS-managed; applies to all record types |


### Evidence fields

| Field | Meaning | Authority | Direction | Details |
|---|---|---|---|---|
| <span id="fact-field-delivery-stage"></span>Delivery Stage | Evidence-derived governed delivery stage. Projected from repository/GitHub delivery evidence. | `derived` | `evidence` | ID `delivery_stage`; provider `single_select`; KIS-managed; applies to all record types; vocabulary `delivery_stage` |
| <span id="fact-field-blocked-by"></span>Blocked By | Provider-observed dependency or blocker reference; explicit empty differs from unavailable evidence. Read from GitHub Project dependency evidence. | `github` | `evidence` | ID `blocked_by`; provider `text`; KIS-managed; applies to all record types |
| <span id="fact-field-complexity"></span>Complexity | Repository change-governance complexity projected into Work. Projected from authoritative schema-v4 governed change scope. | `repository_change` | `evidence` | ID `complexity`; provider `single_select`; KIS-managed; applies to all record types; vocabulary `complexity` |
| <span id="fact-field-risk-triggers"></span>Risk Triggers | Comma-separated repository change-governance risk-trigger tokens. Projected from authoritative governed change scope. | `repository_change` | `evidence` | ID `risk_triggers`; provider `text`; KIS-managed; applies to all record types |
| <span id="fact-field-project-id"></span>Project ID | Stable KIS project registry identity for the work item. Derived from the registered repository-to-project mapping. | `derived` | `evidence` | ID `project_id`; provider `text`; KIS-managed; applies to all record types |
| <span id="fact-field-repository"></span>Repository | GitHub repository identity of the source item. Read from the GitHub source item/provider binding. | `github` | `evidence` | ID `repository`; provider `repository`; KIS-managed; applies to all record types |
| <span id="fact-field-change-id"></span>Change ID | Canonical governed repository change ID once one exists. Projected from authoritative local change scope. | `repository_change` | `evidence` | ID `change_id`; provider `text`; KIS-managed; applies to all record types; required for `governed_change` |
| <span id="fact-field-verification"></span>Verification | Repository/source verification state; never live-runtime commissioning state. Projected from provider-native or governed verification evidence. | `actions` | `evidence` | ID `verification`; provider `single_select`; KIS-managed; applies to all record types; vocabulary `verification` |
| <span id="fact-field-authority-revision"></span>Authority Revision | Revision identity of the authority evidence used for the Work record. Projected from Git/provider revision evidence. | `git` | `evidence` | ID `authority_revision`; provider `text`; KIS-managed; applies to all record types |
| <span id="fact-field-created"></span>Created | Provider-native creation timestamp used as deterministic age evidence. Read from GitHub native item metadata. | `github` | `evidence` | ID `created`; provider `native_datetime`; provider-managed; applies to all record types |
| <span id="fact-field-live-verification"></span>Live Verification | Post-merge live runtime verification state, distinct from source Verification. Projected by the deterministic commissioning lifecycle under #419. | `derived` | `evidence` | ID `live_verification`; provider `single_select`; KIS-managed; applies to all record types; vocabulary `live_verification` |
| <span id="fact-field-commissioning-key"></span>Commissioning Key | Deterministic commissioning identity: the exact obligation key for one required surface, or the deterministic set key for a source merge with multiple required surfaces. Derived by the commissioning classifier/runner under #419; source projection uses a set-<digest24> key when multiple obligations must be aggregated. | `derived` | `evidence` | ID `commissioning_key`; provider `text`; KIS-managed; applies to all record types |
| <span id="fact-field-live-verification-evidence"></span>Live Verification Evidence | Compact reference to durable live-verification evidence or linked commissioning work; never free-form logs. Projected from commissioning evidence under #419. | `derived` | `evidence` | ID `live_verification_evidence`; provider `text`; KIS-managed; applies to all record types |


### Handoff fields

| Field | Meaning | Authority | Direction | Details |
|---|---|---|---|---|
| <span id="fact-field-documentation-impact"></span>Documentation Impact | Expected or completed documentation impact for the work/change. Starts as Work command data and becomes governed change evidence. | `work_management_then_repository_change` | `handoff` | ID `documentation_impact`; provider `single_select`; KIS-managed; applies to all record types; required for `ready_metadata`; vocabulary `documentation_impact` |
| <span id="fact-field-module"></span>Module | Optional bounded module or subsystem context for the work. Set by Work and handed to governed change planning when applicable. | `work_management_then_repository_change` | `handoff` | ID `module`; provider `text`; KIS-managed; applies to all record types |


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
| <span id="fact-vocabulary-status-inbox"></span>Inbox | `inbox` | Captured work not yet triaged. |
| <span id="fact-vocabulary-status-triage"></span>Triage | `triage` | Work being classified and prepared for a disposition. |
| <span id="fact-vocabulary-status-proposed"></span>Proposed | `proposed` | Work proposed for acceptance but not yet approved. |
| <span id="fact-vocabulary-status-approved"></span>Approved | `approved` | Accepted work that is not yet admitted to the executable queue. |
| <span id="fact-vocabulary-status-ready"></span>Ready | `ready` | Work admitted for deterministic next-work eligibility subject to readiness, claim, and dependency guards. |
| <span id="fact-vocabulary-status-active"></span>Active | `active` | Work currently claimed for execution. |
| <span id="fact-vocabulary-status-blocked"></span>Blocked | `blocked` | Work that cannot proceed because a blocking condition is present. |
| <span id="fact-vocabulary-status-on-hold"></span>On Hold | `on_hold` | Work intentionally paused pending a declared review trigger. |
| <span id="fact-vocabulary-status-deferred"></span>Deferred | `deferred` | Work postponed for later reconsideration with a declared review trigger. |
| <span id="fact-vocabulary-status-rejected"></span>Rejected | `rejected` | Work explicitly not accepted for execution in its current form. |
| <span id="fact-vocabulary-status-superseded"></span>Superseded | `superseded` | Work replaced by a newer authoritative record or outcome. |
| <span id="fact-vocabulary-status-done"></span>Done | `done` | Work whose required completion and closeout gates are satisfied. |


### Record type values

Classification of the purpose of a Work record.

| Value | Token | Meaning |
|---|---|---|
| <span id="fact-vocabulary-record-type-idea"></span>Idea | `idea` | Uncommitted candidate work requiring triage before it becomes actionable. |
| <span id="fact-vocabulary-record-type-task"></span>Task | `task` | A bounded actionable unit of work. |
| <span id="fact-vocabulary-record-type-specification-slice"></span>Specification Slice | `specification_slice` | A bounded specification or delivery slice tracked as work. |
| <span id="fact-vocabulary-record-type-review-run"></span>Review Run | `review_run` | A record representing one review execution and its evidence. |
| <span id="fact-vocabulary-record-type-finding"></span>Finding | `finding` | An actionable observation produced by review, verification, audit, or commissioning. |
| <span id="fact-vocabulary-record-type-decision"></span>Decision | `decision` | A record of an explicit authoritative choice. |
| <span id="fact-vocabulary-record-type-assumption"></span>Assumption | `assumption` | A proposition tracked because later evidence may validate or invalidate it. |
| <span id="fact-vocabulary-record-type-risk"></span>Risk | `risk` | A potential adverse condition tracked for mitigation or disposition. |
| <span id="fact-vocabulary-record-type-approval"></span>Approval | `approval` | A record of an explicit approval decision. |
| <span id="fact-vocabulary-record-type-hold"></span>Hold | `hold` | A record whose purpose is to track a pause or hold condition. |
| <span id="fact-vocabulary-record-type-research"></span>Research | `research` | A bounded investigation intended to produce evidence or a decision. |
| <span id="fact-vocabulary-record-type-defect"></span>Defect | `defect` | A known incorrect or broken product or system behavior requiring correction. |
| <span id="fact-vocabulary-record-type-security-finding"></span>Security Finding | `security_finding` | A finding whose material impact is security-related. |


### Priority values

Relative scheduling importance used by the current deterministic Work queue.

| Value | Token | Meaning |
|---|---|---|
| <span id="fact-vocabulary-priority-critical"></span>Critical | `critical` | Highest configured scheduling importance. |
| <span id="fact-vocabulary-priority-high"></span>High | `high` | High scheduling importance below Critical. |
| <span id="fact-vocabulary-priority-medium"></span>Medium | `medium` | Normal scheduling importance below High. |
| <span id="fact-vocabulary-priority-low"></span>Low | `low` | Lowest configured scheduling importance. |


### Effort values

Relative implementation or coordination size used by the current deterministic Work queue.

| Value | Token | Meaning |
|---|---|---|
| <span id="fact-vocabulary-effort-tiny"></span>Tiny | `tiny` | Smallest configured relative effort. |
| <span id="fact-vocabulary-effort-small"></span>Small | `small` | Small relative effort. |
| <span id="fact-vocabulary-effort-medium"></span>Medium | `medium` | Moderate relative effort. |
| <span id="fact-vocabulary-effort-large"></span>Large | `large` | Largest configured relative effort. |


### Delivery stage values

Evidence-derived stage of governed repository delivery.

| Value | Token | Meaning |
|---|---|---|
| <span id="fact-vocabulary-delivery-stage-none"></span>None | `none` | No governed delivery stage has been established. |
| <span id="fact-vocabulary-delivery-stage-change-created"></span>Change Created | `change_created` | A governed repository change has been created. |
| <span id="fact-vocabulary-delivery-stage-implementing"></span>Implementing | `implementing` | Implementation is in progress. |
| <span id="fact-vocabulary-delivery-stage-pr-open"></span>PR Open | `pr_open` | A pull request is open for the governed change. |
| <span id="fact-vocabulary-delivery-stage-review"></span>Review | `review` | The governed change is in review. |
| <span id="fact-vocabulary-delivery-stage-ci-pending"></span>CI Pending | `ci_pending` | Provider-native verification is pending. |
| <span id="fact-vocabulary-delivery-stage-ci-failed"></span>CI Failed | `ci_failed` | Provider-native verification failed. |
| <span id="fact-vocabulary-delivery-stage-ci-passed"></span>CI Passed | `ci_passed` | Provider-native verification passed for the applicable head. |
| <span id="fact-vocabulary-delivery-stage-merged"></span>Merged | `merged` | The governed change has been observed merged. |
| <span id="fact-vocabulary-delivery-stage-documentation"></span>Documentation | `documentation` | Post-merge documentation reconciliation is due or in progress. |
| <span id="fact-vocabulary-delivery-stage-commissioning"></span>Commissioning | `commissioning` | Live verification or commissioning is pending or in progress. |
| <span id="fact-vocabulary-delivery-stage-complete"></span>Complete | `complete` | Delivery and required closeout evidence are complete. |


### Documentation impact values

Repository documentation impact projected from Work to governed change and back as evidence.

| Value | Token | Meaning |
|---|---|---|
| <span id="fact-vocabulary-documentation-impact-not-assessed"></span>Not Assessed | `not_assessed` | Documentation impact has not yet been assessed. |
| <span id="fact-vocabulary-documentation-impact-none"></span>None | `none` | No documentation change is required, with rationale recorded where required. |
| <span id="fact-vocabulary-documentation-impact-planned"></span>Planned | `planned` | Documentation changes are planned. |
| <span id="fact-vocabulary-documentation-impact-in-progress"></span>In Progress | `in_progress` | Documentation changes are being implemented. |
| <span id="fact-vocabulary-documentation-impact-pre-merge-complete"></span>Pre-merge Complete | `pre_merge_complete` | Required pre-merge documentation work is complete. |
| <span id="fact-vocabulary-documentation-impact-post-merge-complete"></span>Post-merge Complete | `post_merge_complete` | Required post-merge documentation reconciliation is complete. |


### Complexity values

Projection of repository change-governance complexity; detailed classification criteria remain owned by change-governance settings.

| Value | Token | Meaning |
|---|---|---|
| <span id="fact-vocabulary-complexity-small"></span>Small | `small` | Repository change-governance Small classification. |
| <span id="fact-vocabulary-complexity-medium"></span>Medium | `medium` | Repository change-governance Medium classification. |
| <span id="fact-vocabulary-complexity-large"></span>Large | `large` | Repository change-governance Large classification. |


### Origin values

Source context that caused a Work record to be created.

| Value | Token | Meaning |
|---|---|---|
| <span id="fact-vocabulary-origin-operator"></span>Operator | `operator` | Created directly from operator intent. |
| <span id="fact-vocabulary-origin-review"></span>Review | `review` | Created from review evidence. |
| <span id="fact-vocabulary-origin-verification"></span>Verification | `verification` | Created from verification evidence. |
| <span id="fact-vocabulary-origin-implementation"></span>Implementation | `implementation` | Created from implementation activity or discovery. |
| <span id="fact-vocabulary-origin-research"></span>Research | `research` | Created from research activity or evidence. |


### Disposition values

Current decision disposition for records that require an explicit disposition.

| Value | Token | Meaning |
|---|---|---|
| <span id="fact-vocabulary-disposition-open"></span>Open | `open` | No terminal disposition has been selected. |
| <span id="fact-vocabulary-disposition-accepted"></span>Accepted | `accepted` | The record or proposition is accepted. |
| <span id="fact-vocabulary-disposition-rejected"></span>Rejected | `rejected` | The record or proposition is rejected. |
| <span id="fact-vocabulary-disposition-superseded"></span>Superseded | `superseded` | A newer authoritative record replaces this one. |
| <span id="fact-vocabulary-disposition-mitigated"></span>Mitigated | `mitigated` | The tracked risk or finding has been mitigated. |
| <span id="fact-vocabulary-disposition-deferred"></span>Deferred | `deferred` | Disposition is intentionally postponed. |


### Verification values

Repository/source verification state; it does not represent post-merge live runtime proof.

| Value | Token | Meaning |
|---|---|---|
| <span id="fact-vocabulary-verification-not-run"></span>Not Run | `not_run` | Repository/source verification has not run. |
| <span id="fact-vocabulary-verification-pending"></span>Pending | `pending` | Repository/source verification is pending or running. |
| <span id="fact-vocabulary-verification-passed"></span>Passed | `passed` | Repository/source verification passed for the applicable evidence identity. |
| <span id="fact-vocabulary-verification-failed"></span>Failed | `failed` | Repository/source verification failed. |
| <span id="fact-vocabulary-verification-blocked"></span>Blocked | `blocked` | Repository/source verification cannot currently complete. |


### Severity values

Relative material impact of a finding or risk.

| Value | Token | Meaning |
|---|---|---|
| <span id="fact-vocabulary-severity-critical"></span>Critical | `critical` | Highest material impact requiring urgent attention. |
| <span id="fact-vocabulary-severity-high"></span>High | `high` | High material impact. |
| <span id="fact-vocabulary-severity-medium"></span>Medium | `medium` | Moderate material impact. |
| <span id="fact-vocabulary-severity-low"></span>Low | `low` | Limited material impact. |


### Confidence values

Relative confidence classification for finding and assumption evidence; current Work authority does not define quantitative or qualitative thresholds.

| Value | Token | Meaning |
|---|---|---|
| <span id="fact-vocabulary-confidence-high"></span>High | `high` | Highest configured confidence label; no additional threshold is defined by current Work authority. |
| <span id="fact-vocabulary-confidence-medium"></span>Medium | `medium` | Middle configured confidence label; no additional threshold is defined by current Work authority. |
| <span id="fact-vocabulary-confidence-low"></span>Low | `low` | Lowest configured confidence label; no additional threshold is defined by current Work authority. |


### Live verification values

Post-merge live runtime verification state, distinct from repository/source Verification.

| Value | Token | Meaning |
|---|---|---|
| <span id="fact-vocabulary-live-verification-not-assessed"></span>Not Assessed | `not_assessed` | The need for live verification has not yet been classified. |
| <span id="fact-vocabulary-live-verification-not-required"></span>Not Required | `not_required` | Deterministic classification found no live verification obligation. |
| <span id="fact-vocabulary-live-verification-pending"></span>Pending | `pending` | Live verification is required and has not yet completed. |
| <span id="fact-vocabulary-live-verification-passed"></span>Passed | `passed` | Required live verification passed against the actual exposed capability or runtime path. |
| <span id="fact-vocabulary-live-verification-failed"></span>Failed | `failed` | Required live verification ran and failed its expected invariant. |
| <span id="fact-vocabulary-live-verification-blocked"></span>Blocked | `blocked` | Required live verification cannot currently complete. |


## Source and authority

This page projects `urn:uuid:a0e914e6-64b0-561f-ad39-393287ce71c5` version `1.0.0`. The MRD remains authoritative; this generated page has no write-back authority.
