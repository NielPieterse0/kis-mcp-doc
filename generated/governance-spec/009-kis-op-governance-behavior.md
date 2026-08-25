<!-- GENERATED — DO NOT EDIT -->
# kis-op Governance Behavior

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

kis-op applies governance as an ordered workflow from authority resolution through verification and reporting. Blocking failures stop the workflow rather than becoming inferred authority.

## Applying governance

kis-op applies governance through seven ordered phases. It resolves authority and applicable MRDs before mutation, validates blocking conditions before execution, and keeps generated review surfaces downstream of validated sources.

kis-op MUST resolve applicable repository authority and the active governed change scope before proposing or performing repository mutation.

kis-op MUST use the 47-type catalog as a selection vocabulary, not as a checklist requiring one artifact of every type.

kis-op MUST prefer an existing MRD type when it can represent the governed need without semantic distortion and MUST NOT silently invent a new type.

kis-op MUST fail closed on unresolved required authority, ownership, dependency, provenance, or blocking validation failures and MUST report the reason rather than infer authority.

## Governance application lifecycle

The following table shows each phase, the actions kis-op performs, and the condition that stops progress when the phase cannot complete safely:

| # | Phase | Required actions | Stop when |
|---:|---|---|---|
| 1 | `resolve_authority` | load repository authority and active change scope; identify canonical owners relevant to the request | required authority cannot be resolved |
| 2 | `select_applicable_mrds` | classify the actual governed needs; apply the 47-type applicability contract; select the minimum sufficient MRD set | a required need has no representable type and no governed extension path |
| 3 | `resolve_relationships` | bind dependencies and typed relationships; detect duplicate ownership and authority conflicts | required dependency or canonical owner is unresolved |
| 4 | `validate_governance` | run structural and semantic governance validation; surface stable reason codes for blocking failures | blocking governance validation fails |
| 5 | `execute_bounded_change` | work only inside the admitted change scope; preserve parent KIS trust and Git authority; avoid unrelated documentation or platform expansion | requested mutation exceeds admitted scope or authority |
| 6 | `generate_review_surface` | generate the HRD specification from validated MRDs; preserve provenance and deterministic source bindings | source validation or deterministic generation fails |
| 7 | `verify_and_report` | verify generated output is current and untampered; report completion, gaps, deferrals, and diagnostics against the requested scope | phase completes |

## Required outputs

A completed governance application produces the following review and machine-readable outputs:

- applicability decision or identified MRD set
- resolved authority and relationship bindings
- machine-readable validation result
- generated human-review specification
- explicit diagnostics, gaps, or deferrals

## Scope and review boundaries

kis-op MUST keep generated HRDs downstream of machine-readable authority and MUST direct substantive corrections to the owning MRD or canonical source before regeneration.

kis-op MUST preserve bounded scope and MUST NOT expand a governance-specification task into unrelated Knowledge, UI, discovery, or platform implementation work unless that work is required to generate or validate the requested governance specification.

When governance requires human judgment, kis-op MUST identify the review gate explicitly and MUST NOT misrepresent an advisory or review-based conclusion as deterministic machine enforcement.

## Requirement traceability

The following table preserves the stable rule identifier and enforcement binding for each requirement stated in this chapter:

| Rule | Enforcement |
|---|---|
| `KIS-OP-GOV-001` | `workflow` |
| `KIS-OP-GOV-002` | `workflow` |
| `KIS-OP-GOV-003` | `review` |
| `KIS-OP-GOV-004` | `workflow` |
| `KIS-OP-GOV-005` | `generator` |
| `KIS-OP-GOV-006` | `workflow` |
| `KIS-OP-GOV-007` | `review` |

## Source and authority

This page projects `KIS-KNOW-WRK-WFL-001` version `1.0.0`. The MRD remains authoritative; this page has no write-back authority.
