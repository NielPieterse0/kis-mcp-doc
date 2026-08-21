from __future__ import annotations

import hashlib
import json
from pathlib import Path

from kis_mcp_doc.governance import GovernanceRepository
from kis_mcp_doc.render import build_governance_spec, verify_governance_spec


ROOT = Path(__file__).resolve().parents[1]
MRD_ROOT = ROOT / "mrd" / "governance"
PUBLICATION = ROOT / "publication" / "governance-spec.json"


def test_render_is_byte_deterministic(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    first = tmp_path / "first"
    second = tmp_path / "second"

    build_governance_spec(repo, PUBLICATION, first)
    build_governance_spec(repo, PUBLICATION, second)

    assert (first / "specification.md").read_bytes() == (second / "specification.md").read_bytes()
    assert (first / "manifest.json").read_bytes() == (second / "manifest.json").read_bytes()


def test_rendered_spec_contains_six_normative_sections_and_catalog(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)
    markdown = (output / "specification.md").read_text(encoding="utf-8")

    for heading in (
        "## 1. Classification",
        "## 2. Layering",
        "## 3. Dependency Rules",
        "## 4. Provenance",
        "## 5. Lifecycle",
        "## 6. Machine Validation",
    ):
        assert heading in markdown
    assert "SEM-DOM" in markdown
    assert "47" in markdown
    assert "GENERATED — DO NOT EDIT" in markdown


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
