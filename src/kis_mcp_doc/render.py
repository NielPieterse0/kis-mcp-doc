from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .governance import GovernanceRepository, canonical_hash


def build_governance_spec(
    repository: GovernanceRepository,
    publication_path: Path,
    output: Path,
    *,
    replace: bool = False,
) -> dict[str, Any]:
    validation = repository.validate()
    if validation["status"] != "valid":
        raise ValueError(f"governance MRDs are invalid: {validation['diagnostics']}")

    publication_path = Path(publication_path)
    output = Path(output)
    config = json.loads(publication_path.read_text(encoding="utf-8"))
    documents = repository.load()
    ordered = sorted(
        documents.values(),
        key=lambda item: (item["content"]["section_order"], item["_mrd"]["id"]),
    )
    markdown = _render_markdown(config, ordered)
    index = _build_index(repository, documents)
    dependency_map = _build_dependency_map(documents)

    parent = output.parent
    parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", suffix=".tmp", dir=parent))
    try:
        files: dict[str, bytes] = {
            config["output_file"]: markdown.encode("utf-8"),
            "data/mrd-index.json": _json_bytes(index),
            "data/dependency-map.json": _json_bytes(dependency_map),
        }
        for relative, payload in files.items():
            path = staging / Path(*relative.split("/"))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        manifest = _build_manifest(repository, publication_path, config, documents, files, validation)
        (staging / "manifest.json").write_bytes(_json_bytes(manifest))
        if output.exists():
            if not replace:
                raise FileExistsError(f"output already exists: {output}")
            shutil.rmtree(output)
        os.replace(staging, output)
        return manifest
    except Exception:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise


def verify_governance_spec(
    repository: GovernanceRepository,
    publication_path: Path,
    output: Path,
) -> dict[str, Any]:
    diagnostics: list[dict[str, str]] = []
    output = Path(output)
    manifest_path = output / "manifest.json"
    if not manifest_path.is_file():
        return _verification_result([_verification_diag("GENERATED_MANIFEST_MISSING", "manifest.json is missing")])
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return _verification_result([_verification_diag("GENERATED_MANIFEST_INVALID", str(error))])

    current_validation = repository.validate()
    if current_validation["status"] != "valid":
        diagnostics.append(_verification_diag("SOURCE_MRD_INVALID", "current governance MRDs do not validate"))

    source_by_id = repository.load()
    input_by_id = {item["id"]: item for item in manifest.get("inputs", {}).get("mrds", [])}
    for doc_id, document in source_by_id.items():
        declaration = input_by_id.get(doc_id)
        if declaration is None:
            diagnostics.append(_verification_diag("SOURCE_MRD_SET_MISMATCH", f"source MRD not declared: {doc_id}"))
            continue
        current = _document_bytes(repository, doc_id, document)
        if hashlib.sha256(current).hexdigest() != declaration.get("sha256"):
            diagnostics.append(_verification_diag("SOURCE_MRD_HASH_MISMATCH", f"source MRD changed: {doc_id}"))
    if set(input_by_id) != set(source_by_id):
        diagnostics.append(_verification_diag("SOURCE_MRD_SET_MISMATCH", "manifest MRD set differs from current source set"))

    current_source_files = {
        item["path"]: item for item in _source_file_declarations(repository, source_by_id)
    }
    declared_source_files = {
        item["path"]: item
        for item in manifest.get("inputs", {}).get("source_files", [])
    }
    if set(current_source_files) != set(declared_source_files):
        diagnostics.append(
            _verification_diag(
                "SOURCE_FILE_SET_MISMATCH",
                "manifest canonical source-file set differs from current MRD dependencies",
            )
        )
    for relative, current in current_source_files.items():
        declared = declared_source_files.get(relative)
        if declared is not None and current["sha256"] != declared.get("sha256"):
            diagnostics.append(
                _verification_diag(
                    "SOURCE_FILE_HASH_MISMATCH",
                    f"canonical source file changed: {relative}",
                )
            )

    publication_bytes = Path(publication_path).read_bytes()
    if hashlib.sha256(publication_bytes).hexdigest() != manifest.get("inputs", {}).get("publication", {}).get("sha256"):
        diagnostics.append(_verification_diag("PUBLICATION_CONFIG_HASH_MISMATCH", "publication configuration changed"))

    for declaration in manifest.get("generator", {}).get("sources", []):
        path = repository.root / declaration.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != declaration.get("sha256"):
            diagnostics.append(_verification_diag("GENERATOR_HASH_MISMATCH", f"generator source changed: {declaration.get('path')}"))

    manifest_files = manifest.get("files", [])
    if canonical_hash(manifest_files) != manifest.get("bundle_sha256"):
        diagnostics.append(
            _verification_diag(
                "GENERATED_BUNDLE_HASH_MISMATCH",
                "manifest bundle digest does not match its file declarations",
            )
        )
    declared_files = {item["path"]: item for item in manifest_files}
    expected_files = set(declared_files) | {"manifest.json"}
    actual_files = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    }
    if actual_files != expected_files:
        diagnostics.append(
            _verification_diag(
                "GENERATED_FILE_SET_MISMATCH",
                "generated bundle file inventory differs from the manifest",
            )
        )
    for relative, declaration in declared_files.items():
        path = output / Path(*relative.split("/"))
        if not path.is_file():
            diagnostics.append(_verification_diag("GENERATED_FILE_MISSING", f"generated file missing: {relative}"))
            continue
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != declaration.get("sha256") or len(payload) != declaration.get("bytes"):
            diagnostics.append(_verification_diag("GENERATED_FILE_HASH_MISMATCH", f"generated file changed: {relative}"))
    return _verification_result(diagnostics)


