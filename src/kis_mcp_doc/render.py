from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .canonical import canonical_hash, canonical_source_bytes, normative_keywords_statement, resolve_repo_file
from .governance import GovernanceRepository
from .harvest import load_harvest_registry
from .litho import load_litho_evidence
from .publication_kernel import exact_bundle_diagnostics, file_declarations, write_bundle


_PUBLICATION_SCHEMA = "contracts/publication/v2/governance-spec.schema.json"
_MANIFEST_SCHEMA = "contracts/publication/v2/manifest.schema.json"
_LITHO_SCHEMA = "contracts/documentation/litho/v1/package.schema.json"
_HARVEST_SCHEMA = "contracts/documentation/harvest/v1/registry.schema.json"
_HARVEST_REGISTRY = "publication/harvest-sources.json"
_DOCUMENTATION_POLICY = "prescriptives/documentation/01-reference-standard.mrd.json"
_DOCUMENTATION_REGISTRY = "prescriptives/documentation/02-reference-registry.mrd.json"
_DOCUMENTATION_PUBLICATION = "publication/documentation-reference-standard.json"
_PUBLICATION_ARCHITECTURE = "prescriptives/documentation/03-publication-architecture.mrd.json"
_PUBLICATION_FAMILY_REGISTRY = "prescriptives/documentation/04-publication-family-registry.mrd.json"
_PUBLICATION_FAMILY_SCHEMA = "contracts/publication/family/v1/registry.schema.json"
_DOCUMENTATION_OUTPUT_CLASS = "human_readable_specification"
_REFERENCE_OUTPUT_CLASS = "generated_reference"


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
    write_bundle(output, files, manifest, replace=replace)
    return manifest


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

    diagnostics.extend(
        exact_bundle_diagnostics(
            output,
            expected_payloads,
            manifest,
            code_prefix=None,
        )
    )
    declared_files = {item["path"]: item for item in manifest_files}
    for relative in expected_payloads:
        path = output / Path(*relative.split("/"))
        if not path.is_file():
            continue
        actual_payload = path.read_bytes()
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


