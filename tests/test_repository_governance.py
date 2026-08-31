from __future__ import annotations

import json
import shutil
from pathlib import Path

from kis_mcp_doc.repository_governance import RepositoryGovernanceRepository, enforcement_projection

ROOT = Path(__file__).resolve().parents[1]
GOV = Path("prescriptives/governance/01-repository-governance.json")
REG = Path("prescriptives/governance/02-prescriptive-artefact-registry.json")
GRAMMAR = Path("prescriptives/governance/03-directory-grammar.json")


def _copy_repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", ".venv", ".work", ".temp", ".pytest_cache", ".ruff_cache", "__pycache__", "generated"))
    return target


def _load(root: Path, relative: Path) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def _write(root: Path, relative: Path, value: dict) -> None:
    (root / relative).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _codes(root: Path) -> set[str]:
    return {item["code"] for item in RepositoryGovernanceRepository(root).validate()["diagnostics"]}


def test_repository_governance_is_valid() -> None:
    result = RepositoryGovernanceRepository(ROOT).validate()
    assert result["status"] == "valid", result["diagnostics"]
    repo = RepositoryGovernanceRepository(ROOT)
    assert repo.role_for("prescriptives/mrd-specification/01-classification.mrd.json") == "prescriptive"
    assert repo.role_for("src/kis_mcp_doc/governance.py") == "implementation"
    assert repo.role_for("tests/test_governance_validator.py") == "verification"
    assert repo.role_for("generated/mrd-specification/001-specification.md") == "derived_generated"


def test_rejects_ambiguous_semantic_role(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); gov = _load(root, GOV)
    gov["classification_rules"].append({"pattern": "AGENTS.md", "role": "implementation"}); _write(root, GOV, gov)
    assert "REPOSITORY_ROLE_RESOLUTION_INVALID" in _codes(root)


def test_rejects_duplicate_fact_owner(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); reg = _load(root, REG)
    duplicate = reg["entries"][0]["fact_ids"][0]; reg["entries"][1]["fact_ids"] = [duplicate]; _write(root, REG, reg)
    assert "PRESCRIPTIVE_FACT_OWNER_DUPLICATE" in _codes(root)


def test_rejects_ambiguous_or_missing_slot(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); grammar = _load(root, GRAMMAR)
    duplicate = dict(grammar["slots"][0]); duplicate["slot_id"] = "duplicate-root"; grammar["slots"].append(duplicate); _write(root, GRAMMAR, grammar)
    assert "REPOSITORY_SLOT_RESOLUTION_INVALID" in _codes(root)


def test_rejects_unknown_top_level_directory(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); rogue = root / "random-folder" / "file.txt"; rogue.parent.mkdir(); rogue.write_text("persistent\n")
    assert "REPOSITORY_DIRECTORY_UNKNOWN" in _codes(root)


def test_generated_role_is_non_authoritative(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); grammar = _load(root, GRAMMAR)
    slot = next(x for x in grammar["slots"] if x["slot_id"] == "generated"); slot["authority_constraints"]["write_back"] = True; _write(root, GRAMMAR, grammar)
    assert "GENERATED_AUTHORITY_PROHIBITED" in _codes(root)


def test_rejects_missing_or_reused_negative_fixture(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); gov = _load(root, GOV)
    gov["rules"][1]["verification"]["negative_fixture"] = gov["rules"][0]["verification"]["negative_fixture"]; _write(root, GOV, gov)
    assert "REPOSITORY_NEGATIVE_FIXTURE_MISSING" in _codes(root)


def test_rejects_slot_without_demonstrated_need(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); grammar = _load(root, GRAMMAR); grammar["slots"][0]["origin"] = {}; _write(root, GRAMMAR, grammar)
    assert "REPOSITORY_SLOT_ORIGIN_MISSING" in _codes(root)


def test_rejects_authoritative_work_workspace(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); grammar = _load(root, GRAMMAR); grammar["reserved_workspace"]["canonical_authority"] = True; _write(root, GRAMMAR, grammar)
    assert "REPOSITORY_WORKSPACE_POLICY_INVALID" in _codes(root)


def test_rejects_unjustified_human_review(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); gov = _load(root, GOV); gov["validation_policy"]["order"] = ["human_review", "deterministic_validator"]; _write(root, GOV, gov)
    assert "REPOSITORY_REVIEW_POLICY_INVALID" in _codes(root)


def test_rejects_governance_mrd_specification_overlap(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); source = root / "prescriptives/mrd-specification/01-classification.mrd.json"; target = root / "prescriptives/governance/99-classification.mrd.json"; shutil.copy2(source, target)
    assert "REPOSITORY_GOVERNANCE_BOUNDARY_INVALID" in _codes(root)


