<!-- GENERATED — DO NOT EDIT -->
# Authority and reconciliation policy

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

Define authority ownership, repository handoff, Project reconciliation, and no-drift rules.

## Change governance

### Complexities

#### Large

**Artifacts:** scope.json, spec.md, plan.md, tasks.md, closeout.md

**Base reviews:** code-quality

**Description:** Work spanning components or system boundaries, independently reviewable subwork, substantial state or architecture change, a new integration, or significant release or commissioning coordination.

**Max verifications:** 20

#### Medium

**Artifacts:** scope.json, spec.md, plan.md, tasks.md, closeout.md

**Base reviews:** code-quality

**Description:** Several dependent steps or bounded design/shared-interface work in one contained area.

**Max verifications:** 20

#### Small

**Artifacts:** scope.json, change.md

**Base reviews:** None

**Description:** One bounded straightforward outcome with no material design or interface redesign.

**Max verifications:** 6

**Review types:** code-quality, safety-security, architecture, performance, test-quality, documentation, api-contracts

### Risk triggers

#### Architecture boundary

**Description:** A module, provider, subsystem, ownership, dependency-direction, or system-boundary contract changes.

**Reviews:** architecture

#### Deployment

**Description:** Deployment, release, environment promotion, or commissioning behavior changes.

**Reviews:** None

#### Destructive

**Description:** The change can remove, replace, invalidate, or irreversibly transform durable resources or state.

**Reviews:** None

#### External action

**Description:** The change can cause externally observable actions through an approved provider or integration.

**Reviews:** None

#### Migration

**Description:** Existing state, schema, configuration, or users require migration or compatibility handling.

**Reviews:** None

#### Money

**Description:** Payments, balances, billing, settlement, or other monetary-value behavior changes.

**Reviews:** None

#### Persistent state

**Description:** Durable state, stored records, or persistence semantics change.

**Reviews:** None

#### Public contract

**Description:** A public or externally consumed interface, schema, command, tool, API, or contract changes.

**Reviews:** api-contracts

#### Secrets

**Description:** Secret material, credentials, key handling, or secret-storage behavior changes.

**Reviews:** safety-security

#### Security

**Description:** Authentication, authorization, trust-boundary, or security-control behavior changes.

**Reviews:** safety-security

#### Sensitive data

**Description:** Personal, regulated, confidential, or otherwise sensitive data handling changes.

**Reviews:** safety-security

**Schema version:** 1

## Github project schema

### Fields

#### Status

**Options:** Inbox, Triage, Proposed, Approved, Ready, Active, Blocked, On Hold, Deferred, Rejected, Superseded, Done

**Type:** single_select

#### Record Type

**Options:** Idea, Task, Specification Slice, Review Run, Finding, Decision, Assumption, Risk, Approval, Hold, Research, Defect, Security Finding

**Type:** single_select

#### Priority

**Options:** Critical, High, Medium, Low

**Type:** single_select

#### Effort

**Options:** Tiny, Small, Medium, Large

**Type:** single_select

#### Delivery Stage

**Options:** None, Change Created, Implementing, PR Open, Review, CI Pending, CI Failed, CI Passed, Merged, Documentation, Commissioning, Complete

**Type:** single_select

#### Execution Owner

**Options:** None

**Type:** text

#### Blocked By

**Options:** None

**Type:** text

#### Documentation Impact

**Options:** Not Assessed, None, Planned, In Progress, Pre-merge Complete, Post-merge Complete

**Type:** single_select

#### Complexity

**Options:** Small, Medium, Large

**Type:** single_select

#### Risk Triggers

**Options:** None

**Type:** text

#### Project ID

**Options:** None

**Type:** text

#### Repository

**Options:** None

**Type:** repository

#### Module

**Options:** None

**Type:** text

#### Change ID

**Options:** None

**Type:** text

#### Origin

**Options:** Operator, Review, Verification, Implementation, Research

**Type:** single_select

#### Disposition

**Options:** Open, Accepted, Rejected, Superseded, Mitigated, Deferred

**Type:** single_select

#### Verification

**Options:** Not Run, Pending, Passed, Failed, Blocked

**Type:** single_select

#### Severity

**Options:** Critical, High, Medium, Low

**Type:** single_select

#### Confidence

**Options:** High, Medium, Low

**Type:** single_select

#### Review Trigger

**Options:** None

**Type:** text

#### Target Date

**Options:** None

**Type:** date

#### Iteration

**Options:** None

**Type:** iteration

#### Source Review

**Options:** None

**Type:** text

#### Authority Revision

**Options:** None

**Type:** text

#### External Link

**Options:** None

**Type:** text

#### Live Verification

**Options:** Not Assessed, Not Required, Pending, Passed, Failed, Blocked

**Type:** single_select

#### Commissioning Key

**Options:** None

**Type:** text

#### Live Verification Evidence

**Options:** None

**Type:** text

**Portfolio id:** default

**Schema version:** 1

### Views

#### 01 Inbox

**Filter:** status:Inbox

**Group by:** None

**Layout:** table

**Purpose:** Untriaged ideas and tasks

**Sort by:** None

**Vertical group by:** None

**Visible fields:** Title, Status, Record Type, Priority, Effort, Repository

#### 02 Programme Table

**Filter:** status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred

**Group by:** None

**Layout:** table

**Purpose:** All active records and key fields

**Sort by:** None

**Vertical group by:** None

**Visible fields:** Title, Status, Record Type, Priority, Effort, Execution Owner, Repository, Change ID, Delivery Stage

#### 03 Delivery Board

**Filter:** status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred

**Group by:** None

**Layout:** board

**Purpose:** Delivery flow grouped by lifecycle status

**Sort by:** None

**Vertical group by:** Status

