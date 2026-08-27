from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .documentation_site import route_entries, validate_documentation_site
from .publication_kernel import bundle_diagnostics, bundle_manifest_fields, file_declarations, write_bundle

_CONFIG = "publication/documentation-search.json"
_SEARCH_SOURCE = "src/kis_mcp_doc/documentation_search.py"
_SITE_SOURCE = "src/kis_mcp_doc/documentation_site.py"
_TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
_SEARCH_CONTRACT = {
    "version": 2,
    "title_weight": 5,
    "ranking": ["matched_terms", "score", "route"],
}


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _tokens(text: str, minimum: int) -> list[str]:
    return [token.lower() for token in _TOKEN_RE.findall(text) if len(token) >= minimum]


def _search_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        try:
            value = json.loads(text)
            text = json.dumps(value, ensure_ascii=False, sort_keys=True)
        except json.JSONDecodeError:
            pass
    return " ".join(text.replace("\n", " ").split())


def validate_documentation_search(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    diagnostics: list[dict[str, str]] = []
    try:
        config = _load_json(root / _CONFIG)
    except Exception as error:
        return {"status": "invalid", "diagnostics": [{"code": "SEARCH_CONFIG_INVALID", "message": str(error)}]}
    if not isinstance(config.get("default_limit"), int) or config["default_limit"] < 1:
        diagnostics.append({"code": "SEARCH_CONFIG_INVALID", "message": "default_limit must be a positive integer"})
    if not isinstance(config.get("minimum_token_length"), int) or config["minimum_token_length"] < 1:
        diagnostics.append({"code": "SEARCH_CONFIG_INVALID", "message": "minimum_token_length must be a positive integer"})
    site = validate_documentation_site(root)
    if site["status"] != "valid":
        diagnostics.append({"code": "SEARCH_SITE_INVALID", "message": "documentation site source model must be valid before search is built"})
    try:
        entries = route_entries(root)
        routes_path = root / "generated/documentation-site/routes.json"
        actual_routes = json.loads(routes_path.read_text(encoding="utf-8")) if routes_path.is_file() else None
        if actual_routes != entries:
            diagnostics.append({"code": "SEARCH_SITE_STALE", "message": "generated site route inventory differs from current registry-derived routes"})
        routes = [entry["route"] for entry in entries]
        if len(routes) != len(set(routes)):
            diagnostics.append({"code": "SEARCH_ROUTE_DUPLICATE", "message": "site routes are not unique"})
        for entry in entries:
            if not (root / entry["source"]).is_file():
                diagnostics.append({"code": "SEARCH_SOURCE_MISSING", "message": entry["source"]})
    except Exception as error:
        diagnostics.append({"code": "SEARCH_ROUTE_DISCOVERY_FAILED", "message": str(error)})
    return {"status": "invalid" if diagnostics else "valid", "diagnostics": diagnostics}


def render_search_index(root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    root = Path(root).resolve()
    validation = validate_documentation_search(root)
    if validation["status"] != "valid":
        raise ValueError("documentation search validation failed: " + "; ".join(item["code"] for item in validation["diagnostics"]))
    config = _load_json(root / _CONFIG)
    minimum = config["minimum_token_length"]
    records = []
    inputs = []
    for entry in route_entries(root):
        source = root / entry["source"]
        text = _search_text(source)
        counts = Counter(_tokens(text, minimum))
        title_counts = Counter(_tokens(entry["title"], minimum))
        records.append({
            "id": hashlib.sha256(entry["route"].encode("utf-8")).hexdigest()[:16],
            "route": entry["route"],
            "title": entry["title"],
            "family": entry["family"],
            "surface": entry["surface"],
            "source": entry["source"],
            "terms": dict(sorted(counts.items())),
            "title_terms": dict(sorted(title_counts.items())),
            "excerpt": text[:320],
        })
        payload = source.read_bytes()
        inputs.append({"path": entry["source"], "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)})
    index = {
        "schema_version": 2,
        "algorithm": "kis-static-search-v2",
        "contract": _SEARCH_CONTRACT,
        "minimum_token_length": minimum,
        "default_limit": config["default_limit"],
        "documents": sorted(records, key=lambda item: item["route"]),
    }
    files = {"search-index.json": (json.dumps(index, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")}
    for relative in (_CONFIG, _SEARCH_SOURCE, _SITE_SOURCE):
        payload = (root / relative).read_bytes()
        inputs.append({"path": relative, "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)})
    manifest = {
        "contract": {"name": "kis-documentation-search", "version": 2},
        "generator": {"name": "kis-mcp-doc", "algorithm": "documentation-search-v2"},
        "documents": len(records),
        "inputs": sorted(inputs, key=lambda item: item["path"]),
        "files": file_declarations(files),
        **bundle_manifest_fields(files),
    }
    return files, manifest


def build_documentation_search(root: Path, output: Path | None = None, *, replace: bool = False) -> dict[str, Any]:
    root = Path(root).resolve()
    output = Path(output) if output is not None else root / "generated/documentation-search"
    files, manifest = render_search_index(root)
    write_bundle(output, files, manifest, replace=replace)
    return manifest


def verify_documentation_search(root: Path, output: Path | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    output = Path(output) if output is not None else root / "generated/documentation-search"
    try:
        files, manifest = render_search_index(root)
    except Exception as error:
        return {"status": "invalid", "diagnostics": [{"code": "SEARCH_RENDER_FAILED", "message": str(error)}]}
    diagnostics = bundle_diagnostics(output, files, manifest, code_prefix="SEARCH")
    return {"status": "invalid" if diagnostics else "valid", "diagnostics": diagnostics}


def _rank_search_index(index: dict[str, Any], query: str, limit: int | None = None) -> list[dict[str, Any]]:
    requested = limit if limit is not None else index["default_limit"]
    if isinstance(requested, bool) or not isinstance(requested, int) or requested < 1:
        raise ValueError("search limit must be a positive integer")
    terms = _tokens(query, index["minimum_token_length"])
    if not terms:
        return []
    title_weight = index.get("contract", {}).get("title_weight", _SEARCH_CONTRACT["title_weight"])
    scored = []
    for document in index.get("documents", []):
        score = sum(document.get("terms", {}).get(term, 0) for term in terms)
        score += title_weight * sum(document.get("title_terms", {}).get(term, 0) for term in terms)
        matched = sum(1 for term in terms if document.get("terms", {}).get(term, 0) or document.get("title_terms", {}).get(term, 0))
        if score:
            scored.append((matched, score, document["route"], document))
    scored.sort(key=lambda item: (-item[0], -item[1], item[2]))
    return [{"route": item[3]["route"], "title": item[3]["title"], "family": item[3]["family"], "surface": item[3]["surface"], "excerpt": item[3]["excerpt"], "score": item[1]} for item in scored[:requested]]


def search_documentation(root: Path, query: str, *, limit: int | None = None) -> list[dict[str, Any]]:
    root = Path(root).resolve()
    index = _load_json(root / "generated/documentation-search/search-index.json")
    return _rank_search_index(index, query, limit)
