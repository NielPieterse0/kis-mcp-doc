<!-- GENERATED — DO NOT EDIT -->
# kis-op Governance Specification

<div id="enable-section-numbers" />

> **Status:** draft
> **Version:** 2.0.0
> **Authority:** Generated human-readable projection; the source MRDs are authoritative.
> **Generator:** kis-mcp-doc 0.1.0 / governance-spec-v2

Governance contract for MRD selection, authority, lifecycle, enforcement, and kis-op behavior

## Overview

This specification is a deterministic human-readable projection of 9 validated governance MRDs. It prescribes how `kis-op` selects and applies the KIS MRD governance model while preserving repository authority, provenance, lifecycle, and enforcement boundaries.

The 47 MRD types form a governed selection vocabulary. A repository or change uses only the minimum sufficient applicable types; the catalog is not a requirement to instantiate all 47 types.

Substantive changes belong in the owning MRD or canonical repository source and are then regenerated into this review surface. The generated document is a downstream review projection, not an independent write-back authority.

The capitalized terms **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, **MAY**, and **OPTIONAL** express normative requirements when they appear in all capitals.

## Specification Contents

- [1. Classification](#1-classification)
- [2. Applicability and Selection](#2-applicability-and-selection)
- [3. Authority, Ownership, and Relationships](#3-authority-ownership-and-relationships)
- [4. Layering](#4-layering)
- [5. Dependency Rules](#5-dependency-rules)
- [6. Provenance](#6-provenance)
- [7. Lifecycle](#7-lifecycle)
- [8. kis-op Governance Behavior](#8-kis-op-governance-behavior)
- [9. Validation and Enforcement](#9-validation-and-enforcement)
- [Traceability](#traceability)

## 1. Classification

Define the stable functional vocabulary used to classify KIS MRDs without coupling classification to repository layout.

### Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-CLASS-001` | Every MRD MUST declare exactly one class and one type from this catalog. | `validator` |
| `KIS-MRD-CLASS-002` | Classification MUST describe what an artifact does, not where the artifact is stored. | `review` |
| `KIS-MRD-CLASS-003` | A new MRD type MUST NOT be introduced when an existing catalog type adequately represents the artifact. | `review` |
| `KIS-MRD-CLASS-004` | Artifacts MUST NOT be created merely to populate unused catalog types; absence of an unused type has no compliance implication. | `workflow` |
| `KIS-MRD-CLASS-005` | The catalog MAY be extended by a versioned governance amendment when a genuine artifact need cannot be represented by an existing type. | `workflow` |

### Classes

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

### Type catalog (47 allowed types)

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

## 2. Applicability and Selection

Select the minimum sufficient governed MRD set for the actual repository need rather than instantiating the full catalog by default.

### Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-APP-001` | A repository or change MUST NOT instantiate all 47 MRD types by default; it MUST select only types whose applicability conditions are satisfied. | `workflow` |
| `KIS-MRD-APP-002` | Selection MUST classify the governed need by function before considering file location, technology, framework, or current implementation shape. | `review` |
| `KIS-MRD-APP-003` | When several types could represent the same need, the minimum sufficient non-duplicative set MUST be selected and each governed fact MUST retain one canonical owner. | `review` |
| `KIS-MRD-APP-004` | A required applicability trigger with no selected or existing canonical artifact MUST be reported as a governance gap before dependent implementation is accepted. | `validator` |
| `KIS-MRD-APP-005` | A technology or stack change, including adoption of tools such as uv, MUST first be represented using existing functional types such as version constraints, configuration, package manifests, contracts, or workflows when those types are sufficient. | `review` |
| `KIS-MRD-APP-006` | A new MRD type MAY be proposed only when the need cannot be represented without semantic distortion by any existing type, and the proposal MUST enter through a versioned governance amendment. | `workflow` |

### Selection contract

- Baseline catalog: `47` MRD types
- Default disposition: `not_applicable`
- Allowed dispositions: `required`, `optional`, `not_applicable`, `deferred`

#### Selection order

1. identify the governed fact, decision, workflow, configuration, contract, prompt, evaluation, evidence, or derived view
2. match the need to an existing MRD type by function
3. apply the type trigger and select only the minimum sufficient artifacts
4. bind each selected artifact to its canonical owner and dependencies
5. record required gaps or justified deferrals before implementation
6. propose a catalog amendment only when no existing type can represent the need

### Type applicability catalog

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

## 3. Authority, Ownership, and Relationships

Ensure every governed fact has one canonical owner and every non-owning artifact preserves authority through explicit typed relationships instead of restating truth.

### Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-OWN-001` | Every governed fact MUST have exactly one current canonical owner. | `review` |
| `KIS-MRD-OWN-002` | A non-owning MRD or repository artifact MAY summarize or project an owned fact for its audience but MUST reference the canonical owner and MUST NOT redefine the fact as independent authority. | `review` |
| `KIS-MRD-OWN-003` | Generated HRDs, indexes, dependency maps, and other META projections MUST remain downstream of their canonical sources and MUST NOT become write-back authority. | `generator` |
| `KIS-MRD-OWN-004` | Relationships between governed artifacts MUST use the governed relationship vocabulary; ad hoc relationship labels MUST NOT silently create new semantics. | `validator` |
| `KIS-MRD-OWN-005` | When two sources appear to own the same current fact, kis-op MUST surface the conflict and resolve ownership through the applicable authority order before accepting dependent work. | `workflow` |
| `KIS-MRD-OWN-006` | Supersession MUST preserve the previous owner's stable identity and lineage while making the replacement unambiguous. | `validator` |

### Ownership contract

- Canonical owners per governed fact: `1`
- Non-owner posture: `reference_not_restate`
- Derived posture: `projection_only`
- Conflict posture: `surface_diagnostic_and_resolve_against_current_owner`

### Canonical owner kinds

| Kind | Meaning |
|---|---|
| `prescriptive_mrd` | Machine-readable governance or product authority intentionally adopted as the canonical owner. |
| `executable_repo_source` | Code, configuration, schema, contract, or test that canonically owns an executable fact under repository authority routing. |
| `parent_governance_source` | A higher-authority KIS source that remains canonical until a governed adoption changes ownership. |

### Governed relationship vocabulary

| Relationship | Meaning |
|---|---|
| `depends_on` | The source requires the target authority to be valid or interpretable. |
| `validated_by` | The source is structurally or semantically checked by the target contract or validator. |
| `governs` | The source prescribes requirements for the target. |
| `constrains` | The source restricts permitted values or behavior of the target. |
| `selects` | The source chooses among behaviors already permitted by the target authority. |
| `maps_to` | The source translates deterministically to the target representation. |
| `implements` | The source is an implementation of target authority. |
| `evidences` | The source records evidence about the target without becoming its authority. |
| `projects` | The source is a generated view of the target and has no write-back authority. |
| `references` | The source points to the target owner without restating the governed fact as new authority. |
| `supersedes` | The source replaces the target while preserving lineage. |

## 4. Layering

Define authority ordering for MRD dependencies.

### Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-LAYER-001` | An MRD MAY depend only on an MRD in the same layer or a higher-authority layer with a lower layer number. | `validator` |
| `KIS-MRD-LAYER-002` | An MRD MUST NOT depend on an MRD in a lower-authority layer with a higher layer number. | `validator` |
| `KIS-MRD-LAYER-003` | Layer assignment expresses authority ordering, not storage location or implementation order. | `review` |

### Authority layers

| Layer | Name | Interpretation |
|---|---|---|
| `L0` | Foundational semantics | Defines meaning. |
| `L1` | Constraints and governance | Restricts permitted meaning or behavior. |
| `L2` | Decisions and workflows | Determines behavior. |
| `L3` | Configuration and mappings | Selects or configures allowed behavior. |
| `L4` | Evaluation and agent behavior | Measures or evaluates behavior. |
| `L5` | Evidence and observations | Records what happened. |

### Direction examples

| Source | Target | Valid |
|---|---|---|
| `L3` | `L2` | Yes |
| `L3` | `L0` | Yes |
| `L1` | `L3` | No |
| `L0` | `L2` | No |

## 5. Dependency Rules

Make all authority dependencies explicit, stable, resolvable, and acyclic.

### Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-DEP-001` | Every dependency target MUST resolve. | `validator` |
| `KIS-MRD-DEP-002` | MRD-to-MRD dependency direction MUST satisfy the L0-L5 authority ordering. | `validator` |
| `KIS-MRD-DEP-003` | The MRD dependency graph MUST be acyclic. | `validator` |
| `KIS-MRD-DEP-004` | Duplicate dependency edges MUST be rejected. | `validator` |
| `KIS-MRD-DEP-005` | Dependency identities MUST be stable; canonical non-MRD dependencies MUST use repo: paths. | `validator` |
| `KIS-MRD-DEP-006` | A META-DEP projection MAY be generated from the validated dependency graph and MUST NOT become primary authority. | `generator` |

### Dependency target forms

| Kind | Field | Example |
|---|---|---|
| mrd | `mrd_id` | `KIS-KNOW-SEM-REG-001` |
| canonical_source | `source` | `repo:contracts/mrd/v1/mrd.schema.json` |

## 6. Provenance

Preserve authority direction and distinguish authored prescription from derived implementation views and captured evidence.

### Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-PROV-001` | Record mode MUST express authority and mutability; KIS does not define a separate generation_mode in the core standard. | `validator` |
| `KIS-MRD-PROV-002` | Code harvesting MAY produce candidate or meta/descriptive MRDs but MUST NOT automatically create prescriptive authority. | `workflow` |
| `KIS-MRD-PROV-003` | A harvested candidate becomes prescriptive only through explicit adoption or review; after adoption, implementation MUST conform to the prescriptive MRD. | `workflow` |
| `KIS-MRD-PROV-004` | Inferred facts MUST NOT become normative automatically and MUST NOT appear as active prescriptive facts. | `validator` |
| `KIS-MRD-PROV-005` | Generated human-readable documents and META projections MUST NOT write back authority into their sources. | `generator` |
| `KIS-MRD-PROV-006` | The provenance source fingerprint MUST deterministically identify the declared provenance source set. | `validator` |
| `KIS-MRD-PROV-007` | Author intent, invariants, choices, and contracts; derive implementation observations; capture runtime evidence; evaluate conformance between them. | `review` |
| `KIS-MRD-PROV-008` | A repo_path provenance source MUST carry the SHA-256 of the resolved repository file; a mismatch MUST invalidate provenance. | `validator` |

### Record modes

| Record mode | Meaning | Mutability |
|---|---|---|
| `prescriptive` | What must be true. Authored, reviewed, and explicitly adopted as governing authority. | `versioned` |
| `descriptive` | What happened or is observed. Captured evidence or records. | `immutable_after_creation` |
| `meta` | A generated representation, index, or map of other authority. | `regenerate_only` |

### Fact quality

| Quality | Meaning |
|---|---|
| `direct` | Explicitly present in an admitted source. |
| `derived` | Deterministic transformation of direct facts. |
| `inferred` | Interpretation not directly guaranteed by an admitted source. |

### Provenance source kinds

| Kind | Resolution requirement |
|---|---|
| `operator_direction` | stable opaque identity |
| `repo_path` | must resolve inside repository and carry the current file SHA-256 |
| `external_reference` | must carry an immutable SHA-256 fingerprint |

## 7. Lifecycle

Define minimal lifecycle and mutability rules for each record mode.

### Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-LIFE-001` | Active prescriptive MRDs MUST have resolved dependencies and valid provenance. | `validator` |
| `KIS-MRD-LIFE-002` | Descriptive EVD records MUST be immutable after creation. | `workflow` |
| `KIS-MRD-LIFE-003` | META records MUST be regenerated from their sources rather than manually maintained. | `generator` |
| `KIS-MRD-LIFE-004` | A derived or generated artifact MUST be treated as stale when its declared source fingerprint no longer matches its admitted sources. | `generator` |
| `KIS-MRD-LIFE-005` | Superseded MRDs MUST remain addressable for lineage and MUST identify their replacement when one exists. | `validator` |
| `KIS-MRD-LIFE-006` | Git history is the change history; a duplicate body changelog is not required by the core MRD standard. | `review` |

### State machines

| Record mode | States | Allowed transitions |
|---|---|---|
| `prescriptive` | draft → active → superseded | draft → active; active → superseded |
| `descriptive` | created → retained | created → retained |
| `meta` | generated → replaced | generated → replaced |

## 8. kis-op Governance Behavior

Prescribe how kis-op applies the governance model when inspecting, planning, changing, validating, and presenting governed repository work.

### Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-OP-GOV-001` | kis-op MUST resolve applicable repository authority and the active governed change scope before proposing or performing repository mutation. | `workflow` |
| `KIS-OP-GOV-002` | kis-op MUST use the 47-type catalog as a selection vocabulary, not as a checklist requiring one artifact of every type. | `workflow` |
| `KIS-OP-GOV-003` | kis-op MUST prefer an existing MRD type when it can represent the governed need without semantic distortion and MUST NOT silently invent a new type. | `review` |
| `KIS-OP-GOV-004` | kis-op MUST fail closed on unresolved required authority, ownership, dependency, provenance, or blocking validation failures and MUST report the reason rather than infer authority. | `workflow` |
| `KIS-OP-GOV-005` | kis-op MUST keep generated HRDs downstream of machine-readable authority and MUST direct substantive corrections to the owning MRD or canonical source before regeneration. | `generator` |
| `KIS-OP-GOV-006` | kis-op MUST preserve bounded scope and MUST NOT expand a governance-specification task into unrelated Knowledge, UI, discovery, or platform implementation work unless that work is required to generate or validate the requested governance specification. | `workflow` |
| `KIS-OP-GOV-007` | When governance requires human judgment, kis-op MUST identify the review gate explicitly and MUST NOT misrepresent an advisory or review-based conclusion as deterministic machine enforcement. | `review` |

### Governance application lifecycle

| # | Phase | Required actions | Stop when |
|---:|---|---|---|
| 1 | `resolve_authority` | load repository authority and active change scope; identify canonical owners relevant to the request | required authority cannot be resolved |
| 2 | `select_applicable_mrds` | classify the actual governed needs; apply the 47-type applicability contract; select the minimum sufficient MRD set | a required need has no representable type and no governed extension path |
| 3 | `resolve_relationships` | bind dependencies and typed relationships; detect duplicate ownership and authority conflicts | required dependency or canonical owner is unresolved |
| 4 | `validate_governance` | run structural and semantic governance validation; surface stable reason codes for blocking failures | blocking governance validation fails |
| 5 | `execute_bounded_change` | work only inside the admitted change scope; preserve parent KIS trust and Git authority; avoid unrelated documentation or platform expansion | requested mutation exceeds admitted scope or authority |
| 6 | `generate_review_surface` | generate the HRD specification from validated MRDs; preserve provenance and deterministic source bindings | source validation or deterministic generation fails |
| 7 | `verify_and_report` | verify generated output is current and untampered; report completion, gaps, deferrals, and diagnostics against the requested scope | phase completes |

### Required outputs

- applicability decision or identified MRD set
- resolved authority and relationship bindings
- machine-readable validation result
- generated human-review specification
- explicit diagnostics, gaps, or deferrals

## 9. Validation and Enforcement

Define how structural and semantic governance requirements are checked, which enforcement mode applies, and which blocking failures must fail closed.

### Normative rules

| Rule | Requirement | Enforcement |
|---|---|---|
| `KIS-MRD-VAL-001` | Every MRD MUST pass structural, dependency, provenance, and lifecycle validation before it is accepted as valid. | `validator` |
| `KIS-MRD-VAL-002` | Validation failures MUST emit stable reason codes and machine-readable diagnostics. | `validator` |
| `KIS-MRD-VAL-003` | A validation result MUST report classification, layering, dependencies, provenance, lifecycle, and schema check status. | `validator` |
| `KIS-MRD-VAL-004` | Governance MRDs MUST validate through the public composed governance MRD profile, which binds the reusable core envelope to governance content. | `schema` |
| `KIS-MRD-VAL-005` | Any structural schema failure in the governance MRD set MUST short-circuit semantic validation for the entire set, because cross-record semantics are valid only over a structurally valid governance set. | `validator` |

### Enforcement modes

| Mode | Meaning | Blocking |
|---|---|---|
| `schema` | JSON Schema rejects structurally invalid authority before semantic checks. | Yes |
| `validator` | Deterministic semantic validation emits stable machine-readable reason codes. | Yes |
| `workflow` | KIS/kis-op governed workflow prevents prohibited state transitions or unadmitted mutation. | Yes |
| `generator` | Deterministic generation and stale-output verification enforce one-way source-to-view behavior. | Yes |
| `review` | Human or agent review is required where semantic adequacy cannot be proven deterministically. | Yes |

### Validation dimensions

#### Structural

- required fields present
- identifier shape
- schema-compatible envelope and payload
- exactly one owner for each governance concern
- public composed governance MRD profile

#### Applicability

- all 47 catalog types have one selection trigger
- applicability catalog matches classification catalog exactly
- minimum-sufficient selection is prescribed
- extension path remains versioned

#### Ownership

- one canonical owner is prescribed for each governed fact
- dependency relationship labels use the governed relationship vocabulary
- generated projections remain non-authoritative

#### Dependency

- all targets resolve
- layer direction valid
- no cycles
- no duplicate edges
- stable dependency identities

#### Provenance

- source kinds valid
- repo sources resolve
- external references are fingerprinted
- source fingerprint matches source set
- no inferred normative facts

#### Lifecycle

- record mode recognized
- status valid for mode
- active authority resolves
- EVD descriptive posture
- META meta posture
- supersession targets resolve

#### Operator_Behavior

- kis-op phases are complete and ordered
- blocking stop conditions are explicit
- generated review surface is downstream of validated authority

### Result contract

- Status: `valid`, `invalid`
- Check keys: `classification`, `applicability`, `ownership`, `layering`, `dependencies`, `provenance`, `lifecycle`, `operator_behavior`, `schema`
- Diagnostics on failure: required

### Stable reason codes

- `MRD_SCHEMA_INVALID`
- `MRD_RULE_ID_DUPLICATE`
- `MRD_GOVERNANCE_CONCERN_MISSING`
- `MRD_GOVERNANCE_CONCERN_DUPLICATE`
- `MRD_ID_CLASS_TYPE_MISMATCH`
- `MRD_CLASS_UNKNOWN`
- `MRD_TYPE_INVALID`
- `MRD_CATALOG_COUNT_MISMATCH`
- `MRD_LAYER_INVALID`
- `MRD_DEPENDENCY_UNRESOLVED`
- `MRD_DEPENDENCY_LAYER_VIOLATION`
- `MRD_DEPENDENCY_CYCLE`
- `MRD_DEPENDENCY_DUPLICATE`
- `MRD_SOURCE_UNRESOLVED`
- `MRD_SOURCE_FINGERPRINT_MISMATCH`
- `MRD_SOURCE_HASH_MISMATCH`
- `MRD_NORMATIVE_INFERENCE_PROHIBITED`
- `MRD_RECORD_MODE_INVALID`
- `MRD_STATUS_INVALID`
- `MRD_EVD_RECORD_MODE_INVALID`
- `MRD_META_RECORD_MODE_INVALID`
- `MRD_SUPERSESSION_UNRESOLVED`
- `MRD_CLASS_CATALOG_MISMATCH`
- `MRD_LAYER_CATALOG_MISMATCH`
- `MRD_RECORD_MODE_CATALOG_MISMATCH`
- `MRD_META_FACT_QUALITY_INVALID`
- `MRD_VALIDATION_CONTRACT_MISMATCH`
- `MRD_APPLICABILITY_CATALOG_MISMATCH`
- `MRD_RELATIONSHIP_UNKNOWN`
- `MRD_OPERATOR_BEHAVIOR_INVALID`
- `MRD_ENFORCEMENT_BINDING_INVALID`

## Traceability

Each normative section above is projected from exactly one prescriptive MRD:

| Section | MRD | Version | Provenance sources |
|---|---|---:|---|
| 1. Classification | `KIS-KNOW-SEM-REG-001` | 1.0.0 | KIS-OPERATOR-DIRECTION-2026-08-21, SVX-LIB-STD-003-v3.3.15 |
| 2. Applicability and Selection | `KIS-KNOW-DEC-TAB-001` | 1.0.0 | KIS-OPERATOR-DIRECTION-2026-08-22 |
| 3. Authority, Ownership, and Relationships | `KIS-KNOW-CON-POL-002` | 1.0.0 | KIS-OPERATOR-DIRECTION-2026-08-22 |
| 4. Layering | `KIS-KNOW-SEM-ENUM-001` | 1.0.0 | KIS-OPERATOR-DIRECTION-2026-08-21 |
| 5. Dependency Rules | `KIS-KNOW-CON-CTR-001` | 1.0.0 | KIS-OPERATOR-DIRECTION-2026-08-21 |
| 6. Provenance | `KIS-KNOW-CON-POL-001` | 1.0.0 | KIS-OPERATOR-DIRECTION-2026-08-21 |
| 7. Lifecycle | `KIS-KNOW-WRK-STM-001` | 1.0.0 | KIS-OPERATOR-DIRECTION-2026-08-21 |
| 8. kis-op Governance Behavior | `KIS-KNOW-WRK-WFL-001` | 1.0.0 | KIS-OPERATOR-DIRECTION-2026-08-22 |
| 9. Validation and Enforcement | `KIS-KNOW-EVL-TST-001` | 2.0.0 | KIS-OPERATOR-DIRECTION-2026-08-21 |

Build hashes and the derived META-IDX / META-DEP projections are recorded in the adjacent `manifest.json` and `data/` files.
