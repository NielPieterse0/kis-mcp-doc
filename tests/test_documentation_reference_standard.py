from __future__ import annotations

import json
from pathlib import Path

import pytest

from kis_mcp_doc.cli import main
from kis_mcp_doc.documentation_reference import (
    DocumentationReferenceRepository,
    build_documentation_reference_standard,
    verify_documentation_reference_standard,
)


ROOT = Path(__file__).resolve().parents[1]


def _repo() -> DocumentationReferenceRepository:
    return DocumentationReferenceRepository(ROOT)


def test_reference_standard_validates_official_baseline() -> None:
    result = _repo().validate()

    assert result["status"] == "valid"
    assert result["checks"] == {
        "schema": "pass",
        "authority": "pass",
        "harvest_binding": "pass",
        "pinning": "pass",
        "lifecycle": "pass",
        "provenance": "pass",
    }


def test_reference_registry_has_ten_bounded_sources() -> None:
    documents = _repo().load()
    registry = documents["urn:uuid:d6110859-d683-5aab-86ff-ceecd899e38d"]["content"]
    sources = {item["id"]: item for item in registry["references"]}

    assert len(sources) == 10
    assert sources["mcp-2026"]["role"] == "normative_external"
    assert sources["google-developer-style"]["role"] == "prescriptive_external"
    for source_id in (
        "sentry-mcp", "github-mcp", "azure-mcp", "playwright-mcp",
        "atlassian-rovo-mcp", "figma-mcp", "aws-labs-mcp", "cloudflare-mcp",
    ):
        assert sources[source_id]["role"] == "implementation_reference"
        assert sources[source_id]["may_define_kis_facts"] is False
        assert source_id not in sources[source_id]["permitted_uses"]


def test_reference_registry_resolves_mcp_harvest_identity() -> None:
    registry = _repo().load()["urn:uuid:d6110859-d683-5aab-86ff-ceecd899e38d"]["content"]
    mcp = next(item for item in registry["references"] if item["id"] == "mcp-2026")

    assert mcp["harvest_source_id"] == "mcp-spec-2026-07-28"
    assert mcp["pin"]["kind"] == "content_sha256"
    assert len(mcp["pin"]["value"]) == 64


def test_non_normative_source_cannot_claim_canonical_authority(tmp_path: Path) -> None:
    repo = _repo()
    documents = repo.load()
    registry = documents["urn:uuid:d6110859-d683-5aab-86ff-ceecd899e38d"]
    github = next(item for item in registry["content"]["references"] if item["id"] == "github-mcp")
    github["may_define_kis_facts"] = True

    result = repo.validate_documents(documents)

    assert result["status"] == "invalid"
    assert any(item["code"] == "REFERENCE_AUTHORITY_PROMOTION_FORBIDDEN" for item in result["diagnostics"])


def test_unpinned_active_reference_fails_closed() -> None:
    repo = _repo()
    documents = repo.load()
    registry = documents["urn:uuid:d6110859-d683-5aab-86ff-ceecd899e38d"]
    sentry = next(item for item in registry["content"]["references"] if item["id"] == "sentry-mcp")
    sentry["pin"] = None

    result = repo.validate_documents(documents)

    assert result["status"] == "invalid"
    assert any(item["code"] == "REFERENCE_PIN_REQUIRED" for item in result["diagnostics"])


