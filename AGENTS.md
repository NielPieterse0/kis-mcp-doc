# kis-mcp-doc — Governance + Knowledge/Docs

Workspace: `C:\Projects\kis-mcp-doc`

## Mandate

`kis-mcp-doc` is the engineering and proving ground for KIS governance and Knowledge/Docs capabilities that are intended for later governed adoption into `kis-mcp`.

Governance engineering covers machine-readable authority, applicability and selection, ownership, relationships, lifecycle, enforcement, and generated human review surfaces. Knowledge/Docs engineering covers the bridge from governed project reality to durable, queryable, traceable knowledge and generated human documentation.

The long-term objective is governed, source-derived knowledge and documentation: authoritative facts live in code, contracts, schemas, configuration, tests, governed MRDs, and verified upstream sources; human-readable documents are generated views of those facts.

The immediate product mandate is the generated `kis-op` Governance Specification defined below. Broader Knowledge/Docs capability work remains future scope until that mandate is complete.

## Authority

1. Read and follow parent `C:\Projects\kis-mcp\AGENTS.md` as the KIS platform governance, harness, trust, and change-workflow authority.
2. This repository owns the engineering and proving-ground work for both KIS governance and Knowledge/Docs capabilities intended for later governed adoption into `kis-mcp`.
3. This file specializes that engineering scope and repository posture. It never overrides parent KIS hard rules, provider policy, project binding, Work Management, Discover, Skills, Git, verification, or publication authority.
4. Governance models developed here may prescribe repository identity, authority, ownership, scope, governed relationships, provenance requirements, lifecycle, and enforcement, but they become parent KIS authority only after governed adoption into `kis-mcp`.
5. Harvest repositories and external references are evidence and design sources, never automatic KIS authority.

## Repository posture

This repository is code-first and MRD-first.

`AGENTS.md` is the only hand-authored Markdown file permitted in this repository. The current bootstrap edit is the explicit grace-period exception that establishes this rule.

Do not create or maintain hand-authored `README.md`, `SPEC.md`, `docs/**/*.md`, runbooks, architecture prose, decision records, plans, or other durable Markdown truth. If a human-readable Markdown view is needed, define the source model and generator, then generate the view.

All other durable knowledge must be represented as governed machine-readable records and executable artefacts: MRDs, JSON/YAML data where approved, JSON Schemas, contracts, source/configuration, tests, generators, manifests, hashes, indexes, and generated build output.

Generated Markdown is allowed only as an explicitly derived output. It must be reproducible, provenance-bearing, stale-detectable, and never edited as authority.

Temporary analysis belongs in KIS-approved temporary/change state, not as new durable repository documentation.

Until this workspace has an independently verified Git identity and KIS project binding, do not pretend that Git revision, remote identity, branch, or PR evidence exists. Establish those through the KIS bootstrap/governance route before normal implementation slices.

## Knowledge ownership

Knowledge owns the normalized project knowledge model and the services built on it, including:

- source registration, acquisition metadata, revision/freshness tracking, and provenance;
- repository/entity/relationship knowledge and cross-domain graph views;
- semantic and structural retrieval, filtering, trace, compare, impact, and health operations;
- durable project memory and retrieval policy, with explicit scope, source, confidence, freshness, and supersession semantics;
- context assembly for agents without silently converting inference into authority;
- transformation of governed facts and MRDs into specifications, procedures, decisions, architecture, operations, governance, and other human views;
- deterministic generation, validation, packaging, publication manifests, and stale-view detection;
- adapters to approved KIS providers and research/semantic tools.

This repository may design and prescribe repository-governance contracts, but it does not independently exercise parent KIS trust policy, change admission, Git authority, provider security policy, or execution authority. Those remain governed by the parent `kis-mcp` authority until any new governance contract is formally adopted there.

Memory is knowledge, not hidden authority. A remembered statement must remain distinguishable from verified repository truth, generated inference, external evidence, and operator direction. Conflicts are resolved against the current canonical owner, not by memory recency alone.

## Model and provider posture

The primary product target is the OpenAI GPT ecosystem: GPT models, ChatGPT, Codex, and OpenAI-compatible agent/tooling surfaces. Design Knowledge interfaces, generated context, retrieval payloads, agent workflows, documentation outputs, and evaluation primarily for those consumers unless a governed slice explicitly broadens the target.

