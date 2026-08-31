from pathlib import Path
import json
import re
import shutil

import pytest
import kis_mcp_doc.work_management as work_module
from kis_mcp_doc.work_management import WorkManagementRepository, build_work_management_spec, verify_work_management_spec

ROOT = Path(__file__).resolve().parents[1]


def copied_work_repository(tmp_path):
    root = tmp_path / "repo"
    for name in ("contracts", "prescriptives", "publication", "evidence", "src"):
        shutil.copytree(ROOT / name, root / name)
    return root, WorkManagementRepository(root)


def test_work_management_mrds_validate():
    result = WorkManagementRepository(ROOT).validate()
    assert result["status"] == "valid", result

def test_work_management_spec_is_deterministic(tmp_path):
    repo=WorkManagementRepository(ROOT)
    first=tmp_path/"first"; second=tmp_path/"second"
    build_work_management_spec(repo,first)
    build_work_management_spec(repo,second)
    a={p.relative_to(first).as_posix():p.read_bytes() for p in first.rglob("*") if p.is_file()}
    b={p.relative_to(second).as_posix():p.read_bytes() for p in second.rglob("*") if p.is_file()}
    assert a==b


def test_work_management_manifest_v2_declares_generator_provenance(tmp_path):
    manifest=build_work_management_spec(WorkManagementRepository(ROOT),tmp_path/"build")
    assert manifest["contract"] == {"name":"kis-work-management-spec-build","version":2}
    assert manifest["generator"]["name"] == "kis-mcp-doc"
    assert {item["path"] for item in manifest["generator"]["sources"]} == {
        "src/kis_mcp_doc/canonical.py",
        "src/kis_mcp_doc/publication_kernel.py",
        "src/kis_mcp_doc/work_management.py",
        "contracts/mrd/v1/mrd.schema.json",
        "contracts/work-management/v1/content.schema.json",
        "contracts/work-management/v1/work-management-mrd.schema.json",
    }


def test_work_management_publication_consumes_documentation_reference_profile(tmp_path):
    repo=WorkManagementRepository(ROOT); out=tmp_path/"build"
    manifest=build_work_management_spec(repo,out)
    config=json.loads((ROOT/"publication/work-management-spec.json").read_text(encoding="utf-8"))
    assert config["documentation_reference"] == {
        "output_class": "human_readable_specification",
        "policy_mrd": "urn:uuid:ae7e7dc1-2b8b-5988-845d-24df49dcfe0a",
        "registry_mrd": "urn:uuid:d6110859-d683-5aab-86ff-ceecd899e38d",
    }
    source_paths={item["path"] for item in manifest["inputs"]["source_files"]}
    assert source_paths == {
        "contracts/publication/family/v1/registry.schema.json",
        "prescriptives/documentation/01-reference-standard.mrd.json",
        "prescriptives/documentation/02-reference-registry.mrd.json",
        "prescriptives/documentation/03-publication-architecture.mrd.json",
        "prescriptives/documentation/04-publication-family-registry.mrd.json",
        "publication/documentation-reference-standard.json",
        "evidence/work-management/canonical-snapshot.json",
    }
    assert "`urn:uuid:ae7e7dc1-2b8b-5988-845d-24df49dcfe0a`" in (out/"001-specification.md").read_text(encoding="utf-8")


