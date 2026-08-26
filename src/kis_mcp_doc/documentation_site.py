from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

from .canonical import canonical_hash
from .publication_kernel import PublicationFamilyRegistry, bundle_diagnostics, bundle_manifest_fields, file_declarations, write_bundle

_CONFIG = "publication/documentation-site.json"
_REGISTRY = "mrd/documentation/04-publication-family-registry.mrd.json"
_SITE_SOURCE = "src/kis_mcp_doc/documentation_site.py"
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")


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
    target = target.split("#", 1)[0]
    if not target or "://" in target or target.startswith("mailto:"):
        return None
    return (source.parent / target).resolve()


def _markdown_graph(root: Path, family: dict[str, Any]) -> tuple[set[str], dict[str, set[str]], list[dict[str, str]]]:
    output = (root / family["output"]).resolve()
    pages = {
        path.relative_to(output).as_posix()
        for path in output.glob("*.md")
        if path.name != "specification.md"
    }
    graph = {page: set() for page in pages}
    diagnostics: list[dict[str, str]] = []
    for page in sorted(pages):
        source = output / page
        text = source.read_text(encoding="utf-8")
        for _, target in _LINK_RE.findall(text):
            resolved = _resolve_link(root, source, target)
            if resolved is None:
                continue
            if not resolved.is_file():
                diagnostics.append({"code": "SITE_BROKEN_SOURCE_LINK", "message": f"{_source_key(source, root)} -> {target}"})
                continue
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


def _rewrite_link(source: Path, target: str, source_to_route: dict[str, str], root: Path) -> str:
    resolved = _resolve_link(root, source, target)
    if resolved is None:
        return target
    key = _source_key(resolved, root) if resolved.exists() else ""
    route = source_to_route.get(key)
    fragment = "#" + target.split("#", 1)[1] if "#" in target else ""
    return route + fragment if route else target


def _markdown_html(text: str, source: Path, source_to_route: dict[str, str], root: Path) -> str:
    lines: list[str] = []
    in_list = False
    for raw in text.splitlines():
        if raw.startswith("<!--"):
            continue
        heading = _HEADING_RE.match(raw)
        if heading:
            if in_list:
                lines.append("</ul>")
                in_list = False
            level = len(heading.group(1))
            lines.append(f"<h{level}>{html.escape(heading.group(2))}</h{level}>")
            continue
        if raw.startswith("- "):
            if not in_list:
                lines.append("<ul>")
                in_list = True
            body = html.escape(raw[2:])
            for label, target in _LINK_RE.findall(raw[2:]):
                escaped = html.escape(f"[{label}]({target})")
                href = html.escape(_rewrite_link(source, target, source_to_route, root), quote=True)
                body = body.replace(escaped, f'<a href="{href}">{html.escape(label)}</a>')
            lines.append(f"<li>{body}</li>")
            continue
        if in_list:
            lines.append("</ul>")
            in_list = False
        if raw.strip():
            body = html.escape(raw)
            for label, target in _LINK_RE.findall(raw):
                escaped = html.escape(f"[{label}]({target})")
                href = html.escape(_rewrite_link(source, target, source_to_route, root), quote=True)
                body = body.replace(escaped, f'<a href="{href}">{html.escape(label)}</a>')
            lines.append(f"<p>{body}</p>")
    if in_list:
        lines.append("</ul>")
    return "\n".join(lines)


def _page(title: str, body: str, breadcrumb: str, prev_next: str = "") -> bytes:
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{html.escape(title)}</title><link rel=\"stylesheet\" href=\"/assets/site.css\"></head><body>"
            "<header><a href=\"/\">KIS Documentation</a><nav><a href=\"/docs/\">Docs</a> <a href=\"/specification/\">Specification</a> <a href=\"/reference/\">Reference</a> <a href=\"/search/\">Search</a></nav></header>"
            f"<main><div class=\"breadcrumbs\">{breadcrumb}</div>{body}{prev_next}</main></body></html>\n").encode("utf-8")


def _route_file(route: str) -> str:
    return "index.html" if route == "/" else route.strip("/") + "/index.html"


