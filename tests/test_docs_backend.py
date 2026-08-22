from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from kis_mcp_doc.cli import main
from kis_mcp_doc.governance import GovernanceRepository
from kis_mcp_doc.harvest import load_harvest_registry
from kis_mcp_doc.litho import load_litho_evidence
from kis_mcp_doc.render import build_governance_spec, verify_governance_spec


ROOT = Path(__file__).resolve().parents[1]
MRD_ROOT = ROOT / "mrd" / "governance"
PUBLICATION = ROOT / "publication" / "governance-spec.json"


def _repo() -> GovernanceRepository:
    return GovernanceRepository(ROOT, MRD_ROOT)


def _write_litho_package(
    root: Path,
    *,
    content: str = "# Architecture\n\nDerived analysis.\n",
    assertions: list[dict[str, object]] | None = None,
) -> Path:
    root.mkdir()
    page = root / "2.Architecture.md"
    page.write_text(content, encoding="utf-8")
    payload = page.read_bytes()
    manifest = {
        "contract": {"name": "litho-evidence-package", "version": 1},
        "provider": {"name": "litho", "version": "1.5.0"},
        "target": {"repository": "example/repo", "revision": "abc123"},
        "evidence_class": "inferred",
        "files": [
            {
                "path": "2.Architecture.md",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
            }
        ],
    }
    if assertions is not None:
        manifest["assertions"] = assertions
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return root


def test_litho_package_is_loaded_only_as_inferred_evidence(tmp_path: Path) -> None:
    package = _write_litho_package(tmp_path / "litho")

    evidence = load_litho_evidence(ROOT, package)

    assert evidence["provider"] == {"name": "litho", "version": "1.5.0"}
    assert evidence["target"] == {"repository": "example/repo", "revision": "abc123"}
    assert evidence["evidence_class"] == "inferred"
    assert evidence["pages"][0]["title"] == "Architecture"
    assert evidence["pages"][0]["content"].startswith("# Architecture")


def test_litho_package_hash_tampering_fails_closed(tmp_path: Path) -> None:
    package = _write_litho_package(tmp_path / "litho")
    (package / "2.Architecture.md").write_text("tampered\n", encoding="utf-8")

    with pytest.raises(ValueError, match="hash"):
        load_litho_evidence(ROOT, package)


def test_governance_build_uses_mcp_spec_2025_multi_page_profile(tmp_path: Path) -> None:
    output = tmp_path / "build"

    manifest = build_governance_spec(_repo(), PUBLICATION, output)

    expected_pages = {
        "000-index.md",
        "001-specification.md",
        "002-classification.md",
        "003-applicability-and-selection.md",
        "004-authority-ownership-and-relationships.md",
        "005-layering.md",
        "006-dependency-rules.md",
        "007-provenance.md",
        "008-lifecycle.md",
        "009-kis-op-governance-behavior.md",
        "010-validation-and-enforcement.md",
        "specification.md",
    }
    actual_pages = {path.name for path in output.glob("*.md")}
    assert expected_pages == actual_pages
    assert manifest["contract"]["version"] == 2
    assert manifest["specification"]["layout_profile"] == "mcp-spec-2025"
    root = (output / "001-specification.md").read_text(encoding="utf-8")
    assert '<div id="enable-section-numbers" />' in root
    assert "BCP 14" in root and "RFC2119" in root and "RFC8174" in root
    assert "## Overview" in root
    assert "## Detailed specification" in root
    assert "002-classification.md" in root
    assert (output / "specification.md").read_bytes() == (output / "001-specification.md").read_bytes()
    assert verify_governance_spec(_repo(), PUBLICATION, output)["status"] == "valid"


def test_litho_evidence_is_published_as_labeled_non_authoritative_page(tmp_path: Path) -> None:
    package = _write_litho_package(tmp_path / "litho")
    output = tmp_path / "build"

    manifest = build_governance_spec(
        _repo(), PUBLICATION, output, litho_package=package
    )

    page = (output / "090-code-derived-analysis.md").read_text(encoding="utf-8")
    assert "Inferred evidence" in page
    assert "MUST NOT be treated as canonical authority" in page
    assert "Derived analysis." in page
    assert manifest["inputs"]["external_evidence"][0]["provider"] == "litho"
    assert manifest["inputs"]["external_evidence"][0]["evidence_class"] == "inferred"
    assert verify_governance_spec(
        _repo(), PUBLICATION, output, litho_package=package
    )["status"] == "valid"


