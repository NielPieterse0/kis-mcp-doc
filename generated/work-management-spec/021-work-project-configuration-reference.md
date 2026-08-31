<!-- GENERATED — DO NOT EDIT -->
# Work Project configuration reference

<div id="enable-section-numbers" />

[Owning specification chapter: Authority and reconciliation policy](006-authority-and-reconciliation-policy.md) | [Documentation index](000-index.md)

> **Output class:** `generated_reference`. This page is an exact lookup projection of canonical Work Management policy and configuration. It has no write-back authority.

Authority determines which system may change a fact. Reconciliation then compares provider state with those owners and reports drift instead of choosing a new truth. Generated documentation stays downstream of every canonical source.

## Authority principles

- Work Management owns command fields.
- Repository change governance owns Change ID, Complexity, and Risk Triggers after a governed change exists.
- GitHub owns provider-native source identity and observed dependency evidence.
- Actions and governed verification evidence own source Verification.
- Generated specifications are downstream review projections with no write-back authority.
- Conflicts and unavailable evidence fail closed or remain explicitly unknown.

## Change-governance handoff

Work Management carries change-planning data into repository governance, but repository change governance owns the governed change facts once a change exists. This projection uses change-governance schema version `1`.

| Complexity | Meaning | Artifacts | Base reviews | Max verifications |
|---|---|---|---|---|
| Large | Work spanning components or system boundaries, independently reviewable subwork, substantial state or architecture change, a new integration, or significant release or commissioning coordination. | scope.json, spec.md, plan.md, tasks.md, closeout.md | code-quality | 20 |
| Medium | Several dependent steps or bounded design/shared-interface work in one contained area. | scope.json, spec.md, plan.md, tasks.md, closeout.md | code-quality | 20 |
| Small | One bounded straightforward outcome with no material design or interface redesign. | scope.json, change.md | None | 6 |

Supported review types: `code-quality`, `safety-security`, `architecture`, `performance`, `test-quality`, `documentation`, `api-contracts`.

### Risk triggers

| Risk trigger | When it applies | Required review |
|---|---|---|
| Architecture boundary | A module, provider, subsystem, ownership, dependency-direction, or system-boundary contract changes. | `architecture` |
| Deployment | Deployment, release, environment promotion, or commissioning behavior changes. | None |
| Destructive | The change can remove, replace, invalidate, or irreversibly transform durable resources or state. | None |
| External action | The change can cause externally observable actions through an approved provider or integration. | None |
| Migration | Existing state, schema, configuration, or users require migration or compatibility handling. | None |
| Money | Payments, balances, billing, settlement, or other monetary-value behavior changes. | None |
| Persistent state | Durable state, stored records, or persistence semantics change. | None |
| Public contract | A public or externally consumed interface, schema, command, tool, API, or contract changes. | `api-contracts` |
| Secrets | Secret material, credentials, key handling, or secret-storage behavior changes. | `safety-security` |
| Security | Authentication, authorization, trust-boundary, or security-control behavior changes. | `safety-security` |
| Sensitive data | Personal, regulated, confidential, or otherwise sensitive data handling changes. | `safety-security` |

## GitHub Project schema

The configured Project schema belongs to portfolio `default` and uses schema version `1`. Fields and allowed single-select options are explicit so provider drift can be detected.

