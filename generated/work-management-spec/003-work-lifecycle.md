<!-- GENERATED — DO NOT EDIT -->
# Work lifecycle

<div id="enable-section-numbers" />

[Previous: Work Management domain model](002-work-management-domain-model.md) | [Next: Work operations](004-work-operations.md) | [Index](000-index.md)

<span id="mrd-urn-uuid-7f58b5b4-9808-5c06-bbed-75a8526685f3"></span>

A work item moves through explicit states. Project-visible states describe the shared work queue, while internal states such as Review, Verification, and Documentation describe delivery activity without creating new GitHub Project status values.

## Work status and delivery stage

Work Status and Delivery Stage are separate dimensions. The diagram shows the canonical Work lifecycle graph and Delivery Stage sequence independently; it does not map a work state to a delivery stage.

```mermaid
flowchart LR
  subgraph work_status["Work Status"]
    status_inbox["Inbox"]
    status_triage["Triage"]
    status_proposed["Proposed"]
    status_approved["Approved"]
    status_ready["Ready"]
    status_active["Active"]
    status_review["Review (internal)"]
    status_verification["Verification (internal)"]
    status_documentation["Documentation (internal)"]
    status_blocked["Blocked"]
    status_on_hold["On Hold"]
    status_deferred["Deferred"]
    status_rejected["Rejected"]
    status_superseded["Superseded"]
    status_done["Done"]
    status_active --> status_ready
    status_active --> status_review
    status_active --> status_blocked
    status_active --> status_on_hold
    status_active --> status_deferred
    status_active --> status_done
    status_active --> status_superseded
    status_approved --> status_ready
    status_approved --> status_active
    status_approved --> status_on_hold
    status_approved --> status_deferred
    status_approved --> status_superseded
    status_blocked --> status_ready
    status_blocked --> status_active
    status_blocked --> status_on_hold
    status_blocked --> status_deferred
    status_blocked --> status_superseded
    status_deferred --> status_triage
    status_deferred --> status_proposed
    status_deferred --> status_approved
    status_deferred --> status_rejected
    status_deferred --> status_superseded
    status_documentation --> status_done
    status_documentation --> status_active
    status_documentation --> status_blocked
    status_documentation --> status_superseded
    status_inbox --> status_triage
    status_inbox --> status_deferred
    status_inbox --> status_rejected
    status_inbox --> status_superseded
    status_on_hold --> status_ready
    status_on_hold --> status_active
    status_on_hold --> status_deferred
    status_on_hold --> status_rejected
    status_on_hold --> status_superseded
    status_proposed --> status_approved
    status_proposed --> status_deferred
    status_proposed --> status_rejected
    status_proposed --> status_superseded
    status_ready --> status_active
    status_ready --> status_on_hold
    status_ready --> status_deferred
    status_ready --> status_superseded
    status_rejected --> status_triage
    status_rejected --> status_superseded
    status_review --> status_active
    status_review --> status_verification
    status_review --> status_blocked
    status_review --> status_on_hold
    status_review --> status_superseded
    status_triage --> status_proposed
    status_triage --> status_approved
    status_triage --> status_deferred
    status_triage --> status_rejected
    status_triage --> status_superseded
    status_verification --> status_active
    status_verification --> status_documentation
    status_verification --> status_blocked
    status_verification --> status_superseded
  end
  subgraph delivery_stage["Delivery Stage"]
    stage_none["none"]
    stage_change_created["change_created"]
    stage_implementing["implementing"]
    stage_pr_open["pr_open"]
    stage_review["review"]
    stage_ci_pending["ci_pending"]
    stage_ci_failed["ci_failed"]
    stage_ci_passed["ci_passed"]
    stage_merged["merged"]
    stage_documentation["documentation"]
    stage_commissioning["commissioning"]
    stage_complete["complete"]
    stage_none --> stage_change_created
    stage_change_created --> stage_implementing
    stage_implementing --> stage_pr_open
    stage_pr_open --> stage_review
    stage_review --> stage_ci_pending
    stage_ci_pending --> stage_ci_failed
    stage_ci_failed --> stage_ci_passed
    stage_ci_passed --> stage_merged
    stage_merged --> stage_documentation
    stage_documentation --> stage_commissioning
    stage_commissioning --> stage_complete
  end
```

## State model

| State | Meaning | GitHub Project status | Token |
|---|---|---|---|
| Inbox | Captured work not yet triaged. | Yes | `inbox` |
| Triage | Work being classified. | Yes | `triage` |
| Proposed | Work proposed for approval. | Yes | `proposed` |
| Approved | Accepted work not yet admitted to Ready. | Yes | `approved` |
| Ready | Executable queue state subject to readiness guards. | Yes | `ready` |
| Active | Claimed execution state. | Yes | `active` |
| Review | Internal delivery state for review activity. | No | `review` |
| Verification | Internal delivery state for verification activity. | No | `verification` |
| Documentation | Internal delivery state for documentation reconciliation. | No | `documentation` |
| Blocked | Execution cannot proceed because a blocker is present. | Yes | `blocked` |
| On Hold | Intentionally paused pending a review trigger. | Yes | `on_hold` |
| Deferred | Postponed for later reconsideration. | Yes | `deferred` |
| Rejected | Not accepted for execution in current form. | Yes | `rejected` |
| Superseded | Replaced by newer authoritative work. | Yes | `superseded` |
| Done | Required completion gates are satisfied. | Yes | `done` |