def test_litho_package_rejects_machine_local_absolute_paths(tmp_path: Path) -> None:
    package = _write_litho_package(
        tmp_path / "litho",
        content="# Architecture\n\nObserved at C:\\Users\\analyst\\project\\src.\n",
    )

    with pytest.raises(ValueError, match="machine-local absolute path"):
        load_litho_evidence(ROOT, package)


def test_cli_build_and_check_accept_litho_package(tmp_path: Path) -> None:
    package = _write_litho_package(tmp_path / "litho")
    output = tmp_path / "build"

    assert main([
        "--root", str(ROOT), "build", "--output", str(output),
        "--litho-package", str(package),
    ]) == 0
    assert (output / "090-code-derived-analysis.md").is_file()
    assert main([
        "--root", str(ROOT), "check-generated", "--output", str(output),
        "--litho-package", str(package),
    ]) == 0


def test_harvest_registry_pins_adopted_sources_without_machine_paths() -> None:
    registry = load_harvest_registry(ROOT)
    sources = {item["id"]: item for item in registry["sources"]}

    assert sources["doc-solution"]["identity"] == "NielPieterse0/doc-solution"
    assert sources["doc-solution"]["pinned_revision"] == "acf9ffd139ee009d3b921d5cd7c24691bb1c4737"
    assert sources["mcp-spec-2025-11-25"]["content_sha256"] == "2fe1f78c929deba4597c69d2c8adef57280666c6bba7b9587bcc4b53c89f0944"
    assert sources["litho"]["identity"] == "sopaco/deepwiki-rs"
    assert sources["litho"]["trust_classification"] == "advisory_external_evidence"
    serialized = json.dumps(registry, sort_keys=True)
    assert "C:\\\\Projects" not in serialized


def test_build_manifest_binds_harvest_registry(tmp_path: Path) -> None:
    output = tmp_path / "build"
    manifest = build_governance_spec(_repo(), PUBLICATION, output)

    declaration = manifest["inputs"]["harvest_registry"]
    registry_path = ROOT / "publication" / "harvest-sources.json"
    assert declaration["path"] == "publication/harvest-sources.json"
    assert declaration["version"] == "1.0.0"
    assert declaration["sha256"] == hashlib.sha256(registry_path.read_bytes()).hexdigest()


def test_litho_structured_assertion_surfaces_canonical_contradiction(tmp_path: Path) -> None:
    assertion = {
        "id": "claim-type-count",
        "source_path": "2.Architecture.md",
        "canonical_source": "repo:mrd/governance/01-classification.mrd.json",
        "json_pointer": "/content/catalog_policy/expected_type_count",
        "observed_value": 48,
    }
    package = _write_litho_package(
        tmp_path / "litho",
        assertions=[assertion],
    )

    evidence = load_litho_evidence(ROOT, package)

    assert evidence["diagnostics"] == [{
        "code": "EXTERNAL_EVIDENCE_CONTRADICTS_CANONICAL",
        "assertion_id": "claim-type-count",
        "source_path": "2.Architecture.md",
        "canonical_source": "repo:mrd/governance/01-classification.mrd.json",
        "json_pointer": "/content/catalog_policy/expected_type_count",
        "observed_value": 48,
        "canonical_value": 47,
    }]


def test_litho_contradiction_is_preserved_in_published_evidence(tmp_path: Path) -> None:
    assertion = {
        "id": "claim-type-count",
        "source_path": "2.Architecture.md",
        "canonical_source": "repo:mrd/governance/01-classification.mrd.json",
        "json_pointer": "/content/catalog_policy/expected_type_count",
        "observed_value": 48,
    }
    package = _write_litho_package(tmp_path / "litho", assertions=[assertion])
    output = tmp_path / "build"

    manifest = build_governance_spec(
        _repo(), PUBLICATION, output, litho_package=package
    )

    page = (output / "090-code-derived-analysis.md").read_text(encoding="utf-8")
    evidence = json.loads((output / "data/litho-evidence.json").read_text(encoding="utf-8"))
    assert "EXTERNAL_EVIDENCE_CONTRADICTS_CANONICAL" in page
    assert evidence["diagnostics"][0]["canonical_value"] == 47
    canonical = manifest["inputs"]["external_evidence"][0]["canonical_sources"][0]
    assert canonical["path"] == "mrd/governance/01-classification.mrd.json"
    assert len(canonical["sha256"]) == 64
