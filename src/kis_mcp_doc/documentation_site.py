from __future__ import annotations

import hashlib
import html
import json
import math
import re
import textwrap
from pathlib import Path
from typing import Any

from .canonical import canonical_hash
from .publication_kernel import PublicationFamilyRegistry, bundle_diagnostics, bundle_manifest_fields, file_declarations, write_bundle

_CONFIG = "publication/documentation-site.json"
_REGISTRY = "mrd/documentation/04-publication-family-registry.mrd.json"
_SITE_SOURCE = "src/kis_mcp_doc/documentation_site.py"
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_ORDERED_LIST_RE = re.compile(r"^\d+\.\s+(.+)$")
_TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
_SAFE_ANCHOR_RE = re.compile(r'^<(span|div) id="([A-Za-z0-9_.:-]+)"\s*(?:></\1>|/>)$')
_SAFE_INLINE_ANCHOR_RE = re.compile(r'<span id="([A-Za-z0-9_.:-]+)"></span>')
_CODE_SPAN_RE = re.compile(r"`([^`]+)`")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _surface(family: dict[str, Any]) -> str:
    return "docs" if family.get("output_classes") == ["human_documentation"] else "specification"


def _domain(family_id: str) -> str:
    for suffix in ("-docs", "-spec"):
        if family_id.endswith(suffix):
            return family_id[:-len(suffix)]
    return family_id


def _source_key(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _title_from_markdown(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _heading_anchor(value: str) -> str:
    raw = "".join(character.lower() if character.isalnum() else "-" for character in value)
    return "-".join(part for part in raw.split("-") if part)


def _fragment_ids(text: str) -> set[str]:
    fragments = set(_SAFE_INLINE_ANCHOR_RE.findall(text))
    for line in text.splitlines():
        safe = _SAFE_ANCHOR_RE.match(line.strip())
        if safe:
            fragments.add(safe.group(2))
        heading = _HEADING_RE.match(line)
        if heading:
            fragments.add(_heading_anchor(re.sub(r"[`*_]", "", heading.group(2))))
    return fragments


def _route_for(family: dict[str, Any], relative: str) -> str:
    path = Path(relative)
    if path.suffix.lower() == ".md":
        base = f"/{_surface(family)}/{_domain(family['id'])}"
        return base + "/" if path.name == "000-index.md" else f"{base}/{path.stem}/"
    base = f"/reference/{family['id']}"
    stem = path.with_suffix("").as_posix()
    return f"{base}/{stem}/"


def _source_files(root: Path, family: dict[str, Any]) -> list[Path]:
    output = root / family["output"]
    return sorted(
        path
        for path in output.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".md", ".json"}
        and path.name != "specification.md"
    )


def route_entries(root: Path) -> list[dict[str, str]]:
    registry = PublicationFamilyRegistry(root)
    if registry.validate()["status"] != "valid":
        raise ValueError("publication family registry is invalid")
    entries: list[dict[str, str]] = []
    for family in registry.load()["content"]["families"]:
        output = root / family["output"]
        for path in _source_files(root, family):
            relative = path.relative_to(output).as_posix()
            text = path.read_text(encoding="utf-8")
            title = _title_from_markdown(text, path.stem) if path.suffix.lower() == ".md" else path.stem.replace("-", " ").title()
            entries.append({
                "route": _route_for(family, relative),
                "source": _source_key(path, root),
                "family": family["id"],
                "surface": _surface(family) if path.suffix.lower() == ".md" else "reference",
                "title": title,
            })
    return entries


def _resolve_link(root: Path, source: Path, target: str) -> Path | None:
    if target.startswith("#"):
        return source.resolve()
    target = target.split("#", 1)[0]
    if not target or "://" in target or target.startswith("mailto:"):
        return None
    return (source.parent / target).resolve()


def _markdown_graph(root: Path, family: dict[str, Any]) -> tuple[set[str], dict[str, set[str]], list[dict[str, str]]]:
    output = (root / family["output"]).resolve()
    pages = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*.md")
        if path.name != "specification.md"
    }
    graph = {page: set() for page in pages}
    diagnostics: list[dict[str, str]] = []
    for page in sorted(pages):
        source = output / page
        text = source.read_text(encoding="utf-8")
        levels = [len(match.group(1)) for line in text.splitlines() if (match := _HEADING_RE.match(line))]
        if levels.count(1) != 1 or any(current > previous + 1 for previous, current in zip(levels, levels[1:])):
            diagnostics.append({"code": "SITE_HEADING_HIERARCHY_INVALID", "message": _source_key(source, root)})
        for _, target in _LINK_RE.findall(text):
            resolved = _resolve_link(root, source, target)
            if resolved is None:
                continue
            if not resolved.is_file():
                diagnostics.append({"code": "SITE_BROKEN_SOURCE_LINK", "message": f"{_source_key(source, root)} -> {target}"})
                continue
            if "#" in target:
                fragment = target.split("#", 1)[1]
                if fragment and resolved.suffix.lower() == ".md":
                    target_text = resolved.read_text(encoding="utf-8")
                    if fragment not in _fragment_ids(target_text):
                        diagnostics.append({"code": "SITE_BROKEN_SOURCE_FRAGMENT", "message": f"{_source_key(source, root)} -> {target}"})
            try:
                linked = resolved.relative_to(output).as_posix()
            except ValueError:
                continue
            if linked in pages:
                graph[page].add(linked)
    return pages, graph, diagnostics


