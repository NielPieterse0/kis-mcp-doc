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
    lifecycle=(out/"003-work-lifecycle.md").read_text(encoding="utf-8")
    operations=(out/"004-work-operations.md").read_text(encoding="utf-8")
    selection=(out/"005-next-work-selection.md").read_text(encoding="utf-8")
    authority=(out/"006-authority-and-reconciliation-policy.md").read_text(encoding="utf-8")
    conformance=(out/"008-work-management-conformance.md").read_text(encoding="utf-8")

    assert "<!-- GENERATED — DO NOT EDIT -->" in domain
    assert "Work Management uses three authority directions" in domain
    assert "| Field | Meaning | Authority | Direction |" in domain
    assert "\n### Status\n" not in domain
    assert "**Id:**" not in domain
    assert "A work item moves through explicit states" in lifecycle
    assert "| State | Meaning | GitHub Project status |" in lifecycle
    assert "Work Management exposes a bounded set of operations" in operations
    assert "| Operation | Purpose | Effect | Implementation surface |" in operations
    assert "Selection is deterministic" in selection
    assert "1. Keep only candidates" in selection
    assert "Authority determines which system may change a fact" in authority
    assert "| Field | Type | Options |" in authority
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

    domain=(out/"002-work-management-domain-model.md").read_text(encoding="utf-8")
    for field in docs["KIS-WORK-SEM-REG-001"]["content"]["fields"]:
        assert field["name"] in domain
        assert f"`{field['id']}`" in domain
    for vocabulary in docs["KIS-WORK-SEM-REG-001"]["content"]["vocabularies"]:
        for value in vocabulary["values"]:
            assert value["label"] in domain
            assert f"`{value['token']}`" in domain

    lifecycle=(out/"003-work-lifecycle.md").read_text(encoding="utf-8")
    for guard in docs["KIS-WORK-WRK-STM-001"]["content"]["guards"]:
        assert f"`{guard['id']}`" in lifecycle
        assert f"`{guard['reason_code']}`" in lifecycle

    operations=(out/"004-work-operations.md").read_text(encoding="utf-8")
    for operation in docs["KIS-WORK-WRK-WFL-001"]["content"]["operations"]:
        assert f"`{operation['id']}`" in operations
        assert f"`{operation['implementation_surface']}`" in operations

    selection=(out/"005-next-work-selection.md").read_text(encoding="utf-8")
    for rule in docs["KIS-WORK-DEC-SCR-001"]["content"]["rules"]:
        assert f"`{rule['id']}`" in selection
        if rule["reason_code"] is not None:
            assert f"`{rule['reason_code']}`" in selection

    authority=(out/"006-authority-and-reconciliation-policy.md").read_text(encoding="utf-8")
    policy=docs["KIS-WORK-CON-POL-001"]["content"]
    for field in policy["github_project_schema"]["fields"]:
        assert field["name"] in authority
    for view in policy["github_project_schema"]["views"]:
        assert view["name"] in authority


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
