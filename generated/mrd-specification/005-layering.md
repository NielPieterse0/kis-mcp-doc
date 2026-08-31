<!-- GENERATED — DO NOT EDIT -->
# Layering

<div id="enable-section-numbers" />

[Previous: Authority, Ownership, and Relationships](004-authority-ownership-and-relationships.md) | [Next: Dependency Rules](006-dependency-rules.md) | [Index](000-index.md)

Authority layers constrain the direction of MRD dependencies. They express which governed facts can depend on which other facts, not repository layout or implementation order.

## Authority model

The governance model uses six authority layers from `L0` through `L5`. Lower layer numbers have higher authority for dependency direction; the layer does not describe storage location or implementation order.

<span id="rule-kis-mrd-layer-001"></span>
An MRD MAY depend only on an MRD in the same layer or a higher-authority layer with a lower layer number.

<span id="rule-kis-mrd-layer-002"></span>
An MRD MUST NOT depend on an MRD in a lower-authority layer with a higher layer number.

<span id="rule-kis-mrd-layer-003"></span>
Layer assignment expresses authority ordering, not storage location or implementation order.

## Authority layers

The following table defines what each authority layer represents:

| Layer | Name | Interpretation |
|---|---|---|
| `L0` | Foundational semantics | Defines meaning. |
| `L1` | Constraints and governance | Restricts permitted meaning or behavior. |
| `L2` | Decisions and workflows | Determines behavior. |
| `L3` | Configuration and mappings | Selects or configures allowed behavior. |
| `L4` | Evaluation and agent behavior | Measures or evaluates behavior. |
| `L5` | Evidence and observations | Records what happened. |

## Direction examples

The following examples show valid and invalid dependency directions under the authority ordering:

| Source | Target | Valid |
|---|---|---|
| `L3` | `L2` | Yes |
| `L3` | `L0` | Yes |
| `L1` | `L3` | No |
| `L0` | `L2` | No |

## Requirement traceability

The following table preserves the stable rule identifier and enforcement binding for each requirement stated in this chapter:

| Rule | Enforcement |
|---|---|
| `KIS-MRD-LAYER-001` | `validator` |
| `KIS-MRD-LAYER-002` | `validator` |
| `KIS-MRD-LAYER-003` | `review` |

## Source and authority

This page projects `urn:uuid:8a9346a9-0c83-5fa4-a91d-2de6ca3d57a9` version `1.0.0`. The MRD remains authoritative; this page has no write-back authority.
