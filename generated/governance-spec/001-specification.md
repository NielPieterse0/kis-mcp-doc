<!-- GENERATED — DO NOT EDIT -->
# kis-op Governance Specification

<div id="enable-section-numbers" />

Governance contract for MRD selection, authority, lifecycle, enforcement, and kis-op behavior

This specification defines the generated human-review contract for KIS governance. The validated MRDs and canonical repository sources are authoritative; this corpus is a deterministic projection for review and navigation.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [RFC2119] [RFC8174] when, and only when, they appear in all capitals.

## Overview

The governance model is defined by 9 validated prescriptive MRDs. It uses the 47 MRD types as a minimum-sufficient selection vocabulary and keeps generated documentation downstream of canonical authority.

Substantive changes are made in the owning MRD, contract, schema, code, configuration, or test and then regenerated. Missing or inferred facts are never promoted into normative authority by the renderer.

## Key details

- 47 governed MRD types with explicit applicability rules
- one canonical owner for each governed fact
- typed dependencies, provenance, lifecycle, and enforcement
- deterministic generated review surfaces with stale/tamper detection

## Detailed specification

- [Classification](002-classification.md)
- [Applicability and Selection](003-applicability-and-selection.md)
- [Authority, Ownership, and Relationships](004-authority-ownership-and-relationships.md)
- [Layering](005-layering.md)
- [Dependency Rules](006-dependency-rules.md)
- [Provenance](007-provenance.md)
- [Lifecycle](008-lifecycle.md)
- [kis-op Governance Behavior](009-kis-op-governance-behavior.md)
- [Validation and Enforcement](010-validation-and-enforcement.md)

## Traceability

See the [documentation index](000-index.md), [MRD index](data/mrd-index.json), [dependency map](data/dependency-map.json), and [build manifest](manifest.json) for exact source identities, hashes, and generated-file declarations.
