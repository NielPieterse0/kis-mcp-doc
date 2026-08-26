<!-- GENERATED — DO NOT EDIT -->
# Authority and reconciliation policy

<div id="enable-section-numbers" />

[Previous: Next-work selection](005-next-work-selection.md) | [Next: Provider and command-plane boundary](007-provider-and-command-plane-boundary.md) | [Index](000-index.md)

<span id="mrd-kis-work-con-pol-001"></span>

Authority determines which system may change a fact. Reconciliation compares observed provider state with those owners and surfaces drift rather than choosing a new truth. Generated documentation remains downstream of every canonical source.

## Authority principles

- Work Management owns command fields.
- Repository change governance owns Change ID, Complexity, and Risk Triggers after a governed change exists.
- GitHub owns provider-native source identity and observed dependency evidence.
- Actions and governed verification evidence own source Verification.
- Generated specifications are downstream review projections with no write-back authority.
- Conflicts and unavailable evidence fail closed or remain explicitly unknown.

## Change-governance handoff

Work Management carries planning data into repository governance, but repository change governance owns governed change identity, complexity, and risk once a change exists. The current handoff uses change-governance schema version `1`.

Complexity and risk classification therefore remain repository-change facts after handoff. Work Management may display them as evidence but does not reclassify them independently.

## Reconciliation

Reconciliation follows authority direction: command fields may be brought to the intended Work Management state; evidence fields are re-read from their owner; handoff fields change authority when the governed change takes ownership. Conflicting or unavailable evidence remains explicit rather than being normalized into a convenient value.

## Exact Project and policy reference

The complete change-classification tables, GitHub Project schema, views, bindings, features, gates, and evidence limits are exact lookup data. See the [Work Project configuration reference](021-work-project-configuration-reference.md).

## Source and authority

This page projects `KIS-WORK-CON-POL-001` version `1.0.0`. The MRD remains authoritative; this generated page has no write-back authority.