def test_rejects_invalid_evidence_precedence(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); gov = _load(root, GOV); gov["evidence_model"]["conformance_evidence_precedence"][1]["rank"] = 1; _write(root, GOV, gov)
    assert "REPOSITORY_EVIDENCE_PRECEDENCE_INVALID" in _codes(root)


def test_rejects_authored_enforcement_register(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); path = root / "prescriptives/governance/04-enforcement-register.json"; path.write_text(json.dumps(enforcement_projection(_load(root, GOV)), indent=2) + "\n")
    assert "REPOSITORY_ENFORCEMENT_PROJECTION_INVALID" in _codes(root)


def test_rejects_prescriptive_without_projection_disposition(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); reg = _load(root, REG); reg["entries"][0]["human_projection"] = {}; _write(root, REG, reg)
    assert "PRESCRIPTIVE_HUMAN_PROJECTION_MISSING" in _codes(root)


def test_rejects_semantically_encoded_mrd_identity(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); path = next((root / "prescriptives/mrd-specification").glob("*.mrd.json")); doc = json.loads(path.read_text()); doc["_mrd"]["id"] = "KIS-KNOW-SEM-REG-001"; path.write_text(json.dumps(doc, indent=2) + "\n")
    assert "MRD_IDENTITY_METADATA_INVALID" in _codes(root)


def test_enforcement_register_is_exact_projection() -> None:
    gov = json.loads((ROOT / GOV).read_text(encoding="utf-8")); projection = enforcement_projection(gov)
    assert projection["authority"] == "derived_non_authoritative"
    assert [x["rule_id"] for x in projection["entries"]] == [x["rule_id"] for x in gov["rules"]]


def test_rejects_unresolved_rule_assurance_reference(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); gov = _load(root, GOV)
    gov["rules"][0]["implementation"][0]["artifact"] = "src/missing-control.py"; _write(root, GOV, gov)
    assert "REPOSITORY_RULE_ASSURANCE_REFERENCE_INVALID" in _codes(root)


def test_rejects_illegal_relationship_direction(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); reg = _load(root, REG)
    reg["entries"][0]["relationships"]["verified_by"] = ["AGENTS.md"]; _write(root, REG, reg)
    assert "REPOSITORY_RELATIONSHIP_INVALID" in _codes(root)


def test_rejects_normative_rule_restatement(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); gov = _load(root, GOV)
    with (root / "AGENTS.md").open("a", encoding="utf-8") as handle:
        handle.write("\n" + gov["rules"][0]["statement"] + "\n")
    assert "REPOSITORY_NORMATIVE_RESTATEMENT_PROHIBITED" in _codes(root)


def test_rejects_invalid_governance_lifecycle(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); gov = _load(root, GOV)
    gov["rules"][0]["lifecycle"]["superseded_by"] = gov["rules"][0]["rule_id"]; _write(root, GOV, gov)
    assert "REPOSITORY_GOVERNANCE_VOCABULARY_INVALID" in _codes(root)


def test_rejects_incomplete_rule_contract(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); gov = _load(root, GOV)
    del gov["rules"][0]["evidence"]; _write(root, GOV, gov)
    assert "REPOSITORY_RULE_SCHEMA_INVALID" in _codes(root)


def test_rejects_explicitly_prohibited_artefact_type(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); grammar = _load(root, GRAMMAR)
    slot = next(item for item in grammar["slots"] if item["slot_id"] == "implementation")
    slot["prohibited_artefact_types"].append("implementation"); _write(root, GRAMMAR, grammar)
    assert "REPOSITORY_SLOT_ARTEFACT_PROHIBITED" in _codes(root)


def test_rejects_incomplete_slot_contract(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); grammar = _load(root, GRAMMAR)
    del grammar["slots"][0]["purpose"]; _write(root, GRAMMAR, grammar)
    assert "REPOSITORY_SLOT_CONTRACT_INVALID" in _codes(root)


def test_rejects_rule_without_scope_or_rationale(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); gov = _load(root, GOV)
    del gov["rules"][0]["scope"]; _write(root, GOV, gov)
    assert "REPOSITORY_RULE_SCHEMA_INVALID" in _codes(root)


def test_rejects_unbounded_residual_review(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path); gov = _load(root, GOV)
    residual_rule = next(item for item in gov["rules"] if item["verification"]["method"] == "deterministic_plus_residual_review")
    del residual_rule["verification"]["residual_review"]["justification"]; _write(root, GOV, gov)
    assert "REPOSITORY_REVIEW_POLICY_INVALID" in _codes(root)