def test_reference_standard_build_is_deterministic_and_verifiable(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"

    manifest_a = build_documentation_reference_standard(_repo(), first)
    manifest_b = build_documentation_reference_standard(_repo(), second)

    assert manifest_a == manifest_b
    assert (first / "001-specification.md").read_bytes() == (second / "001-specification.md").read_bytes()
    assert (first / "002-reference-catalogue.md").read_bytes() == (second / "002-reference-catalogue.md").read_bytes()
    assert verify_documentation_reference_standard(_repo(), first)["status"] == "valid"


def test_reference_standard_generated_page_explains_authority_and_output_classes(tmp_path: Path) -> None:
    output = tmp_path / "build"
    build_documentation_reference_standard(_repo(), output)
    page = (output / "001-specification.md").read_text(encoding="utf-8")

    assert "# Documentation Reference Standard" in page
    assert "## Authority model" in page
    assert "## Documentation output classes" in page
    assert "human documentation" in page.lower()
    assert "human-readable specification" in page.lower()
    assert "generated reference" in page.lower()
    assert "MUST NOT" in page


def test_generated_tamper_is_detected(tmp_path: Path) -> None:
    output = tmp_path / "build"
    build_documentation_reference_standard(_repo(), output)
    (output / "002-reference-catalogue.md").write_text("tampered\n", encoding="utf-8")

    result = verify_documentation_reference_standard(_repo(), output)

    assert result["status"] == "invalid"
    assert any(item["code"] == "GENERATED_FILE_CONTENT_MISMATCH" for item in result["diagnostics"])


def test_cli_reference_commands(tmp_path: Path) -> None:
    output = tmp_path / "build"

    assert main(["--root", str(ROOT), "references-validate"]) == 0
    assert main(["--root", str(ROOT), "references-build", "--output", str(output)]) == 0
    assert main(["--root", str(ROOT), "references-check-generated", "--output", str(output)]) == 0


def test_registry_projection_is_machine_readable(tmp_path: Path) -> None:
    output = tmp_path / "build"
    build_documentation_reference_standard(_repo(), output)
    registry = json.loads((output / "data" / "reference-registry.json").read_text(encoding="utf-8"))

    assert registry["registry_version"] == "1.0.0"
    assert len(registry["references"]) == 10


def test_research_reference_pin_must_bind_registered_evidence() -> None:
    repo = _repo()
    documents = repo.load()
    registry = documents["urn:uuid:d6110859-d683-5aab-86ff-ceecd899e38d"]
    source = next(item for item in registry["content"]["references"] if item["id"] == "sentry-mcp")
    source["pin"]["value"] = "0" * 64

    result = repo.validate_documents(documents)

    assert result["status"] == "invalid"
    assert any(item["code"] == "REFERENCE_EVIDENCE_PIN_MISMATCH" for item in result["diagnostics"])


def test_mrd_provenance_fingerprint_mismatch_fails() -> None:
    repo = _repo()
    documents = repo.load()
    documents["urn:uuid:ae7e7dc1-2b8b-5988-845d-24df49dcfe0a"]["_mrd"]["provenance"]["source_fingerprint"] = "sha256:" + ("0" * 64)

    result = repo.validate_documents(documents)

    assert result["status"] == "invalid"
    assert any(item["code"] == "REFERENCE_PROVENANCE_FINGERPRINT_MISMATCH" for item in result["diagnostics"])


def test_reference_repository_rejects_repository_source_escape(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    import shutil
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", ".venv", ".work"))
    outside = root.parent / "outside.txt"
    outside.write_text("outside\n", encoding="utf-8")
    policy_path = root / "prescriptives/documentation/01-reference-standard.mrd.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    policy["_mrd"]["dependencies"].append({"source": "repo:../outside.txt", "relationship": "depends_on"})
    policy_path.write_text(json.dumps(policy, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = DocumentationReferenceRepository(root).validate()
    assert result["status"] == "invalid"
    assert "REFERENCE_SOURCE_UNRESOLVED" in {item["code"] for item in result["diagnostics"]}


def test_reference_invalid_result_has_failed_check() -> None:
    from kis_mcp_doc.documentation_reference import _diag, _result
    checks = {key: "pass" for key in ("schema", "authority", "harvest_binding", "pinning", "lifecycle", "provenance")}
    result = _result([_diag("REFERENCE_SOURCE_UNRESOLVED", "broken source")], checks)
    assert result["status"] == "invalid"
    assert "fail" in result["checks"].values()