def validate_governance_publication(
    repository: GovernanceRepository,
    publication_path: Path,
) -> dict[str, Any]:
    try:
        _load_publication_config(repository, publication_path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        return _verification_result([
            _verification_diag("PUBLICATION_CONFIG_INVALID", str(error))
        ])
    return _verification_result([])


def _load_publication_config(repository: GovernanceRepository, publication_path: Path) -> dict[str, Any]:
    config = json.loads(Path(publication_path).read_text(encoding="utf-8"))
    schema_config = dict(config)
    schema_config.pop("documentation_reference", None)
    _validate_contract(repository.root, _PUBLICATION_SCHEMA, schema_config, "publication configuration")
    _validate_documentation_reference_binding(repository.root, config)
    return config


def _validate_documentation_reference_binding(root: Path, config: dict[str, Any]) -> None:
    binding = config.get("documentation_reference")
    expected = {
        "output_class": _DOCUMENTATION_OUTPUT_CLASS,
        "policy_mrd": "KIS-DOC-CON-POL-001",
        "registry_mrd": "KIS-DOC-SEM-REG-001",
    }
    if binding != expected:
        raise ValueError(f"publication documentation_reference must equal {expected}")

    policy = json.loads((root / _DOCUMENTATION_POLICY).read_text(encoding="utf-8"))
    registry = json.loads((root / _DOCUMENTATION_REGISTRY).read_text(encoding="utf-8"))
    if policy.get("_mrd", {}).get("id") != binding["policy_mrd"]:
        raise ValueError("documentation reference policy binding does not resolve")
    if registry.get("_mrd", {}).get("id") != binding["registry_mrd"]:
        raise ValueError("documentation reference registry binding does not resolve")
    output_classes = {item.get("class") for item in policy.get("content", {}).get("output_classes", [])}
    if binding["output_class"] not in output_classes:
        raise ValueError("documentation reference output class is not governed by the policy")
    if _REFERENCE_OUTPUT_CLASS not in output_classes:
        raise ValueError("generated-reference output class is not governed by the policy")
    authority_roles = {
        item.get("role"): item.get("may_define_kis_facts")
        for item in policy.get("content", {}).get("authority_model", [])
    }
    for reference in registry.get("content", {}).get("references", []):
        role = reference.get("role")
        if role not in authority_roles:
            raise ValueError(f"documentation reference role is not governed: {role}")
        if reference.get("may_define_kis_facts") is not False:
            raise ValueError(f"external documentation reference cannot define KIS facts: {reference.get('id')}")


def _generator_source_declarations(repository: GovernanceRepository) -> list[dict[str, Any]]:
    declarations = []
    for relative in (
        "src/kis_mcp_doc/canonical.py",
        "src/kis_mcp_doc/governance.py",
        "src/kis_mcp_doc/harvest.py",
        "src/kis_mcp_doc/litho.py",
        "src/kis_mcp_doc/publication_kernel.py",
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
    return file_declarations(files)


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
    reference_pages = _governance_reference_pages(ordered)
    coverage = _governance_semantic_coverage(ordered)
    files: dict[str, bytes] = {
        "000-index.md": _render_corpus_index(config, ordered, litho_evidence, reference_pages).encode("utf-8"),
        "001-specification.md": root_page,
        config["output_file"]: root_page,
        "data/mrd-index.json": _json_bytes(_build_index(repository, documents)),
        "data/dependency-map.json": _json_bytes(_build_dependency_map(documents)),
        "data/semantic-coverage.json": _json_bytes(coverage),
    }
    for index, document in enumerate(ordered):
        previous = None if index == 0 else ordered[index - 1]
        following = None if index + 1 == len(ordered) else ordered[index + 1]
        files[_document_page_name(document)] = _render_document_page(
            config, document, previous=previous, following=following
        ).encode("utf-8")
    for relative, payload in reference_pages.items():
        files[relative] = payload.encode("utf-8")
    if litho_evidence is not None:
        files["090-code-derived-analysis.md"] = _render_litho_page(config, litho_evidence).encode("utf-8")
        files["data/litho-evidence.json"] = _json_bytes(_normalized_litho_evidence(litho_evidence))
    _validate_governance_semantic_coverage(files, coverage)
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
        | {
            _DOCUMENTATION_POLICY,
            _DOCUMENTATION_REGISTRY,
            _DOCUMENTATION_PUBLICATION,
            _PUBLICATION_ARCHITECTURE,
            _PUBLICATION_FAMILY_REGISTRY,
            _PUBLICATION_FAMILY_SCHEMA,
        }
    )
    declarations = []
    for relative in paths:
        resolved = resolve_repo_file(repository.root, "repo:" + relative)
        if resolved is None:
            raise ValueError(f"canonical source declaration does not resolve inside repository: {relative}")
        payload = canonical_source_bytes(resolved)
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
    reference_pages: dict[str, str],
) -> str:
    lines = [
        "<!-- GENERATED — DO NOT EDIT -->",
        f"# {config['title']} — documentation index",
        "",
        "This generated collection follows the `mcp-spec` publication profile. Source MRDs remain authoritative; these pages are review projections.",
        "",
        "## Specification pages",
        "",
        "- [Specification](001-specification.md)",
    ]
    for document in documents:
        lines.append(f"- [{document['content']['heading']}]({_document_page_name(document)})")
    if litho_evidence is not None:
        lines.append("- [Code-derived analysis](090-code-derived-analysis.md) — inferred evidence, not authority")
    lines.extend(["", "## Generated reference", ""])
    reference_titles = {
        "020-applicability-catalog.md": "MRD applicability catalog",
        "021-relationship-vocabulary.md": "Governed relationship vocabulary",
        "022-validation-reason-codes.md": "Validation reason codes",
    }
    for relative in reference_pages:
        lines.append(f"- [{reference_titles[relative]}]({relative})")
    lines.extend([
        "",
        "## Machine-readable traceability",
        "",
        "- [MRD index](data/mrd-index.json)",
        "- [Dependency map](data/dependency-map.json)",
        "- [Semantic coverage](data/semantic-coverage.json)",
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
        "The publication follows `KIS-DOC-CON-POL-001` as a `human_readable_specification`. MCP 2026 applies only within its bounded protocol domain, Google guidance affects presentation only, and implementation references cannot create or override KIS governance facts.",
        "",
        normative_keywords_statement(),
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
        "See the [documentation index](000-index.md), [MRD index](data/mrd-index.json), [dependency map](data/dependency-map.json), [semantic coverage](data/semantic-coverage.json), and [build manifest](manifest.json) for exact source identities, page/anchor mappings, hashes, and generated-file declarations.",
        "",
    ])
    return "\n".join(lines)


