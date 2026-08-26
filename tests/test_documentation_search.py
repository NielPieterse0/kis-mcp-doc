from __future__ import annotations

import json
import shutil
from pathlib import Path

from kis_mcp_doc.documentation_search import build_documentation_search, search_documentation, validate_documentation_search, verify_documentation_search

ROOT = Path(__file__).parents[1]


def test_search_validation_and_index_cover_site_routes(tmp_path: Path) -> None:
    assert validate_documentation_search(ROOT) == {"status": "valid", "diagnostics": []}
    output = tmp_path / "search"
    manifest = build_documentation_search(ROOT, output)
    index = json.loads((output / "search-index.json").read_text(encoding="utf-8"))
    assert manifest["documents"] == len(index["documents"])
    assert any(item["route"] == "/docs/governance/" for item in index["documents"])
    assert any(item["route"].startswith("/reference/governance-spec/") for item in index["documents"])


def test_search_ranking_is_stable_and_prefers_title_matches() -> None:
    results = search_documentation(ROOT, "governance authority", limit=5)
    assert results
    assert results == search_documentation(ROOT, "governance authority", limit=5)
    assert any(item["family"] in {"governance-docs", "governance-spec"} for item in results)


def test_search_exact_verification_detects_tamper(tmp_path: Path) -> None:
    output = tmp_path / "search"
    build_documentation_search(ROOT, output)
    assert verify_documentation_search(ROOT, output)["status"] == "valid"
    (output / "search-index.json").write_text("{}\n", encoding="utf-8")
    codes = {item["code"] for item in verify_documentation_search(ROOT, output)["diagnostics"]}
    assert "SEARCH_GENERATED_FILE_CONTENT_MISMATCH" in codes


def test_search_rejects_stale_site(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", ".venv", ".work"))
    (root / "generated/documentation-site/routes.json").write_text("[]\n", encoding="utf-8")
    codes = {item["code"] for item in validate_documentation_search(root)["diagnostics"]}
    assert "SEARCH_SITE_STALE" in codes