def _build_manifest(
    repository: GovernanceRepository,
    publication_path: Path,
    config: dict[str, Any],
    documents: dict[str, dict[str, Any]],
    files: dict[str, bytes],
    validation: dict[str, Any],
) -> dict[str, Any]:
    inputs = []
    for doc_id, document in sorted(documents.items()):
        payload = _document_bytes(repository, doc_id, document)
        inputs.append({
            "id": doc_id,
            "path": _document_relative_path(repository, doc_id),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "version": document["_mrd"]["version"],
        })
    generator_sources = []
    for relative in ("src/kis_mcp_doc/governance.py", "src/kis_mcp_doc/render.py"):
        payload = (repository.root / relative).read_bytes()
        generator_sources.append({"path": relative, "sha256": hashlib.sha256(payload).hexdigest()})
    file_declarations = [
        {"path": path, "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}
        for path, payload in sorted(files.items())
    ]
    return {
        "contract": {"name": "kis-governance-spec-build", "version": 1},
        "specification": {"title": config["title"], "version": config["version"], "status": config["status"]},
        "generator": {**config["generator"], "sources": generator_sources},
        "inputs": {
            "mrds": inputs,
            "source_set_sha256": canonical_hash(inputs),
            "source_files": _source_file_declarations(repository, documents),
            "publication": {
                "path": publication_path.relative_to(repository.root).as_posix(),
                "sha256": hashlib.sha256(publication_path.read_bytes()).hexdigest(),
            },
        },
        "validation": validation,
        "files": file_declarations,
        "bundle_sha256": canonical_hash(file_declarations),
    }


def _source_file_declarations(
    repository: GovernanceRepository,
    documents: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    paths = sorted(
        {
            dependency["source"][5:]
            for document in documents.values()
            for dependency in document["_mrd"]["dependencies"]
            if "source" in dependency and dependency["source"].startswith("repo:")
        }
    )
    declarations = []
    for relative in paths:
        payload = (repository.root / Path(*relative.split("/"))).read_bytes()
        declarations.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
            }
        )
    return declarations


