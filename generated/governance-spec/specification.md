<!-- GENERATED — DO NOT EDIT -->
# KIS MRD Governance Specification

> **Status:** stabilized
> **Version:** 1.0.0
> **Authority:** Generated human-readable projection; the source MRDs are authoritative.
> **Generator:** kis-mcp-doc 0.1.0 / governance-spec-v1

Core governance standard for KIS machine-readable documents

This document is a deterministic human-readable projection of the six validated governance MRDs listed in Traceability.

The capitalized terms **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, **MAY**, and **REQUIRED** express normative requirements as authored in the source MRDs.

## 1. Classification

Define the stable functional vocabulary used to classify KIS MRDs without coupling classification to repository layout.

### Normative rules

- **KIS-MRD-CLASS-001** — Every MRD MUST declare exactly one class and one type from this catalog.
- **KIS-MRD-CLASS-002** — Classification MUST describe what an artifact does, not where the artifact is stored.
- **KIS-MRD-CLASS-003** — A new MRD type MUST NOT be introduced when an existing catalog type adequately represents the artifact.
- **KIS-MRD-CLASS-004** — Artifacts MUST NOT be created merely to populate unused catalog types; absence of an unused type has no compliance implication.
- **KIS-MRD-CLASS-005** — The catalog MAY be extended by a versioned governance amendment when a genuine artifact need cannot be represented by an existing type.

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

## 2. Layering

Define authority ordering for MRD dependencies.

### Normative rules

- **KIS-MRD-LAYER-001** — An MRD MAY depend only on an MRD in the same layer or a higher-authority layer with a lower layer number.
- **KIS-MRD-LAYER-002** — An MRD MUST NOT depend on an MRD in a lower-authority layer with a higher layer number.
- **KIS-MRD-LAYER-003** — Layer assignment expresses authority ordering, not storage location or implementation order.

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

## 3. Dependency Rules

Make all authority dependencies explicit, stable, resolvable, and acyclic.

### Normative rules

- **KIS-MRD-DEP-001** — Every dependency target MUST resolve.
- **KIS-MRD-DEP-002** — MRD-to-MRD dependency direction MUST satisfy the L0-L5 authority ordering.
- **KIS-MRD-DEP-003** — The MRD dependency graph MUST be acyclic.
- **KIS-MRD-DEP-004** — Duplicate dependency edges MUST be rejected.
- **KIS-MRD-DEP-005** — Dependency identities MUST be stable; canonical non-MRD dependencies MUST use repo: paths.
- **KIS-MRD-DEP-006** — A META-DEP projection MAY be generated from the validated dependency graph and MUST NOT become primary authority.

### Dependency target forms

| Kind | Field | Example |
|---|---|---|
| mrd | `mrd_id` | `KIS-KNOW-SEM-REG-001` |
| canonical_source | `source` | `repo:contracts/mrd/v1/mrd.schema.json` |

## 4. Provenance

Preserve authority direction and distinguish authored prescription from derived implementation views and captured evidence.

### Normative rules

- **KIS-MRD-PROV-001** — Record mode MUST express authority and mutability; KIS does not define a separate generation_mode in the core standard.
- **KIS-MRD-PROV-002** — Code harvesting MAY produce candidate or meta/descriptive MRDs but MUST NOT automatically create prescriptive authority.
- **KIS-MRD-PROV-003** — A harvested candidate becomes prescriptive only through explicit adoption or review; after adoption, implementation MUST conform to the prescriptive MRD.
- **KIS-MRD-PROV-004** — Inferred facts MUST NOT become normative automatically and MUST NOT appear as active prescriptive facts.
- **KIS-MRD-PROV-005** — Generated human-readable documents and META projections MUST NOT write back authority into their sources.
- **KIS-MRD-PROV-006** — The provenance source fingerprint MUST deterministically identify the declared provenance source set.
- **KIS-MRD-PROV-007** — Author intent, invariants, choices, and contracts; derive implementation observations; capture runtime evidence; evaluate conformance between them.
- **KIS-MRD-PROV-008** — A repo_path provenance source MUST carry the SHA-256 of the resolved repository file; a mismatch MUST invalidate provenance.

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

## 5. Lifecycle

Define minimal lifecycle and mutability rules for each record mode.

### Normative rules

- **KIS-MRD-LIFE-001** — Active prescriptive MRDs MUST have resolved dependencies and valid provenance.
- **KIS-MRD-LIFE-002** — Descriptive EVD records MUST be immutable after creation.
- **KIS-MRD-LIFE-003** — META records MUST be regenerated from their sources rather than manually maintained.
- **KIS-MRD-LIFE-004** — A derived or generated artifact MUST be treated as stale when its declared source fingerprint no longer matches its admitted sources.
- **KIS-MRD-LIFE-005** — Superseded MRDs MUST remain addressable for lineage and MUST identify their replacement when one exists.
- **KIS-MRD-LIFE-006** — Git history is the change history; a duplicate body changelog is not required by the core MRD standard.

### State machines

| Record mode | States | Allowed transitions |
|---|---|---|
| `prescriptive` | draft → active → superseded | draft → active; active → superseded |
| `descriptive` | created → retained | created → retained |
| `meta` | generated → replaced | generated → replaced |

## 6. Machine Validation

Fail closed when structural, dependency, provenance, or lifecycle invariants do not hold.

### Normative rules

- **KIS-MRD-VAL-001** — Every MRD MUST pass structural, dependency, provenance, and lifecycle validation before it is accepted as valid.
- **KIS-MRD-VAL-002** — Validation failures MUST emit stable reason codes and machine-readable diagnostics.
- **KIS-MRD-VAL-003** — A validation result MUST report classification, layering, dependencies, provenance, lifecycle, and schema check status.

### Validation dimensions

#### Structural

- required fields present
- identifier shape
- schema-compatible envelope and payload
- exactly one owner for each governance concern

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

### Result contract

- Status: `valid`, `invalid`
- Check keys: `classification`, `layering`, `dependencies`, `provenance`, `lifecycle`, `schema`
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

## Traceability

Each normative section above is projected from exactly one prescriptive MRD:

| Section | MRD | Version | Provenance sources |
|---|---|---:|---|
| 1. Classification | `KIS-KNOW-SEM-REG-001` | 1.0.0 | KIS-OPERATOR-DIRECTION-2026-08-21, SVX-LIB-STD-003-v3.3.15 |
| 2. Layering | `KIS-KNOW-SEM-ENUM-001` | 1.0.0 | KIS-OPERATOR-DIRECTION-2026-08-21 |
| 3. Dependency Rules | `KIS-KNOW-CON-CTR-001` | 1.0.0 | KIS-OPERATOR-DIRECTION-2026-08-21 |
| 4. Provenance | `KIS-KNOW-CON-POL-001` | 1.0.0 | KIS-OPERATOR-DIRECTION-2026-08-21 |
| 5. Lifecycle | `KIS-KNOW-WRK-STM-001` | 1.0.0 | KIS-OPERATOR-DIRECTION-2026-08-21 |
| 6. Machine Validation | `KIS-KNOW-EVL-TST-001` | 1.0.0 | KIS-OPERATOR-DIRECTION-2026-08-21 |

Build hashes and the derived META-IDX / META-DEP projections are recorded in the adjacent `manifest.json` and `data/` files.
