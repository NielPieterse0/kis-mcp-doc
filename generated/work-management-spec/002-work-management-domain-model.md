<!-- GENERATED — DO NOT EDIT -->
# Work Management domain model

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

Define canonical Work Management entities, fields, vocabularies, and authority directions.

## Fields

### Status

**Applicable record types:** *

**Authority:** work_management

**Definition:** Operational Work lifecycle status.

**Direction:** command

**Id:** status

**Managed:** Yes

**Population:** Set by explicit Work lifecycle operations.

**Provider type:** single_select

**Required contexts:** None

**Vocabulary:** status

### Record Type

**Applicable record types:** *

**Authority:** work_management

**Definition:** Purpose classification of the Work record.

**Direction:** command

**Id:** record_type

**Managed:** Yes

**Population:** Set during intake/triage and changed only by explicit Work authority.

**Provider type:** single_select

**Required contexts:** ready_metadata

**Vocabulary:** record_type

### Priority

**Applicable record types:** *

**Authority:** work_management

**Definition:** Relative scheduling importance.

**Direction:** command

**Id:** priority

**Managed:** Yes

**Population:** Set by Work Management and consumed by selection ranking.

**Provider type:** single_select

**Required contexts:** ready_metadata

**Vocabulary:** priority

### Effort

**Applicable record types:** *

**Authority:** work_management

**Definition:** Relative implementation or coordination effort.

**Direction:** command

**Id:** effort

**Managed:** Yes

**Population:** Set by Work Management and consumed by selection ranking.

**Provider type:** single_select

**Required contexts:** ready_metadata

**Vocabulary:** effort

### Delivery Stage

**Applicable record types:** *

**Authority:** derived

**Definition:** Evidence-derived governed delivery stage.

**Direction:** evidence

**Id:** delivery_stage

**Managed:** Yes

**Population:** Projected from repository/GitHub delivery evidence.

**Provider type:** single_select

**Required contexts:** None

**Vocabulary:** delivery_stage

### Execution Owner

**Applicable record types:** *

**Authority:** work_management

**Definition:** Stable identity of the current execution claimant.

**Direction:** command

**Id:** execution_owner

**Managed:** Yes

**Population:** Set and cleared only by claim/release lifecycle operations.

**Provider type:** text

**Required contexts:** active_claim

**Vocabulary:** None

### Blocked By

**Applicable record types:** *

**Authority:** github

**Definition:** Provider-observed dependency or blocker reference; explicit empty differs from unavailable evidence.

**Direction:** evidence

**Id:** blocked_by

**Managed:** Yes

**Population:** Read from GitHub Project dependency evidence.

**Provider type:** text

**Required contexts:** None

**Vocabulary:** None

### Documentation Impact

**Applicable record types:** *

**Authority:** work_management_then_repository_change

**Definition:** Expected or completed documentation impact for the work/change.

**Direction:** handoff

**Id:** documentation_impact

**Managed:** Yes

**Population:** Starts as Work command data and becomes governed change evidence.

**Provider type:** single_select

**Required contexts:** ready_metadata

**Vocabulary:** documentation_impact

### Complexity

**Applicable record types:** *

**Authority:** repository_change

**Definition:** Repository change-governance complexity projected into Work.

**Direction:** evidence

**Id:** complexity

**Managed:** Yes

**Population:** Projected from authoritative schema-v4 governed change scope.

**Provider type:** single_select

**Required contexts:** None

**Vocabulary:** complexity

### Risk Triggers

**Applicable record types:** *

**Authority:** repository_change

**Definition:** Comma-separated repository change-governance risk-trigger tokens.

**Direction:** evidence

**Id:** risk_triggers

**Managed:** Yes

**Population:** Projected from authoritative governed change scope.

**Provider type:** text

**Required contexts:** None

**Vocabulary:** None

### Project ID

**Applicable record types:** *

**Authority:** derived

**Definition:** Stable KIS project registry identity for the work item.

**Direction:** evidence

**Id:** project_id

