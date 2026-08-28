import json
import runpy
from pathlib import Path

from kis_mcp_doc.public_repository import (
    CLOSING,
    build_public_repository_surfaces,
    public_repository_outputs,
    validate_public_repository,
    verify_public_repository_surfaces,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "publication" / "public-repository.json"


def test_public_repository_contract_names_required_surfaces_and_controls():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    assert config["generated_files"] == [
        "README.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        ".github/pull_request_template.md",
    ]
    assert config["minimum_powershell_major"] == 7
    assert config["repository_controls"]["required_check"] == "verify"
    assert config["repository_controls"]["main_protected"] is True
    assert config["repository_controls"]["merge_strategy"] == "merge_commit_only"


def test_generated_public_surfaces_are_current_and_explicit():
    result = verify_public_repository_surfaces(ROOT)
    assert result == {"status": "valid", "findings": []}
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "Public visibility does not grant reuse" in readme
    assert "generated from those sources" in readme
    assert "Work Management retains completion authority" in contributing
    assert "private vulnerability reporting" in security


def test_public_surface_builder_is_deterministic(tmp_path):
    config = CONFIG.read_text(encoding="utf-8")
    target = tmp_path / "repo"
    (target / "publication").mkdir(parents=True)
    (target / "publication" / "public-repository.json").write_text(config, encoding="utf-8")
    expected = public_repository_outputs(ROOT)
    first = build_public_repository_surfaces(target)
    second = build_public_repository_surfaces(target)
    assert first == second
    for relative, text in expected.items():
        assert (target / relative).read_text(encoding="utf-8") == text


def test_closing_keyword_guard_covers_github_reference_forms():
    for text in (
        "Fixes #123",
        "closes NielPieterse0/kis-mcp-doc#123",
        "Resolved https://github.com/NielPieterse0/kis-mcp-doc/issues/123",
    ):
        assert CLOSING.search(text)
    assert not CLOSING.search("Related to #123")


def test_public_repository_validation_passes_current_tree():
    assert validate_public_repository(ROOT) == {"status": "valid", "findings": []}


def test_canonical_workflow_has_full_history_and_public_hygiene_gate():
    workflow = (ROOT / ".github" / "workflows" / "work-management.yml").read_text(
        encoding="utf-8"
    )
    assert "fetch-depth: 0" in workflow
    assert "public-validate" in (ROOT / "scripts" / "verify.ps1").read_text(encoding="utf-8")


def test_generated_markdown_allowlist_comes_from_public_contract():
    verify = (ROOT / "scripts" / "verify.ps1").read_text(encoding="utf-8")
    assert "public-repository.json" in verify
    assert "generated_files" in verify


def test_generated_surface_allowlist_cannot_expand_without_generator_ownership(tmp_path):
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    config["generated_files"].append("UNOWNED.md")
    target = tmp_path / "repo"
    (target / "publication").mkdir(parents=True)
    (target / "publication" / "public-repository.json").write_text(
        json.dumps(config), encoding="utf-8"
    )
    build_public_repository_surfaces(target)
    result = verify_public_repository_surfaces(target)
    assert result["status"] == "invalid"
    assert "generated_files must exactly match generator-owned public surfaces" in result["findings"]
