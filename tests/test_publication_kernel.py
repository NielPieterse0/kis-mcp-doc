from __future__ import annotations

import json
from pathlib import Path

import pytest

import kis_mcp_doc.publication_adapters as publication_adapters
import kis_mcp_doc.publication_kernel as publication_kernel
from kis_mcp_doc.cli import main
from kis_mcp_doc.publication_kernel import (
    PublicationFamilyRegistry,
    build_registered_publication,
    bundle_manifest_fields,
    exact_bundle_diagnostics,
    file_declarations,
    validate_registered_publications,
    verify_registered_publications,
    write_bundle,
)

ROOT = Path(__file__).parents[1]


def test_registry_discovers_all_governed_publication_families_and_output_classes() -> None:
    registry = PublicationFamilyRegistry(ROOT)
    assert registry.validate() == {"status": "valid", "diagnostics": []}
    families = registry.load()["content"]["families"]
    assert [family["id"] for family in families] == [
        "governance-spec",
        "work-management-spec",
        "documentation-reference-standard",
        "governance-docs",
        "work-management-docs",
    ]
    assert families[0]["output_classes"] == ["human_readable_specification", "generated_reference"]
    assert families[1]["output_classes"] == ["human_readable_specification", "generated_reference"]
    assert families[3]["output_classes"] == ["human_documentation"]
    assert families[4]["output_classes"] == ["human_documentation"]
    assert registry.load()["content"]["adapter_protocol_version"] == 1


def test_registry_rejects_adapter_protocol_version_drift(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    import shutil
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', '.venv', '.work'))
    path = root / "mrd/documentation/04-publication-family-registry.mrd.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["content"]["adapter_protocol_version"] = 2
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    codes = {item["code"] for item in PublicationFamilyRegistry(root).validate()["diagnostics"]}
    assert "PUBLICATION_ADAPTER_PROTOCOL_VERSION_INVALID" in codes
    assert "PUBLICATION_FAMILY_REGISTRY_SCHEMA_INVALID" in codes


def test_registry_rejects_duplicate_output_and_unsupported_output_class(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    import shutil
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', '.venv', '.work'))
    path = root / "mrd/documentation/04-publication-family-registry.mrd.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["content"]["families"][0]["output_classes"] = ["generated_reference"]
    doc["content"]["families"][1]["id"] = doc["content"]["families"][0]["id"]
    doc["content"]["families"][1]["output"] = doc["content"]["families"][0]["output"]
    doc["content"]["families"][2]["output_classes"] = ["not-governed"]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    result = PublicationFamilyRegistry(root).validate()
    codes = {item["code"] for item in result["diagnostics"]}
    assert "PUBLICATION_FAMILY_ID_DUPLICATE" in codes
    assert "PUBLICATION_FAMILY_OUTPUT_DUPLICATE" in codes
    assert "PUBLICATION_FAMILY_REGISTRY_SCHEMA_INVALID" in codes


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("mrd_root", "mrd/../../outside", "PUBLICATION_FAMILY_MRD_ROOT_INVALID"),
        ("publication_config", "publication/../outside.json", "PUBLICATION_FAMILY_CONFIG_INVALID"),
        ("output", "generated/../outside", "PUBLICATION_FAMILY_OUTPUT_INVALID"),
    ],
)
def test_registry_rejects_traversal_in_registered_paths(
    tmp_path: Path, field: str, value: str, code: str
) -> None:
    root = tmp_path / "repo"
    import shutil
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', '.venv', '.work'))
    path = root / "mrd/documentation/04-publication-family-registry.mrd.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["content"]["families"][0][field] = value
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    codes = {item["code"] for item in PublicationFamilyRegistry(root).validate()["diagnostics"]}
    assert code in codes
    assert "PUBLICATION_FAMILY_REGISTRY_SCHEMA_INVALID" in codes