**Managed:** Yes

**Population:** Derived from the registered repository-to-project mapping.

**Provider type:** text

**Required contexts:** None

**Vocabulary:** None

### Repository

**Applicable record types:** *

**Authority:** github

**Definition:** GitHub repository identity of the source item.

**Direction:** evidence

**Id:** repository

**Managed:** Yes

**Population:** Read from the GitHub source item/provider binding.

**Provider type:** repository

**Required contexts:** None

**Vocabulary:** None

### Module

**Applicable record types:** *

**Authority:** work_management_then_repository_change

**Definition:** Optional bounded module or subsystem context for the work.

**Direction:** handoff

**Id:** module

**Managed:** Yes

**Population:** Set by Work and handed to governed change planning when applicable.

**Provider type:** text

**Required contexts:** None

**Vocabulary:** None

### Change ID

**Applicable record types:** *

**Authority:** repository_change

**Definition:** Canonical governed repository change ID once one exists.

**Direction:** evidence

**Id:** change_id

**Managed:** Yes

**Population:** Projected from authoritative local change scope.

**Provider type:** text

**Required contexts:** governed_change

**Vocabulary:** None

### Origin

**Applicable record types:** *

**Authority:** work_management

**Definition:** Context that originated the record.

**Direction:** command

**Id:** origin

**Managed:** Yes

**Population:** Set when the Work record is created or classified.

**Provider type:** single_select

**Required contexts:** None

**Vocabulary:** origin

### Disposition

**Applicable record types:** *

**Authority:** work_management

**Definition:** Explicit decision disposition for records that use disposition semantics.

**Direction:** command

**Id:** disposition

**Managed:** Yes

**Population:** Set by explicit Work decision/review operations.

**Provider type:** single_select

**Required contexts:** None

**Vocabulary:** disposition

### Verification

**Applicable record types:** *

**Authority:** actions

**Definition:** Repository/source verification state; never live-runtime commissioning state.

**Direction:** evidence

**Id:** verification

**Managed:** Yes

**Population:** Projected from provider-native or governed verification evidence.

**Provider type:** single_select

**Required contexts:** None

**Vocabulary:** verification

### Severity

**Applicable record types:** finding, security_finding, risk

**Authority:** work_management

**Definition:** Relative material impact for finding/risk records.

**Direction:** command

**Id:** severity

**Managed:** Yes

**Population:** Set when a finding or risk is classified.

**Provider type:** single_select

**Required contexts:** finding_or_risk

**Vocabulary:** severity

### Confidence

**Applicable record types:** finding, security_finding, assumption

**Authority:** work_management

**Definition:** Evidence confidence for finding/assumption records.

**Direction:** command

**Id:** confidence

**Managed:** Yes

**Population:** Set from the evidence quality supporting the record.

**Provider type:** single_select

**Required contexts:** finding_or_assumption

**Vocabulary:** confidence

### Review Trigger

**Applicable record types:** *

**Authority:** work_management

**Definition:** Condition or date/event trigger for reconsidering paused work.

**Direction:** command

**Id:** review_trigger

**Managed:** Yes

**Population:** Required when work enters On Hold or Deferred.

**Provider type:** text

**Required contexts:** hold_or_defer

**Vocabulary:** None

### Target Date

**Applicable record types:** *

**Authority:** work_management

**Definition:** Optional target date for planned work or reconsideration.

**Direction:** command

**Id:** target_date

**Managed:** Yes

**Population:** Set explicitly by Work Management.

**Provider type:** date

**Required contexts:** None

**Vocabulary:** None

### Iteration

**Applicable record types:** *

**Authority:** work_management

**Definition:** Optional provider iteration assignment.

**Direction:** command

**Id:** iteration

**Managed:** Yes

**Population:** Set explicitly by Work Management.

**Provider type:** iteration

**Required contexts:** None

**Vocabulary:** None

### Source Review

**Applicable record types:** *

**Authority:** work_management

**Definition:** Reference to the review source that produced or governs the record.

