from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

import pytest
import kis_mcp_doc.render as render_module
from kis_mcp_doc.governance import GovernanceRepository, canonical_source_bytes
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


def test_repository_text_line_endings_do_not_change_bundle(tmp_path: Path) -> None:
    root, repo, publication = copied_repository(tmp_path)
    first = tmp_path / "first"
    second = tmp_path / "second"
    paths = (
        root / "src" / "kis_mcp_doc" / "render.py",
        root / "contracts" / "mrd" / "v1" / "mrd.schema.json",
        root / "mrd" / "governance" / "01-classification.mrd.json",
        publication,
        root / "publication" / "harvest-sources.json",
    )
    for path in paths:
        payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        path.write_bytes(payload)
    build_governance_spec(repo, publication, first)

    for path in paths:
        lf_payload = path.read_bytes()
        crlf_payload = lf_payload.replace(b"\n", b"\r\n")
        assert crlf_payload != lf_payload
        assert b"\r\n" in crlf_payload
        path.write_bytes(crlf_payload)
    build_governance_spec(repo, publication, second)

    first_files = {
        path.relative_to(first).as_posix(): path.read_bytes()
        for path in first.rglob("*")
        if path.is_file()
    }
    second_files = {
        path.relative_to(second).as_posix(): path.read_bytes()
        for path in second.rglob("*")
        if path.is_file()
    }
    assert second_files == first_files


def test_unknown_utf8_source_remains_byte_exact(tmp_path: Path) -> None:
    source = tmp_path / "payload.bin"
    payload = b"header\r\nbody\r\n"
    source.write_bytes(payload)

    assert canonical_source_bytes(source) == payload


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
    applicability = (output / "003-applicability-and-selection.md").read_text(encoding="utf-8")
    behavior = (output / "009-kis-op-governance-behavior.md").read_text(encoding="utf-8")
    validation = (output / "010-validation-and-enforcement.md").read_text(encoding="utf-8")
    assert "## Type catalog (47 allowed types)" in classification
    assert "SEM-DOM" in classification
    assert "## Selecting governance artifacts" in applicability
    assert applicability.index("## Selecting governance artifacts") < applicability.index("## Applicability reference")
    assert "A repository or change MUST NOT instantiate all 47 MRD types by default" in applicability
    assert "020-applicability-catalog.md" in applicability
    assert "## Governance application lifecycle" in behavior
    assert "kis-op applies governance through seven ordered phases" in behavior
    assert "## Validation model" in validation
    assert validation.index("## Validation model") < validation.index("## Enforcement modes")
    assert "### Operator behavior" in validation
    assert "Operator_Behavior" not in validation
    assert "## Requirement traceability" in validation
    assert "| Rule | Enforcement |" in validation
    assert "| Rule | Requirement | Enforcement |" not in validation
    assert "## Normative rules" not in validation
    assert "# kis-op Governance Specification" in root
    assert "## Overview" in root
    assert "## Detailed specification" in root
    assert "GENERATED — DO NOT EDIT" in root


def test_human_composition_preserves_normative_authority_and_traceability(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)

    documents = repo.load()
    for document in documents.values():
        page = (output / render_module._document_page_name(document)).read_text(encoding="utf-8")
        assert "## Normative rules" not in page
        assert "| Rule | Requirement | Enforcement |" not in page
        assert "## Requirement traceability" in page
        for rule in document["content"].get("rules", []):
            assert rule["statement"] in page
            assert f"| `{rule['rule_id']}` | `{rule['enforcement']}` |" in page


def test_governance_generated_reference_separates_lookup_catalogs_and_preserves_navigation(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)
    docs = repo.load()

    applicability_doc = next(doc for doc in docs.values() if doc["content"]["concern"] == "applicability")
    ownership_doc = next(doc for doc in docs.values() if doc["content"]["concern"] == "ownership")
    validation_doc = next(doc for doc in docs.values() if doc["content"]["concern"] == "validation")

    applicability = (output / "003-applicability-and-selection.md").read_text(encoding="utf-8")
    applicability_ref = (output / "020-applicability-catalog.md").read_text(encoding="utf-8")
    relationship_ref = (output / "021-relationship-vocabulary.md").read_text(encoding="utf-8")
    reason_ref = (output / "022-validation-reason-codes.md").read_text(encoding="utf-8")

    assert "| Code | Name | Use when |" not in applicability
    assert "`generated_reference`" in applicability_ref
    for item in applicability_doc["content"]["type_applicability"]:
        assert f"`{item['code']}`" in applicability_ref
        assert item["use_when"] in applicability_ref
    for item in ownership_doc["content"]["relationship_catalog"]:
        assert f"`{item['code']}`" in relationship_ref
        assert item["meaning"] in relationship_ref
    for code in validation_doc["content"]["reason_codes"]:
        assert f"`{code}`" in reason_ref

    classification = (output / "002-classification.md").read_text(encoding="utf-8")
    assert "[Previous: Specification](001-specification.md)" in classification
    assert "[Next: Applicability and Selection](003-applicability-and-selection.md)" in classification
    index = (output / "000-index.md").read_text(encoding="utf-8")
    assert "## Generated reference" in index
    assert "020-applicability-catalog.md" in index


