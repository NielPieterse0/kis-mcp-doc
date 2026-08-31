<!-- GENERATED — DO NOT EDIT -->
# Model authority and relationships

Ensure every governed fact has one canonical owner and every non-owning artifact preserves authority through explicit typed relationships instead of restating truth.

MRDs represent ownership and typed relationships without making repository-wide Governance part of the MRD format itself.

- Canonical owner count represented by the MRD model: **1**.
- Non-owner posture: `reference_not_restate`.
- Derived posture: `projection_only`.

## Relationship vocabulary

- `depends_on` ? The source requires the target authority to be valid or interpretable.
- `validated_by` ? The source is structurally or semantically checked by the target contract or validator.
- `governs` ? The source prescribes requirements for the target.
- `constrains` ? The source restricts permitted values or behavior of the target.
- `selects` ? The source chooses among behaviors already permitted by the target authority.
- `maps_to` ? The source translates deterministically to the target representation.
- `implements` ? The source is an implementation of target authority.
- `evidences` ? The source records evidence about the target without becoming its authority.
- `projects` ? The source is a generated view of the target and has no write-back authority.
- `references` ? The source points to the target owner without restating the governed fact as new authority.
- `supersedes` ? The source replaces the target while preserving lineage.

Use the [MRD Specification](../mrd-specification/001-specification.md) for exact dependency and layering constraints.
