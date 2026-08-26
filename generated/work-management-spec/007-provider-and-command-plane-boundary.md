<!-- GENERATED — DO NOT EDIT -->
# Provider and command-plane boundary

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

Define the configured command plane and GitHub Project provider boundary.

## Command plane

### Claim

**Auto expiry:** No

**Execution owner field:** Execution Owner

### Completion

**Require no active claim after close:** No

**Terminal state:** done

### Delivery

**Change created stage:** change_created

**Change id field:** Change ID

**Complete stage:** complete

**Complexity field:** Complexity

**Risk triggers field:** Risk Triggers

**Stage field:** Delivery Stage

**Delivery stages:** none, change_created, implementing, pr_open, review, ci_pending, ci_failed, ci_passed, merged, documentation, commissioning, complete

### Field authority

#### Authority revision

**Authority:** git

**Direction:** evidence

#### Blocked by

**Authority:** github

**Direction:** evidence

#### Change id

**Authority:** repository_change

**Direction:** evidence

#### Commissioning key

**Authority:** derived

**Direction:** evidence

#### Complexity

**Authority:** repository_change

**Direction:** evidence

#### Confidence

**Authority:** work_management

**Direction:** command

#### Created

**Authority:** github

**Direction:** evidence

#### Delivery stage

**Authority:** derived

**Direction:** evidence

#### Disposition

**Authority:** work_management

**Direction:** command

#### Documentation impact

**Authority:** work_management_then_repository_change

**Direction:** handoff

#### Effort

**Authority:** work_management

**Direction:** command

#### Execution owner

**Authority:** work_management

**Direction:** command

#### External link

**Authority:** work_management

**Direction:** command

#### Iteration

**Authority:** work_management

**Direction:** command

#### Live verification

**Authority:** derived

**Direction:** evidence

#### Live verification evidence

**Authority:** derived

**Direction:** evidence

#### Module

**Authority:** work_management_then_repository_change

**Direction:** handoff

#### Origin

**Authority:** work_management

**Direction:** command

#### Priority

**Authority:** work_management

**Direction:** command

#### Project id

**Authority:** derived

**Direction:** evidence

#### Record type

**Authority:** work_management

**Direction:** command

#### Repository

**Authority:** github

**Direction:** evidence

#### Review trigger

**Authority:** work_management

**Direction:** command

#### Risk triggers

**Authority:** repository_change

**Direction:** evidence

#### Severity

**Authority:** work_management

**Direction:** command

#### Source review

**Authority:** work_management

**Direction:** command

#### Status

**Authority:** work_management

**Direction:** command

#### Target date

**Authority:** work_management

**Direction:** command

#### Verification

**Authority:** actions

**Direction:** evidence

### Intake aliases

**Todo:** inbox

### Queue

**Blocked by field:** Blocked By

**Created field:** Created

**Effort field:** Effort

**Effort order:** tiny, small, medium, large

**Eligible states:** ready

**Priority field:** Priority

**Priority order:** critical, high, medium, low

**Ranking:** priority, effort, created_order, record_id

**State field:** Status

### Readiness

**Required issue sections:** Outcome, Acceptance criteria

**Required project fields:** Record Type, Priority, Effort, Documentation Impact

**Requires dependencies understood:** Yes

**Schema version:** 1

### Transition requirements

**Deferred:** Review Trigger

**On hold:** Review Trigger

### Transitions

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

**Work states:** inbox, triage, proposed, approved, ready, active, blocked, on_hold, deferred, rejected, superseded, done

## Provider contract

**Live observation:** not captured in this revision because provider inventory response was invalid

**Project:** NielPieterse0/1

**Read model:** bounded inventory and schema observation

**Write model:** preview or idempotent mutation

## Source and authority

This page projects `KIS-WORK-CTR-SVC-001` version `1.0.0`. The MRD is authoritative; this generated page has no write-back authority.