OpenAI-first does not mean OpenAI-only. Keep model-facing contracts portable where doing so does not weaken the primary GPT/Codex/ChatGPT experience or introduce unnecessary abstraction.

Use KIS capability/provider registration as the exposure boundary. Do not build private side-door integrations that bypass KIS provider governance.

NVIDIA NIM/free API endpoints are an approved auxiliary LLM execution resource when available through KIS. They may be used for bounded runner agents, parallel document analysis, candidate synthesis, review/evaluation, DeepWiki-style repository processing, and other non-authoritative workloads. Their outputs remain evidence or generated proposals until verified through the owning source and Knowledge validation path.

Serena, Graphify if onboarded, DeepWiki/Litho-derived capabilities if adopted, and future repository/search/graph/research MCPs may contribute semantic evidence, graph evidence, candidate relationships, retrieval, or analysis. Their output is advisory evidence until verified and classified against governed project sources.

Provider availability must be discovered at runtime. Never hardcode the continued presence, version, capability, security posture, or authority of a provider into Knowledge semantics.

Prefer composition: deterministic repository evidence + governed metadata + semantic enrichment + graph enrichment + bounded model-assisted processing. Do not replace deterministic identity, revision, ownership, contract, schema, test, or provenance evidence with embeddings or LLM inference.

## Harvest source registry — bootstrap inventory

The first implementation slices must convert this bootstrap list into a machine-readable, versioned harvest-source registry with source role, path/identity, revision strategy, trust classification, acquisition method, and applicable contracts.

- `C:\Projects\kis-mcp` — primary KIS governance/harness source; harvest Discover, providers, capabilities, contracts, settings, tests, change slices, Work Management, and current implementation facts without duplicating parent authority.
- `C:\Projects\doc-solution` — harvest deterministic documentation/knowledge patterns, normalized governance models, provenance, lookup/filter/trace/impact/health/compare contracts, architecture/governance views, project-documentation build/publication, and human-doc generation lessons.
- `C:\Projects\GPT-OS` — harvest machine-readable governance sources, generated governance/documentation views, authority routing, module-boundary contracts, publication packages, integrity checks, and source-to-view verification patterns.
- `C:\Projects\supervox` — harvest MRD taxonomy, metadata envelopes, stable IDs, binding semantics, template inheritance, modular contracts, validation gates, cross-reference discipline, and MRD-to-document-type patterns such as specifications, procedures, and decision records.
- `C:\Projects\References\mcp-specification\mcp-spec-2025-11-25-direct-md-clean` — target/reference corpus for the first specification-generation mandate while FastMCP 4.x remains a transitional implementation target; use its layout, navigation feel, section decomposition, normative presentation, and MCP specification corpus as parity evidence, not as KIS authority.
- DeepWiki/Litho and Graphify — keep as paired external reference candidates during Knowledge architecture development. Continuously compare their repository-understanding, graph, wiki/document generation, retrieval, MCP/tool exposure, and agent-processing patterns against the native KIS Knowledge design. Prefer selective adoption or composition over wholesale replacement unless later evidence justifies a different decision.

Pin harvest evidence to concrete revisions/hashes whenever the source supports them. Never silently harvest a moving source and present the result as reproducible.

## First product mandate — generated `kis-op` Governance Specification

The first delivery target is the generated human-reviewable `kis-op` Governance Specification, derived from governed machine-readable authority and presented with conventions comparable to the captured MCP 2025 specification set.

Until that governance specification is complete, keep implementation scope on prescribing the `kis-op` governance model: the 47-MRD baseline, applicability and selection, lifecycle, ownership, relationships and bindings, validation and enforcement, extensibility, and the behavior expected from `kis-op`. Broader Knowledge/Docs platform work remains future scope unless it is strictly required to generate or validate this governance specification.

Build the bridge in slices from governed governance authority to normalized model to rendered specification. Do not manually reproduce the target Markdown.

The required progression for this first mandate is:

1. Use the MCP 2025 corpus as presentation and specification-structure evidence, not as KIS authority.
2. Preserve the existing 47-MRD classification baseline and prescribe explicit applicability and minimum-sufficient selection rules for every type.
3. Prescribe canonical fact ownership, governed relationships and bindings, authority layering, provenance, lifecycle, extensibility, and `kis-op` operating behavior as machine-readable MRDs.
4. Make deterministic portions machine-enforceable through schemas, validators, workflow contracts, generated-view checks, and stable diagnostics; label review-based enforcement distinctly.
5. Generate the human-reviewable `kis-op` Governance Specification from the validated MRDs with MCP-spec-style overview, navigation, normative requirements, references, and traceability.
6. Verify exact source coverage, deterministic generation, provenance, stale/tamper detection, and requirements-to-implementation completeness.
7. Treat operator review and acceptance of the generated governance specification as the gate before broadening into the wider Knowledge/Docs product surface.

