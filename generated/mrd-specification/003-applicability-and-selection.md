<!-- GENERATED — DO NOT EDIT -->
# Applicability and Selection

<div id="enable-section-numbers" />

[Previous: Classification](002-classification.md) | [Next: Authority, Ownership, and Relationships](004-authority-ownership-and-relationships.md) | [Index](000-index.md)

Governance artifacts are selected according to the need being governed. The 47-type MRD catalog is a vocabulary for choosing the minimum sufficient set, not a checklist that every repository or change must populate.

## Selecting governance artifacts

Selection starts from the 47-type catalog with `not_applicable` as the default disposition. A selected type can be classified as `required`, `optional`, `not_applicable`, `deferred`. The goal is to represent the governed need without creating duplicate authority.

<span id="rule-kis-mrd-app-001"></span>
A repository or change MUST NOT instantiate all 47 MRD types by default; it MUST select only types whose applicability conditions are satisfied.

<span id="rule-kis-mrd-app-002"></span>
Selection MUST classify the governed need by function before considering file location, technology, framework, or current implementation shape.

<span id="rule-kis-mrd-app-003"></span>
When several types could represent the same need, the minimum sufficient non-duplicative set MUST be selected and each governed fact MUST retain one canonical owner.

## Selection process

Apply the following process in order. It starts with the governed need and only considers a catalog extension after existing types have been tested for fit:

1. Identify the governed fact, decision, workflow, configuration, contract, prompt, evaluation, evidence, or derived view.
2. Match the need to an existing MRD type by function.
3. Apply the type trigger and select only the minimum sufficient artifacts.
4. Bind each selected artifact to its canonical owner and dependencies.
5. Record required gaps or justified deferrals before implementation.
6. Propose a catalog amendment only when no existing type can represent the need.

<span id="rule-kis-mrd-app-004"></span>
A required applicability trigger with no selected or existing canonical artifact MUST be reported as a governance gap before dependent implementation is accepted.

## Applicability reference

The complete 47-type selection catalog is an exact lookup surface. See the [MRD applicability catalog](020-applicability-catalog.md) for every type, name, and applicability trigger.

## Extending the catalog

Technology and stack choices do not create new MRD types by themselves. First represent the need with the existing functional vocabulary when that vocabulary is sufficient.

<span id="rule-kis-mrd-app-005"></span>
A technology or stack change, including adoption of tools such as uv, MUST first be represented using existing functional types such as version constraints, configuration, package manifests, contracts, or workflows when those types are sufficient.

<span id="rule-kis-mrd-app-006"></span>
A new MRD type MAY be proposed only when the need cannot be represented without semantic distortion by any existing type, and the proposal MUST enter through a versioned governance amendment.

## Requirement traceability

The following table preserves the stable rule identifier and enforcement binding for each requirement stated in this chapter:

| Rule | Enforcement |
|---|---|
| `KIS-MRD-APP-001` | `workflow` |
| `KIS-MRD-APP-002` | `review` |
| `KIS-MRD-APP-003` | `review` |
| `KIS-MRD-APP-004` | `validator` |
| `KIS-MRD-APP-005` | `review` |
| `KIS-MRD-APP-006` | `workflow` |

## Source and authority

This page projects `urn:uuid:6673613f-70e0-5004-aba9-103da53e5040` version `1.0.0`. The MRD remains authoritative; this page has no write-back authority.
