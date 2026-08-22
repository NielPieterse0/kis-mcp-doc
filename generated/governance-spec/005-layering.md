<!-- GENERATED — DO NOT EDIT -->
# Layering

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

## Overview

Define authority ordering for MRD dependencies.

## Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-LAYER-001` | An MRD MAY depend only on an MRD in the same layer or a higher-authority layer with a lower layer number. | `validator` |
| `KIS-MRD-LAYER-002` | An MRD MUST NOT depend on an MRD in a lower-authority layer with a higher layer number. | `validator` |
| `KIS-MRD-LAYER-003` | Layer assignment expresses authority ordering, not storage location or implementation order. | `review` |

## Authority layers

| Layer | Name | Interpretation |
|---|---|---|
| `L0` | Foundational semantics | Defines meaning. |
| `L1` | Constraints and governance | Restricts permitted meaning or behavior. |
| `L2` | Decisions and workflows | Determines behavior. |
| `L3` | Configuration and mappings | Selects or configures allowed behavior. |
| `L4` | Evaluation and agent behavior | Measures or evaluates behavior. |
| `L5` | Evidence and observations | Records what happened. |

## Direction examples

| Source | Target | Valid |
|---|---|---|
| `L3` | `L2` | Yes |
| `L3` | `L0` | Yes |
| `L1` | `L3` | No |
| `L0` | `L2` | No |

## Source and authority

This page projects `KIS-KNOW-SEM-ENUM-001` version `1.0.0`. The MRD remains authoritative; this page has no write-back authority.