def _build_index(repository: GovernanceRepository, documents: dict[str, dict[str, Any]]) -> dict[str, Any]:
    records = []
    for doc_id, document in sorted(documents.items()):
        payload = _document_bytes(repository, doc_id, document)
        envelope = document["_mrd"]
        records.append({
            "id": doc_id,
            "path": _document_relative_path(repository, doc_id),
            "class": envelope["class"],
            "type": envelope["type"],
            "layer": envelope["layer"],
            "record_mode": envelope["record_mode"],
            "status": envelope["status"],
            "version": envelope["version"],
            "sha256": hashlib.sha256(payload).hexdigest(),
        })
    return {"_mrd_projection": {"class": "META", "type": "IDX", "record_mode": "meta"}, "records": records}


def _build_dependency_map(documents: dict[str, dict[str, Any]]) -> dict[str, Any]:
    edges = []
    for doc_id, document in sorted(documents.items()):
        for dependency in document["_mrd"]["dependencies"]:
            edge = {"from": doc_id, "relationship": dependency["relationship"]}
            if "mrd_id" in dependency:
                edge.update({"target_kind": "mrd", "to": dependency["mrd_id"]})
            else:
                edge.update({"target_kind": "source", "to": dependency["source"]})
            edges.append(edge)
    edges.sort(key=lambda item: (item["from"], item["target_kind"], item["to"], item["relationship"]))
    return {"_mrd_projection": {"class": "META", "type": "DEP", "record_mode": "meta"}, "edges": edges}


def _document_relative_path(repository: GovernanceRepository, doc_id: str) -> str:
    for path in sorted(repository.mrd_root.glob("*.mrd.json")):
        try:
            candidate = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if candidate.get("_mrd", {}).get("id") == doc_id:
            return path.relative_to(repository.root).as_posix()
    raise KeyError(doc_id)


