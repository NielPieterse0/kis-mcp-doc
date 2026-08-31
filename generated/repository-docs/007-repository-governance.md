<!-- GENERATED — DO NOT EDIT -->
# Repository Governance

Canonical repository-wide authority is projected here without write-back authority.

Repository Governance is distinct from the MRD Specification. Governance controls repository-wide authority, ownership, placement, assurance, evidence precedence, change application, and verification policy; the MRD Specification defines what a conforming MRD is.

## Governed construct vocabulary

| Construct | Normative | Meaning |
|---|---|---|
| `principle` | Yes | Stable repository-wide invariant that constrains subordinate policy and rules. |
| `policy` | Yes | Authoritative decision framework that governs a defined scope. |
| `rule` | Yes | Testable mandatory statement with a stable identity and assurance contract. |
| `requirement` | Yes | Domain-scoped mandatory statement governed by its specification owner and assurance contract. |
| `implementation` | No | Executable mechanism that makes a prescription true. |
| `verification` | No | Executable or bounded check that evaluates a prescription against state. |
| `evidence` | No | Revision-bound result emitted by verification or an accepted evidence source. |
| `projection` | No | Derived human or machine view that cannot write back authority. |

## Relationship law

| Relationship | From | To | Authority effect |
|---|---|---|---|
| `specializes` | policy, rule, requirement | principle, policy, rule, requirement | `subordinate_no_override` |
| `references` | principle, policy, rule, requirement, implementation, verification, evidence, projection | principle, policy, rule, requirement, implementation, verification, evidence, projection | `none` |
| `implements` | implementation | rule, requirement, policy | `none` |
| `verifies` | verification | rule, requirement, implementation | `none` |
| `evidences` | evidence | verification, rule, requirement, implementation | `none` |
| `projects` | projection | principle, policy, rule, requirement, implementation, verification, evidence | `none` |
| `supersedes` | principle, policy, rule, requirement | principle, policy, rule, requirement | `lifecycle_only` |

## Conformance evidence precedence

Normative ownership and observed implementation state are separate planes. Lower-precedence evidence cannot override fresher higher-precedence conformance evidence.

| Rank | Evidence class | Examples |
|---:|---|---|
| 1 | `executable_state` | implementation, configuration |
| 2 | `deterministic_verification` | validators, tests, local canonical verification |
| 3 | `provider_ci` | GitHub Actions exact-head checks |
| 4 | `release_checks` | release/package verification |
| 5 | `specification_status` | declared implementation status in specification metadata |
| 6 | `human_narrative` | review notes, documentation prose, status summaries |

## Validation policy

Human review MUST be used only when deterministic or bounded machine validation is infeasible or disproportionate for the residual question.

Validation order: `schema` -> `deterministic_validator` -> `workflow_gate` -> `generated_exactness` -> `bounded_semantic_review` -> `human_review`.

## Governed rules

| Rule | Scope | Origin | Method | Failure code |
|---|---|---|---|---|
| `KIS-REPO-GOV-001` | persistent repository artefacts | `#72` | `deterministic` | `REPOSITORY_ROLE_RESOLUTION_INVALID` |
| `KIS-REPO-GOV-002` | prescriptive artefacts, governed facts | `#80` | `deterministic` | `PRESCRIPTIVE_FACT_OWNER_DUPLICATE` |
| `KIS-REPO-GOV-003` | persistent repository artefacts | `#74` | `deterministic` | `REPOSITORY_SLOT_RESOLUTION_INVALID` |
| `KIS-REPO-GOV-004` | repository structure | `#74` | `deterministic` | `REPOSITORY_DIRECTORY_UNKNOWN` |
| `KIS-REPO-GOV-005` | generated outputs | `#77` | `deterministic` | `GENERATED_AUTHORITY_PROHIBITED` |
| `KIS-REPO-GOV-006` | deterministic governed rules | `#76` | `deterministic` | `REPOSITORY_NEGATIVE_FIXTURE_MISSING` |
| `KIS-REPO-GOV-007` | directory grammar slots | `#72` | `deterministic_plus_residual_review` | `REPOSITORY_SLOT_ORIGIN_MISSING` |
| `KIS-REPO-GOV-008` | .work | `#72` | `deterministic` | `REPOSITORY_WORKSPACE_POLICY_INVALID` |
| `KIS-REPO-GOV-009` | validation policy | `#70` | `deterministic` | `REPOSITORY_REVIEW_POLICY_INVALID` |
| `KIS-REPO-GOV-010` | prescriptives/governance, prescriptives/mrd-specification | `#79` | `deterministic` | `REPOSITORY_GOVERNANCE_BOUNDARY_INVALID` |
| `KIS-REPO-GOV-011` | conformance evidence | `#82` | `deterministic` | `REPOSITORY_EVIDENCE_PRECEDENCE_INVALID` |
| `KIS-REPO-GOV-012` | rule enforcement projection | `#83` | `deterministic` | `REPOSITORY_ENFORCEMENT_PROJECTION_INVALID` |
| `KIS-REPO-GOV-013` | prescriptive registry | `#78` | `deterministic` | `PRESCRIPTIVE_HUMAN_PROJECTION_MISSING` |
| `KIS-REPO-GOV-014` | MRD identity metadata | `#81` | `deterministic` | `MRD_IDENTITY_METADATA_INVALID` |
| `KIS-REPO-GOV-015` | repository governance model and governed repository state | `#86` | `deterministic` | `REPOSITORY_RULE_ASSURANCE_REFERENCE_INVALID` |
| `KIS-REPO-GOV-016` | repository governance model and governed repository state | `#75` | `deterministic` | `REPOSITORY_RELATIONSHIP_INVALID` |
| `KIS-REPO-GOV-017` | repository governance model and governed repository state | `#86` | `deterministic_plus_residual_review` | `REPOSITORY_NORMATIVE_RESTATEMENT_PROHIBITED` |
| `KIS-REPO-GOV-018` | repository governance model and governed repository state | `#88` | `deterministic` | `REPOSITORY_GOVERNANCE_VOCABULARY_INVALID` |
| `KIS-REPO-GOV-019` | repository governance model and governed repository state | `#87` | `deterministic` | `REPOSITORY_RULE_SCHEMA_INVALID` |
| `KIS-REPO-GOV-020` | repository governance model and governed repository state | `#74` | `deterministic` | `REPOSITORY_SLOT_ARTEFACT_PROHIBITED` |
| `KIS-REPO-GOV-021` | repository governance model and governed repository state | `#73` | `deterministic` | `REPOSITORY_SLOT_CONTRACT_INVALID` |
| `KIS-REPO-GOV-022` | repository governance model and governed repository state | `#84` | `deterministic` | `REPOSITORY_RULE_SCHEMA_INVALID` |
| `KIS-REPO-GOV-023` | repository governance model and governed repository state | `#85` | `deterministic` | `REPOSITORY_REVIEW_POLICY_INVALID` |

