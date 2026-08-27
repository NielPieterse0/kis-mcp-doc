from __future__ import annotations

import json
import shutil
from pathlib import Path

from kis_mcp_doc.documentation_site import _markdown_html, build_documentation_site, route_entries, validate_documentation_site, verify_documentation_site

ROOT = Path(__file__).parents[1]


def test_site_validation_and_registry_derived_routes_are_complete() -> None:
    assert validate_documentation_site(ROOT) == {"status": "valid", "diagnostics": []}
    entries = route_entries(ROOT)
    assert any(item["route"] == "/docs/governance/" for item in entries)
    assert any(item["route"] == "/docs/work-management/" for item in entries)
    assert any(item["route"] == "/specification/governance/" for item in entries)
    assert any(item["route"] == "/specification/work-management/" for item in entries)
    assert all(item["family"] for item in entries)
    assert len({item["route"] for item in entries}) == len(entries)


def test_site_build_has_entry_points_navigation_and_breadcrumbs(tmp_path: Path) -> None:
    output = tmp_path / "site"
    manifest = build_documentation_site(ROOT, output)
    assert manifest["contract"] == {"name": "kis-documentation-site", "version": 1}
    assert (output / "index.html").is_file()
    assert (output / "docs/governance/index.html").is_file()
    assert (output / "specification/governance/index.html").is_file()
    page = (output / "docs/governance/index.html").read_text(encoding="utf-8")
    assert "breadcrumbs" in page
    assert "rel=\"next\"" in page
    assert "/specification/governance/001-specification/" in page
    validation_page = (output / "specification/governance/010-validation-and-enforcement/index.html").read_text(encoding="utf-8")
    assert '<span id="rule-kis-mrd-val-005"></span>' in validation_page
    assert "<table>" in validation_page
    assert "| Mode | Meaning | Blocking |" not in validation_page
    css = (output / "assets/site.css").read_text(encoding="utf-8")
    assert "table{width:100%" in css
    assert "blockquote{" in css


def test_site_detects_broken_source_link_and_orphan(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", ".venv", ".work"))
    index = root / "generated/governance-docs/000-index.md"
    index.write_text(index.read_text(encoding="utf-8").replace("002-understand-authority.md", "missing.md"), encoding="utf-8")
    codes = {item["code"] for item in validate_documentation_site(root)["diagnostics"]}
    assert "SITE_BROKEN_SOURCE_LINK" in codes
    assert "SITE_ORPHAN_PAGE" in codes


def test_site_exact_verification_detects_tamper(tmp_path: Path) -> None:
    output = tmp_path / "site"
    build_documentation_site(ROOT, output)
    assert verify_documentation_site(ROOT, output)["status"] == "valid"
    (output / "index.html").write_text("tampered", encoding="utf-8")
    codes = {item["code"] for item in verify_documentation_site(ROOT, output)["diagnostics"]}
    assert "SITE_GENERATED_FILE_CONTENT_MISMATCH" in codes


def test_site_manifest_inputs_bind_registered_publications(tmp_path: Path) -> None:
    output = tmp_path / "site"
    manifest = build_documentation_site(ROOT, output)
    inputs = {item["path"] for item in manifest["inputs"]}
    assert "mrd/documentation/04-publication-family-registry.mrd.json" in inputs
    assert "generated/governance-docs/000-index.md" in inputs
    assert "generated/work-management-spec/000-index.md" in inputs


def test_markdown_renderer_preserves_expected_document_formatting() -> None:
    source = ROOT / "generated/governance-spec/010-validation-and-enforcement.md"
    markdown = """<span id=\"rule-example\"></span>\n\n## Modes\n\n| Mode | Meaning |\n|---|---|\n| <span id=\"fact-row\"></span>`schema` | **Structural** validation |\n\n- first item\n- second with [link](000-index.md)\n\n> Important note\n\nUse `inline code` and **bold** and *emphasis*.\n\n```json\n{\"ok\": true}\n```\n\n---\n"""
    rendered = _markdown_html(markdown, source, {}, ROOT, "/kis-mcp-doc")
    assert '<span id="rule-example"></span>' in rendered
    assert "<table>" in rendered and "<thead>" in rendered and "<tbody>" in rendered
    assert '<span id="fact-row"></span><code>schema</code>' in rendered
    assert "<strong>Structural</strong>" in rendered
    assert "<ul>" in rendered and "<li>first item</li>" in rendered
    assert "<blockquote><p>Important note</p></blockquote>" in rendered
    assert "Use <code>inline code</code> and <strong>bold</strong> and <em>emphasis</em>." in rendered
    assert '<pre><code class="language-json">{&quot;ok&quot;: true}</code></pre>' in rendered
    assert "<hr>" in rendered