**Direction:** command

**Id:** source_review

**Managed:** Yes

**Population:** Set when review-derived records are captured.

**Provider type:** text

**Required contexts:** None

**Vocabulary:** None

### Authority Revision

**Applicable record types:** *

**Authority:** git

**Definition:** Revision identity of the authority evidence used for the Work record.

**Direction:** evidence

**Id:** authority_revision

**Managed:** Yes

**Population:** Projected from Git/provider revision evidence.

**Provider type:** text

**Required contexts:** None

**Vocabulary:** None

### External Link

**Applicable record types:** *

**Authority:** work_management

**Definition:** Optional bounded external reference associated with the work.

**Direction:** command

**Id:** external_link

**Managed:** Yes

**Population:** Set explicitly by Work Management.

**Provider type:** text

**Required contexts:** None

**Vocabulary:** None

### Created

**Applicable record types:** *

**Authority:** github

**Definition:** Provider-native creation timestamp used as deterministic age evidence.

**Direction:** evidence

**Id:** created

**Managed:** No

**Population:** Read from GitHub native item metadata.

**Provider type:** native_datetime

**Required contexts:** None

**Vocabulary:** None

### Live Verification

**Applicable record types:** *

**Authority:** derived

**Definition:** Post-merge live runtime verification state, distinct from source Verification.

**Direction:** evidence

**Id:** live_verification

**Managed:** Yes

**Population:** Projected by the deterministic commissioning lifecycle under #419.

**Provider type:** single_select

**Required contexts:** None

**Vocabulary:** live_verification

### Commissioning Key

**Applicable record types:** *

**Authority:** derived

**Definition:** Deterministic commissioning identity: the exact obligation key for one required surface, or the deterministic set key for a source merge with multiple required surfaces.

**Direction:** evidence

**Id:** commissioning_key

**Managed:** Yes

**Population:** Derived by the commissioning classifier/runner under #419; source projection uses a set-<digest24> key when multiple obligations must be aggregated.

**Provider type:** text

**Required contexts:** None

**Vocabulary:** None

### Live Verification Evidence

**Applicable record types:** *

**Authority:** derived

**Definition:** Compact reference to durable live-verification evidence or linked commissioning work; never free-form logs.

**Direction:** evidence

**Id:** live_verification_evidence

**Managed:** Yes

**Population:** Projected from commissioning evidence under #419.

**Provider type:** text

**Required contexts:** None

**Vocabulary:** None

## Rules

Every managed field has one authority and one direction., Project-native evidence is observed, not redefined by generated documentation.

## Vocabularies

### status

**Definition:** Operational Work lifecycle status projected to GitHub Project Status.

**Id:** status

#### Values

##### Inbox

**Definition:** Captured work not yet triaged.

**Token:** inbox

##### Triage

**Definition:** Work being classified and prepared for a disposition.

**Token:** triage

##### Proposed

**Definition:** Work proposed for acceptance but not yet approved.

**Token:** proposed

##### Approved

**Definition:** Accepted work that is not yet admitted to the executable queue.

**Token:** approved

##### Ready

**Definition:** Work admitted for deterministic next-work eligibility subject to readiness, claim, and dependency guards.

**Token:** ready

##### Active

**Definition:** Work currently claimed for execution.

**Token:** active

##### Blocked

**Definition:** Work that cannot proceed because a blocking condition is present.

**Token:** blocked

##### On Hold

**Definition:** Work intentionally paused pending a declared review trigger.

**Token:** on_hold

##### Deferred

**Definition:** Work postponed for later reconsideration with a declared review trigger.

**Token:** deferred

##### Rejected

**Definition:** Work explicitly not accepted for execution in its current form.

**Token:** rejected

##### Superseded

**Definition:** Work replaced by a newer authoritative record or outcome.

**Token:** superseded

##### Done

**Definition:** Work whose required completion and closeout gates are satisfied.

**Token:** done

### record type

**Definition:** Classification of the purpose of a Work record.

**Id:** record_type

#### Values

