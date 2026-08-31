<!-- GENERATED — DO NOT EDIT -->
# Repository Structure Definition and Directory Grammar

This generated structure definition projects the canonical Directory Grammar. Every persistent governed artefact has exactly one legal slot; unknown or ambiguous placement fails closed.

Every persistent governed artefact resolves to exactly one legal slot. Unknown, ambiguous, or prohibited placement is invalid by default; amend the grammar before adding a new structural class.

## Slot contracts

| Slot | Patterns | Purpose | Permitted / prohibited types | Roles | Authority | Relationships | Editability / lifecycle | Verification | Origin |
|---|---|---|---|---|---|---|---|---|---|
| `root-authority` | `AGENTS.md` | Repository operating authority | repository_authority / none | prescriptive | canonical_owner_required=True, generated_may_own=False | references, implements, verifies, evidences, projects | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `governance` | `prescriptives/governance/**` | Repository-wide Governance authority | governance_prescriptive / none | prescriptive | canonical_owner_required=True, domain=governance | references, implements, verifies, evidences, projects | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#71` |
| `mrd-specification` | `prescriptives/mrd-specification/**` | MRD conformance specification records | mrd / none | prescriptive | canonical_owner_required=True, domain=mrd_specification, repository_governance_forbidden=True | references, implements, verifies, evidences, projects | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#79` |
| `documentation-prescriptives` | `prescriptives/documentation/**` | Documentation-domain prescriptions | mrd / none | prescriptive | canonical_owner_required=True, domain=documentation | references, implements, verifies, evidences, projects | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `work-management-prescriptives` | `prescriptives/work-management/**` | Work Management domain prescriptions | mrd / none | prescriptive | canonical_owner_required=True, domain=work_management | references, implements, verifies, evidences, projects | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `contracts` | `contracts/**` | Machine-readable schemas and contracts | contract / none | prescriptive | canonical_owner_required=True | references, implements, verifies, evidences, projects | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `publication` | `publication/**` | Publication intent and family configuration | publication_configuration / none | prescriptive | canonical_owner_required=True | references, implements, verifies, evidences, projects | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `implementation` | `src/**` | Executable product implementation | implementation / governance_prescriptive, mrd, contract, repository_authority | implementation | canonical_owner_required=False, may_override_prescriptive=False | implements, references, projects, evidences, verifies | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `scripts` | `scripts/**` | Executable local automation and verification | script / none | implementation, verification | canonical_owner_required=False, may_override_prescriptive=False | implements, verifies, references, projects, evidences | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `tests` | `tests/**` | Executable verification source | test / governance_prescriptive, mrd, contract, repository_authority | verification | canonical_owner_required=False, may_override_prescriptive=False | verifies, references, evidences | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `evidence` | `evidence/**` | Retained bounded evidence | evidence / governance_prescriptive, mrd, contract, repository_authority | evidence | canonical_owner_required=False, may_override_prescriptive=False | evidences, references | `source_editable` / `retained_evidence` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `generated` | `generated/**` | Deterministic generated projections | generated_projection / governance_prescriptive, mrd, contract, repository_authority, platform_prescriptive, publication_configuration | derived_generated | canonical_owner_required=False, may_override_prescriptive=False, write_back=False | projects, references | `generated_only` / `reproducible` / `repository_history` | `kis-doc repository-governance-validate` | `#77` |
| `tooling` | `tooling/**` | Repository implementation tooling | tooling / none | implementation | canonical_owner_required=False | implements, references, projects, evidences, verifies | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `github-codeowners` | `.github/CODEOWNERS` | Provider-required ownership routing | platform_prescriptive / none | prescriptive | canonical_owner_required=True | references, implements, verifies, evidences, projects | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `github-workflows` | `.github/workflows/**` | Provider CI controls | platform_verification / none | verification | canonical_owner_required=False | verifies, references, evidences | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `github-pr-template` | `.github/pull_request_template.md` | Generated contributor projection | generated_human_surface / none | derived_generated | canonical_owner_required=False, write_back=False | projects, references | `generated_only` / `reproducible` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `work-change-records` | `.work/changes/**` | Governed change intent and historical evidence | change_record / governance_prescriptive, mrd, contract, repository_authority | evidence | canonical_owner_required=False, product_authority=False | evidences, references | `source_editable` / `historical_evidence` / `repository_history` | `kis-doc repository-governance-validate` | `#72` |
| `root-human-surfaces` | `README.md`; `CONTRIBUTING.md`; `SECURITY.md` | Generated public repository orientation | generated_human_surface / none | derived_generated | canonical_owner_required=False, write_back=False | projects, references | `generated_only` / `reproducible` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `root-config` | `pyproject.toml`; `uv.lock`; `.editorconfig`; `.gitattributes`; `.gitignore` | Repository build and source-control configuration | repository_configuration / none | implementation | canonical_owner_required=False | implements, references, projects, evidences, verifies | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |
| `github-provider-config` | `.github/dependabot.yml` | Provider dependency automation configuration | repository_configuration / none | implementation | canonical_owner_required=False | implements, references, projects, evidences, verifies | `source_editable` / `persistent` / `repository_history` | `kis-doc repository-governance-validate` | `#73` |

## Relationship contracts

| Registry key | Semantic relationship | Direction | Source roles | Target roles |
|---|---|---|---|---|
| `verified_by` | `verifies` | `target_to_source` | `prescriptive` | `verification`, `implementation` |
| `projected_by` | `projects` | `target_to_source` | `prescriptive` | `implementation` |
| `evidence_emitted_by` | `evidences` | `target_to_source` | `prescriptive` | `verification`, `implementation` |

## Reserved workspace

`.work` is disposable/non-product authority. It is not published, cannot be required as product input, and cannot be promoted into persistent product structure without amending the Directory Grammar first.

