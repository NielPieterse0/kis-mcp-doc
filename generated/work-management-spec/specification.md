<!-- GENERATED — DO NOT EDIT -->
# KIS Work Management Specification

<div id="enable-section-numbers" />

Governed operating specification for work intake, state, selection, delivery, reconciliation, and GitHub Project integration.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY", and "OPTIONAL" are normative when they appear in all capitals.

## Overview

Work Management separates command authority from evidence. It governs work-item semantics, lifecycle state, deterministic selection, provider reconciliation, delivery evidence, and closeout while keeping repository change governance authoritative for governed change facts.

The specification is generated from seven prescriptive MRDs harvested from the pinned `kis-mcp` implementation contracts. Live GitHub Project evidence that could not be observed remains explicitly unavailable rather than inferred.

## Detailed specification

- [Work Management domain model](002-work-management-domain-model.md)
- [Work lifecycle](003-work-lifecycle.md)
- [Work operations](004-work-operations.md)
- [Next-work selection](005-next-work-selection.md)
- [Authority and reconciliation policy](006-authority-and-reconciliation-policy.md)
- [Provider and command-plane boundary](007-provider-and-command-plane-boundary.md)
- [Work Management conformance](008-work-management-conformance.md)

## Traceability

See the [documentation index](000-index.md) and [build manifest](manifest.json) for source identities and hashes.
