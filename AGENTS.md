# kis-mcp-doc — Knowledge

Workspace: `C:\Projects\kis-mcp\.kis-mcp-doc`

## Mandate

`kis-mcp-doc` owns the KIS knowledge capability. Documentation is one generated projection of that capability, not the product boundary.

The capability owns the bridge from governed project reality to durable, queryable, traceable knowledge and generated human documentation. Its scope includes repository knowledge, provenance, retrieval, relationships, impact analysis, memory, publication-ready document models, and integration of approved research/semantic providers.

The long-term objective is code-derived documentation: authoritative facts live in code, contracts, schemas, configuration, tests, governed MDRs, and verified upstream sources; human-readable documents are generated views of those facts.

This repository is the reference implementation and proving ground for the Knowledge/Docs capability that will later land into `kis-mcp` through normal KIS governed slices.

## Authority

1. Read `C:\Projects\AGENTS.md`.
2. Read and follow parent `C:\Projects\kis-mcp\AGENTS.md` as the KIS governance, harness, trust, and change-workflow authority.
3. This file specializes only Knowledge/Docs scope and repository posture. It never overrides parent KIS hard rules, provider policy, project binding, Work Management, Discover, Skills, Git, verification, or publication authority.
4. `C:\Projects\kis-mcp\.kis-mcp-gov\AGENTS.md` defines the Gov/Doc boundary: Gov owns repository identity, authority, ownership, scope, governed relationships, and provenance requirements; Doc consumes those facts and must not redefine them.
5. Harvest repositories and external references are evidence and design sources, never automatic KIS authority.

## Repository posture

This repository is code-first and MDR-first.

`AGENTS.md` is the only hand-authored Markdown file permitted in this repository. The current bootstrap edit is the explicit grace-period exception that establishes this rule.

Do not create or maintain hand-authored `README.md`, `SPEC.md`, `docs/**/*.md`, runbooks, architecture prose, decision records, plans, or other durable Markdown truth. If a human-readable Markdown view is needed, define the source model and generator, then generate the view.

All other durable knowledge must be represented as governed machine-readable records and executable artefacts: MDRs, JSON/YAML data where approved, JSON Schemas, contracts, source/configuration, tests, generators, manifests, hashes, indexes, and generated build output.

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
- transformation of governed facts and MDRs into specifications, procedures, decisions, architecture, operations, governance, and other human views;
- deterministic generation, validation, packaging, publication manifests, and stale-view detection;
- adapters to approved KIS providers and research/semantic tools.

Knowledge does not own repository governance, trust policy, change admission, Git authority, provider security policy, or execution authority. Consume those through KIS/Gov contracts.

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
- `C:\Projects\kis-mcp\.kis-mcp-gov` — upstream governance semantics for identity, authority, ownership, scope, relationships, and provenance requirements.
- `C:\Projects\doc-solution` — harvest deterministic documentation/knowledge patterns, normalized governance models, provenance, lookup/filter/trace/impact/health/compare contracts, architecture/governance views, project-documentation build/publication, and human-doc generation lessons.
- `C:\Projects\GPT-OS` — harvest machine-readable governance sources, generated governance/documentation views, authority routing, module-boundary contracts, publication packages, integrity checks, and source-to-view verification patterns.
- `C:\Projects\supervox` — harvest MDR taxonomy, metadata envelopes, stable IDs, binding semantics, template inheritance, modular contracts, validation gates, cross-reference discipline, and MDR-to-document-type patterns such as specifications, procedures, and decision records.
- `C:\Projects\References\mcp-specification\mcp-docs-2026-07-28-direct-md-clean` — transitional target/reference corpus for the first specification-generation mandate; use its layout, navigation feel, section decomposition, and MCP specification corpus as parity evidence, not as KIS authority.
- DeepWiki/Litho and Graphify — keep as paired external reference candidates during Knowledge architecture development. Continuously compare their repository-understanding, graph, wiki/document generation, retrieval, MCP/tool exposure, and agent-processing patterns against the native KIS Knowledge design. Prefer selective adoption or composition over wholesale replacement unless later evidence justifies a different decision.

Pin harvest evidence to concrete revisions/hashes whenever the source supports them. Never silently harvest a moving source and present the result as reproducible.

## First product mandate — generated specification

The first delivery target is a generated specification experience comparable to the captured MCP documentation set.

Build the bridge in slices from source reality to normalized knowledge to rendered documents. Do not manually reproduce the target Markdown.

The required progression is:

1. Inventory the target MCP documentation structure and the corresponding KIS code/contracts/configuration/evidence needed to express equivalent KIS facts.
2. Define MDRs and schemas that can represent those facts without embedding presentation-specific prose as authority.
3. Build deterministic harvest/adaptation from KIS sources into the normalized knowledge/MDR layer.
4. Build renderers that generate the human documentation and specification views from that layer.
5. Compare generated output against the target corpus for information coverage, structure, navigation, metadata, references, readability, and provenance.
6. Iterate the bridge until generated output is sufficient to replace transitional hand-authored documentation.
7. Retire replaced Markdown only through KIS-safe recoverable change handling; never preserve two current canonical owners for the same fact.

The intended product surface starts with human Documents, then Specification, and may add governed views such as Repository Governance, Harness, Operations, architecture, decisions, procedures, and other knowledge projections. View taxonomy must come from MDR/document-type contracts, not ad hoc page creation.

## Slice and development workflow

Use the same KIS slice lifecycle, governance semantics, complexity/risk handling, Work Management integration, change claims, verification discipline, revision/version posture, and landing model as `kis-mcp`.

The lifecycle semantics must match KIS even when Doc uses different storage representation. Because this repository forbids hand-authored Markdown beyond `AGENTS.md`, change specifications, plans, tasks, decisions, evidence, and closeout state must be machine-readable MDRs or generated views of MDRs rather than independently maintained Markdown.

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

## MDR and generation requirements

MDRs must be schema-valid, versioned, stable-ID-bearing where identity matters, and explicit about ownership, source/provenance, status, revision, relationships/bindings, and supersession where applicable.

Adopt useful SuperVOX concepts selectively: metadata envelopes, stable IDs, document classes/types, bindings, template inheritance, validation contracts, machine-readability checks, and resolvable cross-references. Do not import SuperVOX domain authority or naming blindly.

Generated documentation must be reproducible from pinned inputs and generator version. Every publication package must make source revisions, hashes, generator identity/version, diagnostics, and staleness detectable.

Generated views must never become a write-back authority. Changes are made to the owning source/MDR/code/contract and regenerated.

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