<span id="fact-work-state-inbox"></span>
<span id="fact-work-state-triage"></span>
<span id="fact-work-state-proposed"></span>
<span id="fact-work-state-approved"></span>
<span id="fact-work-state-ready"></span>
<span id="fact-work-state-active"></span>
<span id="fact-work-state-review"></span>
<span id="fact-work-state-verification"></span>
<span id="fact-work-state-documentation"></span>
<span id="fact-work-state-blocked"></span>
<span id="fact-work-state-on-hold"></span>
<span id="fact-work-state-deferred"></span>
<span id="fact-work-state-rejected"></span>
<span id="fact-work-state-superseded"></span>
<span id="fact-work-state-done"></span>

## Transitions

Transitions are explicit. A work item **MUST** move only to a destination listed for its current state. On Hold and Deferred also require a Review Trigger.

| From | Allowed next states | Additional requirement |
|---|---|---|
| Active | Ready, Review, Blocked, On Hold, Deferred, Done, Superseded | None |
| Approved | Ready, Active, On Hold, Deferred, Superseded | None |
| Blocked | Ready, Active, On Hold, Deferred, Superseded | None |
| Deferred | Triage, Proposed, Approved, Rejected, Superseded | Review Trigger |
| Documentation | Done, Active, Blocked, Superseded | None |
| Done | No transitions | None |
| Inbox | Triage, Deferred, Rejected, Superseded | None |
| On Hold | Ready, Active, Deferred, Rejected, Superseded | Review Trigger |
| Proposed | Approved, Deferred, Rejected, Superseded | None |
| Ready | Active, On Hold, Deferred, Superseded | None |
| Rejected | Triage, Superseded | None |
| Review | Active, Verification, Blocked, On Hold, Superseded | None |
| Superseded | No transitions | None |
| Triage | Proposed, Approved, Deferred, Rejected, Superseded | None |
| Verification | Active, Documentation, Blocked, Superseded | None |

## Readiness and claims

Before a work item can enter Ready, it **MUST** satisfy all configured readiness requirements:

- The source issue contains **Outcome** and **Acceptance criteria**.
- The Project record contains **Record Type**, **Priority**, **Effort**, and **Documentation Impact**.
- Dependencies are understood.

Execution claims use the **Execution Owner** field. Claims do not expire automatically.

At intake, the alias `todo` is normalized to `inbox`.

## Delivery and completion

Delivery is tracked separately from the work state. The configured delivery-stage sequence is:

<span id="fact-delivery-stage-none"></span>`none`, <span id="fact-delivery-stage-change-created"></span>`change_created`, <span id="fact-delivery-stage-implementing"></span>`implementing`, <span id="fact-delivery-stage-pr-open"></span>`pr_open`, <span id="fact-delivery-stage-review"></span>`review`, <span id="fact-delivery-stage-ci-pending"></span>`ci_pending`, <span id="fact-delivery-stage-ci-failed"></span>`ci_failed`, <span id="fact-delivery-stage-ci-passed"></span>`ci_passed`, <span id="fact-delivery-stage-merged"></span>`merged`, <span id="fact-delivery-stage-documentation"></span>`documentation`, <span id="fact-delivery-stage-commissioning"></span>`commissioning`, <span id="fact-delivery-stage-complete"></span>`complete`

The **Delivery Stage** field stores that stage. **Change ID**, **Complexity**, and **Risk Triggers** connect the work record to repository change governance. The sequence starts its governed change at `change_created` and reaches `complete` when delivery is complete.

Completion targets `done`. The current configuration does not require the execution claim to be absent after close.

## Completion and activation guards

Guards reject or qualify transitions when required evidence is missing or inconsistent:

| Guard | Applies when | Rule | Result | Reason |
|---|---|---|---|---|
| `approval-before-active` | `approval_required_and_incomplete` | Reject activation when the record requires approval and approval is incomplete. | `reject` to `active` | `approval_incomplete` |
| `completion-no-active-claim` | `completion_requires_no_active_claim_and_claim_present` | When configured, reject completion while an execution claim remains. | `reject` to `done` | `active_claim_present` |
| `completion-documentation-due` | `required_documentation_reconciliation_due` | Required post-merge documentation reconciliation must be completed before Done. | `reject` to `done` | `documentation_reconciliation_due` |
| `completion-documentation-due-advisory` | `advisory_documentation_reconciliation_due` | Advisory post-merge documentation reconciliation may complete with an explicit advisory reason. | `allow_with_reason` to `done` | `documentation_reconciliation_advisory_due` |
| `completion-documentation-unrecorded` | `required_documentation_reconciliation_unrecorded` | Required post-merge documentation milestone must be recorded before Done. | `reject` to `done` | `documentation_reconciliation_unrecorded` |
| `completion-documentation-unrecorded-advisory` | `advisory_documentation_reconciliation_unrecorded` | Advisory documentation reconciliation may complete without a recorded post-merge milestone, with an explicit advisory reason. | `allow_with_reason` to `done` | `documentation_reconciliation_advisory_incomplete` |
| `completion-documentation-incomplete` | `required_documentation_incomplete` | Required documentation impact must be complete before Done. | `reject` to `done` | `documentation_incomplete` |
| `completion-documentation-incomplete-advisory` | `advisory_documentation_incomplete` | Advisory documentation may complete while incomplete, with an explicit advisory reason. | `allow_with_reason` to `done` | `documentation_advisory_incomplete` |

## Source and authority

This page projects `urn:uuid:7f58b5b4-9808-5c06-bbed-75a8526685f3` version `1.0.0`. The MRD remains authoritative; this generated page has no write-back authority.