**Visible fields:** Title, Priority, Effort, Execution Owner, Repository, Delivery Stage

#### 04 Roadmap

**Filter:** record-type:"Specification Slice",Task status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred,Rejected,Superseded,Done

**Group by:** None

**Layout:** roadmap

**Purpose:** Dated or iterated specification and implementation slices

**Sort by:** None

**Vertical group by:** None

**Visible fields:** None

#### 05 Specification Slices

**Filter:** record-type:"Specification Slice" status:Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred,Rejected,Superseded,Done

**Group by:** None

**Layout:** table

**Purpose:** Proposed through completed specification records

**Sort by:** None

**Vertical group by:** None

**Visible fields:** Title, Status, Priority, Change ID, Delivery Stage, Repository

#### 06 Decisions

**Filter:** record-type:Decision status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred,Rejected,Superseded,Done

**Group by:** None

**Layout:** table

**Purpose:** Proposed, accepted, rejected, and superseded decisions

**Sort by:** None

**Vertical group by:** None

**Visible fields:** Title, Status, Disposition, Review Trigger, Authority Revision, Repository

#### 07 Assumptions and Risks

**Filter:** record-type:Assumption,Risk status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred

**Group by:** None

**Layout:** table

**Purpose:** Open validation and mitigation work

**Sort by:** None

**Vertical group by:** None

**Visible fields:** Title, Status, Severity, Confidence, Review Trigger, Disposition, Repository

#### 08 Holds and Deferred

**Filter:** status:"On Hold",Deferred

**Group by:** None

**Layout:** table

**Purpose:** Paused items with review triggers

**Sort by:** None

**Vertical group by:** None

**Visible fields:** Title, Status, Review Trigger, Execution Owner, Blocked By, Target Date, Repository

#### 09 Reviews and Findings

**Filter:** record-type:"Review Run",Finding,"Security Finding" status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred,Rejected,Superseded,Done

**Group by:** None

**Layout:** table

**Purpose:** Review runs and extracted records

**Sort by:** None

**Vertical group by:** None

**Visible fields:** Title, Status, Severity, Confidence, Source Review, Verification, Disposition, Repository

#### 10 Verification

**Filter:** verification:Pending,Failed,Blocked status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred,Rejected,Superseded,Done

**Group by:** None

**Layout:** table

**Purpose:** Work awaiting or failing verification

**Sort by:** None

**Vertical group by:** None

**Visible fields:** Title, Status, Verification, Change ID, Delivery Stage, Repository

#### 11 Documentation and Closeout

**Filter:** delivery-stage:Documentation,Commissioning status:Inbox,Triage,Proposed,Approved,Ready,Active,Blocked,"On Hold",Deferred,Rejected,Superseded,Done

**Group by:** None

**Layout:** table

**Purpose:** Records awaiting documentation reconciliation or final closeout

**Sort by:** None

**Vertical group by:** None

**Visible fields:** Title, Status, Documentation Impact, Change ID, Delivery Stage, Repository

#### 12 Completed

**Filter:** status:Done

**Group by:** None

**Layout:** table

**Purpose:** Closed records retained for history

**Sort by:** None

**Vertical group by:** None

**Visible fields:** Title, Record Type, Repository, Change ID, Delivery Stage, Verification, Authority Revision

## Principles

Work Management owns command fields., Repository change governance owns Change ID, Complexity, and Risk Triggers after a governed change exists., GitHub owns provider-native source identity and observed dependency evidence., Actions and governed verification evidence own source Verification., Generated specifications are downstream review projections with no write-back authority., Conflicts and unavailable evidence fail closed or remain explicitly unknown.

## Project bindings

### Backend bindings

#### Item 1

**Binding id:** github-default

**Owner:** NielPieterse0

**Owner type:** user

**Project number:** 1

**Provider:** github-mcp

**Enabled:** Yes

### Evidence

**Max file bytes:** 1048576

**Max total bytes:** 4194304

### Features

**Intake:** read_only

**Programme status:** enabled

**Reconciliation:** enabled

**Review import:** read_only

### Gates

**Change traceability:** required

**Decision authority:** advisory

**Hold integrity:** advisory

**Programme drift:** advisory

**Project schema drift:** advisory

**Project settings:** required

**Review disposition:** advisory

**Verification evidence:** required

### Managed projects

#### Item 1

**Backend binding:** github-default

**Display name:** ChatGPT-skill

**Local root:** C:\Projects\ChatGPT-skill

**Project id:** chatgpt-skill

**Repository:** NielPieterse0/chatgpt-skill

#### Item 2

**Backend binding:** github-default

**Display name:** college

**Local root:** C:\Projects\college

**Project id:** college

**Repository:** NielPieterse0/college

#### Item 3

**Backend binding:** github-default

**Display name:** commodity

**Local root:** C:\Projects\commodity

**Project id:** commodity

**Repository:** NielPieterse0/commodity

#### Item 4

**Backend binding:** github-default

**Display name:** import-isolate

**Local root:** C:\Projects\import-isolate

**Project id:** import-isolate

**Repository:** NielPieterse0/import-isolate

#### Item 5

**Backend binding:** github-default

**Display name:** kis-mcp

**Local root:** C:\Projects\kis-mcp

**Project id:** kis-mcp

**Repository:** NielPieterse0/kis-mcp

#### Item 6

**Backend binding:** github-default

**Display name:** kis-mcp-doc

**Local root:** C:\Projects\kis-mcp-doc

**Project id:** kis-mcp-doc

**Repository:** NielPieterse0/kis-mcp-doc

**Portfolio id:** default

**Schema version:** 1

## Source and authority

This page projects `KIS-WORK-CON-POL-001` version `1.0.0`. The MRD is authoritative; this generated page has no write-back authority.