| Field | Type | Options |
|---|---|---|
| <span id="fact-project-field-status"></span>Status | `single_select` | Inbox, Triage, Proposed, Approved, Ready, Active, Blocked, On Hold, Deferred, Rejected, Superseded, Done |
| <span id="fact-project-field-record-type"></span>Record Type | `single_select` | Idea, Task, Specification Slice, Review Run, Finding, Decision, Assumption, Risk, Approval, Hold, Research, Defect, Security Finding |
| <span id="fact-project-field-priority"></span>Priority | `single_select` | Critical, High, Medium, Low |
| <span id="fact-project-field-effort"></span>Effort | `single_select` | Tiny, Small, Medium, Large |
| <span id="fact-project-field-delivery-stage"></span>Delivery Stage | `single_select` | None, Change Created, Implementing, PR Open, Review, CI Pending, CI Failed, CI Passed, Merged, Documentation, Commissioning, Complete |
| <span id="fact-project-field-execution-owner"></span>Execution Owner | `text` | Not applicable |
| <span id="fact-project-field-blocked-by"></span>Blocked By | `text` | Not applicable |
| <span id="fact-project-field-documentation-impact"></span>Documentation Impact | `single_select` | Not Assessed, None, Planned, In Progress, Pre-merge Complete, Post-merge Complete |
| <span id="fact-project-field-complexity"></span>Complexity | `single_select` | Small, Medium, Large |
| <span id="fact-project-field-risk-triggers"></span>Risk Triggers | `text` | Not applicable |
| <span id="fact-project-field-project-id"></span>Project ID | `text` | Not applicable |
| <span id="fact-project-field-repository"></span>Repository | `repository` | Not applicable |
| <span id="fact-project-field-module"></span>Module | `text` | Not applicable |
| <span id="fact-project-field-change-id"></span>Change ID | `text` | Not applicable |
| <span id="fact-project-field-origin"></span>Origin | `single_select` | Operator, Review, Verification, Implementation, Research |
| <span id="fact-project-field-disposition"></span>Disposition | `single_select` | Open, Accepted, Rejected, Superseded, Mitigated, Deferred |
| <span id="fact-project-field-verification"></span>Verification | `single_select` | Not Run, Pending, Passed, Failed, Blocked |
| <span id="fact-project-field-severity"></span>Severity | `single_select` | Critical, High, Medium, Low |
| <span id="fact-project-field-confidence"></span>Confidence | `single_select` | High, Medium, Low |
| <span id="fact-project-field-review-trigger"></span>Review Trigger | `text` | Not applicable |
| <span id="fact-project-field-target-date"></span>Target Date | `date` | Not applicable |
| <span id="fact-project-field-iteration"></span>Iteration | `iteration` | Not applicable |
| <span id="fact-project-field-source-review"></span>Source Review | `text` | Not applicable |
| <span id="fact-project-field-authority-revision"></span>Authority Revision | `text` | Not applicable |
| <span id="fact-project-field-external-link"></span>External Link | `text` | Not applicable |
| <span id="fact-project-field-live-verification"></span>Live Verification | `single_select` | Not Assessed, Not Required, Pending, Passed, Failed, Blocked |
| <span id="fact-project-field-commissioning-key"></span>Commissioning Key | `text` | Not applicable |
| <span id="fact-project-field-live-verification-evidence"></span>Live Verification Evidence | `text` | Not applicable |


### Project views

Views are derived navigation surfaces over the same Project data. Their filters and visible fields do not create new authority.

