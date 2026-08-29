from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from kis_mcp_doc.documentation_search import _rank_search_index, build_documentation_search, search_documentation, validate_documentation_search, verify_documentation_search
from kis_mcp_doc.documentation_site import _browser_search_script

ROOT = Path(__file__).parents[1]


def test_search_validation_and_index_cover_site_routes(tmp_path: Path) -> None:
    assert validate_documentation_search(ROOT) == {"status": "valid", "diagnostics": []}
    output = tmp_path / "search"
    manifest = build_documentation_search(ROOT, output)
    index = json.loads((output / "search-index.json").read_text(encoding="utf-8"))
    assert manifest["documents"] == len(index["documents"])
    assert any(item["route"] == "/docs/governance/" for item in index["documents"])
    assert any(item["route"] == "/docs/repository/" for item in index["documents"])
    assert any(item["route"].startswith("/reference/governance-spec/") for item in index["documents"])
    assert not any(item["family"].startswith("work-management") for item in index["documents"])


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


def test_search_rejects_non_positive_explicit_limits() -> None:
    import pytest
    for value in (0, -1, True):
        with pytest.raises(ValueError, match="positive integer"):
            search_documentation(ROOT, "governance", limit=value)
        with pytest.raises(ValueError, match="positive integer"):
            search_documentation(ROOT, "a", limit=value)


def test_search_punctuation_uses_one_token_contract() -> None:
    slash = search_documentation(ROOT, "governance/authority", limit=10)
    comma = search_documentation(ROOT, "governance, authority", limit=10)
    spaced = search_documentation(ROOT, "governance authority", limit=10)
    assert slash == comma == spaced


def test_search_index_declares_versioned_contract(tmp_path: Path) -> None:
    output = tmp_path / "search"
    build_documentation_search(ROOT, output)
    index = json.loads((output / "search-index.json").read_text(encoding="utf-8"))
    assert index["algorithm"] == "kis-static-search-v2"
    assert index["contract"] == {"version": 2, "title_weight": 5, "ranking": ["matched_terms", "score", "route"]}


def test_browser_and_python_share_cross_runtime_golden_vectors(tmp_path: Path) -> None:
    documents = [
        {"route":"/a/","title":"Project schema","family":"f","surface":"docs","excerpt":"a","terms":{"project":1,"schema":1,"governance":1,"authority":1,"work-management":1},"title_terms":{"project":1,"schema":1}},
        {"route":"/b/","title":"Governance","family":"f","surface":"docs","excerpt":"b","terms":{"governance":2,"authority":1},"title_terms":{"governance":1}},
        {"route":"/c/","title":"Authority","family":"f","surface":"docs","excerpt":"c","terms":{"governance":2,"authority":1},"title_terms":{"authority":1}},
    ]
    index = {"minimum_token_length":2,"default_limit":10,"contract":{"version":2,"title_weight":5,"ranking":["matched_terms","score","route"]},"documents":documents}
    vectors = [
        ["project schema", 10], ["governance/authority", 10],
        ["governance, authority", 10], ["work-management", 10],
        ["a governance", 10], ["governance authority", 2], ["governance", 2],
    ]
    expected = [[item["route"] for item in _rank_search_index(index, query, limit)] for query, limit in vectors]
    script = tmp_path / "search.js"; script.write_text(_browser_search_script(""), encoding="utf-8")
    payload = tmp_path / "index.json"; payload.write_text(json.dumps(index), encoding="utf-8")
    harness = "const fs=require('fs');const [s,p,v]=process.argv.slice(1);eval(fs.readFileSync(s,'utf8'));const i=JSON.parse(fs.readFileSync(p,'utf8'));const x=JSON.parse(v);console.log(JSON.stringify(x.map(([q,l])=>kisRankSearch(i,q,l).map(r=>r.d.route))));"
    result = subprocess.run(
        ["node", "-e", harness, str(script), str(payload), json.dumps(vectors)],
        check=True, capture_output=True, text=True,
    )
    assert json.loads(result.stdout) == expected
