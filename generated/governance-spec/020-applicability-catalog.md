<!-- GENERATED — DO NOT EDIT -->
# MRD applicability catalog

<div id="enable-section-numbers" />

[Owning specification chapter: Applicability and Selection](003-applicability-and-selection.md) | [Documentation index](000-index.md)

> **Output class:** `generated_reference`. This page is an exact lookup projection of canonical Governance authority. It has no write-back authority.

Use this catalog after the specification's minimum-sufficient selection process identifies the governed need. The table does not require one artifact per row.

| Code | Name | Use when |
|---|---|---|
| <span id="fact-applicability-sem-ent"></span>`SEM-ENT` | Entity definition schema | Use when a governed domain needs a canonical entity shape, identity, fields, or structural definition. |
| <span id="fact-applicability-sem-enum"></span>`SEM-ENUM` | Enumeration schema | Use when a finite controlled vocabulary or closed set of allowed values must be authoritative. |
| <span id="fact-applicability-sem-ont"></span>`SEM-ONT` | Ontology | Use when governed concepts and their semantic relationships need an explicit ontology. |
| <span id="fact-applicability-sem-reg"></span>`SEM-REG` | Registry | Use when named governed entries require one authoritative registry with stable identifiers. |
| <span id="fact-applicability-sem-dom"></span>`SEM-DOM` | Domain definition register | Use when a domain boundary, scope, vocabulary ownership, or domain definition must be registered. |
| <span id="fact-applicability-sem-asr"></span>`SEM-ASR` | Assertion rules | Use when invariants or semantic assertions must be stated independently of implementation code. |
| <span id="fact-applicability-con-vrs"></span>`CON-VRS` | Version constraint | Use when allowed, required, minimum, maximum, or compatible versions must be constrained. |
| <span id="fact-applicability-con-bnd"></span>`CON-BND` | Boundary rule | Use when an authority, security, filesystem, network, module, or responsibility boundary must be constrained. |
| <span id="fact-applicability-con-pol"></span>`CON-POL` | Policy implementation | Use when durable policy determines what is permitted, prohibited, required, or conditionally allowed. |
| <span id="fact-applicability-con-ctr"></span>`CON-CTR` | Constraint contract | Use when constraints themselves require a reusable machine-consumable contract. |
| <span id="fact-applicability-dec-tab"></span>`DEC-TAB` | Decision table | Use when an outcome can be selected deterministically from a finite set of conditions in tabular form. |
| <span id="fact-applicability-dec-tre"></span>`DEC-TRE` | Decision tree | Use when ordered or branching conditions determine a governed outcome more clearly than a table. |
| <span id="fact-applicability-dec-scr"></span>`DEC-SCR` | Scoring model | Use when weighted criteria or scores determine a governed classification, threshold, or decision. |
| <span id="fact-applicability-wrk-stm"></span>`WRK-STM` | State machine | Use when governed state, permitted transitions, and terminal states must be explicit. |
| <span id="fact-applicability-wrk-prc"></span>`WRK-PRC` | Process definition | Use when a repeatable ordered process with defined inputs, steps, and outputs must be prescribed. |
| <span id="fact-applicability-wrk-apr"></span>`WRK-APR` | Approval workflow | Use when approval, rejection, escalation, or sign-off flow must be governed. |
| <span id="fact-applicability-wrk-ctr"></span>`WRK-CTR` | Phase contract | Use when a workflow phase requires explicit entry, exit, handoff, or completion conditions. |
| <span id="fact-applicability-wrk-wfl"></span>`WRK-WFL` | Workflow definition | Use when several governed steps, roles, decisions, or phases form an end-to-end workflow. |
| <span id="fact-applicability-wrk-act"></span>`WRK-ACT` | Action or automation workflow | Use when a bounded action or automation sequence must be executable under governance. |
| <span id="fact-applicability-cfg-env"></span>`CFG-ENV` | Environment config | Use when environment-specific values select allowed behavior without redefining policy. |
| <span id="fact-applicability-cfg-flg"></span>`CFG-FLG` | Feature flag | Use when a governed feature can be enabled or disabled through an explicit flag. |
| <span id="fact-applicability-cfg-prm"></span>`CFG-PRM` | Runtime parameter | Use when a runtime parameter selects among already-permitted behaviors or limits. |
| <span id="fact-applicability-map-fld"></span>`MAP-FLD` | Field mapping | Use when fields in one governed structure translate deterministically to fields in another. |
| <span id="fact-applicability-map-fmt"></span>`MAP-FMT` | Format translation | Use when one representation or serialization format must translate deterministically to another. |
| <span id="fact-applicability-map-mig"></span>`MAP-MIG` | Migration map | Use when a versioned structure, identifier, or data model requires an explicit migration mapping. |
| <span id="fact-applicability-ctr-api"></span>`CTR-API` | API contract | Use when callable request/response behavior requires an explicit API interface contract. |
| <span id="fact-applicability-ctr-evt"></span>`CTR-EVT` | Event contract | Use when produced or consumed events require stable names, payloads, and delivery semantics. |
| <span id="fact-applicability-ctr-svc"></span>`CTR-SVC` | Service contract | Use when a service boundary, capability, inputs, outputs, or service-level interface must be contracted. |
| <span id="fact-applicability-man-pkg"></span>`MAN-PKG` | Package manifest | Use when a package's governed identity, contents, dependencies, or distribution metadata must be declared. |
| <span id="fact-applicability-man-bom"></span>`MAN-BOM` | Bill of materials | Use when constituent components or dependencies must be inventoried as a bill of materials. |
| <span id="fact-applicability-man-rel"></span>`MAN-REL` | Release manifest | Use when a release needs an authoritative manifest of version, contents, provenance, and release facts. |
| <span id="fact-applicability-man-skl"></span>`MAN-SKL` | Skill manifest | Use when a reusable skill package needs a governed capability and asset manifest. |
| <span id="fact-applicability-man-act"></span>`MAN-ACT` | Action manifest | Use when available actions or automations must be inventoried separately from their workflow definitions. |
| <span id="fact-applicability-prm-sys"></span>`PRM-SYS` | System prompt | Use when durable system-level model instructions are governed as an explicit prompt artifact. |
| <span id="fact-applicability-prm-rol"></span>`PRM-ROL` | Role prompt | Use when a durable role-specific behavior or responsibility prompt must be governed. |
| <span id="fact-applicability-prm-ctx"></span>`PRM-CTX` | Context prompt | Use when reusable context assembly or context framing instructions must be governed. |
| <span id="fact-applicability-prm-tol"></span>`PRM-TOL` | Tool prompt | Use when model-facing instructions for invoking or interpreting a tool must be governed. |
| <span id="fact-applicability-evl-tst"></span>`EVL-TST` | Test suite | Use when deterministic or machine-evaluable conformance tests define acceptance of governed behavior. |
| <span id="fact-applicability-evl-rub"></span>`EVL-RUB` | Rubric | Use when qualitative or multi-criterion review requires an explicit scoring or assessment rubric. |
| <span id="fact-applicability-evl-ben"></span>`EVL-BEN` | Benchmark | Use when comparable performance, quality, or capability measurement requires a stable benchmark. |
| <span id="fact-applicability-evd-log"></span>`EVD-LOG` | Log | Use when an immutable operational or governance log is itself required evidence. |
| <span id="fact-applicability-evd-apr"></span>`EVD-APR` | Approval record | Use when an approval decision must be retained as evidence distinct from the approval workflow. |
| <span id="fact-applicability-evd-lin"></span>`EVD-LIN` | Lineage record | Use when lineage, derivation, handoff, or provenance events must be retained as evidence. |
| <span id="fact-applicability-evd-tsr"></span>`EVD-TSR` | Test result snapshot | Use when a test or verification result must be retained as an immutable evidence snapshot. |
| <span id="fact-applicability-meta-idx"></span>`META-IDX` | Index | Generate when consumers need a derived index over governed artifacts; never author it as primary truth. |
| <span id="fact-applicability-meta-dep"></span>`META-DEP` | Dependency map | Generate when consumers need a derived dependency graph or map; never author it as primary truth. |
| <span id="fact-applicability-meta-map"></span>`META-MAP` | Metadata map | Generate when consumers need derived metadata joins or lookup maps; never author it as primary truth. |


## Source and authority

This reference projects `KIS-KNOW-DEC-TAB-001` version `1.0.0`. The MRD remains authoritative.
