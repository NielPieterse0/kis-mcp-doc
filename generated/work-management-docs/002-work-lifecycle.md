<!-- GENERATED — DO NOT EDIT -->
# Move work through its lifecycle

Define Work states, transitions, readiness, claims, delivery stages, completion gates, and guards.

Work Status and Delivery Stage are separate dimensions. Change one only through its owning authority.

## Work states

- **Inbox** (`inbox`): Captured work not yet triaged.
- **Triage** (`triage`): Work being classified.
- **Proposed** (`proposed`): Work proposed for approval.
- **Approved** (`approved`): Accepted work not yet admitted to Ready.
- **Ready** (`ready`): Executable queue state subject to readiness guards.
- **Active** (`active`): Claimed execution state.
- **Review** (`review`): Internal delivery state for review activity.
- **Verification** (`verification`): Internal delivery state for verification activity.
- **Documentation** (`documentation`): Internal delivery state for documentation reconciliation.
- **Blocked** (`blocked`): Execution cannot proceed because a blocker is present.
- **On Hold** (`on_hold`): Intentionally paused pending a review trigger.
- **Deferred** (`deferred`): Postponed for later reconsideration.
- **Rejected** (`rejected`): Not accepted for execution in current form.
- **Superseded** (`superseded`): Replaced by newer authoritative work.
- **Done** (`done`): Required completion gates are satisfied.

## Before work becomes Ready

- Required Project fields: Record Type, Priority, Effort, Documentation Impact.
- Required issue sections: Outcome, Acceptance criteria.
- Dependencies must be understood.

See the [Work Management Specification](../work-management-spec/001-specification.md) for every allowed transition and guard.
