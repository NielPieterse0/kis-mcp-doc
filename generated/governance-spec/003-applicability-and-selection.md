<!-- GENERATED — DO NOT EDIT -->
# Applicability and Selection

<div id="enable-section-numbers" />

[Specification](001-specification.md) | [Documentation index](000-index.md)

Governance artifacts are selected according to the need being governed. The 47-type MRD catalog is a vocabulary for choosing the minimum sufficient set, not a checklist that every repository or change must populate.

## Selecting governance artifacts

Selection starts from the 47-type catalog with `not_applicable` as the default disposition. A selected type can be classified as `required`, `optional`, `not_applicable`, `deferred`. The goal is to represent the governed need without creating duplicate authority.

A repository or change MUST NOT instantiate all 47 MRD types by default; it MUST select only types whose applicability conditions are satisfied.

Selection MUST classify the governed need by function before considering file location, technology, framework, or current implementation shape.

When several types could represent the same need, the minimum sufficient non-duplicative set MUST be selected and each governed fact MUST retain one canonical owner.

## Selection process

Apply the following process in order. It starts with the governed need and only considers a catalog extension after existing types have been tested for fit:

1. Identify the governed fact, decision, workflow, configuration, contract, prompt, evaluation, evidence, or derived view.
2. Match the need to an existing MRD type by function.
3. Apply the type trigger and select only the minimum sufficient artifacts.
4. Bind each selected artifact to its canonical owner and dependencies.
5. Record required gaps or justified deferrals before implementation.
6. Propose a catalog amendment only when no existing type can represent the need.

A required applicability trigger with no selected or existing canonical artifact MUST be reported as a governance gap before dependent implementation is accepted.

## MRD type applicability

Use the following catalog to determine when each MRD type applies. The table is a selection reference; it does not require an artifact for every row:

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

## Extending the catalog

Technology and stack choices do not create new MRD types by themselves. First represent the need with the existing functional vocabulary when that vocabulary is sufficient.

A technology or stack change, including adoption of tools such as uv, MUST first be represented using existing functional types such as version constraints, configuration, package manifests, contracts, or workflows when those types are sufficient.

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

This page projects `KIS-KNOW-DEC-TAB-001` version `1.0.0`. The MRD remains authoritative; this page has no write-back authority.
