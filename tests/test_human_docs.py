from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from kis_mcp_doc.governance import GovernanceRepository
from kis_mcp_doc.human_docs import (
    build_human_docs_family,
    validate_human_docs_family,
    verify_human_docs_family,
)
from kis_mcp_doc.publication_kernel import PublicationFamilyRegistry
from kis_mcp_doc.work_management import WorkManagementRepository

ROOT = Path(__file__).resolve().parents[1]


def _family(family_id: str) -> dict:
    return PublicationFamilyRegistry(ROOT).family(family_id)


def test_human_documentation_families_are_registered_separately_from_specs() -> None:
    registry = PublicationFamilyRegistry(ROOT)
    assert registry.validate() == {"status": "valid", "diagnostics": []}
    governance = registry.family("mrd-specification-docs")
    work = registry.family("work-management-docs")
    assert governance["output_classes"] == ["human_documentation"]
    assert work["output_classes"] == ["human_documentation"]


def test_governance_docs_are_deterministic_and_source_derived(tmp_path: Path) -> None:
    family = _family("mrd-specification-docs")
    first = tmp_path / "first"
    second = tmp_path / "second"
    a = build_human_docs_family(ROOT, family, "mrd-specification", output=first)
    b = build_human_docs_family(ROOT, family, "mrd-specification", output=second)
    assert a == b
    assert {p.relative_to(first).as_posix(): p.read_bytes() for p in first.rglob("*") if p.is_file()} == {
        p.relative_to(second).as_posix(): p.read_bytes() for p in second.rglob("*") if p.is_file()
    }
    docs = GovernanceRepository(ROOT, ROOT / "prescriptives/mrd-specification").load()
    classification = next(doc for doc in docs.values() if doc["content"]["concern"] == "classification")
    page = (first / "002-classify-and-select.md").read_text(encoding="utf-8")
    assert str(classification["content"]["catalog_policy"]["expected_type_count"]) in page
    assert "stable opaque MRD identity" not in page
    assert not re.search(r"^## \d+\.", page, flags=re.MULTILINE)
    assert "MRD Specification" in page


def test_work_docs_are_deterministic_and_preserve_state_authority(tmp_path: Path) -> None:
    family = _family("work-management-docs")
    first = tmp_path / "first"
    second = tmp_path / "second"
    build_human_docs_family(ROOT, family, "work-management", output=first)
    build_human_docs_family(ROOT, family, "work-management", output=second)
    assert {p.relative_to(first).as_posix(): p.read_bytes() for p in first.rglob("*") if p.is_file()} == {
        p.relative_to(second).as_posix(): p.read_bytes() for p in second.rglob("*") if p.is_file()
    }
    docs = WorkManagementRepository(ROOT).load()
    lifecycle = docs["urn:uuid:7f58b5b4-9808-5c06-bbed-75a8526685f3"]["content"]
    page = (first / "002-work-lifecycle.md").read_text(encoding="utf-8")
    assert "Work Status and Delivery Stage are separate dimensions" in page
    for state in lifecycle["states"]:
        assert state["label"] in page
        assert f"`{state['token']}`" in page
    complete = (first / "004-complete-work.md").read_text(encoding="utf-8")
    for stage in lifecycle["delivery"]["stages"]:
        assert f"`{stage}`" in complete


def test_human_docs_traceability_points_only_to_canonical_mrds(tmp_path: Path) -> None:
    for family_id, kind in (("mrd-specification-docs", "mrd-specification"), ("work-management-docs", "work-management")):
        family = _family(family_id)
        output = tmp_path / family_id
        build_human_docs_family(ROOT, family, kind, output=output)
        trace = json.loads((output / "data/source-traceability.json").read_text(encoding="utf-8"))
        source_ids = set(_family_source_ids(family))
        assert trace["output_class"] == "human_documentation"
        assert all(set(topic["source_mrds"]) <= source_ids for topic in trace["topics"])


def _family_source_ids(family: dict) -> list[str]:
    return [json.loads(path.read_text(encoding="utf-8"))["_mrd"]["id"] for path in sorted((ROOT / family["mrd_root"]).glob("*.mrd.json"))]


def test_human_docs_links_resolve_against_repository(tmp_path: Path) -> None:
    for family_id, kind in (("mrd-specification-docs", "mrd-specification"), ("work-management-docs", "work-management")):
        family = _family(family_id)
        output = tmp_path / family_id
        build_human_docs_family(ROOT, family, kind, output=output)
        for page in output.glob("*.md"):
            text = page.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)#]+)", text):
                if "://" in target:
                    continue
                if target.startswith("../"):
                    resolved = ROOT / "generated" / family_id / target
                else:
                    resolved = page.parent / target
                assert resolved.resolve().exists(), f"broken link in {page.name}: {target}"


def test_human_docs_verifier_detects_tampering(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", ".venv", ".work"))
    family = PublicationFamilyRegistry(root).family("mrd-specification-docs")
    output = root / family["output"]
    shutil.rmtree(output)
    build_human_docs_family(root, family, "mrd-specification")
    assert verify_human_docs_family(root, family, "mrd-specification")["status"] == "valid"
    (output / "000-index.md").write_text("tampered\n", encoding="utf-8")
    result = verify_human_docs_family(root, family, "mrd-specification")
    assert result["status"] == "invalid"
    assert any(item["code"] == "HUMAN_DOCUMENTATION_GENERATED_FILE_CONTENT_MISMATCH" for item in result["diagnostics"])
