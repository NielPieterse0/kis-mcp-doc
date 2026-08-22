<!-- GENERATED — DO NOT EDIT -->
# Authority, Ownership, and Relationships

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

## Overview

Ensure every governed fact has one canonical owner and every non-owning artifact preserves authority through explicit typed relationships instead of restating truth.

## Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-OWN-001` | Every governed fact MUST have exactly one current canonical owner. | `review` |
| `KIS-MRD-OWN-002` | A non-owning MRD or repository artifact MAY summarize or project an owned fact for its audience but MUST reference the canonical owner and MUST NOT redefine the fact as independent authority. | `review` |
| `KIS-MRD-OWN-003` | Generated HRDs, indexes, dependency maps, and other META projections MUST remain downstream of their canonical sources and MUST NOT become write-back authority. | `generator` |
| `KIS-MRD-OWN-004` | Relationships between governed artifacts MUST use the governed relationship vocabulary; ad hoc relationship labels MUST NOT silently create new semantics. | `validator` |
| `KIS-MRD-OWN-005` | When two sources appear to own the same current fact, kis-op MUST surface the conflict and resolve ownership through the applicable authority order before accepting dependent work. | `workflow` |
| `KIS-MRD-OWN-006` | Supersession MUST preserve the previous owner's stable identity and lineage while making the replacement unambiguous. | `validator` |

## Ownership contract

- Canonical owners per governed fact: `1`
- Non-owner posture: `reference_not_restate`
- Derived posture: `projection_only`
- Conflict posture: `surface_diagnostic_and_resolve_against_current_owner`

## Canonical owner kinds

| Kind | Meaning |
|---|---|
| `prescriptive_mrd` | Machine-readable governance or product authority intentionally adopted as the canonical owner. |
| `executable_repo_source` | Code, configuration, schema, contract, or test that canonically owns an executable fact under repository authority routing. |
| `parent_governance_source` | A higher-authority KIS source that remains canonical until a governed adoption changes ownership. |

## Governed relationship vocabulary

| Relationship | Meaning |
|---|---|
| `depends_on` | The source requires the target authority to be valid or interpretable. |
| `validated_by` | The source is structurally or semantically checked by the target contract or validator. |
| `governs` | The source prescribes requirements for the target. |
| `constrains` | The source restricts permitted values or behavior of the target. |
| `selects` | The source chooses among behaviors already permitted by the target authority. |
| `maps_to` | The source translates deterministically to the target representation. |
| `implements` | The source is an implementation of target authority. |
| `evidences` | The source records evidence about the target without becoming its authority. |
| `projects` | The source is a generated view of the target and has no write-back authority. |
| `references` | The source points to the target owner without restating the governed fact as new authority. |
| `supersedes` | The source replaces the target while preserving lineage. |

## Source and authority

This page projects `KIS-KNOW-CON-POL-002` version `1.0.0`. The MRD remains authoritative; this page has no write-back authority.
