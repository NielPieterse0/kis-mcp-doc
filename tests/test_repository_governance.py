from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from kis_mcp_doc.repository_governance import RepositoryGovernanceRepository

ROOT = Path(__file__).resolve().parents[1]
GOV = Path("prescriptives/repository-governance/01-repository-governance.json")
REG = Path("prescriptives/repository-governance/02-prescriptive-artefact-registry.json")
ENF = Path("prescriptives/repository-governance/04-enforcement-register.json")

def _copy_repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", ".venv", ".work", ".pytest_cache", ".ruff_cache", "__pycache__", "generated"))
    return target

def _codes(result: dict[str, object]) -> set[str]:
    return {item["code"] for item in result["diagnostics"]}

def test_repository_governance_is_valid() -> None:
    result = RepositoryGovernanceRepository(ROOT).validate()
    assert result["status"] == "valid", result["diagnostics"]
    repo = RepositoryGovernanceRepository(ROOT)
    assert repo.role_for("prescriptives/governance/01-classification.mrd.json") == "prescriptive"
    assert repo.role_for("src/kis_mcp_doc/governance.py") == "implementation"
    assert repo.role_for("tests/test_governance_validator.py") == "verification"
    assert repo.role_for("generated/governance-spec/001-specification.md") == "derived_generated"
    assert repo.role_for("evidence/work-management/canonical-snapshot.json") == "evidence"

def test_rejects_unclassified_persistent_artefact(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    (root / "mystery.bin").write_bytes(b"unknown")
    result = RepositoryGovernanceRepository(root).validate()
    assert "REPOSITORY_ARTEFACT_UNCLASSIFIED" in _codes(result)

def test_rejects_duplicate_fact_owner(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    path = root / REG
    registry = json.loads(path.read_text(encoding="utf-8"))
    duplicate = registry["entries"][0]["fact_ids"][0]
    registry["entries"][1]["fact_ids"] = [duplicate]
    path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    result = RepositoryGovernanceRepository(root).validate()
    assert "PRESCRIPTIVE_FACT_OWNER_DUPLICATE" in _codes(result)

def test_rejects_unknown_top_level_directory(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    rogue = root / "random-folder" / "file.txt"
    rogue.parent.mkdir()
    rogue.write_text("persistent\n", encoding="utf-8")
    result = RepositoryGovernanceRepository(root).validate()
    assert "REPOSITORY_DIRECTORY_UNKNOWN" in _codes(result)

def test_rejects_untracked_unknown_directory_in_git_repo(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    rogue = root / "untracked-random-folder" / "file.txt"
    rogue.parent.mkdir()
    rogue.write_text("persistent\n", encoding="utf-8")
    result = RepositoryGovernanceRepository(root).validate()
    assert "REPOSITORY_DIRECTORY_UNKNOWN" in _codes(result)

def test_transient_egg_info_is_not_governed_structure(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    transient = root / "src" / "kis_mcp_doc.egg-info" / "top_level.txt"
    transient.parent.mkdir()
    transient.write_text("kis_mcp_doc\n", encoding="utf-8")
    result = RepositoryGovernanceRepository(root).validate()
    assert result["status"] == "valid", result["diagnostics"]

def test_rejects_unknown_prescriptive_domain(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    rogue = root / "prescriptives" / "random-domain" / "rule.json"
    rogue.parent.mkdir()
    rogue.write_text("{}\n", encoding="utf-8")
    result = RepositoryGovernanceRepository(root).validate()
    assert "REPOSITORY_SUBDIRECTORY_UNKNOWN" in _codes(result)

def test_generated_role_is_non_authoritative(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    path = root / GOV
    governance = json.loads(path.read_text(encoding="utf-8"))
    generated = next(item for item in governance["classification_rules"] if item["pattern"] == "generated/**")
    generated["role"] = "prescriptive"
    path.write_text(json.dumps(governance, indent=2) + "\n", encoding="utf-8")
    (root / "generated").mkdir(exist_ok=True)
    (root / "generated" / "rogue.md").write_text("derived\n", encoding="utf-8")
    result = RepositoryGovernanceRepository(root).validate()
    assert "PRESCRIPTIVE_ARTEFACT_UNREGISTERED" in _codes(result)

def test_rejects_missing_negative_fixture(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    path = root / ENF
    register = json.loads(path.read_text(encoding="utf-8"))
    register["entries"][0]["negative_fixture"] = "test_fixture_does_not_exist"
    path.write_text(json.dumps(register, indent=2) + "\n", encoding="utf-8")
    result = RepositoryGovernanceRepository(root).validate()
    assert "REPOSITORY_NEGATIVE_FIXTURE_MISSING" in _codes(result)
