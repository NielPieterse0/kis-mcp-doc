<!-- GENERATED -- DO NOT EDIT -->
# Documentation Reference Standard

<div id="enable-section-numbers" />

Source roles, authority boundaries, provenance, lifecycle, and permitted use for KIS documentation references

This specification governs how documentation references can influence KIS documentation. It keeps source authority separate from presentation guidance and implementation evidence.

## Authority model

- **`canonical_kis`:** KIS-specific facts, behavior, policy, configuration, lifecycle, and adopted requirements; may define KIS facts.
- **`normative_external`:** The bounded conformance domain owned by the external standard; MUST NOT define KIS facts.
- **`prescriptive_external`:** Presentation or practice guidance where KIS authority is silent; MUST NOT define KIS facts.
- **`implementation_reference`:** Bounded reusable documentation or engineering patterns; MUST NOT define KIS facts.
- **`inferred_evidence`:** Derived evidence requiring verification against an owning source; MUST NOT define KIS facts.

## Documentation output classes

### Human documentation

Teach concepts, tasks, workflows, examples, architecture, and operations in reader-oriented prose.

Canonical KIS facts supply factual content; approved references may inform organization and presentation only.

### Human-readable specification

Explain adopted normative behavior while preserving requirement strength, identifiers, ownership, and traceability.

Adopted KIS MRDs and applicable normative external standards supply requirements; generated prose remains non-authoritative.

### Generated reference

Expose exact tools, schemas, settings, policies, states, relationships, capabilities, permissions, and provenance.

Only canonical KIS facts or explicitly applicable normative protocol facts may populate factual reference data.

## Reference registry

Refresh references only through a governed registry change. Deterministic builds use the pinned registry state and never fetch live sources.

Metadata and bounded pattern summaries are permitted. Harvesting reusable source content requires source-specific license and attribution review first.

## Conflict behavior

When a reference conflicts with a canonical owner, KIS surfaces the conflict and keeps the canonical owner unchanged. Unsupported authority promotion and active unpinned references fail validation.

## Requirements

### KIS-DOC-REF-001

Every admitted documentation reference MUST declare one source role, bounded permitted uses, provenance, freshness strategy, lifecycle state, and authority limit.

### KIS-DOC-REF-002

KIS-owned factual content MUST remain sourced from its current canonical owner; a documentation reference MUST NOT become a second owner.

### KIS-DOC-REF-003

MCP 2026-07-28 MUST be treated as normative only within its applicable MCP protocol-conformance domain.

### KIS-DOC-REF-004

Google Developer Documentation guidance MUST remain presentation guidance and MUST NOT define KIS runtime or governance semantics.

### KIS-DOC-REF-005

Implementation references and inferred evidence MUST NOT populate canonical KIS facts without a separately governed adoption decision.

### KIS-DOC-REF-006

Material used by deterministic generation MUST resolve to a reproducible revision or content hash; live moving web content MUST NOT be a silent build input.

### KIS-DOC-REF-007

Contradictions with a canonical owner MUST surface as diagnostics and MUST NOT silently change the canonical value.

### KIS-DOC-REF-008

Generated documentation MUST remain a deterministic review projection with no write-back authority.

### KIS-DOC-REF-009

External content MUST NOT be harvested beyond metadata or bounded evidence until licensing, attribution, and reuse constraints are recorded.

## Source and authority

This page is generated from `KIS-DOC-CON-POL-001` and `KIS-DOC-SEM-REG-001`. It has no write-back authority.