##### Idea

**Definition:** Uncommitted candidate work requiring triage before it becomes actionable.

**Token:** idea

##### Task

**Definition:** A bounded actionable unit of work.

**Token:** task

##### Specification Slice

**Definition:** A bounded specification or delivery slice tracked as work.

**Token:** specification_slice

##### Review Run

**Definition:** A record representing one review execution and its evidence.

**Token:** review_run

##### Finding

**Definition:** An actionable observation produced by review, verification, audit, or commissioning.

**Token:** finding

##### Decision

**Definition:** A record of an explicit authoritative choice.

**Token:** decision

##### Assumption

**Definition:** A proposition tracked because later evidence may validate or invalidate it.

**Token:** assumption

##### Risk

**Definition:** A potential adverse condition tracked for mitigation or disposition.

**Token:** risk

##### Approval

**Definition:** A record of an explicit approval decision.

**Token:** approval

##### Hold

**Definition:** A record whose purpose is to track a pause or hold condition.

**Token:** hold

##### Research

**Definition:** A bounded investigation intended to produce evidence or a decision.

**Token:** research

##### Defect

**Definition:** A known incorrect or broken product or system behavior requiring correction.

**Token:** defect

##### Security Finding

**Definition:** A finding whose material impact is security-related.

**Token:** security_finding

### priority

**Definition:** Relative scheduling importance used by the current deterministic Work queue.

**Id:** priority

#### Values

##### Critical

**Definition:** Highest configured scheduling importance.

**Token:** critical

##### High

**Definition:** High scheduling importance below Critical.

**Token:** high

##### Medium

**Definition:** Normal scheduling importance below High.

**Token:** medium

##### Low

**Definition:** Lowest configured scheduling importance.

**Token:** low

### effort

**Definition:** Relative implementation or coordination size used by the current deterministic Work queue.

**Id:** effort

#### Values

##### Tiny

**Definition:** Smallest configured relative effort.

**Token:** tiny

##### Small

**Definition:** Small relative effort.

**Token:** small

##### Medium

**Definition:** Moderate relative effort.

**Token:** medium

##### Large

**Definition:** Largest configured relative effort.

**Token:** large

### delivery stage

**Definition:** Evidence-derived stage of governed repository delivery.

**Id:** delivery_stage

#### Values

##### None

**Definition:** No governed delivery stage has been established.

**Token:** none

##### Change Created

**Definition:** A governed repository change has been created.

**Token:** change_created

##### Implementing

**Definition:** Implementation is in progress.

**Token:** implementing

##### PR Open

**Definition:** A pull request is open for the governed change.

**Token:** pr_open

##### Review

**Definition:** The governed change is in review.

**Token:** review

##### CI Pending

**Definition:** Provider-native verification is pending.

**Token:** ci_pending

##### CI Failed

**Definition:** Provider-native verification failed.

**Token:** ci_failed

##### CI Passed

**Definition:** Provider-native verification passed for the applicable head.

**Token:** ci_passed

##### Merged

**Definition:** The governed change has been observed merged.

**Token:** merged

##### Documentation

**Definition:** Post-merge documentation reconciliation is due or in progress.

**Token:** documentation

##### Commissioning

**Definition:** Live verification or commissioning is pending or in progress.

**Token:** commissioning

##### Complete

**Definition:** Delivery and required closeout evidence are complete.

**Token:** complete

### documentation impact

**Definition:** Repository documentation impact projected from Work to governed change and back as evidence.

**Id:** documentation_impact

#### Values

##### Not Assessed

**Definition:** Documentation impact has not yet been assessed.

**Token:** not_assessed

##### None

**Definition:** No documentation change is required, with rationale recorded where required.

**Token:** none

##### Planned

**Definition:** Documentation changes are planned.

**Token:** planned

##### In Progress

**Definition:** Documentation changes are being implemented.

**Token:** in_progress

##### Pre-merge Complete

**Definition:** Required pre-merge documentation work is complete.

**Token:** pre_merge_complete

