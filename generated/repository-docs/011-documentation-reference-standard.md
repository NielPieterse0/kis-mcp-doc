<!-- GENERATED — DO NOT EDIT -->
# Documentation Reference Standard

Understand which sources may define facts, which sources may guide presentation, and how conflicts are handled.

Govern how KIS documentation uses canonical KIS authority, normative protocol sources, prescriptive writing guidance, implementation references, and inferred evidence without creating duplicate fact ownership.

## Authority roles

| Role | Domain | May define KIS facts |
|---|---|---|
| `canonical_kis` | KIS-specific facts, behavior, policy, configuration, lifecycle, and adopted requirements | Yes |
| `normative_external` | The bounded conformance domain owned by the external standard | No |
| `prescriptive_external` | Presentation or practice guidance where KIS authority is silent | No |
| `implementation_reference` | Bounded reusable documentation or engineering patterns | No |
| `inferred_evidence` | Derived evidence requiring verification against an owning source | No |

## Output classes

| Class | Purpose | Source rule |
|---|---|---|
| `human_documentation` | Teach concepts, tasks, workflows, examples, architecture, and operations in reader-oriented prose. | Canonical KIS facts supply factual content; approved references may inform organization and presentation only. |
| `human_readable_specification` | Explain adopted normative behavior while preserving requirement strength, identifiers, ownership, and traceability. | Adopted KIS MRDs and applicable normative external standards supply requirements; generated prose remains non-authoritative. |
| `generated_reference` | Expose exact tools, schemas, settings, policies, states, relationships, capabilities, permissions, and provenance. | Only canonical KIS facts or explicitly applicable normative protocol facts may populate factual reference data. |

## Conflict and reproducibility rules

- Canonical conflict: `surface_diagnostic_and_keep_canonical_owner`.
- Unsupported promotion: `block`.
- Stale or unpinned references: `block_when_active_or_used_by_deterministic_generation`.

MCP protocol material is normative only inside its applicable MCP conformance domain. Google Developer Documentation guidance is presentation guidance only; neither source becomes KIS repository authority.