| View | Purpose | Layout | Filter | Grouping / sort | Visible fields |
|---|---|---|---|---|---|
| <span id="fact-project-view-01-inbox"></span>01 Inbox | Untriaged ideas and tasks | `table` | status:Inbox | None | Title, Status, Record Type, Priority, Effort, Repository |
| <span id="fact-project-view-02-programme-table"></span>02 Programme Table | All active records and key fields | `table` | status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred | None | Title, Status, Record Type, Priority, Effort, Execution Owner, Repository, Change ID, Delivery Stage |
| <span id="fact-project-view-03-delivery-board"></span>03 Delivery Board | Delivery flow grouped by lifecycle status | `board` | status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred | vertical group by Status | Title, Priority, Effort, Execution Owner, Repository, Delivery Stage |
| <span id="fact-project-view-04-roadmap"></span>04 Roadmap | Dated or iterated specification and implementation slices | `roadmap` | record-type:"Specification Slice",Task status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred,Rejected,Superseded,Done | None | None |
| <span id="fact-project-view-05-specification-slices"></span>05 Specification Slices | Proposed through completed specification records | `table` | record-type:"Specification Slice" status:Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred,Rejected,Superseded,Done | None | Title, Status, Priority, Change ID, Delivery Stage, Repository |
| <span id="fact-project-view-06-decisions"></span>06 Decisions | Proposed, accepted, rejected, and superseded decisions | `table` | record-type:Decision status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred,Rejected,Superseded,Done | None | Title, Status, Disposition, Review Trigger, Authority Revision, Repository |
| <span id="fact-project-view-07-assumptions-and-risks"></span>07 Assumptions and Risks | Open validation and mitigation work | `table` | record-type:Assumption,Risk status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred | None | Title, Status, Severity, Confidence, Review Trigger, Disposition, Repository |
| <span id="fact-project-view-08-holds-and-deferred"></span>08 Holds and Deferred | Paused items with review triggers | `table` | status:"On Hold",Deferred | None | Title, Status, Review Trigger, Execution Owner, Blocked By, Target Date, Repository |
| <span id="fact-project-view-09-reviews-and-findings"></span>09 Reviews and Findings | Review runs and extracted records | `table` | record-type:"Review Run",Finding,"Security Finding" status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred,Rejected,Superseded,Done | None | Title, Status, Severity, Confidence, Source Review, Verification, Disposition, Repository |
| <span id="fact-project-view-10-verification"></span>10 Verification | Work awaiting or failing verification | `table` | verification:Pending,Failed,Blocked status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred,Rejected,Superseded,Done | None | Title, Status, Verification, Change ID, Delivery Stage, Repository |
| <span id="fact-project-view-11-documentation-and-closeout"></span>11 Documentation and Closeout | Records awaiting documentation reconciliation or final closeout | `table` | delivery-stage:Documentation,Commissioning status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred,Rejected,Superseded,Done | None | Title, Status, Documentation Impact, Change ID, Delivery Stage, Repository |
| <span id="fact-project-view-12-completed"></span>12 Completed | Closed records retained for history | `table` | status:Done | None | Title, Record Type, Repository, Change ID, Delivery Stage, Verification, Authority Revision |


## Project bindings

Project integration is enabled for portfolio `default` under schema version `1`.

### Backend bindings

| Binding | Provider | Owner | Owner type | Project |
|---|---|---|---|---|
| github-default | `github-mcp` | NielPieterse0 | user | 1 |

### Managed projects

| Project ID | Display name | Repository | Local root | Backend |
|---|---|---|---|---|
| chatgpt-skill | ChatGPT-skill | NielPieterse0/chatgpt-skill | `C:\Projects\ChatGPT-skill` | github-default |
| college | college | NielPieterse0/college | `C:\Projects\college` | github-default |
| commodity | commodity | NielPieterse0/commodity | `C:\Projects\commodity` | github-default |
| import-isolate | import-isolate | NielPieterse0/import-isolate | `C:\Projects\import-isolate` | github-default |
| kis-mcp | kis-mcp | NielPieterse0/kis-mcp | `C:\Projects\kis-mcp` | github-default |
| kis-mcp-doc | kis-mcp-doc | NielPieterse0/kis-mcp-doc | `C:\Projects\kis-mcp-doc` | github-default |

### Features and gates

| Feature | Mode |
|---|---|
| Intake | `read_only` |
| Programme status | `enabled` |
| Reconciliation | `enabled` |
| Review import | `read_only` |

| Gate | Strength |
|---|---|
| Change traceability | `required` |
| Decision authority | `advisory` |
| Hold integrity | `advisory` |
| Programme drift | `advisory` |
| Project schema drift | `advisory` |
| Project settings | `required` |
| Review disposition | `advisory` |
| Verification evidence | `required` |

Evidence collection is bounded to `1048576` bytes per file and `4194304` bytes in total.

## Source and authority

This page projects `urn:uuid:c589700c-9c38-5e30-be4c-659084060fa0` version `1.0.0`. The MRD remains authoritative; this generated page has no write-back authority.