##### Post-merge Complete

**Definition:** Required post-merge documentation reconciliation is complete.

**Token:** post_merge_complete

### complexity

**Definition:** Projection of repository change-governance complexity; detailed classification criteria remain owned by change-governance settings.

**Id:** complexity

#### Values

##### Small

**Definition:** Repository change-governance Small classification.

**Token:** small

##### Medium

**Definition:** Repository change-governance Medium classification.

**Token:** medium

##### Large

**Definition:** Repository change-governance Large classification.

**Token:** large

### origin

**Definition:** Source context that caused a Work record to be created.

**Id:** origin

#### Values

##### Operator

**Definition:** Created directly from operator intent.

**Token:** operator

##### Review

**Definition:** Created from review evidence.

**Token:** review

##### Verification

**Definition:** Created from verification evidence.

**Token:** verification

##### Implementation

**Definition:** Created from implementation activity or discovery.

**Token:** implementation

##### Research

**Definition:** Created from research activity or evidence.

**Token:** research

### disposition

**Definition:** Current decision disposition for records that require an explicit disposition.

**Id:** disposition

#### Values

##### Open

**Definition:** No terminal disposition has been selected.

**Token:** open

##### Accepted

**Definition:** The record or proposition is accepted.

**Token:** accepted

##### Rejected

**Definition:** The record or proposition is rejected.

**Token:** rejected

##### Superseded

**Definition:** A newer authoritative record replaces this one.

**Token:** superseded

##### Mitigated

**Definition:** The tracked risk or finding has been mitigated.

**Token:** mitigated

##### Deferred

**Definition:** Disposition is intentionally postponed.

**Token:** deferred

### verification

**Definition:** Repository/source verification state; it does not represent post-merge live runtime proof.

**Id:** verification

#### Values

##### Not Run

**Definition:** Repository/source verification has not run.

**Token:** not_run

##### Pending

**Definition:** Repository/source verification is pending or running.

**Token:** pending

##### Passed

**Definition:** Repository/source verification passed for the applicable evidence identity.

**Token:** passed

##### Failed

**Definition:** Repository/source verification failed.

**Token:** failed

##### Blocked

**Definition:** Repository/source verification cannot currently complete.

**Token:** blocked

### severity

**Definition:** Relative material impact of a finding or risk.

**Id:** severity

#### Values

##### Critical

**Definition:** Highest material impact requiring urgent attention.

**Token:** critical

##### High

**Definition:** High material impact.

**Token:** high

##### Medium

**Definition:** Moderate material impact.

**Token:** medium

##### Low

**Definition:** Limited material impact.

**Token:** low

### confidence

**Definition:** Relative confidence classification for finding and assumption evidence; current Work authority does not define quantitative or qualitative thresholds.

**Id:** confidence

#### Values

##### High

**Definition:** Highest configured confidence label; no additional threshold is defined by current Work authority.

**Token:** high

##### Medium

**Definition:** Middle configured confidence label; no additional threshold is defined by current Work authority.

**Token:** medium

##### Low

**Definition:** Lowest configured confidence label; no additional threshold is defined by current Work authority.

**Token:** low

### live verification

**Definition:** Post-merge live runtime verification state, distinct from repository/source Verification.

**Id:** live_verification

#### Values

##### Not Assessed

**Definition:** The need for live verification has not yet been classified.

**Token:** not_assessed

##### Not Required

**Definition:** Deterministic classification found no live verification obligation.

**Token:** not_required

##### Pending

**Definition:** Live verification is required and has not yet completed.

**Token:** pending

##### Passed

**Definition:** Required live verification passed against the actual exposed capability or runtime path.

**Token:** passed

##### Failed

**Definition:** Required live verification ran and failed its expected invariant.

**Token:** failed

##### Blocked

**Definition:** Required live verification cannot currently complete.

**Token:** blocked

## Source and authority

This page projects `KIS-WORK-SEM-REG-001` version `1.0.0`. The MRD is authoritative; this generated page has no write-back authority.