def _render_document_page(
    config: dict[str, Any],
    document: dict[str, Any],
    *,
    previous: dict[str, Any] | None,
    following: dict[str, Any] | None,
) -> str:
    content = document["content"]
    lines = [
        "<!-- GENERATED — DO NOT EDIT -->",
        f"# {content['heading']}",
        "",
        '<div id="enable-section-numbers" />',
        "",
        _governance_navigation(document, previous, following),
        "",
        _page_intro(content),
        "",
    ]
    body: list[str] = []
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
    _render_rule_traceability(body, content.get("rules", []))
    lines.extend(_promote_headings(body))
    lines.extend([
        "## Source and authority",
        "",
        f"This page projects `{document['_mrd']['id']}` version `{document['_mrd']['version']}`. The MRD remains authoritative; this page has no write-back authority.",
        "",
    ])
    return "\n".join(lines)


def _governance_navigation(
    document: dict[str, Any],
    previous: dict[str, Any] | None,
    following: dict[str, Any] | None,
) -> str:
    parts = []
    if previous is None:
        parts.append("[Previous: Specification](001-specification.md)")
    else:
        parts.append(f"[Previous: {previous['content']['heading']}]({_document_page_name(previous)})")
    if following is not None:
        parts.append(f"[Next: {following['content']['heading']}]({_document_page_name(following)})")
    parts.append("[Index](000-index.md)")
    return " | ".join(parts)


def _reference_header(title: str, owner_page: str, owner_title: str) -> list[str]:
    return [
        "<!-- GENERATED — DO NOT EDIT -->",
        f"# {title}",
        "",
        '<div id="enable-section-numbers" />',
        "",
        f"[Owning specification chapter: {owner_title}]({owner_page}) | [Documentation index](000-index.md)",
        "",
        f"> **Output class:** `{_REFERENCE_OUTPUT_CLASS}`. This page is an exact lookup projection of canonical Governance authority. It has no write-back authority.",
        "",
    ]