def validate_documentation_site(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    diagnostics: list[dict[str, str]] = []
    try:
        config = _load_json(root / _CONFIG)
    except Exception as error:
        return {"status": "invalid", "diagnostics": [{"code": "SITE_CONFIG_INVALID", "message": str(error)}]}
    base_path = config.get("base_path", "")
    if not isinstance(base_path, str) or (base_path and (not base_path.startswith("/") or base_path.endswith("/") or ".." in base_path)):
        diagnostics.append({"code": "SITE_BASE_PATH_INVALID", "message": "base_path must be empty or a normalized absolute path prefix without a trailing slash"})
    for key in ("title", "version", "status"):
        if not isinstance(config.get(key), str) or not config[key].strip():
            diagnostics.append({"code": "SITE_CONFIG_INVALID", "message": f"missing non-empty {key}"})
    registry = PublicationFamilyRegistry(root)
    registry_result = registry.validate()
    diagnostics.extend(registry_result.get("diagnostics", []))
    if registry_result["status"] == "valid":
        entries = route_entries(root)
        routes = [entry["route"] for entry in entries]
        if len(routes) != len(set(routes)):
            diagnostics.append({"code": "SITE_DUPLICATE_ROUTE", "message": "multiple governed sources resolve to the same site route"})
        for family in registry.load()["content"]["families"]:
            pages, graph, link_diags = _markdown_graph(root, family)
            diagnostics.extend(link_diags)
            if pages:
                start = "000-index.md"
                if start not in pages:
                    diagnostics.append({"code": "SITE_FAMILY_INDEX_MISSING", "message": f"{family['id']} has no 000-index.md"})
                    continue
                seen, pending = set(), [start]
                while pending:
                    page = pending.pop()
                    if page in seen:
                        continue
                    seen.add(page)
                    pending.extend(sorted(graph.get(page, set()) - seen))
                for page in sorted(pages - seen):
                    diagnostics.append({"code": "SITE_ORPHAN_PAGE", "message": f"{family['id']}:{page}"})
    return {"status": "invalid" if diagnostics else "valid", "diagnostics": diagnostics}


def _public_url(route: str, base_path: str) -> str:
    return f"{base_path}{route}" if base_path else route


def _rewrite_link(source: Path, target: str, source_to_route: dict[str, str], root: Path, base_path: str) -> str:
    resolved = _resolve_link(root, source, target)
    if resolved is None:
        return target
    key = _source_key(resolved, root) if resolved.exists() else ""
    route = source_to_route.get(key)
    fragment = "#" + target.split("#", 1)[1] if "#" in target else ""
    return _public_url(route, base_path) + fragment if route else target


def _inline_html(text: str, source: Path, source_to_route: dict[str, str], root: Path, base_path: str) -> str:
    placeholders: dict[str, str] = {}

    def stash(value: str) -> str:
        token = f"\x00{len(placeholders)}\x00"
        placeholders[token] = value
        return token

    def code_replace(match: re.Match[str]) -> str:
        return stash(f"<code>{html.escape(match.group(1))}</code>")

    protected = _SAFE_INLINE_ANCHOR_RE.sub(lambda match: stash(f'<span id="{html.escape(match.group(1), quote=True)}"></span>'), text)
    protected = _CODE_SPAN_RE.sub(code_replace, protected)
    links: list[tuple[str, str, str]] = []

    def link_replace(match: re.Match[str]) -> str:
        token = f"\x01{len(links)}\x01"
        links.append((token, match.group(1), match.group(2)))
        return token

    protected = _LINK_RE.sub(link_replace, protected)
    rendered = html.escape(protected)
    rendered = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", rendered)
    for token, label, target in links:
        href = html.escape(_rewrite_link(source, target, source_to_route, root, base_path), quote=True)
        rendered = rendered.replace(html.escape(token), f'<a href="{href}">{html.escape(label)}</a>')
    for token, value in placeholders.items():
        rendered = rendered.replace(html.escape(token), value)
    return rendered


def _table_cells(raw: str) -> list[str]:
    value = raw.strip().strip("|")
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", value)]


def _mermaid_flowchart_svg(source: str) -> str:
    lines = [line.strip() for line in source.splitlines() if line.strip()]
    if not lines:
        raise ValueError("unsupported Mermaid diagram: empty source")
    header = re.fullmatch(r"flowchart\s+(LR|TD)", lines[0])
    if not header:
        raise ValueError("unsupported Mermaid diagram: only flowchart LR/TD is supported")

    direction = header.group(1)
    nodes: dict[str, str] = {}
    groups: dict[str, list[str]] = {}
    group_labels: dict[str, str] = {}
    group_order: list[str] = []
    node_group: dict[str, str | None] = {}
    edges: list[tuple[str, str, str | None]] = []
    current_group: str | None = None
    node_re = re.compile(r'^([A-Za-z0-9_]+)\["(.*)"\]$')
    group_re = re.compile(r'^subgraph\s+([A-Za-z0-9_]+)\["(.*)"\]$')
    edge_re = re.compile(r'^([A-Za-z0-9_]+)(?:\["([^"]*)"\])?\s*-->\s*(?:\|"([^"]*)"\|\s*)?([A-Za-z0-9_]+)(?:\["([^"]*)"\])?$')

    for line in lines[1:]:
        if line == "end":
            current_group = None
            continue
        group_match = group_re.fullmatch(line)
        if group_match:
            current_group = group_match.group(1)
            if current_group in groups:
                raise ValueError(f"unsupported Mermaid diagram: duplicate subgraph {current_group}")
            groups[current_group] = []
            group_labels[current_group] = group_match.group(2)
            group_order.append(current_group)
            continue
        node_match = node_re.fullmatch(line)
        if node_match:
            node_id, label = node_match.groups()
            nodes[node_id] = label
            node_group[node_id] = current_group
            if current_group is not None:
                groups[current_group].append(node_id)
            continue
        edge_match = edge_re.fullmatch(line)
        if edge_match:
            source_id, source_label, edge_label, target_id, target_label = edge_match.groups()
            for node_id, label in ((source_id, source_label), (target_id, target_label)):
                if label is not None:
                    nodes[node_id] = label
                    if node_id not in node_group:
                        node_group[node_id] = current_group
                        if current_group is not None:
                            groups[current_group].append(node_id)
            edges.append((source_id, target_id, edge_label))
            continue
        raise ValueError(f"unsupported Mermaid diagram syntax: {line}")

    for source_id, target_id, _ in edges:
        for node_id in (source_id, target_id):
            if node_id not in nodes:
                nodes[node_id] = node_id
                node_group[node_id] = None

    ungrouped = [node_id for node_id in nodes if node_group.get(node_id) is None]
    sections: list[tuple[str | None, str | None, list[str]]] = []
    if ungrouped:
        sections.append((None, None, ungrouped))
    sections.extend((group_id, group_labels[group_id], groups[group_id]) for group_id in group_order)

    wrapped_labels = {
        node_id: textwrap.wrap(label, width=32, break_long_words=True, break_on_hyphens=False) or [label]
        for node_id, label in nodes.items()
    }
    node_width = 280
    line_height = 18
    max_label_lines = max((len(lines) for lines in wrapped_labels.values()), default=1)
    node_height = 30 + line_height * max_label_lines
    gap_x = 56
    gap_y = 48
    margin = 44
    columns = 4 if direction == "LR" else 3
    positions: dict[str, tuple[int, int]] = {}
    section_boxes: list[tuple[str, int, int, int, int]] = []
    y_cursor = margin
    max_width = 0

    for group_id, label, section_nodes in sections:
        if not section_nodes:
            continue
        section_columns = min(columns, max(1, len(section_nodes)))
        rows = (len(section_nodes) + section_columns - 1) // section_columns
        header_height = 38 if group_id is not None else 0
        section_width = section_columns * node_width + (section_columns - 1) * gap_x
        section_height = header_height + rows * node_height + max(0, rows - 1) * gap_y
        x_origin = margin
        if group_id is not None:
            section_boxes.append((label or group_id, x_origin - 18, y_cursor - 14, section_width + 36, section_height + 28))
        for idx, node_id in enumerate(section_nodes):
            row = idx // section_columns
            col = idx % section_columns
            x = x_origin + col * (node_width + gap_x)
            y = y_cursor + header_height + row * (node_height + gap_y)
            positions[node_id] = (x, y)
        y_cursor += section_height + gap_y + (18 if group_id is not None else 0)
        max_width = max(max_width, section_width + margin * 2)

    def edge_boundary(cx: float, cy: float, toward_x: float, toward_y: float) -> tuple[float, float]:
        dx = toward_x - cx
        dy = toward_y - cy
        if dx == 0 and dy == 0:
            return cx, cy
        scale_x = math.inf if dx == 0 else (node_width / 2) / abs(dx)
        scale_y = math.inf if dy == 0 else (node_height / 2) / abs(dy)
        scale = min(scale_x, scale_y)
        return cx + dx * scale, cy + dy * scale

    height = max(y_cursor + margin - gap_y, 180)
    width = max(max_width, 460)
    diagram_key = hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]
    title_id = f"flowchart-{diagram_key}-title"
    desc_id = f"flowchart-{diagram_key}-desc"
    arrow_id = f"arrow-{diagram_key}"
    node_summary = "; ".join(nodes.values())
    relationship_summary = "; ".join(
        f"{nodes[source_id]} to {nodes[target_id]}" + (f" ({edge_label})" if edge_label else "")
        for source_id, target_id, edge_label in edges
    )
    description = f"Nodes: {node_summary}. Directed relationships: {relationship_summary}."
    parts = [
        f'<figure class="mermaid-diagram"><svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="{title_id} {desc_id}">',
        f'<title id="{title_id}">Flowchart diagram</title><desc id="{desc_id}">{html.escape(description)}</desc>',
        f'<defs><marker id="{arrow_id}" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#57606a"/></marker></defs>',
    ]
    for label, x, y, box_width, box_height in section_boxes:
        parts.append(f'<rect x="{x}" y="{y}" width="{box_width}" height="{box_height}" rx="8" fill="none" stroke="#8c959f" stroke-dasharray="5 4"/>')
        parts.append(f'<text x="{x + 12}" y="{y + 24}" font-family="system-ui,sans-serif" font-size="14" font-weight="600">{html.escape(label)}</text>')
    for source_id, target_id, edge_label in edges:
        if source_id not in positions or target_id not in positions:
            raise ValueError("unsupported Mermaid diagram: edge references an unpositioned node")
        sx, sy = positions[source_id]
        tx, ty = positions[target_id]
        scx, scy = sx + node_width / 2, sy + node_height / 2
        tcx, tcy = tx + node_width / 2, ty + node_height / 2
        x1, y1 = edge_boundary(scx, scy, tcx, tcy)
        x2, y2 = edge_boundary(tcx, tcy, scx, scy)
        parts.append(f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="#57606a" stroke-width="1.5" marker-end="url(#{arrow_id})"/>')
        if edge_label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - 7
            parts.append(f'<text x="{mx:g}" y="{my:g}" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="#24292f">{html.escape(edge_label)}</text>')
    for node_id, label in nodes.items():
        x, y = positions[node_id]
        parts.append(f'<rect x="{x}" y="{y}" width="{node_width}" height="{node_height}" rx="6" fill="#f6f8fa" stroke="#57606a"/>')
        lines = wrapped_labels[node_id]
        first_y = y + node_height / 2 - ((len(lines) - 1) * line_height) / 2 + 5
        parts.append(f'<text x="{x + node_width / 2:g}" y="{first_y:g}" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#24292f">')
        for line_index, line in enumerate(lines):
            dy = "0" if line_index == 0 else str(line_height)
            parts.append(f'<tspan x="{x + node_width / 2:g}" dy="{dy}">{html.escape(line)}</tspan>')
        parts.append('</text>')
    parts.append('</svg><figcaption>Flowchart rendered deterministically from the governed Mermaid source.</figcaption></figure>')
    return "".join(parts)


def _markdown_html(text: str, source: Path, source_to_route: dict[str, str], root: Path, base_path: str) -> str:
    source_lines = text.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    list_kind: str | None = None
    last_heading = "Table"
    index = 0

    def flush_paragraph() -> None:
        if paragraph:
            output.append(f"<p>{_inline_html(' '.join(part.strip() for part in paragraph), source, source_to_route, root, base_path)}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            output.append(f"</{list_kind}>")
            list_kind = None

    while index < len(source_lines):
        raw = source_lines[index]
        stripped = raw.strip()
        if stripped.startswith("<!--"):
            flush_paragraph()
            close_list()
            while index < len(source_lines) and "-->" not in source_lines[index]:
                index += 1
            index += 1
            continue
        if stripped.startswith("```"):
            flush_paragraph()
            close_list()
            language = stripped[3:].strip()
            code_lines: list[str] = []
            index += 1
            while index < len(source_lines) and not source_lines[index].strip().startswith("```"):
                code_lines.append(source_lines[index])
                index += 1
            if language.lower() == "mermaid":
                output.append(_mermaid_flowchart_svg(chr(10).join(code_lines)))
            else:
                class_name = f' class="language-{html.escape(language, quote=True)}"' if language else ""
                output.append(f"<pre><code{class_name}>{html.escape(chr(10).join(code_lines))}</code></pre>")
            index += 1
            continue
        safe_anchor = _SAFE_ANCHOR_RE.match(stripped)
        if safe_anchor:
            flush_paragraph()
            close_list()
            tag, identifier = safe_anchor.groups()
            output.append(f'<{tag} id="{html.escape(identifier, quote=True)}"></{tag}>')
            index += 1
            continue
        heading = _HEADING_RE.match(raw)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            last_heading = re.sub(r"[`*_]", "", heading.group(2)).strip()
            identifier = _heading_anchor(last_heading)
            output.append(f'<h{level} id="{html.escape(identifier, quote=True)}">{_inline_html(heading.group(2), source, source_to_route, root, base_path)}</h{level}>')
            index += 1
            continue
        if stripped in {"---", "***", "___"}:
            flush_paragraph()
            close_list()
            output.append("<hr>")
            index += 1
            continue
        if stripped.startswith("|") and index + 1 < len(source_lines) and _TABLE_SEPARATOR_RE.match(source_lines[index + 1]):
            flush_paragraph()
            close_list()
            headers = _table_cells(raw)
            index += 2
            rows: list[list[str]] = []
            while index < len(source_lines) and source_lines[index].strip().startswith("|"):
                rows.append(_table_cells(source_lines[index]))
                index += 1
            caption = html.escape(last_heading)
            output.append("<table><caption>" + caption + "</caption><thead><tr>" + "".join(f'<th scope="col">{_inline_html(cell, source, source_to_route, root, base_path)}</th>' for cell in headers) + "</tr></thead><tbody>")
            for row in rows:
                output.append("<tr>" + "".join(f"<td>{_inline_html(cell, source, source_to_route, root, base_path)}</td>" for cell in row) + "</tr>")
            output.append("</tbody></table>")
            continue
        unordered = stripped.startswith("- ") or stripped.startswith("* ")
        ordered = _ORDERED_LIST_RE.match(stripped)
        if unordered or ordered:
            flush_paragraph()
            kind = "ul" if unordered else "ol"
            if list_kind != kind:
                close_list()
                output.append(f"<{kind}>")
                list_kind = kind
            item = stripped[2:] if unordered else ordered.group(1)
            output.append(f"<li>{_inline_html(item, source, source_to_route, root, base_path)}</li>")
            index += 1
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            close_list()
            quote_lines: list[str] = []
            while index < len(source_lines) and source_lines[index].strip().startswith(">"):
                quote_lines.append(source_lines[index].strip()[1:].strip())
                index += 1
            output.append(f"<blockquote><p>{_inline_html(' '.join(quote_lines), source, source_to_route, root, base_path)}</p></blockquote>")
            continue
        if not stripped:
            flush_paragraph()
            close_list()
            index += 1
            continue
        close_list()
        paragraph.append(raw)
        index += 1
    flush_paragraph()
    close_list()
    return "\n".join(output)


def _page(title: str, body: str, breadcrumb: str, base_path: str, prev_next: str = "") -> bytes:
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{html.escape(title)}</title><link rel=\"stylesheet\" href=\"{_public_url('/assets/site.css', base_path)}\"></head><body>"
            f"<header><a href=\"{_public_url('/', base_path)}\">KIS Documentation</a><nav><a href=\"{_public_url('/docs/', base_path)}\">Docs</a> <a href=\"{_public_url('/specification/', base_path)}\">Specification</a> <a href=\"{_public_url('/reference/', base_path)}\">Reference</a> <a href=\"{_public_url('/search/', base_path)}\">Search</a></nav></header>"
            f"<main><div class=\"breadcrumbs\">{breadcrumb}</div>{body}{prev_next}</main></body></html>\n").encode("utf-8")


def _route_file(route: str) -> str:
    return "index.html" if route == "/" else route.strip("/") + "/index.html"


def _publication_meta(root: Path, family: dict[str, Any]) -> str:
    config = _load_json(root / family["publication_config"])
    version = html.escape(str(config.get("version", "unknown")))
    status = html.escape(str(config.get("status", "unknown")))
    owner = html.escape(str(family.get("semantic_owner", "unknown")))
    return (f'<aside class="publication-meta"><strong>Version:</strong> {version}. '
            f'<strong>Status:</strong> {status}. <strong>Authority:</strong> generated projection of '
            f'<code>{owner}</code>; canonical sources remain authoritative.</aside>')


def _browser_search_script(base_path: str) -> str:
    return (
        "const B=" + json.dumps(base_path) + ";\n"
        "const TOKEN_RE=/[A-Za-z0-9][A-Za-z0-9_-]*/g;\n"
        "function kisRankSearch(i,q,limit=i.default_limit){\n"
        " if(!Number.isInteger(limit)||limit<1)throw new Error('search limit must be a positive integer');\n"
        " const ts=(q.match(TOKEN_RE)||[]).map(t=>t.toLowerCase()).filter(t=>t.length>=i.minimum_token_length);\n"
        " const weight=i.contract.title_weight;\n"
        " return i.documents.map(d=>{const score=ts.reduce((s,t)=>s+(d.terms[t]||0)+weight*(d.title_terms[t]||0),0);const matched_terms=ts.reduce((n,t)=>n+((d.terms[t]||d.title_terms[t])?1:0),0);return {score,matched_terms,d};})\n"
        "  .filter(x=>x.score>0).sort((a,b)=>b.matched_terms-a.matched_terms||b.score-a.score||(a.d.route<b.d.route?-1:a.d.route>b.d.route?1:0)).slice(0,limit);\n"
        "}\n"
        "globalThis.kisRankSearch=kisRankSearch;\n"
        "if(typeof document!=='undefined'&&typeof fetch!=='undefined'){fetch(B+'/search-index.json').then(r=>r.json()).then(i=>{\n"
        " const f=document.querySelector('#search-form'),q=document.querySelector('#q'),o=document.querySelector('#results');\n"
        " f.addEventListener('submit',e=>{e.preventDefault();const rs=kisRankSearch(i,q.value);o.replaceChildren();\n"
        "  for(const x of rs){const li=document.createElement('li'),a=document.createElement('a');a.href=B+x.d.route;a.textContent=x.d.title;li.append(a,document.createTextNode(' - '+x.d.family));o.appendChild(li);}\n"
        " });\n"
        "});}\n"
    )


def render_documentation_site(root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    root = Path(root).resolve()
    validation = validate_documentation_site(root)
    if validation["status"] != "valid":
        raise ValueError("documentation site validation failed: " + "; ".join(item["code"] for item in validation["diagnostics"]))
    config = _load_json(root / _CONFIG)
    base_path = config.get("base_path", "")
    registry = PublicationFamilyRegistry(root).load()
    entries = route_entries(root)
    source_to_route = {entry["source"]: entry["route"] for entry in entries}
    files: dict[str, bytes] = {}
    families = registry["content"]["families"]
    family_entries = {family["id"]: [entry for entry in entries if entry["family"] == family["id"] and entry["surface"] != "reference"] for family in families}
    for family in families:
        ordered = family_entries[family["id"]]
        for index, entry in enumerate(ordered):
            source = root / entry["source"]
            body = _publication_meta(root, family) + _markdown_html(source.read_text(encoding="utf-8"), source, source_to_route, root, base_path)
            prev_link = f'<a rel="prev" href="{_public_url(ordered[index - 1]["route"], base_path)}">Previous</a>' if index else ""
            next_link = f'<a rel="next" href="{_public_url(ordered[index + 1]["route"], base_path)}">Next</a>' if index + 1 < len(ordered) else ""
            surface_url = _public_url(f"/{entry['surface']}/", base_path)
            crumb = f'<a href="{_public_url("/", base_path)}">Home</a> / <a href="{surface_url}">{entry["surface"].title()}</a> / {html.escape(family["title"])}'
            files[_route_file(entry["route"])] = _page(entry["title"], body, crumb, base_path, f'<nav class="prev-next">{prev_link} {next_link}</nav>')
    family_by_id = {family["id"]: family for family in families}
    for entry in [item for item in entries if item["surface"] == "reference"]:
        source = root / entry["source"]
        body = _publication_meta(root, family_by_id[entry["family"]]) + f"<h1>{html.escape(entry['title'])}</h1><pre>{html.escape(source.read_text(encoding='utf-8'))}</pre>"
        crumb = f'<a href="{_public_url("/", base_path)}">Home</a> / <a href="{_public_url("/reference/", base_path)}">Reference</a> / {html.escape(entry["family"])}'
        files[_route_file(entry["route"])] = _page(entry["title"], body, crumb, base_path)
    for surface in ("docs", "specification", "reference"):
        links = [entry for entry in entries if entry["surface"] == surface and (entry["source"].endswith("000-index.md") or surface == "reference")]
        if surface == "reference":
            first_by_family = {}
            for entry in links:
                first_by_family.setdefault(entry["family"], entry)
            links = list(first_by_family.values())
        body = f"<h1>{surface.title()}</h1><ul>" + "".join(f'<li><a href="{_public_url(item["route"], base_path)}">{html.escape(item["title"])}</a></li>' for item in links) + "</ul>"
        files[_route_file(f"/{surface}/")] = _page(surface.title(), body, f'<a href="{_public_url("/", base_path)}">Home</a>', base_path)
    home_sections = []
    for surface in ("docs", "specification", "reference", "search"):
        href = _public_url(f"/{surface}/", base_path)
        home_sections.append(f'<section><h2><a href="{href}">{surface.title()}</a></h2></section>')
    home_body = f'<h1>{html.escape(config["title"])}</h1><p>{html.escape(config.get("subtitle", ""))}</p>' + "".join(home_sections)
    files["index.html"] = _page(config["title"], home_body, "Home", base_path)
    files["assets/site.css"] = b"body{font-family:system-ui,sans-serif;max-width:72rem;margin:auto;padding:1rem;line-height:1.55}header{display:flex;justify-content:space-between;gap:1rem;border-bottom:1px solid #ccc;padding-bottom:1rem}main{padding-top:1rem}.breadcrumbs,.prev-next{margin:1rem 0;color:#555}nav a{margin-right:.75rem}table{width:100%;border-collapse:collapse;margin:1rem 0;display:block;overflow-x:auto}th,td{border:1px solid #d0d7de;padding:.5rem .75rem;text-align:left;vertical-align:top}th{background:#f6f8fa}pre{overflow:auto;background:#f6f8fa;padding:1rem;border-radius:.25rem}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;background:#f6f8fa;padding:.1rem .25rem;border-radius:.2rem}pre code{background:transparent;padding:0}blockquote{margin:1rem 0;padding:.25rem 1rem;border-left:.25rem solid #d0d7de;color:#57606a}hr{border:0;border-top:1px solid #d0d7de;margin:2rem 0}li+li{margin-top:.25rem}.mermaid-diagram{overflow-x:auto;margin:1rem 0}.mermaid-diagram svg{display:block}.mermaid-diagram figcaption{color:#57606a;font-size:.875rem;margin-top:.5rem}@media(max-width:48rem){header{display:block}header nav{margin-top:.5rem}}\n"
    files["routes.json"] = (json.dumps(entries, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    search_relative = config.get("search_index")
    if isinstance(search_relative, str):
        search_path = root / search_relative
        if not search_path.is_file():
            raise ValueError(f"configured search index does not exist: {search_relative}")
        files["search-index.json"] = search_path.read_bytes()
        files["assets/search.js"] = _browser_search_script(base_path).encode("utf-8")
        script_src = _public_url("/assets/search.js", base_path)
        search_body = f'<h1>Search</h1><form id="search-form"><label for="q">Search governed documentation</label><input id="q" name="q"><button>Search</button></form><ul id="results"></ul><script src="{script_src}"></script>'
        files["search/index.html"] = _page("Search", search_body, f'<a href="{_public_url("/", base_path)}">Home</a> / Search', base_path)
    inputs = []
    extra_inputs = [search_relative] if isinstance(search_relative, str) else []
    for relative in [_CONFIG, _REGISTRY, _SITE_SOURCE] + extra_inputs + [entry["source"] for entry in entries]:
        payload = (root / relative).read_bytes()
        import hashlib
        inputs.append({"path": relative, "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)})
    manifest = {
        "contract": {"name": "kis-documentation-site", "version": 1},
        "generator": {"name": "kis-mcp-doc", "algorithm": "documentation-site-v1"},
        "registry_sha256": canonical_hash(registry),
        "inputs": sorted(inputs, key=lambda item: item["path"]),
        "routes": len(entries),
        "files": file_declarations(files),
        **bundle_manifest_fields(files),
    }
    return files, manifest


def build_documentation_site(root: Path, output: Path | None = None, *, replace: bool = False) -> dict[str, Any]:
    root = Path(root).resolve()
    output = Path(output) if output is not None else root / "generated/documentation-site"
    files, manifest = render_documentation_site(root)
    write_bundle(output, files, manifest, replace=replace)
    return manifest


def verify_documentation_site(root: Path, output: Path | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    output = Path(output) if output is not None else root / "generated/documentation-site"
    try:
        files, manifest = render_documentation_site(root)
    except Exception as error:
        return {"status": "invalid", "diagnostics": [{"code": "SITE_RENDER_FAILED", "message": str(error)}]}
    diagnostics = bundle_diagnostics(output, files, manifest, code_prefix="SITE")
    return {"status": "invalid" if diagnostics else "valid", "diagnostics": diagnostics}