The broader Knowledge/Docs surface remains future scope. It may later add Documents, Repository Governance, Harness, Operations, architecture, decisions, procedures, and other governed projections, but their taxonomy must come from MRD/document-type contracts rather than ad hoc page creation.

## Slice and development workflow

Use the same KIS slice lifecycle, governance semantics, complexity/risk handling, Work Management integration, change claims, verification discipline, revision/version posture, and landing model as `kis-mcp`.

The lifecycle semantics must match KIS even when Doc uses different storage representation. Because this repository forbids hand-authored Markdown beyond `AGENTS.md`, change specifications, plans, tasks, decisions, evidence, and closeout state must be machine-readable MRDs or generated views of MRDs rather than independently maintained Markdown.

Do not weaken the parent workflow to avoid this constraint. Extend the Knowledge model/generator so the normal KIS workflow can be expressed without creating a second documentation system.

When a proven capability is ready for platform adoption, land it into `kis-mcp` as a normal governed KIS change. This repository remains the development/proving ground; parent KIS remains platform authority.

## Source and truth posture

Classify every input before promoting it into project knowledge:

- governing/canonical source;
- canonical machine-readable record;
- executable implementation evidence;
- generated derived view;
- external/reference evidence;
- semantic/research-provider evidence;
- model-generated inference or proposal;
- operator direction.

One governed fact has one canonical owner. Derived knowledge may summarize, index, relate, or render it, but must preserve the source owner and provenance rather than restating itself as new authority.

Inference must be labeled as inference. Unknowns must remain unknown. Contradictions must surface as diagnostics. Fresh evidence may supersede stale evidence only through the owning authority's rules.

## MRD and generation requirements

MRDs must be schema-valid, versioned, stable-ID-bearing where identity matters, and explicit about ownership, source/provenance, status, revision, relationships/bindings, and supersession where applicable.

Adopt useful SuperVOX concepts selectively: metadata envelopes, stable IDs, document classes/types, bindings, template inheritance, validation contracts, machine-readability checks, and resolvable cross-references. Do not import SuperVOX domain authority or naming blindly.

Generated documentation must be reproducible from pinned inputs and generator version. Every publication package must make source revisions, hashes, generator identity/version, diagnostics, and staleness detectable.

Generated views must never become a write-back authority. Changes are made to the owning source/MRD/code/contract and regenerated.

Prefer deterministic transforms for identity, structure, references, metadata, indexes, manifests, and factual tables. LLM assistance may draft candidate narrative or relationships only behind explicit provenance and validation boundaries.

## Validation and completion

For every slice, validate the narrowest applicable source schemas, contracts, generators, renderers, provenance, cross-references, and parent KIS integration. Add tests that prove generated views match their source facts and fail when sources are stale, contradictory, unbound, or invalid.

Do not claim parity from visual similarity alone. Specification parity requires traceable information coverage and correct ownership as well as presentation quality.

A slice is complete only when its machine-readable authority, implementation, tests, generated views, provenance, and KIS workflow evidence agree.

## Anti-patterns

Do not:

- hand-author the final documentation that the product is supposed to generate;
- create parallel Markdown truth because generation is not implemented yet;
- let memory, Graphify, Serena, an LLM, or another research provider override governed repository facts;
- conflate search relevance with authority or confidence;
- copy SuperVOX, GPT-OS, Doc Solution, or MCP reference content wholesale instead of harvesting the reusable contract or pattern;
- encode presentation layout as the only knowledge model;
- publish generated content without revision/hash provenance;
- hide stale, missing, contradictory, or inferred facts;
- create a second workflow beside KIS for convenience;
- treat this repository's experiments as parent KIS authority before they are governed and landed.

## Bootstrap exit condition

The bootstrap/grace period ends after this `AGENTS.md` is established and any non-permitted Markdown has been placed in recoverable quarantine outside this child workspace.

Subsequent durable work must enter through the KIS-governed slice workflow once repository identity and project binding are established.
