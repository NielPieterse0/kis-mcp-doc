<!-- GENERATED — DO NOT EDIT -->
# Dependency Rules

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

## Overview

Make all authority dependencies explicit, stable, resolvable, and acyclic.

## Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-DEP-001` | Every dependency target MUST resolve. | `validator` |
| `KIS-MRD-DEP-002` | MRD-to-MRD dependency direction MUST satisfy the L0-L5 authority ordering. | `validator` |
| `KIS-MRD-DEP-003` | The MRD dependency graph MUST be acyclic. | `validator` |
| `KIS-MRD-DEP-004` | Duplicate dependency edges MUST be rejected. | `validator` |
| `KIS-MRD-DEP-005` | Dependency identities MUST be stable; canonical non-MRD dependencies MUST use repo: paths. | `validator` |
| `KIS-MRD-DEP-006` | A META-DEP projection MAY be generated from the validated dependency graph and MUST NOT become primary authority. | `generator` |

## Dependency target forms

| Kind | Field | Example |
|---|---|---|
| mrd | `mrd_id` | `KIS-KNOW-SEM-REG-001` |
| canonical_source | `source` | `repo:contracts/mrd/v1/mrd.schema.json` |

## Source and authority

This page projects `KIS-KNOW-CON-CTR-001` version `1.0.0`. The MRD remains authoritative; this page has no write-back authority.
