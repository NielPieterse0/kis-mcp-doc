<!-- GENERATED — DO NOT EDIT -->
# Provenance

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

## Overview

Preserve authority direction and distinguish authored prescription from derived implementation views and captured evidence.

## Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-PROV-001` | Record mode MUST express authority and mutability; KIS does not define a separate generation_mode in the core standard. | `validator` |
| `KIS-MRD-PROV-002` | Code harvesting MAY produce candidate or meta/descriptive MRDs but MUST NOT automatically create prescriptive authority. | `workflow` |
| `KIS-MRD-PROV-003` | A harvested candidate becomes prescriptive only through explicit adoption or review; after adoption, implementation MUST conform to the prescriptive MRD. | `workflow` |
| `KIS-MRD-PROV-004` | Inferred facts MUST NOT become normative automatically and MUST NOT appear as active prescriptive facts. | `validator` |
| `KIS-MRD-PROV-005` | Generated human-readable documents and META projections MUST NOT write back authority into their sources. | `generator` |
| `KIS-MRD-PROV-006` | The provenance source fingerprint MUST deterministically identify the declared provenance source set. | `validator` |
| `KIS-MRD-PROV-007` | Author intent, invariants, choices, and contracts; derive implementation observations; capture runtime evidence; evaluate conformance between them. | `review` |
| `KIS-MRD-PROV-008` | A repo_path provenance source MUST carry the SHA-256 of the resolved repository file; a mismatch MUST invalidate provenance. | `validator` |

## Record modes

| Record mode | Meaning | Mutability |
|---|---|---|
| `prescriptive` | What must be true. Authored, reviewed, and explicitly adopted as governing authority. | `versioned` |
| `descriptive` | What happened or is observed. Captured evidence or records. | `immutable_after_creation` |
| `meta` | A generated representation, index, or map of other authority. | `regenerate_only` |

## Fact quality

| Quality | Meaning |
|---|---|
| `direct` | Explicitly present in an admitted source. |
| `derived` | Deterministic transformation of direct facts. |
| `inferred` | Interpretation not directly guaranteed by an admitted source. |

## Provenance source kinds

| Kind | Resolution requirement |
|---|---|
| `operator_direction` | stable opaque identity |
| `repo_path` | must resolve inside repository and carry the current file SHA-256 |
| `external_reference` | must carry an immutable SHA-256 fingerprint |

## Source and authority

This page projects `KIS-KNOW-CON-POL-001` version `1.0.0`. The MRD remains authoritative; this page has no write-back authority.
