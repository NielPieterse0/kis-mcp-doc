from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path
from typing import Any

from .documentation_search import verify_documentation_search
from .documentation_site import verify_documentation_site
from .publication_kernel import bundle_diagnostics, bundle_manifest_fields, file_declarations, write_bundle

_CONFIG = "publication/documentation-release.json"
_SOURCE = "src/kis_mcp_doc/documentation_release.py"
_SITE = "generated/documentation-site"
_SEARCH = "generated/documentation-search"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _decl(path: Path, root: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}

def _site_archive(root: Path) -> bytes:
    output = io.BytesIO()
    site = root / _SITE
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        paths = sorted((p for p in site.rglob("*") if p.is_file()), key=lambda p: p.relative_to(site).as_posix())
        for path in paths:
            relative = path.relative_to(site).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return output.getvalue()


def validate_documentation_release(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    diagnostics: list[dict[str, str]] = []
    try:
        config = _load_json(root / _CONFIG)
    except Exception as error:
        return {"status": "invalid", "diagnostics": [{"code": "RELEASE_CONFIG_INVALID", "message": str(error)}]}
    if config.get("hosting") != "github-pages":
        diagnostics.append({"code": "RELEASE_HOSTING_INVALID", "message": "hosting must be github-pages"})
    if config.get("site_output") != _SITE:
        diagnostics.append({"code": "RELEASE_SITE_OUTPUT_INVALID", "message": f"site_output must be {_SITE}"})
    if verify_documentation_site(root)["status"] != "valid":
        diagnostics.append({"code": "RELEASE_SITE_STALE", "message": "documentation site must be current before release packaging"})
    if verify_documentation_search(root)["status"] != "valid":
        diagnostics.append({"code": "RELEASE_SEARCH_STALE", "message": "documentation search must be current before release packaging"})
    return {"status": "invalid" if diagnostics else "valid", "diagnostics": diagnostics}

def render_documentation_release(root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    root = Path(root).resolve()
    validation = validate_documentation_release(root)
    if validation["status"] != "valid":
        raise ValueError("documentation release validation failed: " + "; ".join(item["code"] for item in validation["diagnostics"]))
    config = _load_json(root / _CONFIG)
    site_manifest = _load_json(root / _SITE / "manifest.json")
    search_manifest = _load_json(root / _SEARCH / "manifest.json")
    archive = _site_archive(root)
    metadata = {
        "schema_version": 1,
        "hosting": config["hosting"],
        "site_output": config["site_output"],
        "base_path": config["base_path"],
        "site_bundle_sha256": site_manifest["bundle_sha256"],
        "search_bundle_sha256": search_manifest["bundle_sha256"],
        "archive_sha256": hashlib.sha256(archive).hexdigest(),
        "archive_bytes": len(archive),
    }
    files = {
        "documentation-site.zip": archive,
        "release-metadata.json": (json.dumps(metadata, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"),
    }
    inputs = [_decl(root / relative, root) for relative in (_CONFIG, _SOURCE, f"{_SITE}/manifest.json", f"{_SEARCH}/manifest.json")]
    manifest = {
        "contract": {"name": "kis-documentation-release", "version": 1},
        "generator": {"name": "kis-mcp-doc", "algorithm": "documentation-release-v1"},
        "inputs": sorted(inputs, key=lambda item: item["path"]),
        "files": file_declarations(files),
        **bundle_manifest_fields(files),
    }
    return files, manifest

def build_documentation_release(root: Path, output: Path | None = None, *, replace: bool = False) -> dict[str, Any]:
    root = Path(root).resolve()
    output = Path(output) if output is not None else root / "generated/documentation-release"
    files, manifest = render_documentation_release(root)
    write_bundle(output, files, manifest, replace=replace)
    return manifest


def verify_documentation_release(root: Path, output: Path | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    output = Path(output) if output is not None else root / "generated/documentation-release"
    try:
        files, manifest = render_documentation_release(root)
    except Exception as error:
        return {"status": "invalid", "diagnostics": [{"code": "RELEASE_RENDER_FAILED", "message": str(error)}]}
    diagnostics = bundle_diagnostics(output, files, manifest, code_prefix="RELEASE")
    return {"status": "invalid" if diagnostics else "valid", "diagnostics": diagnostics}
