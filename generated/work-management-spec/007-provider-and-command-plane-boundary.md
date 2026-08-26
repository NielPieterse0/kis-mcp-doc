<!-- GENERATED — DO NOT EDIT -->
# Provider and command-plane boundary

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

The command plane defines the work states and fields that KIS may change. The provider boundary observes and mutates GitHub Project only through the configured read and write models; provider state does not redefine repository-owned facts.

## Command-plane model

Claims use **Execution Owner** and do not expire automatically. The completion policy targets `done` and does not require the claim to be absent after close.

The command plane exposes these work states: `inbox`, `triage`, `proposed`, `approved`, `ready`, `active`, `blocked`, `on_hold`, `deferred`, `rejected`, `superseded`, `done`. Delivery uses `none`, `change_created`, `implementing`, `pr_open`, `review`, `ci_pending`, `ci_failed`, `ci_passed`, `merged`, `documentation`, `commissioning`, `complete`.

The intake alias `todo` maps to `inbox`.

### Field authority

Each field keeps the authority and direction defined by the Work Management domain model:

| Field | Authority | Direction |
|---|---|---|
| Authority Revision | `git` | `evidence` |
| Blocked By | `github` | `evidence` |
| Change ID | `repository_change` | `evidence` |
| Commissioning Key | `derived` | `evidence` |
| Complexity | `repository_change` | `evidence` |
| Confidence | `work_management` | `command` |
| Created | `github` | `evidence` |
| Delivery Stage | `derived` | `evidence` |
| Disposition | `work_management` | `command` |
| Documentation Impact | `work_management_then_repository_change` | `handoff` |
| Effort | `work_management` | `command` |
| Execution Owner | `work_management` | `command` |
| External Link | `work_management` | `command` |
| Iteration | `work_management` | `command` |
| Live Verification | `derived` | `evidence` |
| Live Verification Evidence | `derived` | `evidence` |
| Module | `work_management_then_repository_change` | `handoff` |
| Origin | `work_management` | `command` |
| Priority | `work_management` | `command` |
| Project ID | `derived` | `evidence` |
| Record Type | `work_management` | `command` |
| Repository | `github` | `evidence` |
| Review Trigger | `work_management` | `command` |
| Risk Triggers | `repository_change` | `evidence` |
| Severity | `work_management` | `command` |
| Source Review | `work_management` | `command` |
| Status | `work_management` | `command` |
| Target Date | `work_management` | `command` |
| Verification | `actions` | `evidence` |

## Queue and readiness

The executable queue accepts state `ready`. It ranks by `priority`, `effort`, `created_order`, `record_id`, using priority order `critical`, `high`, `medium`, `low` and effort order `tiny`, `small`, `medium`, `large`.

Queue inputs come from **Status**, **Priority**, **Effort**, **Created**, and **Blocked By**.

Before the provider-backed command plane can treat work as Ready, the record **MUST** satisfy its configured readiness requirements:

- The source issue contains **Outcome** and **Acceptance criteria**.
- The Project record contains **Record Type**, **Priority**, **Effort**, and **Documentation Impact**.
- Dependencies are understood.

## State transitions

The provider-facing command plane uses the same transition graph as the Work lifecycle chapter. The table is repeated here because the provider adapter validates these exact transitions.

| From | Allowed next states | Additional requirement |
|---|---|---|
| `active` | `ready`, `review`, `blocked`, `on_hold`, `deferred`, `done`, `superseded` | None |
| `approved` | `ready`, `active`, `on_hold`, `deferred`, `superseded` | None |
| `blocked` | `ready`, `active`, `on_hold`, `deferred`, `superseded` | None |
| `deferred` | `triage`, `proposed`, `approved`, `rejected`, `superseded` | Review Trigger |
| `documentation` | `done`, `active`, `blocked`, `superseded` | None |
| `done` | No transitions | None |
| `inbox` | `triage`, `deferred`, `rejected`, `superseded` | None |
| `on_hold` | `ready`, `active`, `deferred`, `rejected`, `superseded` | Review Trigger |
| `proposed` | `approved`, `deferred`, `rejected`, `superseded` | None |
| `ready` | `active`, `on_hold`, `deferred`, `superseded` | None |
| `rejected` | `triage`, `superseded` | None |
| `review` | `active`, `verification`, `blocked`, `on_hold`, `superseded` | None |
| `superseded` | No transitions | None |
| `triage` | `proposed`, `approved`, `deferred`, `rejected`, `superseded` | None |
| `verification` | `active`, `documentation`, `blocked`, `superseded` | None |

## Delivery projection

**Delivery Stage** carries the derived delivery stage. **Change ID**, **Complexity**, and **Risk Triggers** are projected from repository change governance. The change-created stage is `change_created` and the complete stage is `complete`.

## Provider contract

The configured Project is `NielPieterse0/1`. Reads use bounded inventory and schema observation; writes use preview or idempotent mutation.

Live Project evidence was observed; inventory is complete; the configured Project schema is ready with no field, option, type, or view drift in the captured evidence.

Command-plane schema version: `1`.

## Source and authority

This page projects `KIS-WORK-CTR-SVC-001` version `1.0.1`. The MRD remains authoritative; this generated page has no write-back authority.