def test_governance_generated_links_resolve(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)

    for page in output.rglob("*.md"):
        text = page.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)#]+)", text):
            if "://" in target:
                continue
            resolved = (page.parent / target).resolve()
            assert resolved.exists(), f"broken generated link in {page.name}: {target}"


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
        "contracts/publication/family/v1/registry.schema.json",
        "mrd/documentation/01-reference-standard.mrd.json",
        "mrd/documentation/02-reference-registry.mrd.json",
        "mrd/documentation/03-publication-architecture.mrd.json",
        "mrd/documentation/04-publication-family-registry.mrd.json",
        "publication/documentation-reference-standard.json",
    }


def test_governance_publication_consumes_documentation_reference_profile(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    manifest = build_governance_spec(repo, PUBLICATION, output)
    config = json.loads(PUBLICATION.read_text(encoding="utf-8"))

    assert config["documentation_reference"] == {
        "output_class": "human_readable_specification",
        "policy_mrd": "KIS-DOC-CON-POL-001",
        "registry_mrd": "KIS-DOC-SEM-REG-001",
    }
    assert "`KIS-DOC-CON-POL-001`" in (output / "001-specification.md").read_text(encoding="utf-8")
    assert any(item["path"] == "mrd/documentation/01-reference-standard.mrd.json" for item in manifest["inputs"]["source_files"])


def test_governance_publication_rejects_external_authority_promotion(tmp_path: Path) -> None:
    root, repo, publication = copied_repository(tmp_path)
    registry_path = root / "mrd" / "documentation" / "02-reference-registry.mrd.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["content"]["references"][1]["may_define_kis_facts"] = True
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    try:
        build_governance_spec(repo, publication, tmp_path / "build")
    except ValueError as error:
        assert "external documentation reference cannot define KIS facts" in str(error)
    else:
        raise AssertionError("external documentation reference authority promotion was accepted")


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

def test_governance_diagrams_are_derived_from_canonical_mrds(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)
    documents = repo.load()
    lifecycle = documents["KIS-KNOW-WRK-STM-001"]["content"]
    page = (output / "008-lifecycle.md").read_text(encoding="utf-8")
    assert "```mermaid" in page
    expected_edges = {
        f"{render_module._heading_anchor(machine['record_mode'])}_{render_module._heading_anchor(transition['from'])} --> {render_module._heading_anchor(machine['record_mode'])}_{render_module._heading_anchor(transition['to'])}"
        for machine in lifecycle["lifecycles"]
        for transition in machine["transitions"]
    }
    actual_edges = {
        line.strip() for line in page.splitlines()
        if " --> " in line and any(
            line.strip().startswith(render_module._heading_anchor(machine["record_mode"]) + "_")
            for machine in lifecycle["lifecycles"]
        )
    }
    assert actual_edges == expected_edges
    ownership = documents["KIS-KNOW-CON-POL-002"]["content"]["ownership_contract"]
    ownership_page = (output / "004-authority-ownership-and-relationships.md").read_text(encoding="utf-8")
    assert f'Canonical owner count: {ownership["canonical_owner_count"]}' in ownership_page
    assert ownership["non_owner_posture"] in ownership_page
    assert ownership["derived_posture"] in ownership_page
    assert ownership["conflict_posture"] in ownership_page


def test_governance_semantic_coverage_resolves_every_rule_and_reference_fact(tmp_path: Path) -> None:
    repo = GovernanceRepository(ROOT, MRD_ROOT)
    output = tmp_path / "build"
    build_governance_spec(repo, PUBLICATION, output)
    coverage = json.loads((output / "data/semantic-coverage.json").read_text(encoding="utf-8"))
    entries = coverage["entries"]
    keys = [(entry["kind"], entry["id"]) for entry in entries]
    assert len(keys) == len(set(keys))
    expected_rules = {
        rule["rule_id"]
        for document in repo.load().values()
        for rule in document["content"].get("rules", [])
    }
    actual_rules = {entry["id"] for entry in entries if entry["kind"] == "rule"}
    assert actual_rules == expected_rules
    for entry in entries:
        page = output / entry["page"]
        assert page.is_file()
        assert f'id="{entry["anchor"]}"' in page.read_text(encoding="utf-8")


def test_governance_semantic_coverage_rejects_duplicate_and_unresolved_entries() -> None:
    files = {"page.md": b'<span id="anchor-a"></span>'}
    duplicate = {
        "entries": [
            {"kind": "rule", "id": "A", "page": "page.md", "anchor": "anchor-a"},
            {"kind": "rule", "id": "A", "page": "page.md", "anchor": "anchor-a"},
        ]
    }
    with pytest.raises(ValueError, match="duplicate Governance semantic coverage entry"):
        render_module._validate_governance_semantic_coverage(files, duplicate)
    broken = {
        "entries": [
            {"kind": "rule", "id": "A", "page": "page.md", "anchor": "missing"}
        ]
    }
    with pytest.raises(ValueError, match="Governance semantic coverage anchor does not resolve"):
        render_module._validate_governance_semantic_coverage(files, broken)