def _governance_reference_pages(documents: list[dict[str, Any]]) -> dict[str, str]:
    by_concern = {doc["content"]["concern"]: doc for doc in documents}
    applicability = by_concern["applicability"]
    ownership = by_concern["ownership"]
    validation = by_concern["validation"]

    lines = _reference_header("MRD applicability catalog", _document_page_name(applicability), applicability["content"]["heading"])
    lines.extend(["Use this catalog after the specification's minimum-sufficient selection process identifies the governed need. The table does not require one artifact per row.", "", "| Code | Name | Use when |", "|---|---|---|"])
    for item in applicability["content"]["type_applicability"]:
        lines.append(f"| <span id=\"fact-applicability-{_heading_anchor(item['code'])}\"></span>`{item['code']}` | {item['name']} | {item['use_when']} |")
    lines.append("")
    lines.extend(["", "## Source and authority", "", f"This reference projects `{applicability['_mrd']['id']}` version `{applicability['_mrd']['version']}`. The MRD remains authoritative.", ""])
    applicability_page = "\n".join(lines)

    lines = _reference_header("Governed relationship vocabulary", _document_page_name(ownership), ownership["content"]["heading"])
    lines.extend(["Relationships preserve authority by expressing how one governed artifact relates to another without creating duplicate ownership.", "", "| Relationship | Meaning |", "|---|---|"])
    for item in ownership["content"]["relationship_catalog"]:
        lines.append(f"| <span id=\"fact-relationship-{_heading_anchor(item['code'])}\"></span>`{item['code']}` | {item['meaning']} |")
    lines.append("")
    lines.extend(["", "## Source and authority", "", f"This reference projects `{ownership['_mrd']['id']}` version `{ownership['_mrd']['version']}`. The MRD remains authoritative.", ""])
    relationship_page = "\n".join(lines)

    lines = _reference_header("Validation reason codes", _document_page_name(validation), validation["content"]["heading"])
    lines.extend(["Use these stable codes to diagnose validation failures without parsing human-readable error text.", ""])
    for code in validation["content"]["reason_codes"]:
        lines.append(f"- <span id=\"fact-reason-{_heading_anchor(code)}\"></span>`{code}`")
    lines.append("")
    lines.extend(["", "## Source and authority", "", f"This reference projects `{validation['_mrd']['id']}` version `{validation['_mrd']['version']}`. The MRD remains authoritative.", ""])
    reason_page = "\n".join(lines)

    return {
        "020-applicability-catalog.md": applicability_page,
        "021-relationship-vocabulary.md": relationship_page,
        "022-validation-reason-codes.md": reason_page,
    }


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


def _rule_anchor(rule_id: str) -> str:
    return f"rule-{_heading_anchor(rule_id)}"


