<!-- GENERATED — DO NOT EDIT -->
# Troubleshoot governance failures

Use canonical stop conditions and validation evidence to decide what must be fixed before work continues.

## Common blocking situations

- required authority cannot be resolved.
- a required need has no representable type and no governed extension path.
- required dependency or canonical owner is unresolved.
- blocking governance validation fails.
- requested mutation exceeds admitted scope or authority.
- source validation or deterministic generation fails.

## Validation evidence

Validation uses stable reason codes. Do not infer past a blocking diagnostic.

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

Use the [Governance Specification](../governance-spec/001-specification.md) to resolve a reason code against its normative validation contract.
