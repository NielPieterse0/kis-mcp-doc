from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

from kis_mcp_doc.cli import main
from kis_mcp_doc.documentation_release import build_documentation_release, validate_documentation_release, verify_documentation_release
from kis_mcp_doc.documentation_site import build_documentation_site

ROOT = Path(__file__).parents[1]


def test_release_validation_and_archive_are_deterministic(tmp_path: Path) -> None:
    assert validate_documentation_release(ROOT) == {"status": "valid", "diagnostics": []}
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_manifest = build_documentation_release(ROOT, first)
    second_manifest = build_documentation_release(ROOT, second)
    assert first_manifest == second_manifest
    assert (first / "documentation-site.zip").read_bytes() == (second / "documentation-site.zip").read_bytes()
    with zipfile.ZipFile(first / "documentation-site.zip") as archive:
        names = archive.namelist()
        assert "index.html" in names
        assert "search/index.html" in names
        assert "docs/repository/index.html" in names
        assert not any(name.startswith("docs/work-management/") for name in names)
        assert not any(name.startswith("specification/work-management/") for name in names)
        assert not any(name.startswith("reference/work-management-") for name in names)
        assert names == sorted(names)


def test_release_metadata_binds_site_and_search_bundles(tmp_path: Path) -> None:
    output = tmp_path / "release"
    build_documentation_release(ROOT, output)
    metadata = json.loads((output / "release-metadata.json").read_text(encoding="utf-8"))
    site = json.loads((ROOT / "generated/documentation-site/manifest.json").read_text(encoding="utf-8"))
    search = json.loads((ROOT / "generated/documentation-search/manifest.json").read_text(encoding="utf-8"))
    assert metadata["site_bundle_sha256"] == site["bundle_sha256"]
    assert metadata["search_bundle_sha256"] == search["bundle_sha256"]
    assert metadata["base_path"] == "/kis-mcp-doc"

def test_release_verification_detects_tamper(tmp_path: Path) -> None:
    output = tmp_path / "release"
    build_documentation_release(ROOT, output)
    assert verify_documentation_release(ROOT, output)["status"] == "valid"
    (output / "release-metadata.json").write_text("{}\n", encoding="utf-8")
    codes = {item["code"] for item in verify_documentation_release(ROOT, output)["diagnostics"]}
    assert "RELEASE_GENERATED_FILE_CONTENT_MISMATCH" in codes


def test_release_rejects_stale_site(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", ".venv", ".work"))
    (root / "generated/documentation-site/index.html").write_text("tampered", encoding="utf-8")
    codes = {item["code"] for item in validate_documentation_release(root)["diagnostics"]}
    assert "RELEASE_SITE_STALE" in codes


def test_site_uses_github_pages_base_path(tmp_path: Path) -> None:
    output = tmp_path / "site"
    build_documentation_site(ROOT, output)
    home = (output / "index.html").read_text(encoding="utf-8")
    docs = (output / "docs/governance/index.html").read_text(encoding="utf-8")
    script = (output / "assets/search.js").read_text(encoding="utf-8")
    assert 'href="/kis-mcp-doc/docs/"' in home
    assert 'href="/kis-mcp-doc/specification/governance/001-specification/"' in docs
    assert 'const B="/kis-mcp-doc"' in script


def test_release_cli_and_workflows_are_wired(tmp_path: Path) -> None:
    output = tmp_path / "release"
    assert main(["--root", str(ROOT), "release-validate"]) == 0
    assert main(["--root", str(ROOT), "release-build", "--output", str(output)]) == 0
    assert main(["--root", str(ROOT), "release-check-generated", "--output", str(output)]) == 0
    pages = (ROOT / ".github/workflows/documentation-pages.yml").read_text(encoding="utf-8")
    release = (ROOT / ".github/workflows/documentation-release.yml").read_text(encoding="utf-8")
    canonical_ci = (ROOT / ".github/workflows/work-management.yml").read_text(encoding="utf-8")
    verify_script = (ROOT / "scripts/verify.ps1").read_text(encoding="utf-8")
    assert "actions/upload-pages-artifact@fc324d3547104276b827a68afc52ff2a11cc49c9" in pages
    assert "actions/deploy-pages@cd2ce8fcbc39b97be8ca5fce6e763baed58fa128" in pages
    assert "gh release upload" in release
    assert "pwsh -NoProfile -File scripts/verify.ps1 -SkipDependencySync" in canonical_ci
    for command in (
        "publications-check-generated",
        "search-check-generated",
        "site-check-generated",
        "release-check-generated",
    ):
        assert command in verify_script
