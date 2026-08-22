<!-- GENERATED — DO NOT EDIT -->
# Lifecycle

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

## Overview

Define minimal lifecycle and mutability rules for each record mode.

## Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-LIFE-001` | Active prescriptive MRDs MUST have resolved dependencies and valid provenance. | `validator` |
| `KIS-MRD-LIFE-002` | Descriptive EVD records MUST be immutable after creation. | `workflow` |
| `KIS-MRD-LIFE-003` | META records MUST be regenerated from their sources rather than manually maintained. | `generator` |
| `KIS-MRD-LIFE-004` | A derived or generated artifact MUST be treated as stale when its declared source fingerprint no longer matches its admitted sources. | `generator` |
| `KIS-MRD-LIFE-005` | Superseded MRDs MUST remain addressable for lineage and MUST identify their replacement when one exists. | `validator` |
| `KIS-MRD-LIFE-006` | Git history is the change history; a duplicate body changelog is not required by the core MRD standard. | `review` |

## State machines

| Record mode | States | Allowed transitions |
|---|---|---|
| `prescriptive` | draft → active → superseded | draft → active; active → superseded |
| `descriptive` | created → retained | created → retained |
| `meta` | generated → replaced | generated → replaced |

## Source and authority

This page projects `KIS-KNOW-WRK-STM-001` version `1.0.0`. The MRD remains authoritative; this page has no write-back authority.
