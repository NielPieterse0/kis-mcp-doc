<!-- GENERATED — DO NOT EDIT -->
# Work lifecycle

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

Define Work states, transitions, readiness, claims, delivery stages, completion gates, and guards.

## Claim

**Auto expiry:** No

**Execution owner field:** Execution Owner

## Completion

**Require no active claim after close:** No

**Terminal state:** done

## Delivery

**Change created stage:** change_created

**Change id field:** Change ID

**Complete stage:** complete

**Complexity field:** Complexity

**Risk triggers field:** Risk Triggers

**Stage field:** Delivery Stage

**Stages:** none, change_created, implementing, pr_open, review, ci_pending, ci_failed, ci_passed, merged, documentation, commissioning, complete

## Guards

### approval-before-active

**Condition:** approval_required_and_incomplete

**Definition:** Reject activation when the record requires approval and approval is incomplete.

**Disposition:** reject

**Id:** approval-before-active

**Reason code:** approval_incomplete

**Target:** active

### completion-no-active-claim

**Condition:** completion_requires_no_active_claim_and_claim_present

**Definition:** When configured, reject completion while an execution claim remains.

**Disposition:** reject

**Id:** completion-no-active-claim

**Reason code:** active_claim_present

**Target:** done

### completion-documentation-due

**Condition:** required_documentation_reconciliation_due

**Definition:** Required post-merge documentation reconciliation must be completed before Done.

**Disposition:** reject

**Id:** completion-documentation-due

**Reason code:** documentation_reconciliation_due

**Target:** done

### completion-documentation-due-advisory

**Condition:** advisory_documentation_reconciliation_due

**Definition:** Advisory post-merge documentation reconciliation may complete with an explicit advisory reason.

**Disposition:** allow_with_reason

**Id:** completion-documentation-due-advisory

**Reason code:** documentation_reconciliation_advisory_due

**Target:** done

### completion-documentation-unrecorded

**Condition:** required_documentation_reconciliation_unrecorded

**Definition:** Required post-merge documentation milestone must be recorded before Done.

**Disposition:** reject

**Id:** completion-documentation-unrecorded

**Reason code:** documentation_reconciliation_unrecorded

**Target:** done

### completion-documentation-unrecorded-advisory

**Condition:** advisory_documentation_reconciliation_unrecorded

**Definition:** Advisory documentation reconciliation may complete without a recorded post-merge milestone, with an explicit advisory reason.

**Disposition:** allow_with_reason

**Id:** completion-documentation-unrecorded-advisory

**Reason code:** documentation_reconciliation_advisory_incomplete

**Target:** done

### completion-documentation-incomplete

**Condition:** required_documentation_incomplete

**Definition:** Required documentation impact must be complete before Done.

**Disposition:** reject

**Id:** completion-documentation-incomplete

**Reason code:** documentation_incomplete

**Target:** done

### completion-documentation-incomplete-advisory

**Condition:** advisory_documentation_incomplete

**Definition:** Advisory documentation may complete while incomplete, with an explicit advisory reason.

**Disposition:** allow_with_reason

**Id:** completion-documentation-incomplete-advisory

**Reason code:** documentation_advisory_incomplete

**Target:** done

## Intake aliases

**Todo:** inbox

## Readiness

**Required issue sections:** Outcome, Acceptance criteria

**Required project fields:** Record Type, Priority, Effort, Documentation Impact

**Requires dependencies understood:** Yes

## States

### Inbox

**Definition:** Captured work not yet triaged.

**Project status:** Yes

**Token:** inbox

### Triage

**Definition:** Work being classified.

**Project status:** Yes

**Token:** triage

### Proposed

**Definition:** Work proposed for approval.

**Project status:** Yes

**Token:** proposed

### Approved

**Definition:** Accepted work not yet admitted to Ready.

**Project status:** Yes

**Token:** approved

### Ready

**Definition:** Executable queue state subject to readiness guards.

**Project status:** Yes

**Token:** ready

### Active

**Definition:** Claimed execution state.

**Project status:** Yes

**Token:** active

### Review

**Definition:** Internal delivery state for review activity.

**Project status:** No

**Token:** review

### Verification

**Definition:** Internal delivery state for verification activity.

**Project status:** No

**Token:** verification

### Documentation

**Definition:** Internal delivery state for documentation reconciliation.

**Project status:** No

**Token:** documentation

### Blocked

**Definition:** Execution cannot proceed because a blocker is present.

**Project status:** Yes

**Token:** blocked

### On Hold

**Definition:** Intentionally paused pending a review trigger.

**Project status:** Yes

**Token:** on_hold

### Deferred

**Definition:** Postponed for later reconsideration.

**Project status:** Yes

**Token:** deferred

### Rejected

**Definition:** Not accepted for execution in current form.

**Project status:** Yes

**Token:** rejected

### Superseded

**Definition:** Replaced by newer authoritative work.

**Project status:** Yes

**Token:** superseded

### Done

**Definition:** Required completion gates are satisfied.

**Project status:** Yes

**Token:** done

## Transition requirements

**Deferred:** Review Trigger

**On hold:** Review Trigger

## Transitions

**Active:** ready, review, blocked, on_hold, deferred, done, superseded

**Approved:** ready, active, on_hold, deferred, superseded

**Blocked:** ready, active, on_hold, deferred, superseded

**Deferred:** triage, proposed, approved, rejected, superseded

**Documentation:** done, active, blocked, superseded

**Done:** None

**Inbox:** triage, deferred, rejected, superseded

**On hold:** ready, active, deferred, rejected, superseded

**Proposed:** approved, deferred, rejected, superseded

**Ready:** active, on_hold, deferred, superseded

**Rejected:** triage, superseded

**Review:** active, verification, blocked, on_hold, superseded

**Superseded:** None

**Triage:** proposed, approved, deferred, rejected, superseded

**Verification:** active, documentation, blocked, superseded

## Source and authority

This page projects `KIS-WORK-WRK-STM-001` version `1.0.0`. The MRD is authoritative; this generated page has no write-back authority.