def test_work_management_publication_rejects_external_authority_promotion(tmp_path):
    root,repo=copied_work_repository(tmp_path)
    registry_path=root/"prescriptives/documentation/02-reference-registry.mrd.json"
    registry=json.loads(registry_path.read_text(encoding="utf-8"))
    registry["content"]["references"][0]["may_define_kis_facts"]=True
    registry_path.write_text(json.dumps(registry,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    try:
        build_work_management_spec(repo,tmp_path/"build")
    except ValueError as error:
        assert "external documentation reference authority is invalid" in str(error)
    else:
        raise AssertionError("external documentation reference authority promotion was accepted")


def test_work_management_verifier_detects_publication_profile_drift(tmp_path):
    root,repo=copied_work_repository(tmp_path); out=tmp_path/"build"
    build_work_management_spec(repo,out)
    publication=root/"publication/work-management-spec.json"
    config=json.loads(publication.read_text(encoding="utf-8"))
    config["subtitle"] += " Changed after build."
    publication.write_text(json.dumps(config,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    result=verify_work_management_spec(repo,out)
    assert result["status"]=="invalid"
    assert result["diagnostics"][0]["code"]=="WORK_GENERATED_DRIFT"

def test_work_management_generated_bundle_verifies(tmp_path):
    repo=WorkManagementRepository(ROOT); out=tmp_path/"build"
    build_work_management_spec(repo,out)
    assert verify_work_management_spec(repo,out)["status"]=="valid"
    (out/"specification.md").write_text("tampered\n",encoding="utf-8")
    assert verify_work_management_spec(repo,out)["status"]=="invalid"

def test_work_management_verifier_ignores_text_line_endings(tmp_path):
    repo=WorkManagementRepository(ROOT); out=tmp_path/"build"
    build_work_management_spec(repo,out)
    for path in out.rglob("*"):
        if path.is_file():
            payload=path.read_bytes().replace(b"\r\n",b"\n").replace(b"\r",b"\n")
            path.write_bytes(payload.replace(b"\n",b"\r\n"))
    assert verify_work_management_spec(repo,out)["status"]=="valid"

def test_generated_spec_is_human_readable(tmp_path):
    repo=WorkManagementRepository(ROOT); out=tmp_path/"build"
    build_work_management_spec(repo,out)
    domain=(out/"002-work-management-domain-model.md").read_text(encoding="utf-8")
    lifecycle=(out/"003-work-lifecycle.md").read_text(encoding="utf-8")
    operations=(out/"004-work-operations.md").read_text(encoding="utf-8")
    selection=(out/"005-next-work-selection.md").read_text(encoding="utf-8")
    authority=(out/"006-authority-and-reconciliation-policy.md").read_text(encoding="utf-8")
    conformance=(out/"008-work-management-conformance.md").read_text(encoding="utf-8")

    assert "<!-- GENERATED — DO NOT EDIT -->" in domain
    assert "## Authority directions" in domain
    assert "| Field | Meaning | Authority | Direction |" not in domain
    assert "020-work-field-and-vocabulary-reference.md" in domain
    assert "\n### Status\n" not in domain
    assert "**Id:**" not in domain
    assert "A work item moves through explicit states" in lifecycle
    assert "| State | Meaning | GitHub Project status |" in lifecycle
    assert "Work Management exposes a bounded set of operations" in operations
    assert "| Operation | Purpose | Effect | Implementation surface |" in operations
    assert "Selection is deterministic" in selection
    assert "1. Keep only candidates" in selection
    assert "Authority determines which system may change a fact" in authority
    assert "| Field | Type | Options |" not in authority
    assert "021-work-project-configuration-reference.md" in authority
    assert "A Work Management implementation conforms" in conformance
    assert "1. MRD envelopes validate" in conformance
    assert "- `{\"" not in domain
    for page in (domain, lifecycle, operations, selection, authority, conformance):
        assert " | ? |" not in page
        assert " ? " not in page


def test_root_spec_reports_observed_project_evidence(tmp_path):
    repo=WorkManagementRepository(ROOT); out=tmp_path/"build"
    build_work_management_spec(repo,out)
    spec=(out/"001-specification.md").read_text(encoding="utf-8")
    assert "The captured live GitHub Project evidence is observed" in spec
    assert "could not be observed" not in spec

def test_generated_spec_preserves_reference_facts(tmp_path):
    repo=WorkManagementRepository(ROOT); out=tmp_path/"build"
    build_work_management_spec(repo,out)
    docs=repo.load()

    domain=(out/"020-work-field-and-vocabulary-reference.md").read_text(encoding="utf-8")
    for field in docs["urn:uuid:a0e914e6-64b0-561f-ad39-393287ce71c5"]["content"]["fields"]:
        assert field["name"] in domain
        assert f"`{field['id']}`" in domain
    for vocabulary in docs["urn:uuid:a0e914e6-64b0-561f-ad39-393287ce71c5"]["content"]["vocabularies"]:
        for value in vocabulary["values"]:
            assert value["label"] in domain
            assert f"`{value['token']}`" in domain

    lifecycle=(out/"003-work-lifecycle.md").read_text(encoding="utf-8")
    for guard in docs["urn:uuid:7f58b5b4-9808-5c06-bbed-75a8526685f3"]["content"]["guards"]:
        assert f"`{guard['id']}`" in lifecycle
        assert f"`{guard['reason_code']}`" in lifecycle

    operations=(out/"004-work-operations.md").read_text(encoding="utf-8")
    for operation in docs["urn:uuid:3bab4e5b-4c6d-5c21-811c-a7f6cb02ac93"]["content"]["operations"]:
        assert f"`{operation['id']}`" in operations
        assert f"`{operation['implementation_surface']}`" in operations

    selection=(out/"005-next-work-selection.md").read_text(encoding="utf-8")
    for rule in docs["urn:uuid:0c96b519-06db-5616-95be-888c29f2da5c"]["content"]["rules"]:
        assert f"`{rule['id']}`" in selection
        if rule["reason_code"] is not None:
            assert f"`{rule['reason_code']}`" in selection

    authority=(out/"021-work-project-configuration-reference.md").read_text(encoding="utf-8")
    policy=docs["urn:uuid:c589700c-9c38-5e30-be4c-659084060fa0"]["content"]
    for field in policy["github_project_schema"]["fields"]:
        assert field["name"] in authority
    for view in policy["github_project_schema"]["views"]:
        assert view["name"] in authority


def test_work_management_reference_separation_and_navigation(tmp_path):
    repo=WorkManagementRepository(ROOT); out=tmp_path/"build"
    build_work_management_spec(repo,out)

    domain_ref=(out/"020-work-field-and-vocabulary-reference.md").read_text(encoding="utf-8")
    project_ref=(out/"021-work-project-configuration-reference.md").read_text(encoding="utf-8")
    provider=(out/"007-provider-and-command-plane-boundary.md").read_text(encoding="utf-8")
    first=(out/"002-work-management-domain-model.md").read_text(encoding="utf-8")
    index=(out/"000-index.md").read_text(encoding="utf-8")

    assert "`generated_reference`" in domain_ref
    assert "`generated_reference`" in project_ref
    assert "| Field | Meaning | Authority | Direction | Details |" in domain_ref
    assert "| Field | Type | Options |" in project_ref
    assert "| Field | Authority | Direction |" not in provider
    assert "| From | Allowed next states | Additional requirement |" not in provider
    assert "[Work lifecycle](003-work-lifecycle.md)" in provider
    assert "[Previous: Specification](001-specification.md)" in first
    assert "[Next: Work lifecycle](003-work-lifecycle.md)" in first
    assert "## Generated reference" in index


def test_work_management_generated_links_resolve(tmp_path):
    repo=WorkManagementRepository(ROOT); out=tmp_path/"build"
    build_work_management_spec(repo,out)
    for page in out.rglob("*.md"):
        text=page.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)#]+)",text):
            if "://" in target:
                continue
            assert (page.parent/target).resolve().exists(), f"broken generated link in {page.name}: {target}"


def test_snapshot_pins_parent_revision_and_live_project_state():
    data=json.loads((ROOT/"evidence/work-management/canonical-snapshot.json").read_text(encoding="utf-8"))
    assert data["source_revision"]=="b1c7f00a90c063c6cae287669035e358a04295e0"
    observation=data["live_project_observation"]
    assert observation["status"]=="observed"
    assert observation["inventory_complete"] is True
    assert observation["schema_status"]["ready"] is True
    assert observation["schema_status"]["missing_fields"]==[]
    assert observation["schema_status"]["type_mismatches"]==[]
    assert observation["schema_status"]["missing_options"]==[]
    assert observation["schema_status"]["missing_views"]==[]
    assert observation["schema_status"]["view_mismatches"]==[]


def test_work_diagrams_preserve_independent_status_and_delivery_dimensions(tmp_path):
    output = tmp_path / "build"
    repo = WorkManagementRepository(ROOT)
    build_work_management_spec(repo, output)
    docs = repo.load()
    lifecycle = docs["urn:uuid:7f58b5b4-9808-5c06-bbed-75a8526685f3"]["content"]
    page = (output / "003-work-lifecycle.md").read_text(encoding="utf-8")
    assert "Work Status and Delivery Stage are separate dimensions" in page
    assert 'subgraph work_status["Work Status"]' in page
    assert 'subgraph delivery_stage["Delivery Stage"]' in page
    actual_status_edges = {
        line.strip() for line in page.splitlines()
        if line.strip().startswith("status_") and " --> " in line
    }
    expected_status_edges = {
        f"status_{work_module._mermaid_token(source)} --> status_{work_module._mermaid_token(target)}"
        for source, targets in lifecycle["transitions"].items()
        for target in targets
    }
    assert actual_status_edges == expected_status_edges
    actual_stage_edges = {
        line.strip() for line in page.splitlines()
        if line.strip().startswith("stage_") and " --> " in line
    }
    expected_stage_edges = {
        f"stage_{work_module._mermaid_token(first)} --> stage_{work_module._mermaid_token(second)}"
        for first, second in zip(lifecycle["delivery"]["stages"], lifecycle["delivery"]["stages"][1:])
    }
    assert actual_stage_edges == expected_stage_edges
    provider = (output / "007-provider-and-command-plane-boundary.md").read_text(encoding="utf-8")
    assert "## Authority and handoff flow" in provider
    authority = docs["urn:uuid:2f2b1233-37fe-580c-bc75-26a38e9aa7fe"]["content"]["command_plane"]["field_authority"]
    grouped = {}
    for field, contract in authority.items():
        grouped.setdefault((contract["authority"], contract["direction"]), []).append(field)
    for (owner, direction), fields in grouped.items():
        assert f"- `{owner}` -> `{direction}`: {', '.join(sorted(fields))}." in provider


def test_work_semantic_coverage_resolves_declared_facts(tmp_path):
    output = tmp_path / "build"
    repo = WorkManagementRepository(ROOT)
    build_work_management_spec(repo, output)
    coverage = json.loads((output / "data/semantic-coverage.json").read_text(encoding="utf-8"))
    entries = coverage["entries"]
    keys = [(entry["kind"], entry["id"]) for entry in entries]
    assert len(keys) == len(set(keys))
    docs = repo.load()
    assert {entry["id"] for entry in entries if entry["kind"] == "mrd"} == set(docs)
    lifecycle = docs["urn:uuid:7f58b5b4-9808-5c06-bbed-75a8526685f3"]["content"]
    assert {entry["id"] for entry in entries if entry["kind"] == "work_state"} == {
        state["token"] for state in lifecycle["states"]
    }
    assert {entry["id"] for entry in entries if entry["kind"] == "delivery_stage"} == set(lifecycle["delivery"]["stages"])
    for entry in entries:
        page = output / entry["page"]
        assert page.is_file()
        assert f'id="{entry["anchor"]}"' in page.read_text(encoding="utf-8")


def test_work_semantic_coverage_rejects_duplicate_and_unresolved_entries() -> None:
    files = {"page.md": b'<span id="anchor-a"></span>'}
    duplicate = {
        "entries": [
            {"kind": "field", "id": "A", "page": "page.md", "anchor": "anchor-a"},
            {"kind": "field", "id": "A", "page": "page.md", "anchor": "anchor-a"},
        ]
    }
    with pytest.raises(ValueError, match="duplicate Work semantic coverage entry"):
        work_module._validate_work_semantic_coverage(files, duplicate)
    broken = {
        "entries": [
            {"kind": "field", "id": "A", "page": "page.md", "anchor": "missing"}
        ]
    }
    with pytest.raises(ValueError, match="Work semantic coverage anchor does not resolve"):
        work_module._validate_work_semantic_coverage(files, broken)


def test_work_management_rejects_repository_source_escape(tmp_path):
    root, repo = copied_work_repository(tmp_path)
    outside = root.parent / "outside.txt"
    outside.write_text("outside\n", encoding="utf-8")
    path = next((root / "prescriptives/work-management").glob("*.mrd.json"))
    document = json.loads(path.read_text(encoding="utf-8"))
    document["_mrd"]["dependencies"].append({"source": "repo:../outside.txt", "relationship": "depends_on"})
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = repo.validate()
    assert result["status"] == "invalid"
    assert "WORK_MRD_SOURCE_UNRESOLVED" in {item["code"] for item in result["diagnostics"]}


def test_work_management_domain_profile_rejects_empty_content(tmp_path):
    root, repo = copied_work_repository(tmp_path)
    path = next((root / "prescriptives/work-management").glob("*.mrd.json"))
    document = json.loads(path.read_text(encoding="utf-8"))
    document["content"] = {}
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = repo.validate()
    assert result["status"] == "invalid"
    assert "WORK_MRD_SCHEMA_INVALID" in {item["code"] for item in result["diagnostics"]}
