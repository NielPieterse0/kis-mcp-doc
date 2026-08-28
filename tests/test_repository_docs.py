from __future__ import annotations

import json
from pathlib import Path

from kis_mcp_doc.publication_kernel import PublicationFamilyRegistry
from kis_mcp_doc.repository_docs import (
    build_repository_docs,
    repository_model,
    validate_repository_docs,
    verify_repository_docs,
)

ROOT = Path(__file__).parents[1]


def _family() -> dict:
    return PublicationFamilyRegistry(ROOT).family("repository-docs")


def test_repository_model_exposes_metadata_and_typed_relationships() -> None:
    model = repository_model(ROOT)
    by_path = {item["canonical_path"]: item for item in model["artefacts"]}
    agents = by_path["AGENTS.md"]
    assert agents["authority"] == "repository"
    assert agents["content_hash"].startswith("sha256:")
    assert agents["editability"] == "source_editable"
    assert not any(item["canonical_path"].startswith(".work/") for item in model["artefacts"])
    assert not any(item["canonical_path"].startswith("mrd/work-management/") for item in model["artefacts"])
    assert not any(item["canonical_path"].startswith("contracts/work-management/") for item in model["artefacts"])
    assert not any(item["canonical_path"].startswith("generated/") and item["artefact_kind"] != "generated_publication_family" for item in model["artefacts"])
    declared = [item for item in model["relationships"] if item["intent"] == "declared_mrd_dependency"]
    assert declared
    assert all(item["fact_quality"] == "observed" for item in declared)
    derived = [item for item in model["relationships"] if item["intent"] == "authority_direction"]
    assert derived
    assert all(item["fact_quality"] == "derived_from_path_policy" for item in derived)


def test_repository_docs_build_is_deterministic_and_complete(tmp_path: Path) -> None:
    family = _family()
    assert validate_repository_docs(ROOT, family) == {"status": "valid", "diagnostics": []}
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_manifest = build_repository_docs(ROOT, family, output=first)
    second_manifest = build_repository_docs(ROOT, family, output=second)
    assert first_manifest == second_manifest
    assert first_manifest["bundle_sha256"]
    inventory = json.loads((first / "data/artefact-inventory.json").read_text(encoding="utf-8"))
    graph = json.loads((first / "data/relationship-graph.json").read_text(encoding="utf-8"))
    coverage = json.loads((first / "data/coverage-report.json").read_text(encoding="utf-8"))
    assert inventory["revision_binding"]["mode"] == "external_git_manifest"
    assert graph["relationships"]
    assert coverage["source_files"] > 0
    assert (first / "006-coverage-and-freshness.md").is_file()


def test_repository_docs_rejects_wrong_output_class() -> None:
    family = dict(_family())
    family["output_classes"] = ["formal_specification"]
    result = validate_repository_docs(ROOT, family)
    assert result["status"] == "invalid"
    assert result["diagnostics"][0]["code"] == "REPOSITORY_DOCUMENTATION_INVALID"


def test_repository_docs_detects_tampered_generated_output(tmp_path: Path) -> None:
    family = dict(_family())
    family["output"] = str(tmp_path / "bundle")
    build_repository_docs(ROOT, family)
    page = tmp_path / "bundle" / "000-index.md"
    page.write_text(page.read_text(encoding="utf-8") + "tamper\n", encoding="utf-8")
    result = verify_repository_docs(ROOT, family)
    assert result["status"] == "invalid"
    codes = {item["code"] for item in result["diagnostics"]}
    assert "REPOSITORY_DOCUMENTATION_GENERATED_FILE_CONTENT_MISMATCH" in codes