def _governance_semantic_coverage(documents: list[dict[str, Any]]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    by_concern = {document["content"]["concern"]: document for document in documents}
    for document in documents:
        page = _document_page_name(document)
        for rule in document["content"].get("rules", []):
            entries.append({
                "kind": "rule",
                "id": rule["rule_id"],
                "source_mrd": document["_mrd"]["id"],
                "source_version": document["_mrd"]["version"],
                "page": page,
                "anchor": _rule_anchor(rule["rule_id"]),
                "enforcement": rule["enforcement"],
            })
    for item in by_concern["applicability"]["content"]["type_applicability"]:
        entries.append({"kind":"reference_fact","id":f"applicability:{item['code']}","source_mrd":by_concern["applicability"]["_mrd"]["id"],"page":"020-applicability-catalog.md","anchor":f"fact-applicability-{_heading_anchor(item['code'])}"})
    for item in by_concern["ownership"]["content"]["relationship_catalog"]:
        entries.append({"kind":"reference_fact","id":f"relationship:{item['code']}","source_mrd":by_concern["ownership"]["_mrd"]["id"],"page":"021-relationship-vocabulary.md","anchor":f"fact-relationship-{_heading_anchor(item['code'])}"})
    for code in by_concern["validation"]["content"]["reason_codes"]:
        entries.append({"kind":"reference_fact","id":f"reason:{code}","source_mrd":by_concern["validation"]["_mrd"]["id"],"page":"022-validation-reason-codes.md","anchor":f"fact-reason-{_heading_anchor(code)}"})
    return {"schema_version":1,"family":"governance-spec","entries":sorted(entries,key=lambda item:(item["kind"],item["id"]))}


def _validate_governance_semantic_coverage(files: dict[str, bytes], coverage: dict[str, Any]) -> None:
    seen: set[tuple[str, str]] = set()
    for entry in coverage["entries"]:
        key = (entry["kind"], entry["id"])
        if key in seen:
            raise ValueError(f"duplicate Governance semantic coverage entry: {key}")
        seen.add(key)
        page = entry["page"]
        if page not in files:
            raise ValueError(f"Governance semantic coverage page does not exist: {page}")
        marker = f'id="{entry["anchor"]}"'.encode("utf-8")
        if marker not in files[page]:
            raise ValueError(f"Governance semantic coverage anchor does not resolve: {page}#{entry['anchor']}")


def _governance_ownership_diagram(content: dict[str, Any]) -> list[str]:
    contract = content["ownership_contract"]
    return [
        "### Authority and ownership model", "",
        "The diagram groups the four fields of the canonical ownership contract. Connector lines show contract composition only; they do not invent relationships between governed actors.", "",
        "```mermaid", "flowchart TD",
        '  contract["Canonical ownership contract"]',
        f'  contract --> owner["Canonical owner count: {contract["canonical_owner_count"]}"]',
        f'  contract --> nonowner["Non-owner posture: {contract["non_owner_posture"]}"]',
        f'  contract --> derived["Derived posture: {contract["derived_posture"]}"]',
        f'  contract --> conflict["Conflict posture: {contract["conflict_posture"]}"]',
        "```", "",
    ]


def _governance_lifecycle_diagram(content: dict[str, Any]) -> list[str]:
    lines = ["### Lifecycle diagram", "", "Each record mode is shown as its own canonical state machine. Only transitions declared by the lifecycle MRD are drawn.", "", "```mermaid", "flowchart LR"]
    for lifecycle in content["lifecycles"]:
        mode = _heading_anchor(lifecycle["record_mode"])
        lines.append(f'  subgraph {mode}["{lifecycle["record_mode"]}"]')
        for state in lifecycle["states"]:
            node = f"{mode}_{_heading_anchor(state)}"
            lines.append(f'    {node}["{state}"]')
        for transition in lifecycle["transitions"]:
            source = f"{mode}_{_heading_anchor(transition['from'])}"
            target = f"{mode}_{_heading_anchor(transition['to'])}"
            lines.append(f"    {source} --> {target}")
        lines.append("  end")
    lines.extend(["```", ""])
    return lines


def _format_count(value: int) -> str:
    words = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
    return words[value] if 0 <= value < len(words) else str(value)


def _page_intro(content: dict[str, Any]) -> str:
    concern = content["concern"]
    intros = {
        "classification": "KIS MRDs use a functional classification model. Classification describes what an artifact does, independent of where a repository stores or implements it.",
        "applicability": "Governance artifacts are selected according to the need being governed. The 47-type MRD catalog is a vocabulary for choosing the minimum sufficient set, not a checklist that every repository or change must populate.",
        "ownership": "Every governed fact has one current canonical owner. Other artifacts can reference or project that fact, but they do not become independent authority by repeating it.",
        "layering": "Authority layers constrain the direction of MRD dependencies. They express which governed facts can depend on which other facts, not repository layout or implementation order.",
        "dependencies": "Dependencies make authority relationships explicit and verifiable. Each dependency identifies either another MRD or a canonical repository source that the MRD requires.",
        "provenance": "Provenance identifies the authority, origin, and quality of governed facts. It keeps authored prescription, captured observations, and generated projections distinct.",
        "lifecycle": "MRD lifecycle depends on record mode. Prescriptive authority, descriptive evidence, and generated metadata follow different states and mutability rules.",
        "operator_behavior": "kis-op applies governance as an ordered workflow from authority resolution through verification and reporting. Blocking failures stop the workflow rather than becoming inferred authority.",
        "validation": "Governance validation combines structural checks, deterministic semantic checks, workflow controls, generation checks, and explicit review gates. Blocking failures fail closed and produce diagnosable results.",
    }
    return intros[concern]


def _render_rule_statements(lines: list[str], rules: list[dict[str, Any]]) -> None:
    for rule in rules:
        lines.extend([f'<span id="{_rule_anchor(rule["rule_id"])}"></span>', rule["statement"], ""])


def _render_rule_traceability(lines: list[str], rules: list[dict[str, Any]]) -> None:
    lines.extend([
        "### Requirement traceability",
        "",
        "The following table preserves the stable rule identifier and enforcement binding for each requirement stated in this chapter:",
        "",
        "| Rule | Enforcement |",
        "|---|---|",
    ])
    for rule in rules:
        lines.append(f"| `{rule['rule_id']}` | `{rule['enforcement']}` |")
    lines.append("")


def _render_classification(lines: list[str], content: dict[str, Any]) -> None:
    policy = content["catalog_policy"]
    lines.extend([
        "### Classification requirements",
        "",
        f"The catalog contains {policy['expected_class_count']} functional classes and {policy['expected_type_count']} allowed MRD types. Classification is based on function so that the same governed need keeps the same meaning across repository layouts and technology choices.",
        "",
    ])
    _render_rule_statements(lines, content["rules"])
    lines.extend([
        "### Classes",
        "",
        "The following table defines the functional classes used to group MRD types:",
        "",
        "| Class | Name | Definition |",
        "|---|---|---|",
    ])
    for item in content["classes"]:
        lines.append(f"| `{item['code']}` | {item['name']} | {item['definition']} |")
    lines.extend([
        "",
        f"### Type catalog ({policy['expected_type_count']} allowed types)",
        "",
        "The following table lists each governed type and its canonical representation format:",
        "",
        "| Class | Type | Code | Meaning | Canonical format |",
        "|---|---|---|---|---|",
    ])
    for item in content["type_catalog"]:
        lines.append(f"| `{item['class']}` | `{item['type']}` | `{item['code']}` | {item['name']} | {item['canonical_format']} |")
    lines.append("")


def _render_applicability(lines: list[str], content: dict[str, Any]) -> None:
    contract = content["selection_contract"]
    rules = content["rules"]
    dispositions = ", ".join(f"`{value}`" for value in contract["allowed_dispositions"])
    lines.extend([
        "### Selecting governance artifacts",
        "",
        f"Selection starts from the {contract['baseline_type_count']}-type catalog with `{contract['default_disposition']}` as the default disposition. A selected type can be classified as {dispositions}. The goal is to represent the governed need without creating duplicate authority.",
        "",
    ])
    _render_rule_statements(lines, rules[:3])
    lines.extend([
        "### Selection process",
        "",
        "Apply the following process in order. It starts with the governed need and only considers a catalog extension after existing types have been tested for fit:",
        "",
    ])
    for index, step in enumerate(contract["selection_order"], start=1):
        lines.append(f"{index}. {step[0].upper() + step[1:]}.")
    lines.extend([
        "",
        f'<span id="{_rule_anchor(rules[3]["rule_id"])}"></span>',
        rules[3]["statement"],
        "",
        "### Applicability reference",
        "",
        "The complete 47-type selection catalog is an exact lookup surface. See the [MRD applicability catalog](020-applicability-catalog.md) for every type, name, and applicability trigger.",
        "",
        "### Extending the catalog",
        "",
        "Technology and stack choices do not create new MRD types by themselves. First represent the need with the existing functional vocabulary when that vocabulary is sufficient.",
        "",
    ])
    _render_rule_statements(lines, rules[4:])


def _render_ownership(lines: list[str], content: dict[str, Any]) -> None:
    contract = content["ownership_contract"]
    rules = content["rules"]
    lines.extend([
        "### Canonical ownership",
        "",
        f"The ownership contract assigns {_format_count(contract['canonical_owner_count'])} current canonical owner to each governed fact. Non-owners reference rather than restate authority, derived artifacts remain projections, and ownership conflicts are surfaced and resolved against the current owner.",
        "",
    ])
    _render_rule_statements(lines, rules[:3])
    lines.extend(_governance_ownership_diagram(content))
    lines.extend([
        "### Canonical owner kinds",
        "",
        "The following table identifies the kinds of sources that can own governed facts:",
        "",
        "| Kind | Meaning |",
        "|---|---|",
    ])
    for item in content["owner_kinds"]:
        lines.append(f"| `{item['kind']}` | {item['meaning']} |")
    lines.extend([
        "",
        "### Governed relationships",
        "",
        "Non-owning artifacts preserve authority by declaring typed relationships to the sources they depend on, implement, evidence, project, or reference. The vocabulary is governed and closed; ad hoc labels cannot create new relationship semantics.",
        "",
        "See the [governed relationship vocabulary](021-relationship-vocabulary.md) for every relationship code and meaning.",
        "",
    ])
    _render_rule_statements(lines, rules[3:])


def _render_layering(lines: list[str], content: dict[str, Any]) -> None:
    lines.extend([
        "### Authority model",
        "",
        f"The governance model uses {_format_count(len(content['layers']))} authority layers from `L0` through `L5`. Lower layer numbers have higher authority for dependency direction; the layer does not describe storage location or implementation order.",
        "",
    ])
    _render_rule_statements(lines, content["rules"])
    lines.extend([
        "### Authority layers",
        "",
        "The following table defines what each authority layer represents:",
        "",
        "| Layer | Name | Interpretation |",
        "|---|---|---|",
    ])
    for item in content["layers"]:
        lines.append(f"| `{item['code']}` | {item['name']} | {item['interpretation']} |")
    lines.extend([
        "",
        "### Direction examples",
        "",
        "The following examples show valid and invalid dependency directions under the authority ordering:",
        "",
        "| Source | Target | Valid |",
        "|---|---|---|",
    ])
    for item in content["examples"]:
        lines.append(f"| `{item['source']}` | `{item['target']}` | {'Yes' if item['valid'] else 'No'} |")
    lines.append("")


def _render_dependencies(lines: list[str], content: dict[str, Any]) -> None:
    lines.extend([
        "### Dependency model",
        "",
        "A governed dependency must identify a stable target, resolve successfully, follow the authority-layer direction, and remain part of an acyclic graph. Generated dependency maps are projections of that validated graph, not a second source of truth.",
        "",
    ])
    _render_rule_statements(lines, content["rules"])
    lines.extend([
        "### Dependency targets",
        "",
        "Dependencies use one of the following target forms. MRD dependencies use stable MRD IDs; canonical repository dependencies use `repo:` paths:",
        "",
        "| Kind | Field | Example |",
        "|---|---|---|",
    ])
    for item in content["target_forms"]:
        lines.append(f"| {item['kind']} | `{item['field']}` | `{item['example']}` |")
    lines.append("")


def _render_provenance(lines: list[str], content: dict[str, Any]) -> None:
    lines.extend([
        "### Provenance model",
        "",
        "Record mode expresses both authority and mutability, while fact quality describes how directly a fact is supported by admitted evidence. This separation prevents harvested, inferred, or generated material from silently becoming prescriptive authority.",
        "",
    ])
    _render_rule_statements(lines, content["rules"])
    lines.extend([
        "### Record modes",
        "",
        "The following table defines the authority and mutability posture of each record mode:",
        "",
        "| Record mode | Meaning | Mutability |",
        "|---|---|---|",
    ])
    for item in content["record_modes"]:
        lines.append(f"| `{item['mode']}` | {item['meaning']} | `{item['mutability']}` |")
    lines.extend([
        "",
        "### Fact quality",
        "",
        "Fact quality records whether a fact is direct, deterministically derived, or inferred:",
        "",
        "| Quality | Meaning |",
        "|---|---|",
    ])
    for item in content["fact_qualities"]:
        lines.append(f"| `{item['quality']}` | {item['meaning']} |")
    lines.extend([
        "",
        "### Provenance source kinds",
        "",
        "Each provenance source kind has a resolution or fingerprint requirement, as shown in the following table:",
        "",
        "| Kind | Resolution requirement |",
        "|---|---|",
    ])
    for item in content["source_kinds"]:
        lines.append(f"| `{item['kind']}` | {item['resolution']} |")
    lines.append("")


def _render_lifecycle(lines: list[str], content: dict[str, Any]) -> None:
    lines.extend(_governance_lifecycle_diagram(content))
    lines.extend([
        "### State machines",
        "",
        "Each record mode has its own state machine. Prescriptive MRDs move from draft authority to active authority and then supersession; descriptive evidence and generated metadata use lifecycles that match their different mutability rules.",
        "",
        "The following table shows the allowed states and transitions for each record mode:",
        "",
        "| Record mode | States | Allowed transitions |",
        "|---|---|---|",
    ])
    for item in content["lifecycles"]:
        transitions = "; ".join(f"{edge['from']} → {edge['to']}" for edge in item["transitions"])
        lines.append(f"| `{item['record_mode']}` | {' → '.join(item['states'])} | {transitions} |")
    lines.extend(["", "### Lifecycle requirements", ""])
    _render_rule_statements(lines, content["rules"])


def _render_operator_behavior(lines: list[str], content: dict[str, Any]) -> None:
    rules = content["rules"]
    lines.extend([
        "### Applying governance",
        "",
        f"kis-op applies governance through {_format_count(len(content['phases']))} ordered phases. It resolves authority and applicable MRDs before mutation, validates blocking conditions before execution, and keeps generated review surfaces downstream of validated sources.",
        "",
    ])
    _render_rule_statements(lines, rules[:4])
    lines.extend([
        "### Governance application lifecycle",
        "",
        "The following table shows each phase, the actions kis-op performs, and the condition that stops progress when the phase cannot complete safely:",
        "",
        "| # | Phase | Required actions | Stop when |",
        "|---:|---|---|---|",
    ])
    for phase in content["phases"]:
        actions = "; ".join(phase["required_actions"])
        stop_when = "; ".join(phase["stop_when"]) or "phase completes"
        lines.append(f"| {phase['order']} | `{phase['name']}` | {actions} | {stop_when} |")
    lines.extend([
        "",
        "### Required outputs",
        "",
        "A completed governance application produces the following review and machine-readable outputs:",
        "",
    ])
    for output in content["outputs"]:
        lines.append(f"- {output}")
    lines.extend(["", "### Scope and review boundaries", ""])
    _render_rule_statements(lines, rules[4:])


def _render_validation(lines: list[str], content: dict[str, Any]) -> None:
    lines.extend([
        "### Validation model",
        "",
        "Validation first establishes that the governance set is structurally valid, then evaluates the cross-record semantics that depend on that structure. A blocking failure prevents the affected governance state from being accepted as valid and produces machine-readable diagnostics.",
        "",
    ])
    _render_rule_statements(lines, content["rules"])
    lines.extend([
        "### Enforcement modes",
        "",
        "The following table identifies where each kind of governance requirement is enforced and whether failure blocks progress:",
        "",
        "| Mode | Meaning | Blocking |",
        "|---|---|---|",
    ])
    for mode in content["enforcement_modes"]:
        lines.append(f"| `{mode['mode']}` | {mode['meaning']} | {'Yes' if mode['blocking'] else 'No'} |")
    lines.extend([
        "",
        "### Validation dimensions",
        "",
        "Validation covers the following dimensions. Each dimension groups checks that evaluate one governance concern:",
        "",
    ])
    for dimension in content["dimensions"]:
        heading = dimension["name"].replace("_", " ").capitalize()
        lines.append(f"#### {heading}")
        lines.append("")
        for check in dimension["checks"]:
            lines.append(f"- {check}")
        lines.append("")
    result = content["result_contract"]
    statuses = ", ".join(f"`{value}`" for value in result["status_values"])
    checks = ", ".join(f"`{value}`" for value in result["checks"])
    diagnostics = "required" if result["diagnostics_required_on_failure"] else "optional"
    lines.extend([
        "### Validation result",
        "",
        f"A validation result has one of these statuses: {statuses}. It reports these check keys: {checks}. Machine-readable diagnostics on failure are {diagnostics}.",
        "",
        "### Stable reason codes",
        "",
        "Validation failures use stable reason codes so callers can diagnose failure without parsing prose. The complete catalog is exact generated reference rather than part of the conceptual flow.",
        "",
        "See the [validation reason-code reference](022-validation-reason-codes.md) for the complete list.",
        "",
    ])
