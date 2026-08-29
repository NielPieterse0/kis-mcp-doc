<!-- GENERATED — DO NOT EDIT -->
# Coverage and freshness

A repository bundle is complete only when its declared source set and generated output agree.

The current source inventory contains **102** source or declared generated-family artefacts.

## Freshness model

- Every source file is content-hashed in the repository-docs manifest.
- The artefact inventory repeats per-artefact content hashes for direct trace and comparison.
- Exact generated-file inventory and bytes are checked by `publications-check-generated`.
- Site, search, and release verification independently reject stale downstream bundles.
- Exact containing Git revision is bound externally through Git/provider evidence rather than embedded into tracked generated content, avoiding a circular commit identity.

## Coverage exclusions

Historical `.work` records, temporary/runtime state, virtual environments, caches, and generated outputs are not re-ingested as current repository source authority. Work Management remains a separate publication family.
