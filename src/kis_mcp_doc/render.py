from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .governance import GovernanceRepository, canonical_hash


_PUBLICATION_SCHEMA = "contracts/publication/v1/governance-spec.schema.json"
_MANIFEST_SCHEMA = "contracts/publication/v1/manifest.schema.json"


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
    config = _load_publication_config(repository, publication_path)
    documents = repository.load()
    files = _build_output_files(repository, config, documents)

    parent = output.parent
    parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", suffix=".tmp", dir=parent))
    try:
        for relative, payload in files.items():
            path = staging / Path(*relative.split("/"))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        manifest = _build_manifest(repository, publication_path, config, documents, files, validation)
        _validate_contract(repository.root, _MANIFEST_SCHEMA, manifest, "build manifest")
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
        _validate_contract(repository.root, _MANIFEST_SCHEMA, manifest, "build manifest")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        return _verification_result([_verification_diag("GENERATED_MANIFEST_INVALID", str(error))])

    try:
        config = _load_publication_config(repository, Path(publication_path))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        return _verification_result([_verification_diag("PUBLICATION_CONFIG_INVALID", str(error))])

    current_validation = repository.validate()
    if current_validation["status"] != "valid":
        diagnostics.append(_verification_diag("SOURCE_MRD_INVALID", "current governance MRDs do not validate"))
    if manifest.get("validation") != current_validation:
        diagnostics.append(_verification_diag("VALIDATION_RESULT_MISMATCH", "manifest validation result differs from current validation"))

    expected_specification = {"title": config["title"], "version": config["version"], "status": config["status"]}
    if manifest.get("specification") != expected_specification:
        diagnostics.append(_verification_diag("MANIFEST_SPECIFICATION_MISMATCH", "manifest specification metadata differs from publication configuration"))

    try:
        expected_generator = {**config["generator"], "sources": _generator_source_declarations(repository)}
    except OSError as error:
        diagnostics.append(_verification_diag("GENERATOR_SOURCE_UNAVAILABLE", str(error)))
        expected_generator = None
    if expected_generator is not None and manifest.get("generator") != expected_generator:
        diagnostics.append(_verification_diag("GENERATOR_DECLARATION_MISMATCH", "manifest generator declaration differs from current generator contract"))

    documents = repository.load()
    expected_mrds = _mrd_input_declarations(repository, documents)
    declared_mrds = manifest.get("inputs", {}).get("mrds", [])
    if declared_mrds != expected_mrds:
        diagnostics.append(_verification_diag("SOURCE_MRD_SET_MISMATCH", "manifest MRD declarations differ from current source MRDs"))
    if manifest.get("inputs", {}).get("source_set_sha256") != canonical_hash(expected_mrds):
        diagnostics.append(_verification_diag("SOURCE_SET_HASH_MISMATCH", "manifest source-set digest does not match current MRD declarations"))

    expected_source_files = _source_file_declarations(repository, documents)
    declared_source_files = manifest.get("inputs", {}).get("source_files", [])
    expected_by_path = {item["path"]: item for item in expected_source_files}
    declared_by_path = {item.get("path"): item for item in declared_source_files}
    if set(expected_by_path) != set(declared_by_path):
        diagnostics.append(_verification_diag("SOURCE_FILE_SET_MISMATCH", "manifest canonical source-file set differs from current dependencies"))
    for relative, expected in expected_by_path.items():
        declared = declared_by_path.get(relative)
        if declared is not None and declared != expected:
            diagnostics.append(_verification_diag("SOURCE_FILE_HASH_MISMATCH", f"canonical source-file declaration changed: {relative}"))

    publication_bytes = Path(publication_path).read_bytes()
    if hashlib.sha256(publication_bytes).hexdigest() != manifest.get("inputs", {}).get("publication", {}).get("sha256"):
        diagnostics.append(_verification_diag("PUBLICATION_CONFIG_HASH_MISMATCH", "publication configuration changed"))

    manifest_files = manifest.get("files", [])
    if canonical_hash(manifest_files) != manifest.get("bundle_sha256"):
        diagnostics.append(_verification_diag("GENERATED_BUNDLE_HASH_MISMATCH", "manifest bundle digest does not match its file declarations"))

    expected_payloads = _build_output_files(repository, config, documents)
    expected_declarations = _file_declarations(expected_payloads)
    if manifest_files != expected_declarations:
        diagnostics.append(_verification_diag("GENERATED_DECLARATION_MISMATCH", "manifest generated-file declarations differ from deterministic current output"))

    declared_files = {item["path"]: item for item in manifest_files}
    expected_files = set(expected_payloads) | {"manifest.json"}
    actual_files = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
    if actual_files != expected_files:
        diagnostics.append(_verification_diag("GENERATED_FILE_SET_MISMATCH", "generated bundle file inventory differs from deterministic expected output"))

    for relative, expected_payload in expected_payloads.items():
        path = output / Path(*relative.split("/"))
        if not path.is_file():
            diagnostics.append(_verification_diag("GENERATED_FILE_MISSING", f"generated file missing: {relative}"))
            continue
        actual_payload = path.read_bytes()
        if actual_payload != expected_payload:
            diagnostics.append(_verification_diag("GENERATED_FILE_CONTENT_MISMATCH", f"generated file does not match deterministic current output: {relative}"))
        declaration = declared_files.get(relative)
        if declaration is not None and (
            hashlib.sha256(actual_payload).hexdigest() != declaration.get("sha256")
            or len(actual_payload) != declaration.get("bytes")
        ):
            diagnostics.append(_verification_diag("GENERATED_FILE_HASH_MISMATCH", f"generated file changed relative to manifest: {relative}"))
    return _verification_result(diagnostics)

