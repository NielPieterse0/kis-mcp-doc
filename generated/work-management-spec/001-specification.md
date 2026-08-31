<!-- GENERATED — DO NOT EDIT -->
# KIS Work Management Specification

<div id="enable-section-numbers" />

Governed operating specification for work intake, state, selection, delivery, reconciliation, and GitHub Project integration

Work Management is the governed KIS system for capturing, classifying, selecting, executing, verifying, and closing work across registered projects.

This publication follows `urn:uuid:ae7e7dc1-2b8b-5988-845d-24df49dcfe0a` as a `human_readable_specification`. MCP 2026 applies only within its bounded protocol domain, Google guidance affects presentation only, and implementation references cannot create or override Work Management facts.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" are to be interpreted as described in [BCP 14](https://www.rfc-editor.org/info/bcp14), [RFC2119](https://www.rfc-editor.org/rfc/rfc2119), and [RFC8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they appear in all capitals.

## Overview

Work Management gives work one shared lifecycle and one explicit authority model. It separates facts that Work Management may change from evidence observed from GitHub, repository change governance, verification, and derived delivery state.

A GitHub Project provides the shared provider surface, but it does not become the owner of every fact displayed there. Repository change governance remains authoritative for governed change identity, complexity, and risk; GitHub remains authoritative for provider-native source identity and dependency observations; verification systems own their evidence; and Work Management owns its command fields.

The captured live GitHub Project evidence is observed. Inventory is complete, and the configured Project schema is ready with no reported field, option, type, or view drift.

## Key concepts

- **Command data** is changed through Work Management operations, such as status, priority, effort, claims, holds, and deferrals.
- **Evidence data** is observed or projected from its owning source, such as GitHub source identity, repository change facts, verification, and delivery state.
- **Handoff data** begins as Work Management planning data and becomes repository-owned evidence when a governed change takes authority for it.
- **Generated documentation** explains and indexes the governed model. It never writes facts back to Work Management or its sources.

## How work moves

1. Capture work and classify it before it enters the executable queue.
2. Admit work to Ready only after the required source sections, Project fields, and dependency evidence are present.
3. Select Ready work deterministically, then establish an execution claim before activation.
4. Track repository delivery and source verification as evidence without replacing the Work lifecycle state.
5. After merge, reconcile any required documentation and live-verification obligations before the configured completion gates allow Done.

## Detailed specification

- [Work Management domain model](002-work-management-domain-model.md)
- [Work lifecycle](003-work-lifecycle.md)
- [Work operations](004-work-operations.md)
- [Next-work selection](005-next-work-selection.md)
- [Authority and reconciliation policy](006-authority-and-reconciliation-policy.md)
- [Provider and command-plane boundary](007-provider-and-command-plane-boundary.md)
- [Work Management conformance](008-work-management-conformance.md)

## Traceability

See the [documentation index](000-index.md), [semantic coverage](data/semantic-coverage.json), and [build manifest](manifest.json) for exact source identities, MRD versions, page/anchor mappings, hashes, and generated-file declarations.
