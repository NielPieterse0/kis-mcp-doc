<!-- GENERATED — DO NOT EDIT -->
# Validation and Enforcement

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

## Overview

Define how structural and semantic governance requirements are checked, which enforcement mode applies, and which blocking failures must fail closed.

## Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-VAL-001` | Every MRD MUST pass structural, dependency, provenance, and lifecycle validation before it is accepted as valid. | `validator` |
| `KIS-MRD-VAL-002` | Validation failures MUST emit stable reason codes and machine-readable diagnostics. | `validator` |
| `KIS-MRD-VAL-003` | A validation result MUST report classification, layering, dependencies, provenance, lifecycle, and schema check status. | `validator` |
| `KIS-MRD-VAL-004` | Governance MRDs MUST validate through the public composed governance MRD profile, which binds the reusable core envelope to governance content. | `schema` |
| `KIS-MRD-VAL-005` | Any structural schema failure in the governance MRD set MUST short-circuit semantic validation for the entire set, because cross-record semantics are valid only over a structurally valid governance set. | `validator` |

## Enforcement modes

| Mode | Meaning | Blocking |
|---|---|---|
| `schema` | JSON Schema rejects structurally invalid authority before semantic checks. | Yes |
| `validator` | Deterministic semantic validation emits stable machine-readable reason codes. | Yes |
| `workflow` | KIS/kis-op governed workflow prevents prohibited state transitions or unadmitted mutation. | Yes |
| `generator` | Deterministic generation and stale-output verification enforce one-way source-to-view behavior. | Yes |
| `review` | Human or agent review is required where semantic adequacy cannot be proven deterministically. | Yes |

## Validation dimensions

### Structural

- required fields present
- identifier shape
- schema-compatible envelope and payload
- exactly one owner for each governance concern
- public composed governance MRD profile

### Applicability

- all 47 catalog types have one selection trigger
- applicability catalog matches classification catalog exactly
- minimum-sufficient selection is prescribed
- extension path remains versioned

### Ownership

- one canonical owner is prescribed for each governed fact
- dependency relationship labels use the governed relationship vocabulary
- generated projections remain non-authoritative

### Dependency

- all targets resolve
- layer direction valid
- no cycles
- no duplicate edges
- stable dependency identities

### Provenance

- source kinds valid
- repo sources resolve
- external references are fingerprinted
- source fingerprint matches source set
- no inferred normative facts

### Lifecycle

- record mode recognized
- status valid for mode
- active authority resolves
- EVD descriptive posture
- META meta posture
- supersession targets resolve

### Operator Behavior

- kis-op phases are complete and ordered
- blocking stop conditions are explicit
- generated review surface is downstream of validated authority

## Result contract

- Status: `valid`, `invalid`
- Check keys: `classification`, `applicability`, `ownership`, `layering`, `dependencies`, `provenance`, `lifecycle`, `operator_behavior`, `schema`
- Diagnostics on failure: required

## Stable reason codes

- `MRD_SCHEMA_INVALID`
- `MRD_RULE_ID_DUPLICATE`
- `MRD_GOVERNANCE_CONCERN_MISSING`
- `MRD_GOVERNANCE_CONCERN_DUPLICATE`
- `MRD_ID_CLASS_TYPE_MISMATCH`
- `MRD_CLASS_UNKNOWN`
- `MRD_TYPE_INVALID`
- `MRD_CATALOG_COUNT_MISMATCH`
- `MRD_LAYER_INVALID`
- `MRD_DEPENDENCY_UNRESOLVED`
- `MRD_DEPENDENCY_LAYER_VIOLATION`
- `MRD_DEPENDENCY_CYCLE`
- `MRD_DEPENDENCY_DUPLICATE`
- `MRD_SOURCE_UNRESOLVED`
- `MRD_SOURCE_FINGERPRINT_MISMATCH`
- `MRD_SOURCE_HASH_MISMATCH`
- `MRD_NORMATIVE_INFERENCE_PROHIBITED`
- `MRD_RECORD_MODE_INVALID`
- `MRD_STATUS_INVALID`
- `MRD_EVD_RECORD_MODE_INVALID`
- `MRD_META_RECORD_MODE_INVALID`
- `MRD_SUPERSESSION_UNRESOLVED`
- `MRD_CLASS_CATALOG_MISMATCH`
- `MRD_LAYER_CATALOG_MISMATCH`
- `MRD_RECORD_MODE_CATALOG_MISMATCH`
- `MRD_META_FACT_QUALITY_INVALID`
- `MRD_VALIDATION_CONTRACT_MISMATCH`
- `MRD_APPLICABILITY_CATALOG_MISMATCH`
- `MRD_RELATIONSHIP_UNKNOWN`
- `MRD_OPERATOR_BEHAVIOR_INVALID`
- `MRD_ENFORCEMENT_BINDING_INVALID`

## Source and authority

This page projects `KIS-KNOW-EVL-TST-001` version `2.0.0`. The MRD remains authoritative; this page has no write-back authority.