def test_family_adapter_rejects_registered_output_class_drift(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    import shutil
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', '.venv', '.work'))
    path = root / "mrd/documentation/04-publication-family-registry.mrd.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["content"]["families"][0]["output_classes"] = ["generated_reference"]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    result = validate_registered_publications(root, family_ids=["governance-spec"])
    assert result["status"] == "invalid"
    assert any(
        item["code"] == "PUBLICATION_FAMILY_OUTPUT_CLASS_MISMATCH"
        for item in result["families"]["governance-spec"]["diagnostics"]
    )


def test_registered_validation_rejects_invalid_publication_config(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    import shutil
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', '.venv', '.work'))
    publication = root / "publication/governance-spec.json"
    config = json.loads(publication.read_text(encoding="utf-8"))
    config["status"] = "invalid-status"
    publication.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    result = validate_registered_publications(root, family_ids=["governance-spec"])
    assert result["status"] == "invalid"
    assert any(
        item["code"] == "PUBLICATION_CONFIG_INVALID"
        for item in result["families"]["governance-spec"]["diagnostics"]
    )


def test_registry_rejects_adapter_signature_drift(monkeypatch) -> None:
    monkeypatch.setattr(publication_kernel, "_resolve_entrypoint", lambda _value: (lambda only_one: None))
    codes = {item["code"] for item in PublicationFamilyRegistry(ROOT).validate()["diagnostics"]}
    assert "PUBLICATION_FAMILY_ADAPTER_SIGNATURE_INVALID" in codes


def test_file_declarations_and_bundle_hash_are_deterministic() -> None:
    files = {"b.txt": b"two", "a.txt": b"one"}
    first = file_declarations(files)
    second = file_declarations(dict(reversed(list(files.items()))))
    assert first == second
    assert [item["path"] for item in first] == ["a.txt", "b.txt"]
    assert bundle_manifest_fields(files) == bundle_manifest_fields(dict(reversed(list(files.items()))))


@pytest.mark.parametrize("relative", ["../outside.txt", "a\\b.txt", "a//b.txt"])
def test_bundle_paths_must_be_normalized_and_relative(relative: str) -> None:
    with pytest.raises(ValueError, match="normalized relative path"):
        file_declarations({relative: b"payload"})


def test_write_bundle_stages_complete_bundle_and_exact_verification_detects_tamper(tmp_path: Path) -> None:
    output = tmp_path / "bundle"
    manifest = {"files": file_declarations({"a.txt": b"one"}), **bundle_manifest_fields({"a.txt": b"one"})}
    write_bundle(output, {"a.txt": b"one"}, manifest)
    assert exact_bundle_diagnostics(output, {"a.txt": b"one"}, manifest) == []
    (output / "a.txt").write_bytes(b"tampered")
    codes = {item["code"] for item in exact_bundle_diagnostics(output, {"a.txt": b"one"}, manifest)}
    assert "PUBLICATION_GENERATED_FILE_CONTENT_MISMATCH" in codes


def test_write_bundle_refuses_existing_output_without_replace(tmp_path: Path) -> None:
    output = tmp_path / "bundle"
    write_bundle(output, {"a.txt": b"one"}, {"files": file_declarations({"a.txt": b"one"})})
    with pytest.raises(FileExistsError):
        write_bundle(output, {"a.txt": b"two"}, {"files": file_declarations({"a.txt": b"two"})})
    assert (output / "a.txt").read_bytes() == b"one"


def test_write_bundle_restores_previous_complete_bundle_when_replacement_fails(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "bundle"
    write_bundle(output, {"a.txt": b"one"}, {"files": file_declarations({"a.txt": b"one"})})
    real_replace = publication_kernel.os.replace
    calls = 0

    def fail_new_bundle_once(source, target):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated replacement failure")
        return real_replace(source, target)

    monkeypatch.setattr(publication_kernel.os, "replace", fail_new_bundle_once)
    with pytest.raises(OSError, match="simulated replacement failure"):
        write_bundle(
            output,
            {"a.txt": b"two"},
            {"files": file_declarations({"a.txt": b"two"})},
            replace=True,
        )
    assert (output / "a.txt").read_bytes() == b"one"


def test_registered_publication_verification_covers_every_family() -> None:
    result = verify_registered_publications(ROOT)
    assert result["status"] == "valid"
    assert set(result["families"]) == {
        "governance-spec",
        "work-management-spec",
        "documentation-reference-standard",
        "governance-docs",
        "work-management-docs",
    }
    assert all(item["status"] == "valid" for item in result["families"].values())


def test_registered_phase_rejects_invalid_adapter_result(monkeypatch) -> None:
    def invalid_result(_root, _family):
        return {"unexpected": True}

    monkeypatch.setattr(publication_adapters, "validate_governance", invalid_result)
    result = validate_registered_publications(ROOT, family_ids=["governance-spec"])
    assert result["status"] == "invalid"
    assert result["families"]["governance-spec"]["diagnostics"] == [{
        "code": "PUBLICATION_FAMILY_ADAPTER_RESULT_INVALID",
        "message": "governance-spec.validate must return status and diagnostics",
    }]


def test_registered_build_unknown_family_is_structured() -> None:
    result = build_registered_publication(ROOT, "unknown-family")
    assert result["status"] == "invalid"
    assert result["diagnostics"] == [{
        "code": "PUBLICATION_FAMILY_UNKNOWN",
        "message": "unknown publication family: unknown-family",
    }]


def test_registry_cli_validate_and_check_agree_with_registered_families() -> None:
    assert main(["--root", str(ROOT), "publications-validate"]) == 0
    assert main(["--root", str(ROOT), "publications-check-generated"]) == 0
    for validate_command, verify_command in (
        ("validate", "check-generated"),
        ("work-validate", "work-check-generated"),
        ("references-validate", "references-check-generated"),
    ):
        assert main(["--root", str(ROOT), validate_command]) == 0
        assert main(["--root", str(ROOT), verify_command]) == 0


def test_registry_cli_build_dispatches_through_family_adapter(tmp_path: Path, capsys) -> None:
    root = tmp_path / "repo"
    import shutil
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', '.venv', '.work'))
    output = root / "generated/documentation-reference-standard"
    shutil.rmtree(output)
    assert main([
        "--root", str(root), "publications-build",
        "--family", "documentation-reference-standard",
    ]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "valid"
    assert result["family"] == "documentation-reference-standard"
    assert result["diagnostics"] == []
    assert "manifest" in result
    assert (output / "manifest.json").is_file()
    assert (output / "001-specification.md").is_file()


def test_registry_cli_build_unknown_family_is_structured(capsys) -> None:
    assert main([
        "--root", str(ROOT), "publications-build", "--family", "unknown-family"
    ]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "invalid"
    assert result["diagnostics"] == [{
        "code": "PUBLICATION_FAMILY_UNKNOWN",
        "message": "unknown publication family: unknown-family",
    }]


def test_registry_cli_build_existing_output_is_structured(tmp_path: Path, capsys) -> None:
    root = tmp_path / "repo"
    import shutil
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', '.venv', '.work'))
    before = (root / "generated/documentation-reference-standard/manifest.json").read_bytes()
    assert main([
        "--root", str(root), "publications-build", "--family", "documentation-reference-standard"
    ]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "invalid"
    assert result["diagnostics"][0]["code"] == "PUBLICATION_FAMILY_ADAPTER_FAILED"
    assert (root / "generated/documentation-reference-standard/manifest.json").read_bytes() == before


def test_legacy_build_commands_remain_available(tmp_path: Path) -> None:
    assert main(["--root", str(ROOT), "build", "--output", str(tmp_path / "governance")]) == 0
    assert main(["--root", str(ROOT), "work-build", "--output", str(tmp_path / "work")]) == 0
    assert main(["--root", str(ROOT), "references-build", "--output", str(tmp_path / "references")]) == 0
    assert (tmp_path / "governance/manifest.json").is_file()
    assert (tmp_path / "work/manifest.json").is_file()
    assert (tmp_path / "references/manifest.json").is_file()


def test_registry_rejects_unknown_selected_family() -> None:
    result = verify_registered_publications(ROOT, family_ids=["unknown-family"])
    assert result["status"] == "invalid"
    assert result["diagnostics"] == [
        {"code": "PUBLICATION_FAMILY_UNKNOWN", "message": "unknown publication family: unknown-family"}
    ]