def _document_bytes(repository: GovernanceRepository, doc_id: str, document: dict[str, Any]) -> bytes:
    relative = _document_relative_path(repository, doc_id)
    return (repository.root / relative).read_bytes()


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def _verification_diag(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _verification_result(diagnostics: list[dict[str, str]]) -> dict[str, Any]:
    return {"status": "invalid" if diagnostics else "valid", "diagnostics": diagnostics}


def _render_markdown(config: dict[str, Any], documents: list[dict[str, Any]]) -> str:
    lines = [
        "<!-- GENERATED — DO NOT EDIT -->",
        f"# {config['title']}",
        "",
        f"> **Status:** {config['status']}",
        f"> **Version:** {config['version']}",
        "> **Authority:** Generated human-readable projection; the source MRDs are authoritative.",
        f"> **Generator:** {config['generator']['name']} {config['generator']['version']} / {config['generator']['algorithm']}",
        "",
        config["subtitle"],
        "",
        "This document is a deterministic human-readable projection of the six validated governance MRDs listed in Traceability.",
        "",
        "The capitalized terms **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, **MAY**, and **REQUIRED** express normative requirements as authored in the source MRDs.",
        "",
    ]
    for document in documents:
        content = document["content"]
        lines.extend([f"## {content['section_order']}. {content['heading']}", "", content["purpose"], ""])
        _render_rules(lines, content.get("rules", []))
        concern = content["concern"]
        if concern == "classification":
            _render_classification(lines, content)
        elif concern == "layering":
            _render_layering(lines, content)
        elif concern == "dependencies":
            _render_dependencies(lines, content)
        elif concern == "provenance":
            _render_provenance(lines, content)
        elif concern == "lifecycle":
            _render_lifecycle(lines, content)
        elif concern == "validation":
            _render_validation(lines, content)
    lines.extend(["## Traceability", "", "Each normative section above is projected from exactly one prescriptive MRD:", ""])
    lines.extend(["| Section | MRD | Version | Provenance sources |", "|---|---|---:|---|"])
    for document in documents:
        sources = ", ".join(source["source_id"] for source in document["_mrd"]["provenance"]["sources"])
        lines.append(f"| {document['content']['section_order']}. {document['content']['heading']} | `{document['_mrd']['id']}` | {document['_mrd']['version']} | {sources} |")
    lines.extend(["", "Build hashes and the derived META-IDX / META-DEP projections are recorded in the adjacent `manifest.json` and `data/` files.", ""])
    return "\n".join(lines)


def _render_rules(lines: list[str], rules: list[dict[str, Any]]) -> None:
    lines.extend(["### Normative rules", ""])
    for rule in rules:
        lines.append(f"- **{rule['rule_id']}** — {rule['statement']}")
    lines.append("")


def _render_classification(lines: list[str], content: dict[str, Any]) -> None:
    lines.extend(["### Classes", "", "| Class | Name | Definition |", "|---|---|---|"])
    for item in content["classes"]:
        lines.append(f"| `{item['code']}` | {item['name']} | {item['definition']} |")
    lines.extend(["", f"### Type catalog ({content['catalog_policy']['expected_type_count']} allowed types)", "", "| Class | Type | Code | Meaning | Canonical format |", "|---|---|---|---|---|"])
    for item in content["type_catalog"]:
        lines.append(f"| `{item['class']}` | `{item['type']}` | `{item['code']}` | {item['name']} | {item['canonical_format']} |")
    lines.append("")


def _render_layering(lines: list[str], content: dict[str, Any]) -> None:
    lines.extend(["### Authority layers", "", "| Layer | Name | Interpretation |", "|---|---|---|"])
    for item in content["layers"]:
        lines.append(f"| `{item['code']}` | {item['name']} | {item['interpretation']} |")
    lines.extend(["", "### Direction examples", "", "| Source | Target | Valid |", "|---|---|---|"])
    for item in content["examples"]:
        lines.append(f"| `{item['source']}` | `{item['target']}` | {'Yes' if item['valid'] else 'No'} |")
    lines.append("")


def _render_dependencies(lines: list[str], content: dict[str, Any]) -> None:
    lines.extend(["### Dependency target forms", "", "| Kind | Field | Example |", "|---|---|---|"])
    for item in content["target_forms"]:
        lines.append(f"| {item['kind']} | `{item['field']}` | `{item['example']}` |")
    lines.append("")


def _render_provenance(lines: list[str], content: dict[str, Any]) -> None:
    lines.extend(["### Record modes", "", "| Record mode | Meaning | Mutability |", "|---|---|---|"])
    for item in content["record_modes"]:
        lines.append(f"| `{item['mode']}` | {item['meaning']} | `{item['mutability']}` |")
    lines.extend(["", "### Fact quality", "", "| Quality | Meaning |", "|---|---|"])
    for item in content["fact_qualities"]:
        lines.append(f"| `{item['quality']}` | {item['meaning']} |")
    lines.extend(["", "### Provenance source kinds", "", "| Kind | Resolution requirement |", "|---|---|"])
    for item in content["source_kinds"]:
        lines.append(f"| `{item['kind']}` | {item['resolution']} |")
    lines.append("")


def _render_lifecycle(lines: list[str], content: dict[str, Any]) -> None:
    lines.extend(["### State machines", "", "| Record mode | States | Allowed transitions |", "|---|---|---|"])
    for item in content["lifecycles"]:
        transitions = "; ".join(f"{edge['from']} → {edge['to']}" for edge in item["transitions"])
        lines.append(f"| `{item['record_mode']}` | {' → '.join(item['states'])} | {transitions} |")
    lines.append("")


def _render_validation(lines: list[str], content: dict[str, Any]) -> None:
    lines.extend(["### Validation dimensions", ""])
    for dimension in content["dimensions"]:
        lines.append(f"#### {dimension['name'].title()}")
        lines.append("")
        for check in dimension["checks"]:
            lines.append(f"- {check}")
        lines.append("")
    result = content["result_contract"]
    lines.extend(["### Result contract", "", f"- Status: {', '.join(f'`{value}`' for value in result['status_values'])}", f"- Check keys: {', '.join(f'`{value}`' for value in result['checks'])}", f"- Diagnostics on failure: {'required' if result['diagnostics_required_on_failure'] else 'optional'}", "", "### Stable reason codes", ""])
    for code in content["reason_codes"]:
        lines.append(f"- `{code}`")
    lines.append("")