def _validate_contract(root: Path, schema_relative: str, instance: object, label: str) -> None:
    schema_path = root / schema_relative
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(instance),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"unable to load {label} schema: {error}") from error
    if errors:
        error = errors[0]
        location = "/".join(str(part) for part in error.absolute_path) or "$"
        raise ValueError(f"{label} invalid at {location}: {error.message}")


def _load_publication_config(repository: GovernanceRepository, publication_path: Path) -> dict[str, Any]:
    config = json.loads(Path(publication_path).read_text(encoding="utf-8"))
    _validate_contract(repository.root, _PUBLICATION_SCHEMA, config, "publication configuration")
    return config


def _generator_source_declarations(repository: GovernanceRepository) -> list[dict[str, Any]]:
    declarations = []
    for relative in (
        "src/kis_mcp_doc/governance.py",
        "src/kis_mcp_doc/render.py",
        _PUBLICATION_SCHEMA,
        _MANIFEST_SCHEMA,
    ):
        payload = (repository.root / relative).read_bytes()
        declarations.append({"path": relative, "sha256": hashlib.sha256(payload).hexdigest()})
    return declarations


def _mrd_input_declarations(repository: GovernanceRepository, documents: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    declarations = []
    for doc_id, document in sorted(documents.items()):
        payload = _document_bytes(repository, doc_id, document)
        declarations.append({
            "id": doc_id,
            "path": _document_relative_path(repository, doc_id),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "version": document["_mrd"]["version"],
        })
    return declarations


def _file_declarations(files: dict[str, bytes]) -> list[dict[str, Any]]:
    return [
        {"path": path, "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}
        for path, payload in sorted(files.items())
    ]


def _build_output_files(repository: GovernanceRepository, config: dict[str, Any], documents: dict[str, dict[str, Any]]) -> dict[str, bytes]:
    ordered = sorted(documents.values(), key=lambda item: (item["content"]["section_order"], item["_mrd"]["id"]))
    return {
        config["output_file"]: _render_markdown(config, ordered).encode("utf-8"),
        "data/mrd-index.json": _json_bytes(_build_index(repository, documents)),
        "data/dependency-map.json": _json_bytes(_build_dependency_map(documents)),
    }


def _build_manifest(
    repository: GovernanceRepository,
    publication_path: Path,
    config: dict[str, Any],
    documents: dict[str, dict[str, Any]],
    files: dict[str, bytes],
    validation: dict[str, Any],
) -> dict[str, Any]:
    inputs = _mrd_input_declarations(repository, documents)
    generator_sources = _generator_source_declarations(repository)
    file_declarations = _file_declarations(files)
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