def render_documentation_site(root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    root = Path(root).resolve()
    validation = validate_documentation_site(root)
    if validation["status"] != "valid":
        raise ValueError("documentation site validation failed: " + "; ".join(item["code"] for item in validation["diagnostics"]))
    config = _load_json(root / _CONFIG)
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
            body = _markdown_html(source.read_text(encoding="utf-8"), source, source_to_route, root)
            prev_link = f'<a rel="prev" href="{ordered[index-1]["route"]}">Previous</a>' if index else ""
            next_link = f'<a rel="next" href="{ordered[index+1]["route"]}">Next</a>' if index + 1 < len(ordered) else ""
            crumb = f'<a href="/">Home</a> / <a href="/{entry["surface"]}/">{entry["surface"].title()}</a> / {html.escape(family["title"])}'
            files[_route_file(entry["route"])] = _page(entry["title"], body, crumb, f'<nav class="prev-next">{prev_link} {next_link}</nav>')
    for entry in [item for item in entries if item["surface"] == "reference"]:
        source = root / entry["source"]
        body = f"<h1>{html.escape(entry['title'])}</h1><pre>{html.escape(source.read_text(encoding='utf-8'))}</pre>"
        crumb = f'<a href="/">Home</a> / <a href="/reference/">Reference</a> / {html.escape(entry["family"])}'
        files[_route_file(entry["route"])] = _page(entry["title"], body, crumb)
    for surface in ("docs", "specification", "reference"):
        links = [entry for entry in entries if entry["surface"] == surface and (entry["source"].endswith("000-index.md") or surface == "reference")]
        if surface == "reference":
            first_by_family = {}
            for entry in links:
                first_by_family.setdefault(entry["family"], entry)
            links = list(first_by_family.values())
        body = f"<h1>{surface.title()}</h1><ul>" + "".join(f'<li><a href="{item["route"]}">{html.escape(item["title"])}</a></li>' for item in links) + "</ul>"
        files[_route_file(f"/{surface}/")] = _page(surface.title(), body, '<a href="/">Home</a>')
    home_sections = []
    for surface in ("docs", "specification", "reference", "search"):
        home_sections.append(f'<section><h2><a href="/{surface}/">{surface.title()}</a></h2></section>')
    files["index.html"] = _page(config["title"], f'<h1>{html.escape(config["title"])}</h1><p>{html.escape(config.get("subtitle", ""))}</p>' + "".join(home_sections), "Home")
    files["assets/site.css"] = b"body{font-family:system-ui,sans-serif;max-width:72rem;margin:auto;padding:1rem;line-height:1.55}header{display:flex;justify-content:space-between;border-bottom:1px solid #ccc;padding-bottom:1rem}main{padding-top:1rem}.breadcrumbs,.prev-next{margin:1rem 0;color:#555}pre{overflow:auto;background:#f6f8fa;padding:1rem}nav a{margin-right:.75rem}\n"
    files["routes.json"] = (json.dumps(entries, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    search_relative = config.get("search_index")
    if isinstance(search_relative, str):
        search_path = root / search_relative
        if not search_path.is_file():
            raise ValueError(f"configured search index does not exist: {search_relative}")
        search_bytes = search_path.read_bytes()
        files["search-index.json"] = search_bytes
        files["assets/search.js"] = b"fetch('/search-index.json').then(r=>r.json()).then(i=>{const f=document.querySelector('#search-form'),q=document.querySelector('#q'),o=document.querySelector('#results');f.addEventListener('submit',e=>{e.preventDefault();const ts=q.value.toLowerCase().split(/\\s+/).filter(Boolean);const rs=i.documents.map(d=>[ts.reduce((s,t)=>s+(d.title_terms[t]||0)*5+(d.terms[t]||0),0),d]).filter(x=>x[0]>0).sort((a,b)=>b[0]-a[0]||a[1].route.localeCompare(b[1].route)).slice(0,i.default_limit);o.innerHTML=rs.map(x=>`<li><a href=\"${x[1].route}\">${x[1].title}</a> - ${x[1].family}</li>`).join('');});});\n"
        search_body = '<h1>Search</h1><form id="search-form"><label for="q">Search governed documentation</label><input id="q" name="q"><button>Search</button></form><ul id="results"></ul><script src="/assets/search.js"></script>'
        files["search/index.html"] = _page("Search", search_body, '<a href="/">Home</a> / Search')
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
