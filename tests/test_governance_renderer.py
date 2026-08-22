from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import kis_mcp_doc.render as render_module
from kis_mcp_doc.governance import GovernanceRepository
from kis_mcp_doc.render import build_governance_spec, verify_governance_spec


ROOT = Path(__file__).resolve().parents[1]
MRD_ROOT = ROOT / "mrd" / "governance"
PUBLICATION = ROOT / "publication" / "governance-spec.json"


def copied_repository(tmp_path: Path) -> tuple[Path, GovernanceRepository, Path]:
    root = tmp_path / "repo"
    for name in ("contracts", "mrd", "publication", "src"):
        shutil.copytree(ROOT / name, root / name)
    return root, GovernanceRepository(root, root / "mrd" / "governance"), root / "publication" / "governance-spec.json"


def test_render_is_byte_deterministic(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    first = tmp_path / "first"
    second = tmp_path / "second"

    build_governance_spec(repo, PUBLICATION, first)
    build_governance_spec(repo, PUBLICATION, second)

    assert (first / "specification.md").read_bytes() == (second / "specification.md").read_bytes()
    assert (first / "manifest.json").read_bytes() == (second / "manifest.json").read_bytes()


def test_rendered_spec_decomposes_normative_sections_into_mcp_style_pages(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)
    root = (output / "specification.md").read_text(encoding="utf-8")

    expected = {
        "002-classification.md": "# Classification",
        "003-applicability-and-selection.md": "# Applicability and Selection",
        "004-authority-ownership-and-relationships.md": "# Authority, Ownership, and Relationships",
        "005-layering.md": "# Layering",
        "006-dependency-rules.md": "# Dependency Rules",
        "007-provenance.md": "# Provenance",
        "008-lifecycle.md": "# Lifecycle",
        "009-kis-op-governance-behavior.md": "# kis-op Governance Behavior",
        "010-validation-and-enforcement.md": "# Validation and Enforcement",
    }
    for page, heading in expected.items():
        assert heading in (output / page).read_text(encoding="utf-8")
        assert page in root

    classification = (output / "002-classification.md").read_text(encoding="utf-8")
    validation = (output / "010-validation-and-enforcement.md").read_text(encoding="utf-8")
    assert "## Type catalog (47 allowed types)" in classification
    assert "SEM-DOM" in classification
    assert "## Enforcement modes" in validation
    assert "### Operator Behavior" in validation
    assert "Operator_Behavior" not in validation
    assert "| Rule | Requirement | Enforcement |" in validation
    assert "# kis-op Governance Specification" in root
    assert "## Overview" in root
    assert "## Detailed specification" in root
    assert "GENERATED — DO NOT EDIT" in root


def test_manifest_hashes_and_verifier_detect_tampering(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)

    verified = verify_governance_spec(repo, PUBLICATION, output)
    assert verified["status"] == "valid"

    spec = output / "specification.md"
    spec.write_text(spec.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
    result = verify_governance_spec(repo, PUBLICATION, output)

    assert result["status"] == "invalid"
    assert "GENERATED_FILE_HASH_MISMATCH" in {
        item["code"] for item in result["diagnostics"]
    }


def test_manifest_output_hash_matches_file(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    payload = (output / "specification.md").read_bytes()

    declaration = next(item for item in manifest["files"] if item["path"] == "specification.md")
    assert declaration["sha256"] == hashlib.sha256(payload).hexdigest()


def test_manifest_binds_canonical_repo_dependencies(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    manifest = build_governance_spec(repo, PUBLICATION, output)

    source_paths = {item["path"] for item in manifest["inputs"]["source_files"]}
    assert source_paths == {
        "contracts/mrd/v1/mrd.schema.json",
        "contracts/governance/v1/content.schema.json",
        "contracts/governance/v1/governance-mrd.schema.json",
    }


def test_verifier_detects_bundle_digest_tampering(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["bundle_sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = verify_governance_spec(repo, PUBLICATION, output)
    assert "GENERATED_BUNDLE_HASH_MISMATCH" in {
        item["code"] for item in result["diagnostics"]
    }


def test_verifier_detects_canonical_source_hash_tampering(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["inputs"]["source_files"][0]["sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = verify_governance_spec(repo, PUBLICATION, output)
    assert "SOURCE_FILE_HASH_MISMATCH" in {
        item["code"] for item in result["diagnostics"]
    }


def test_verifier_rejects_unexpected_generated_file(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)
    (output / "unexpected.txt").write_text("not declared\n", encoding="utf-8")

    result = verify_governance_spec(repo, PUBLICATION, output)
    assert "GENERATED_FILE_SET_MISMATCH" in {
        item["code"] for item in result["diagnostics"]
    }


def test_publication_config_is_schema_validated(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    invalid = tmp_path / "publication.json"
    config = json.loads(PUBLICATION.read_text(encoding="utf-8"))
    config["status"] = "maybe"
    invalid.write_text(json.dumps(config), encoding="utf-8")

    try:
        build_governance_spec(repo, invalid, tmp_path / "build")
    except ValueError as error:
        assert "publication configuration invalid" in str(error)
    else:
        raise AssertionError("invalid publication configuration was accepted")


def test_manifest_schema_rejects_unknown_fields(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)
    path = output / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["unexpected"] = True
    path.write_text(json.dumps(manifest), encoding="utf-8")

    result = verify_governance_spec(repo, PUBLICATION, output)

    assert result["status"] == "invalid"
    assert "GENERATED_MANIFEST_INVALID" in {
        item["code"] for item in result["diagnostics"]
    }


def test_recomputed_manifest_cannot_hide_generated_content_tampering(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)

    spec = output / "specification.md"
    spec.write_text(spec.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload = spec.read_bytes()
    declaration = next(item for item in manifest["files"] if item["path"] == "specification.md")
    declaration["sha256"] = hashlib.sha256(payload).hexdigest()
    declaration["bytes"] = len(payload)
    index = json.dumps(manifest["files"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest["bundle_sha256"] = hashlib.sha256(index).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = verify_governance_spec(repo, PUBLICATION, output)

    codes = {item["code"] for item in result["diagnostics"]}
    assert "GENERATED_DECLARATION_MISMATCH" in codes
    assert "GENERATED_FILE_CONTENT_MISMATCH" in codes


def test_verifier_reports_unavailable_generator_source(tmp_path: Path, monkeypatch) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)

    def unavailable(_repository: GovernanceRepository):
        raise OSError("generator source missing")

    monkeypatch.setattr(render_module, "_generator_source_declarations", unavailable)
    result = verify_governance_spec(repo, PUBLICATION, output)

    assert result["status"] == "invalid"
    assert "GENERATOR_SOURCE_UNAVAILABLE" in {
        item["code"] for item in result["diagnostics"]
    }


def test_manifest_validation_checks_are_schema_locked(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)
    path = output / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["validation"]["checks"]["unexpected"] = "pass"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    result = verify_governance_spec(repo, PUBLICATION, output)

    assert result["status"] == "invalid"
    assert "GENERATED_MANIFEST_INVALID" in {item["code"] for item in result["diagnostics"]}


def test_invalid_manifest_validation_requires_diagnostics(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)
    path = output / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["validation"]["status"] = "invalid"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    result = verify_governance_spec(repo, PUBLICATION, output)

    assert result["status"] == "invalid"
    assert "GENERATED_MANIFEST_INVALID" in {item["code"] for item in result["diagnostics"]}


def test_valid_manifest_cannot_report_any_failed_check(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    checks = (
        "classification",
        "applicability",
        "ownership",
        "layering",
        "dependencies",
        "provenance",
        "lifecycle",
        "operator_behavior",
        "schema",
    )
    for check in checks:
        output = tmp_path / check
        build_governance_spec(repo, PUBLICATION, output)
        path = output / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["validation"]["checks"][check] = "fail"
        path.write_text(json.dumps(manifest), encoding="utf-8")

        result = verify_governance_spec(repo, PUBLICATION, output)

        assert result["status"] == "invalid"
        assert "GENERATED_MANIFEST_INVALID" in {
            item["code"] for item in result["diagnostics"]
        }


def test_invalid_manifest_requires_at_least_one_failed_check(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)
    path = output / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["validation"]["status"] = "invalid"
    manifest["validation"]["diagnostics"] = [{"check":"schema","code":"MRD_SCHEMA_INVALID","message":"x","location":"$","mrd_id":None}]
    path.write_text(json.dumps(manifest), encoding="utf-8")

    result = verify_governance_spec(repo, PUBLICATION, output)
    assert result["status"] == "invalid"
    assert "GENERATED_MANIFEST_INVALID" in {item["code"] for item in result["diagnostics"]}


def test_verifier_detects_valid_publication_config_drift(tmp_path: Path) -> None:
    root, repo, publication = copied_repository(tmp_path)
    output = tmp_path / "build"
    build_governance_spec(repo, publication, output)

    config = json.loads(publication.read_text(encoding="utf-8"))
    config["version"] = "1.1.1"
    publication.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = verify_governance_spec(repo, publication, output)
    assert result["status"] == "invalid"
    assert "PUBLICATION_CONFIG_HASH_MISMATCH" in {item["code"] for item in result["diagnostics"]}


def test_verifier_detects_generator_source_drift(tmp_path: Path) -> None:
    root, repo, publication = copied_repository(tmp_path)
    output = tmp_path / "build"
    build_governance_spec(repo, publication, output)

    source = root / "src" / "kis_mcp_doc" / "governance.py"
    source.write_text(source.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")

    result = verify_governance_spec(repo, publication, output)
    assert result["status"] == "invalid"
    assert "GENERATOR_DECLARATION_MISMATCH" in {item["code"] for item in result["diagnostics"]}

def test_verifier_detects_mrd_drift_without_rebuild(tmp_path: Path) -> None:
    root, repo, publication = copied_repository(tmp_path)
    output = tmp_path / "build"
    build_governance_spec(repo, publication, output)

    path = root / "mrd" / "governance" / "01-classification.mrd.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["content"]["purpose"] += " Changed after build."
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = verify_governance_spec(repo, publication, output)
    codes = {item["code"] for item in result["diagnostics"]}
    assert result["status"] == "invalid"
    assert "SOURCE_MRD_SET_MISMATCH" in codes
    assert "SOURCE_SET_HASH_MISMATCH" in codes


def test_verifier_detects_generated_data_file_tampering(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)

    index = output / "data" / "mrd-index.json"
    index.write_text(index.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")

    result = verify_governance_spec(repo, PUBLICATION, output)
    assert result["status"] == "invalid"
    assert "GENERATED_FILE_HASH_MISMATCH" in {item["code"] for item in result["diagnostics"]}