<!-- GENERATED — DO NOT EDIT -->
# Dependency Rules

<div id="enable-section-numbers" />

[Previous: Layering](005-layering.md) | [Next: Provenance](007-provenance.md) | [Index](000-index.md)

Dependencies make authority relationships explicit and verifiable. Each dependency identifies either another MRD or a canonical repository source that the MRD requires.

## Dependency model

A governed dependency must identify a stable target, resolve successfully, follow the authority-layer direction, and remain part of an acyclic graph. Generated dependency maps are projections of that validated graph, not a second source of truth.

<span id="rule-kis-mrd-dep-001"></span>
Every dependency target MUST resolve.

<span id="rule-kis-mrd-dep-002"></span>
MRD-to-MRD dependency direction MUST satisfy the L0-L5 authority ordering.

<span id="rule-kis-mrd-dep-003"></span>
The MRD dependency graph MUST be acyclic.

<span id="rule-kis-mrd-dep-004"></span>
Duplicate dependency edges MUST be rejected.

<span id="rule-kis-mrd-dep-005"></span>
Dependency identities MUST be stable; canonical non-MRD dependencies MUST use repo: paths.

<span id="rule-kis-mrd-dep-006"></span>
A META-DEP projection MAY be generated from the validated dependency graph and MUST NOT become primary authority.

## Dependency targets

Dependencies use one of the following target forms. MRD dependencies use stable MRD IDs; canonical repository dependencies use `repo:` paths:

| Kind | Field | Example |
|---|---|---|
| mrd | `mrd_id` | `urn:uuid:8cf956d6-521a-5515-8ce1-d48ab5855617` |
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

This page projects `urn:uuid:7eab1930-3cdf-58ee-8a6e-9d9519a17fba` version `1.0.0`. The MRD remains authoritative; this page has no write-back authority.
