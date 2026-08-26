<!-- GENERATED — DO NOT EDIT -->
# Classification

<div id="enable-section-numbers" />

[Previous: Specification](001-specification.md) | [Next: Applicability and Selection](003-applicability-and-selection.md) | [Index](000-index.md)

KIS MRDs use a functional classification model. Classification describes what an artifact does, independent of where a repository stores or implements it.

## Classification requirements

The catalog contains 12 functional classes and 47 allowed MRD types. Classification is based on function so that the same governed need keeps the same meaning across repository layouts and technology choices.

Every MRD MUST declare exactly one class and one type from this catalog.

Classification MUST describe what an artifact does, not where the artifact is stored.

A new MRD type MUST NOT be introduced when an existing catalog type adequately represents the artifact.

Artifacts MUST NOT be created merely to populate unused catalog types; absence of an unused type has no compliance implication.

The catalog MAY be extended by a versioned governance amendment when a genuine artifact need cannot be represented by an existing type.

## Classes

The following table defines the functional classes used to group MRD types:

| Class | Name | Definition |
|---|---|---|
| `SEM` | Semantics | Defines canonical meaning, vocabulary, entities, enumerations, ontologies, registries, domains, and assertions. |
| `CON` | Constraints | Restricts permitted meaning or behavior through validation, boundaries, policy, and constraint contracts. |
| `DEC` | Decisions | Determines outcomes through decision tables, trees, and scoring models. |
| `WRK` | Workflows | Defines permitted state transitions, processes, approvals, phases, workflows, and actions. |
| `CFG` | Configuration | Selects or parameterizes allowed behavior through environments, flags, and runtime parameters. |
| `MAP` | Mappings | Defines deterministic translation between fields, formats, or versions. |
| `CTR` | Contracts | Defines externally or internally consumable API, event, and service interfaces. |
| `MAN` | Manifests | Declares package, bill-of-materials, release, skill, and action inventories. |
| `PRM` | Prompts | Defines system, role, context, and tool prompt behavior. |
| `EVL` | Evaluations | Defines tests, rubrics, and benchmarks used to measure conformance or quality. |
| `EVD` | Evidence | Records logs, approvals, lineage, and test-result observations. |
| `META` | Derived metadata | Contains generated indexes, dependency maps, and metadata maps; never primary authority. |

## Type catalog (47 allowed types)

The following table lists each governed type and its canonical representation format:

| Class | Type | Code | Meaning | Canonical format |
|---|---|---|---|---|
| `SEM` | `ENT` | `SEM-ENT` | Entity definition schema | JSON Schema |
| `SEM` | `ENUM` | `SEM-ENUM` | Enumeration schema | JSON Schema |
| `SEM` | `ONT` | `SEM-ONT` | Ontology | JSON Schema |
| `SEM` | `REG` | `SEM-REG` | Registry | JSON |
| `SEM` | `DOM` | `SEM-DOM` | Domain definition register | JSON |
| `SEM` | `ASR` | `SEM-ASR` | Assertion rules | JSON Schema |
| `CON` | `VRS` | `CON-VRS` | Version constraint | JSON |
| `CON` | `BND` | `CON-BND` | Boundary rule | JSON |
| `CON` | `POL` | `CON-POL` | Policy implementation | JSON |
| `CON` | `CTR` | `CON-CTR` | Constraint contract | JSON |
| `DEC` | `TAB` | `DEC-TAB` | Decision table | JSON |
| `DEC` | `TRE` | `DEC-TRE` | Decision tree | JSON |
| `DEC` | `SCR` | `DEC-SCR` | Scoring model | JSON |
| `WRK` | `STM` | `WRK-STM` | State machine | JSON |
| `WRK` | `PRC` | `WRK-PRC` | Process definition | JSON |
| `WRK` | `APR` | `WRK-APR` | Approval workflow | JSON |
| `WRK` | `CTR` | `WRK-CTR` | Phase contract | JSON |
| `WRK` | `WFL` | `WRK-WFL` | Workflow definition | JSON |
| `WRK` | `ACT` | `WRK-ACT` | Action or automation workflow | JSON |
| `CFG` | `ENV` | `CFG-ENV` | Environment config | JSON or YAML |
| `CFG` | `FLG` | `CFG-FLG` | Feature flag | JSON or YAML |
| `CFG` | `PRM` | `CFG-PRM` | Runtime parameter | JSON or YAML |
| `MAP` | `FLD` | `MAP-FLD` | Field mapping | JSON |
| `MAP` | `FMT` | `MAP-FMT` | Format translation | JSON |
| `MAP` | `MIG` | `MAP-MIG` | Migration map | JSON |
| `CTR` | `API` | `CTR-API` | API contract | JSON |
| `CTR` | `EVT` | `CTR-EVT` | Event contract | JSON |
| `CTR` | `SVC` | `CTR-SVC` | Service contract | JSON |
| `MAN` | `PKG` | `MAN-PKG` | Package manifest | JSON |
| `MAN` | `BOM` | `MAN-BOM` | Bill of materials | JSON |
| `MAN` | `REL` | `MAN-REL` | Release manifest | JSON |
| `MAN` | `SKL` | `MAN-SKL` | Skill manifest | JSON |
| `MAN` | `ACT` | `MAN-ACT` | Action manifest | JSON |
| `PRM` | `SYS` | `PRM-SYS` | System prompt | JSON |
| `PRM` | `ROL` | `PRM-ROL` | Role prompt | JSON |
| `PRM` | `CTX` | `PRM-CTX` | Context prompt | JSON |
| `PRM` | `TOL` | `PRM-TOL` | Tool prompt | JSON |
| `EVL` | `TST` | `EVL-TST` | Test suite | JSON Schema |
| `EVL` | `RUB` | `EVL-RUB` | Rubric | JSON Schema |
| `EVL` | `BEN` | `EVL-BEN` | Benchmark | JSON Schema |
| `EVD` | `LOG` | `EVD-LOG` | Log | JSON |
| `EVD` | `APR` | `EVD-APR` | Approval record | JSON |
| `EVD` | `LIN` | `EVD-LIN` | Lineage record | JSON |
| `EVD` | `TSR` | `EVD-TSR` | Test result snapshot | JSON |
| `META` | `IDX` | `META-IDX` | Index | JSON |
| `META` | `DEP` | `META-DEP` | Dependency map | JSON |
| `META` | `MAP` | `META-MAP` | Metadata map | JSON |

## Requirement traceability

The following table preserves the stable rule identifier and enforcement binding for each requirement stated in this chapter:

| Rule | Enforcement |
|---|---|
| `KIS-MRD-CLASS-001` | `validator` |
| `KIS-MRD-CLASS-002` | `review` |
| `KIS-MRD-CLASS-003` | `review` |
| `KIS-MRD-CLASS-004` | `workflow` |
| `KIS-MRD-CLASS-005` | `workflow` |

## Source and authority

This page projects `KIS-KNOW-SEM-REG-001` version `1.0.0`. The MRD remains authoritative; this page has no write-back authority.
