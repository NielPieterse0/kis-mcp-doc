<!-- GENERATED — DO NOT EDIT -->
# Applicability and Selection

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

## Overview

Select the minimum sufficient governed MRD set for the actual repository need rather than instantiating the full catalog by default.

## Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-APP-001` | A repository or change MUST NOT instantiate all 47 MRD types by default; it MUST select only types whose applicability conditions are satisfied. | `workflow` |
| `KIS-MRD-APP-002` | Selection MUST classify the governed need by function before considering file location, technology, framework, or current implementation shape. | `review` |
| `KIS-MRD-APP-003` | When several types could represent the same need, the minimum sufficient non-duplicative set MUST be selected and each governed fact MUST retain one canonical owner. | `review` |
| `KIS-MRD-APP-004` | A required applicability trigger with no selected or existing canonical artifact MUST be reported as a governance gap before dependent implementation is accepted. | `validator` |
| `KIS-MRD-APP-005` | A technology or stack change, including adoption of tools such as uv, MUST first be represented using existing functional types such as version constraints, configuration, package manifests, contracts, or workflows when those types are sufficient. | `review` |
| `KIS-MRD-APP-006` | A new MRD type MAY be proposed only when the need cannot be represented without semantic distortion by any existing type, and the proposal MUST enter through a versioned governance amendment. | `workflow` |

## Selection contract

- Baseline catalog: `47` MRD types
- Default disposition: `not_applicable`
- Allowed dispositions: `required`, `optional`, `not_applicable`, `deferred`

### Selection order

1. identify the governed fact, decision, workflow, configuration, contract, prompt, evaluation, evidence, or derived view
2. match the need to an existing MRD type by function
3. apply the type trigger and select only the minimum sufficient artifacts
4. bind each selected artifact to its canonical owner and dependencies
5. record required gaps or justified deferrals before implementation
6. propose a catalog amendment only when no existing type can represent the need

## Type applicability catalog

| Code | Name | Use when |
|---|---|---|
| `SEM-ENT` | Entity definition schema | Use when a governed domain needs a canonical entity shape, identity, fields, or structural definition. |
| `SEM-ENUM` | Enumeration schema | Use when a finite controlled vocabulary or closed set of allowed values must be authoritative. |
| `SEM-ONT` | Ontology | Use when governed concepts and their semantic relationships need an explicit ontology. |
| `SEM-REG` | Registry | Use when named governed entries require one authoritative registry with stable identifiers. |
| `SEM-DOM` | Domain definition register | Use when a domain boundary, scope, vocabulary ownership, or domain definition must be registered. |
| `SEM-ASR` | Assertion rules | Use when invariants or semantic assertions must be stated independently of implementation code. |
| `CON-VRS` | Version constraint | Use when allowed, required, minimum, maximum, or compatible versions must be constrained. |
| `CON-BND` | Boundary rule | Use when an authority, security, filesystem, network, module, or responsibility boundary must be constrained. |
| `CON-POL` | Policy implementation | Use when durable policy determines what is permitted, prohibited, required, or conditionally allowed. |
| `CON-CTR` | Constraint contract | Use when constraints themselves require a reusable machine-consumable contract. |
| `DEC-TAB` | Decision table | Use when an outcome can be selected deterministically from a finite set of conditions in tabular form. |
| `DEC-TRE` | Decision tree | Use when ordered or branching conditions determine a governed outcome more clearly than a table. |
| `DEC-SCR` | Scoring model | Use when weighted criteria or scores determine a governed classification, threshold, or decision. |
| `WRK-STM` | State machine | Use when governed state, permitted transitions, and terminal states must be explicit. |
| `WRK-PRC` | Process definition | Use when a repeatable ordered process with defined inputs, steps, and outputs must be prescribed. |
| `WRK-APR` | Approval workflow | Use when approval, rejection, escalation, or sign-off flow must be governed. |
| `WRK-CTR` | Phase contract | Use when a workflow phase requires explicit entry, exit, handoff, or completion conditions. |
| `WRK-WFL` | Workflow definition | Use when several governed steps, roles, decisions, or phases form an end-to-end workflow. |
| `WRK-ACT` | Action or automation workflow | Use when a bounded action or automation sequence must be executable under governance. |
| `CFG-ENV` | Environment config | Use when environment-specific values select allowed behavior without redefining policy. |
| `CFG-FLG` | Feature flag | Use when a governed feature can be enabled or disabled through an explicit flag. |
| `CFG-PRM` | Runtime parameter | Use when a runtime parameter selects among already-permitted behaviors or limits. |
| `MAP-FLD` | Field mapping | Use when fields in one governed structure translate deterministically to fields in another. |
| `MAP-FMT` | Format translation | Use when one representation or serialization format must translate deterministically to another. |
| `MAP-MIG` | Migration map | Use when a versioned structure, identifier, or data model requires an explicit migration mapping. |
| `CTR-API` | API contract | Use when callable request/response behavior requires an explicit API interface contract. |
| `CTR-EVT` | Event contract | Use when produced or consumed events require stable names, payloads, and delivery semantics. |
| `CTR-SVC` | Service contract | Use when a service boundary, capability, inputs, outputs, or service-level interface must be contracted. |
| `MAN-PKG` | Package manifest | Use when a package's governed identity, contents, dependencies, or distribution metadata must be declared. |
| `MAN-BOM` | Bill of materials | Use when constituent components or dependencies must be inventoried as a bill of materials. |
| `MAN-REL` | Release manifest | Use when a release needs an authoritative manifest of version, contents, provenance, and release facts. |
| `MAN-SKL` | Skill manifest | Use when a reusable skill package needs a governed capability and asset manifest. |
| `MAN-ACT` | Action manifest | Use when available actions or automations must be inventoried separately from their workflow definitions. |
| `PRM-SYS` | System prompt | Use when durable system-level model instructions are governed as an explicit prompt artifact. |
| `PRM-ROL` | Role prompt | Use when a durable role-specific behavior or responsibility prompt must be governed. |
| `PRM-CTX` | Context prompt | Use when reusable context assembly or context framing instructions must be governed. |
| `PRM-TOL` | Tool prompt | Use when model-facing instructions for invoking or interpreting a tool must be governed. |
| `EVL-TST` | Test suite | Use when deterministic or machine-evaluable conformance tests define acceptance of governed behavior. |
| `EVL-RUB` | Rubric | Use when qualitative or multi-criterion review requires an explicit scoring or assessment rubric. |
| `EVL-BEN` | Benchmark | Use when comparable performance, quality, or capability measurement requires a stable benchmark. |
| `EVD-LOG` | Log | Use when an immutable operational or governance log is itself required evidence. |
| `EVD-APR` | Approval record | Use when an approval decision must be retained as evidence distinct from the approval workflow. |
| `EVD-LIN` | Lineage record | Use when lineage, derivation, handoff, or provenance events must be retained as evidence. |
| `EVD-TSR` | Test result snapshot | Use when a test or verification result must be retained as an immutable evidence snapshot. |
| `META-IDX` | Index | Generate when consumers need a derived index over governed artifacts; never author it as primary truth. |
| `META-DEP` | Dependency map | Generate when consumers need a derived dependency graph or map; never author it as primary truth. |
| `META-MAP` | Metadata map | Generate when consumers need derived metadata joins or lookup maps; never author it as primary truth. |

## Source and authority

This page projects `KIS-KNOW-DEC-TAB-001` version `1.0.0`. The MRD remains authoritative; this page has no write-back authority.
