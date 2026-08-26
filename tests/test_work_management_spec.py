from pathlib import Path
import json

from kis_mcp_doc.work_management import WorkManagementRepository, build_work_management_spec, verify_work_management_spec

ROOT = Path(__file__).resolve().parents[1]

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
    assert "<!-- GENERATED — DO NOT EDIT -->" in domain
    assert "- `{\"" not in domain
    assert "**Authority:** work_management" in domain
    assert "### Status" in domain

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
