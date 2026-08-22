from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .governance import GovernanceRepository, canonical_hash, canonical_source_bytes
from .harvest import load_harvest_registry
from .litho import load_litho_evidence


_PUBLICATION_SCHEMA = "contracts/publication/v2/governance-spec.schema.json"
_MANIFEST_SCHEMA = "contracts/publication/v2/manifest.schema.json"
_LITHO_SCHEMA = "contracts/documentation/litho/v1/package.schema.json"
_HARVEST_SCHEMA = "contracts/documentation/harvest/v1/registry.schema.json"
_HARVEST_REGISTRY = "publication/harvest-sources.json"


def build_governance_spec(
    repository: GovernanceRepository,
    publication_path: Path,
    output: Path,
    *,
    replace: bool = False,
    litho_package: Path | None = None,
) -> dict[str, Any]:
    validation = repository.validate()
    if validation["status"] != "valid":
        raise ValueError(f"governance MRDs are invalid: {validation['diagnostics']}")

    publication_path = Path(publication_path)
    output = Path(output)
    config = _load_publication_config(repository, publication_path)
    documents = repository.load()
    harvest_registry = load_harvest_registry(repository.root)
    litho_evidence = (
        load_litho_evidence(repository.root, litho_package)
        if litho_package is not None
        else None
    )
    files = _build_output_files(repository, config, documents, litho_evidence)

    parent = output.parent
    parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", suffix=".tmp", dir=parent))
    try:
        for relative, payload in files.items():
            path = staging / Path(*relative.split("/"))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        manifest = _build_manifest(
            repository,
            publication_path,
            config,
            documents,
            files,
            validation,
            harvest_registry,
            litho_evidence,
        )
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
    *,
    litho_package: Path | None = None,
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

    expected_specification = {
        "title": config["title"],
        "version": config["version"],
        "status": config["status"],
        "layout_profile": config["layout_profile"],
    }
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

    declared_harvest = manifest.get("inputs", {}).get("harvest_registry")
    try:
        current_harvest = load_harvest_registry(repository.root)
        expected_harvest = _harvest_registry_declaration(repository, current_harvest)
    except ValueError as error:
        diagnostics.append(_verification_diag("HARVEST_REGISTRY_INVALID", str(error)))
        expected_harvest = None
    if declared_harvest != expected_harvest:
        diagnostics.append(
            _verification_diag(
                "HARVEST_REGISTRY_MISMATCH",
                "manifest harvest-registry declaration differs from current registry",
            )
        )

    publication_bytes = canonical_source_bytes(Path(publication_path))
    if hashlib.sha256(publication_bytes).hexdigest() != manifest.get("inputs", {}).get("publication", {}).get("sha256"):
        diagnostics.append(_verification_diag("PUBLICATION_CONFIG_HASH_MISMATCH", "publication configuration changed"))

    declared_external = manifest.get("inputs", {}).get("external_evidence", [])
    try:
        current_litho = (
            load_litho_evidence(repository.root, litho_package)
            if litho_package is not None
            else None
        )
    except ValueError as error:
        diagnostics.append(_verification_diag("EXTERNAL_EVIDENCE_INVALID", str(error)))
        current_litho = None
    expected_external = _external_evidence_declarations(current_litho)
    if declared_external != expected_external:
        diagnostics.append(
            _verification_diag(
                "EXTERNAL_EVIDENCE_MISMATCH",
                "manifest external-evidence declarations differ from current input",
            )
        )

    manifest_files = manifest.get("files", [])
    if canonical_hash(manifest_files) != manifest.get("bundle_sha256"):
        diagnostics.append(_verification_diag("GENERATED_BUNDLE_HASH_MISMATCH", "manifest bundle digest does not match its file declarations"))

    expected_payloads = _build_output_files(repository, config, documents, current_litho)
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
        "src/kis_mcp_doc/harvest.py",
        "src/kis_mcp_doc/litho.py",
        "src/kis_mcp_doc/render.py",
        _PUBLICATION_SCHEMA,
        _MANIFEST_SCHEMA,
        _HARVEST_SCHEMA,
        _LITHO_SCHEMA,
    ):
        payload = canonical_source_bytes(repository.root / relative)
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


