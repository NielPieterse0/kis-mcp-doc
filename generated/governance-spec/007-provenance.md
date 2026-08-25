<!-- GENERATED — DO NOT EDIT -->
# Provenance

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

Provenance identifies the authority, origin, and quality of governed facts. It keeps authored prescription, captured observations, and generated projections distinct.

## Provenance model

Record mode expresses both authority and mutability, while fact quality describes how directly a fact is supported by admitted evidence. This separation prevents harvested, inferred, or generated material from silently becoming prescriptive authority.

Record mode MUST express authority and mutability; KIS does not define a separate generation_mode in the core standard.

Code harvesting MAY produce candidate or meta/descriptive MRDs but MUST NOT automatically create prescriptive authority.

A harvested candidate becomes prescriptive only through explicit adoption or review; after adoption, implementation MUST conform to the prescriptive MRD.

Inferred facts MUST NOT become normative automatically and MUST NOT appear as active prescriptive facts.

Generated human-readable documents and META projections MUST NOT write back authority into their sources.

The provenance source fingerprint MUST deterministically identify the declared provenance source set.

Author intent, invariants, choices, and contracts; derive implementation observations; capture runtime evidence; evaluate conformance between them.

A repo_path provenance source MUST carry the SHA-256 of the resolved repository file; a mismatch MUST invalidate provenance.

## Record modes

The following table defines the authority and mutability posture of each record mode:

| Record mode | Meaning | Mutability |
|---|---|---|
| `prescriptive` | What must be true. Authored, reviewed, and explicitly adopted as governing authority. | `versioned` |
| `descriptive` | What happened or is observed. Captured evidence or records. | `immutable_after_creation` |
| `meta` | A generated representation, index, or map of other authority. | `regenerate_only` |

## Fact quality

Fact quality records whether a fact is direct, deterministically derived, or inferred:

| Quality | Meaning |
|---|---|
| `direct` | Explicitly present in an admitted source. |
| `derived` | Deterministic transformation of direct facts. |
| `inferred` | Interpretation not directly guaranteed by an admitted source. |

## Provenance source kinds

Each provenance source kind has a resolution or fingerprint requirement, as shown in the following table:

| Kind | Resolution requirement |
|---|---|
| `operator_direction` | stable opaque identity |
| `repo_path` | must resolve inside repository and carry the current file SHA-256 |
| `external_reference` | must carry an immutable SHA-256 fingerprint |

## Requirement traceability

The following table preserves the stable rule identifier and enforcement binding for each requirement stated in this chapter:

| Rule | Enforcement |
|---|---|
| `KIS-MRD-PROV-001` | `validator` |
| `KIS-MRD-PROV-002` | `workflow` |
| `KIS-MRD-PROV-003` | `workflow` |
| `KIS-MRD-PROV-004` | `validator` |
| `KIS-MRD-PROV-005` | `generator` |
| `KIS-MRD-PROV-006` | `validator` |
| `KIS-MRD-PROV-007` | `review` |
| `KIS-MRD-PROV-008` | `validator` |

## Source and authority

This page projects `KIS-KNOW-CON-POL-001` version `1.0.0`. The MRD remains authoritative; this page has no write-back authority.
