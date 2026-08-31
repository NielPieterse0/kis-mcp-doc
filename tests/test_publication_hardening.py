from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

from kis_mcp_doc.canonical import normative_keywords_statement
from kis_mcp_doc.documentation_reference import DocumentationReferenceRepository, build_documentation_reference_standard
from kis_mcp_doc.documentation_site import build_documentation_site
from kis_mcp_doc.governance import GovernanceRepository
from kis_mcp_doc.human_docs import build_human_docs_family
from kis_mcp_doc.publication_kernel import PublicationFamilyRegistry
from kis_mcp_doc.render import build_governance_spec
from kis_mcp_doc.work_management import WorkManagementRepository, build_work_management_spec

ROOT = Path(__file__).resolve().parents[1]


def test_human_readable_specifications_share_normative_reference_pattern(tmp_path: Path) -> None:
    expected = normative_keywords_statement()
    gov = tmp_path / "gov"
    build_governance_spec(GovernanceRepository(ROOT, ROOT / "prescriptives/mrd-specification"), ROOT / "publication/mrd-specification.json", gov)
    work = tmp_path / "work"; build_work_management_spec(WorkManagementRepository(ROOT), work)
    refs = tmp_path / "refs"; build_documentation_reference_standard(DocumentationReferenceRepository(ROOT), refs)
    for output in (gov, work, refs):
        text = (output / "001-specification.md").read_text(encoding="utf-8")
        assert expected in text
        assert "https://www.rfc-editor.org/info/bcp14" in text


def test_generated_human_docs_enforce_deterministic_heading_style(tmp_path: Path) -> None:
    registry = PublicationFamilyRegistry(ROOT)
    for family_id, kind in (("mrd-specification-docs", "mrd-specification"), ("work-management-docs", "work-management")):
        output = tmp_path / family_id
        build_human_docs_family(ROOT, registry.family(family_id), kind, output=output)
        for page in output.glob("*.md"):
            text = page.read_text(encoding="utf-8")
            headings = [line for line in text.splitlines() if line.startswith("## ")]
            assert all(not re.match(r"^## \d+\.", heading) for heading in headings)
            assert "Mrd" not in text


class _StructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.h1 = 0; self.levels = []; self.tables = []; self._table = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if re.fullmatch(r"h[1-6]", tag):
            level = int(tag[1]); self.levels.append(level); self.h1 += level == 1
        if tag == "table": self._table = {"caption": False, "scopes": []}
        elif tag == "caption" and self._table is not None: self._table["caption"] = True
        elif tag == "th" and self._table is not None: self._table["scopes"].append(dict(attrs).get("scope"))

    def handle_endtag(self, tag: str) -> None:
        if tag == "table" and self._table is not None:
            self.tables.append(self._table); self._table = None


def test_generated_site_structural_accessibility(tmp_path: Path) -> None:
    output = tmp_path / "site"; build_documentation_site(ROOT, output)
    for page in output.rglob("*.html"):
        parser = _StructureParser(); parser.feed(page.read_text(encoding="utf-8"))
        assert parser.h1 == 1, page
        assert all(current <= previous + 1 for previous, current in zip(parser.levels, parser.levels[1:])), page
        assert all(table["caption"] and all(scope == "col" for scope in table["scopes"]) for table in parser.tables), page