def _build_output_files(
    repository: GovernanceRepository,
    config: dict[str, Any],
    documents: dict[str, dict[str, Any]],
    litho_evidence: dict[str, Any] | None,
) -> dict[str, bytes]:
    ordered = sorted(
        documents.values(),
        key=lambda item: (item["content"]["section_order"], item["_mrd"]["id"]),
    )
    root_page = _render_specification_root(config, ordered).encode("utf-8")
    files: dict[str, bytes] = {
        "000-index.md": _render_corpus_index(config, ordered, litho_evidence).encode("utf-8"),
        "001-specification.md": root_page,
        config["output_file"]: root_page,
        "data/mrd-index.json": _json_bytes(_build_index(repository, documents)),
        "data/dependency-map.json": _json_bytes(_build_dependency_map(documents)),
    }
    for document in ordered:
        files[_document_page_name(document)] = _render_document_page(config, document).encode("utf-8")
    if litho_evidence is not None:
        files["090-code-derived-analysis.md"] = _render_litho_page(config, litho_evidence).encode("utf-8")
        files["data/litho-evidence.json"] = _json_bytes(_normalized_litho_evidence(litho_evidence))
    return files


def _build_manifest(
    repository: GovernanceRepository,
    publication_path: Path,
    config: dict[str, Any],
    documents: dict[str, dict[str, Any]],
    files: dict[str, bytes],
    validation: dict[str, Any],
    harvest_registry: dict[str, Any],
    litho_evidence: dict[str, Any] | None,
) -> dict[str, Any]:
    inputs = _mrd_input_declarations(repository, documents)
    generator_sources = _generator_source_declarations(repository)
    file_declarations = _file_declarations(files)
    return {
        "contract": {"name": "kis-governance-spec-build", "version": 2},
        "specification": {
            "title": config["title"],
            "version": config["version"],
            "status": config["status"],
            "layout_profile": config["layout_profile"],
        },
        "generator": {**config["generator"], "sources": generator_sources},
        "inputs": {
            "mrds": inputs,
            "source_set_sha256": canonical_hash(inputs),
            "source_files": _source_file_declarations(repository, documents),
            "harvest_registry": _harvest_registry_declaration(repository, harvest_registry),
            "external_evidence": _external_evidence_declarations(litho_evidence),
            "publication": {
                "path": publication_path.relative_to(repository.root).as_posix(),
                "sha256": hashlib.sha256(canonical_source_bytes(publication_path)).hexdigest(),
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
        payload = canonical_source_bytes(repository.root / Path(*relative.split("/")))
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
    return canonical_source_bytes(repository.root / relative)


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def _verification_diag(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _verification_result(diagnostics: list[dict[str, str]]) -> dict[str, Any]:
    return {"status": "invalid" if diagnostics else "valid", "diagnostics": diagnostics}


def _harvest_registry_declaration(
    repository: GovernanceRepository, registry: dict[str, Any]
) -> dict[str, Any]:
    path = repository.root / _HARVEST_REGISTRY
    return {
        "path": _HARVEST_REGISTRY,
        "version": registry["registry_version"],
        "sha256": hashlib.sha256(canonical_source_bytes(path)).hexdigest(),
    }


def _external_evidence_declarations(evidence: dict[str, Any] | None) -> list[dict[str, Any]]:
    if evidence is None:
        return []
    return [{
        "provider": evidence["provider"]["name"],
        "version": evidence["provider"]["version"],
        "repository": evidence["target"]["repository"],
        "revision": evidence["target"]["revision"],
        "evidence_class": evidence["evidence_class"],
        "manifest_sha256": evidence["manifest_sha256"],
        "files": [
            {key: page[key] for key in ("path", "sha256", "bytes")}
            for page in evidence["pages"]
        ],
        "canonical_sources": evidence["canonical_sources"],
    }]


def _normalized_litho_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract": evidence["contract"],
        "provider": evidence["provider"],
        "target": evidence["target"],
        "evidence_class": evidence["evidence_class"],
        "manifest_sha256": evidence["manifest_sha256"],
        "pages": [
            {key: page[key] for key in ("path", "title", "sha256", "bytes")}
            for page in evidence["pages"]
        ],
        "assertions": evidence["assertions"],
        "diagnostics": evidence["diagnostics"],
        "canonical_sources": evidence["canonical_sources"],
    }


def _document_page_name(document: dict[str, Any]) -> str:
    content = document["content"]
    page_number = int(content["section_order"]) + 1
    return f"{page_number:03d}-{_heading_anchor(content['heading'])}.md"


def _render_corpus_index(
    config: dict[str, Any],
    documents: list[dict[str, Any]],
    litho_evidence: dict[str, Any] | None,
) -> str:
    lines = [
        "<!-- GENERATED — DO NOT EDIT -->",
        f"# {config['title']} — documentation index",
        "",
        "This generated collection follows the `mcp-spec-2025` publication profile. Source MRDs remain authoritative; these pages are review projections.",
        "",
        "## Specification pages",
        "",
        "- [Specification](001-specification.md)",
    ]
    for document in documents:
        lines.append(f"- [{document['content']['heading']}]({_document_page_name(document)})")
    if litho_evidence is not None:
        lines.append("- [Code-derived analysis](090-code-derived-analysis.md) — inferred evidence, not authority")
    lines.extend([
        "",
        "## Machine-readable traceability",
        "",
        "- [MRD index](data/mrd-index.json)",
        "- [Dependency map](data/dependency-map.json)",
    ])
    if litho_evidence is not None:
        lines.append("- [Litho evidence index](data/litho-evidence.json)")
    lines.extend(["- [Build manifest](manifest.json)", ""])
    return "\n".join(lines)


def _render_specification_root(config: dict[str, Any], documents: list[dict[str, Any]]) -> str:
    lines = [
        "<!-- GENERATED — DO NOT EDIT -->",
        f"# {config['title']}",
        "",
        '<div id="enable-section-numbers" />',
        "",
        config["subtitle"],
        "",
        "This specification defines the generated human-review contract for KIS governance. The validated MRDs and canonical repository sources are authoritative; this corpus is a deterministic projection for review and navigation.",
        "",
        'The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [RFC2119] [RFC8174] when, and only when, they appear in all capitals.',
        "",
        "## Overview",
        "",
        f"The governance model is defined by {len(documents)} validated prescriptive MRDs. It uses the 47 MRD types as a minimum-sufficient selection vocabulary and keeps generated documentation downstream of canonical authority.",
        "",
        "Substantive changes are made in the owning MRD, contract, schema, code, configuration, or test and then regenerated. Missing or inferred facts are never promoted into normative authority by the renderer.",
        "",
        "## Key details",
        "",
        "- 47 governed MRD types with explicit applicability rules",
        "- one canonical owner for each governed fact",
        "- typed dependencies, provenance, lifecycle, and enforcement",
        "- deterministic generated review surfaces with stale/tamper detection",
        "",
        "## Detailed specification",
        "",
    ]
    for document in documents:
        lines.append(f"- [{document['content']['heading']}]({_document_page_name(document)})")
    lines.extend([
        "",
        "## Traceability",
        "",
        "See the [documentation index](000-index.md), [MRD index](data/mrd-index.json), [dependency map](data/dependency-map.json), and [build manifest](manifest.json) for exact source identities, hashes, and generated-file declarations.",
        "",
    ])
    return "\n".join(lines)


def _render_document_page(config: dict[str, Any], document: dict[str, Any]) -> str:
    content = document["content"]
    lines = [
        "<!-- GENERATED — DO NOT EDIT -->",
        f"# {content['heading']}",
        "",
        '<div id="enable-section-numbers" />',
        "",
        "[Specification](001-specification.md) | [Documentation index](000-index.md)",
        "",
        "## Overview",
        "",
        content["purpose"],
        "",
    ]
    body: list[str] = []
    _render_rules(body, content.get("rules", []))
    concern = content["concern"]
    if concern == "classification":
        _render_classification(body, content)
    elif concern == "applicability":
        _render_applicability(body, content)
    elif concern == "ownership":
        _render_ownership(body, content)
    elif concern == "layering":
        _render_layering(body, content)
    elif concern == "dependencies":
        _render_dependencies(body, content)
    elif concern == "provenance":
        _render_provenance(body, content)
    elif concern == "lifecycle":
        _render_lifecycle(body, content)
    elif concern == "operator_behavior":
        _render_operator_behavior(body, content)
    elif concern == "validation":
        _render_validation(body, content)
    lines.extend(_promote_headings(body))
    lines.extend([
        "## Source and authority",
        "",
        f"This page projects `{document['_mrd']['id']}` version `{document['_mrd']['version']}`. The MRD remains authoritative; this page has no write-back authority.",
        "",
    ])
    return "\n".join(lines)


def _promote_headings(lines: list[str]) -> list[str]:
    promoted = []
    for line in lines:
        if line.startswith("#### "):
            promoted.append("### " + line[5:])
        elif line.startswith("### "):
            promoted.append("## " + line[4:])
        else:
            promoted.append(line)
    return promoted


def _render_litho_page(config: dict[str, Any], evidence: dict[str, Any]) -> str:
    provider = evidence["provider"]
    target = evidence["target"]
    lines = [
        "<!-- GENERATED — DO NOT EDIT -->",
        "# Code-derived analysis",
        "",
        '<div id="enable-section-numbers" />',
        "",
        "[Specification](001-specification.md) | [Documentation index](000-index.md)",
        "",
        "## Evidence status",
        "",
        "> **Inferred evidence.** This material was produced by Litho code analysis. It MUST NOT be treated as canonical authority and cannot override MRDs, contracts, schemas, code-owned facts, configuration, or tests.",
        "",
        f"- **Provider:** `{provider['name']}` `{provider['version']}`",
        f"- **Target:** `{target['repository']}` at `{target['revision']}`",
        f"- **Evidence class:** `{evidence['evidence_class']}`",
        "",
    ]
    for page in evidence["pages"]:
        lines.extend([f"## {page['title']}", "", f"Source artifact: `{page['path']}` (`{page['sha256']}`)", ""])
        content_lines = page["content"].splitlines()
        if content_lines and content_lines[0].startswith("# "):
            content_lines = content_lines[1:]
        lines.extend(content_lines)
        lines.append("")
    lines.extend(["## Canonical comparison", ""])
    if not evidence["assertions"]:
        lines.extend(["No structured assertions were supplied for canonical comparison.", ""])
    elif not evidence["diagnostics"]:
        lines.extend(["All supplied structured assertions matched their bound canonical JSON facts.", ""])
    else:
        lines.extend([
            "The following inferred assertions contradict their bound canonical facts. Canonical values remain authoritative:",
            "",
        ])
        for diagnostic in evidence["diagnostics"]:
            lines.extend([
                f"- `{diagnostic['code']}` — assertion `{diagnostic['assertion_id']}` at `{diagnostic['canonical_source']}#{diagnostic['json_pointer']}` observed `{json.dumps(diagnostic['observed_value'], ensure_ascii=False, sort_keys=True)}` while the canonical value is `{json.dumps(diagnostic['canonical_value'], ensure_ascii=False, sort_keys=True)}`.",
            ])
        lines.append("")
    lines.extend([
        "## Traceability",
        "",
        "Exact imported file hashes and the Litho package manifest binding are recorded in `data/litho-evidence.json` and `manifest.json`.",
        "",
    ])
    return "\n".join(lines)


def _heading_anchor(value: str) -> str:
    raw = "".join(character.lower() if character.isalnum() else "-" for character in value)
    return "-".join(part for part in raw.split("-") if part)


def _render_rules(lines: list[str], rules: list[dict[str, Any]]) -> None:
    lines.extend([
        "### Normative rules",
        "",
        "| Rule | Requirement | Enforcement |",
        "|---|---|---|",
    ])
    for rule in rules:
        lines.append(f"| `{rule['rule_id']}` | {rule['statement']} | `{rule['enforcement']}` |")
    lines.append("")


def _render_classification(lines: list[str], content: dict[str, Any]) -> None:
    lines.extend(["### Classes", "", "| Class | Name | Definition |", "|---|---|---|"])
    for item in content["classes"]:
        lines.append(f"| `{item['code']}` | {item['name']} | {item['definition']} |")
    lines.extend(["", f"### Type catalog ({content['catalog_policy']['expected_type_count']} allowed types)", "", "| Class | Type | Code | Meaning | Canonical format |", "|---|---|---|---|---|"])
    for item in content["type_catalog"]:
        lines.append(f"| `{item['class']}` | `{item['type']}` | `{item['code']}` | {item['name']} | {item['canonical_format']} |")
    lines.append("")


def _render_applicability(lines: list[str], content: dict[str, Any]) -> None:
    contract = content["selection_contract"]
    lines.extend([
        "### Selection contract",
        "",
        f"- Baseline catalog: `{contract['baseline_type_count']}` MRD types",
        f"- Default disposition: `{contract['default_disposition']}`",
        f"- Allowed dispositions: {', '.join(f'`{value}`' for value in contract['allowed_dispositions'])}",
        "",
        "#### Selection order",
        "",
    ])
    for index, step in enumerate(contract["selection_order"], start=1):
        lines.append(f"{index}. {step}")
    lines.extend([
        "",
        "### Type applicability catalog",
        "",
        "| Code | Name | Use when |",
        "|---|---|---|",
    ])
    for item in content["type_applicability"]:
        lines.append(f"| `{item['code']}` | {item['name']} | {item['use_when']} |")
    lines.append("")


def _render_ownership(lines: list[str], content: dict[str, Any]) -> None:
    contract = content["ownership_contract"]
    lines.extend([
        "### Ownership contract",
        "",
        f"- Canonical owners per governed fact: `{contract['canonical_owner_count']}`",
        f"- Non-owner posture: `{contract['non_owner_posture']}`",
        f"- Derived posture: `{contract['derived_posture']}`",
        f"- Conflict posture: `{contract['conflict_posture']}`",
        "",
        "### Canonical owner kinds",
        "",
        "| Kind | Meaning |",
        "|---|---|",
    ])
    for item in content["owner_kinds"]:
        lines.append(f"| `{item['kind']}` | {item['meaning']} |")
    lines.extend([
        "",
        "### Governed relationship vocabulary",
        "",
        "| Relationship | Meaning |",
        "|---|---|",
    ])
    for item in content["relationship_catalog"]:
        lines.append(f"| `{item['code']}` | {item['meaning']} |")
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


def _render_operator_behavior(lines: list[str], content: dict[str, Any]) -> None:
    lines.extend([
        "### Governance application lifecycle",
        "",
        "| # | Phase | Required actions | Stop when |",
        "|---:|---|---|---|",
    ])
    for phase in content["phases"]:
        actions = "; ".join(phase["required_actions"])
        stop_when = "; ".join(phase["stop_when"]) or "phase completes"
        lines.append(f"| {phase['order']} | `{phase['name']}` | {actions} | {stop_when} |")
    lines.extend(["", "### Required outputs", ""])
    for output in content["outputs"]:
        lines.append(f"- {output}")
    lines.append("")


def _render_validation(lines: list[str], content: dict[str, Any]) -> None:
    lines.extend([
        "### Enforcement modes",
        "",
        "| Mode | Meaning | Blocking |",
        "|---|---|---|",
    ])
    for mode in content["enforcement_modes"]:
        lines.append(f"| `{mode['mode']}` | {mode['meaning']} | {'Yes' if mode['blocking'] else 'No'} |")
    lines.extend(["", "### Validation dimensions", ""])
    for dimension in content["dimensions"]:
        heading = dimension["name"].replace("_", " ").title()
        lines.append(f"#### {heading}")
        lines.append("")
        for check in dimension["checks"]:
            lines.append(f"- {check}")
        lines.append("")
    result = content["result_contract"]
    lines.extend(["### Result contract", "", f"- Status: {', '.join(f'`{value}`' for value in result['status_values'])}", f"- Check keys: {', '.join(f'`{value}`' for value in result['checks'])}", f"- Diagnostics on failure: {'required' if result['diagnostics_required_on_failure'] else 'optional'}", "", "### Stable reason codes", ""])
    for code in content["reason_codes"]:
        lines.append(f"- `{code}`")
    lines.append("")
