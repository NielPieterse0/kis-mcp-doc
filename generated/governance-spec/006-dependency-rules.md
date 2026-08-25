<!-- GENERATED — DO NOT EDIT -->
# Dependency Rules

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

Dependencies make authority relationships explicit and verifiable. Each dependency identifies either another MRD or a canonical repository source that the MRD requires.

## Dependency model

A governed dependency must identify a stable target, resolve successfully, follow the authority-layer direction, and remain part of an acyclic graph. Generated dependency maps are projections of that validated graph, not a second source of truth.

Every dependency target MUST resolve.

MRD-to-MRD dependency direction MUST satisfy the L0-L5 authority ordering.

The MRD dependency graph MUST be acyclic.

Duplicate dependency edges MUST be rejected.

Dependency identities MUST be stable; canonical non-MRD dependencies MUST use repo: paths.

A META-DEP projection MAY be generated from the validated dependency graph and MUST NOT become primary authority.

## Dependency targets

Dependencies use one of the following target forms. MRD dependencies use stable MRD IDs; canonical repository dependencies use `repo:` paths:

| Kind | Field | Example |
|---|---|---|
| mrd | `mrd_id` | `KIS-KNOW-SEM-REG-001` |
| canonical_source | `source` | `repo:contracts/mrd/v1/mrd.schema.json` |

## Requirement traceability

The following table preserves the stable rule identifier and enforcement binding for each requirement stated in this chapter:

| Rule | Enforcement |
|---|---|
| `KIS-MRD-DEP-001` | `validator` |
| `KIS-MRD-DEP-002` | `validator` |
| `KIS-MRD-DEP-003` | `validator` |
| `KIS-MRD-DEP-004` | `validator` |
| `KIS-MRD-DEP-005` | `validator` |
| `KIS-MRD-DEP-006` | `generator` |

## Source and authority

This page projects `KIS-KNOW-CON-CTR-001` version `1.0.0`. The MRD remains authoritative; this page has no write-back authority.
