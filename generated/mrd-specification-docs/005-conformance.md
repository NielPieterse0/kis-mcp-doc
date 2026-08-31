<!-- GENERATED — DO NOT EDIT -->
# Validate MRD conformance

Define MRD structural and semantic conformance checks, stable result semantics, and blocking failure codes.

MRD conformance validation checks the MRD model and its declared relationships. Repository Governance separately governs when and how repository changes are admitted, reviewed, and evidenced.

## Conformance checks

- `classification`
- `applicability`
- `ownership`
- `layering`
- `dependencies`
- `provenance`
- `lifecycle`
- `schema`

## Stable failure codes

- `MRD_SCHEMA_INVALID`
- `MRD_RULE_ID_DUPLICATE`
- `MRD_GOVERNANCE_CONCERN_MISSING`
- `MRD_GOVERNANCE_CONCERN_DUPLICATE`
- `MRD_IDENTITY_INVALID`
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
- `MRD_ENFORCEMENT_BINDING_INVALID`

Use the [MRD Specification](../mrd-specification/001-specification.md) for the exact result contract and enforcement bindings.
