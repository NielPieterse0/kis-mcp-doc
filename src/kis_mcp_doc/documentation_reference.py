from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .canonical import canonical_hash, canonical_source_bytes, normative_keywords_statement, resolve_repo_file
from .harvest import load_harvest_registry
from .publication_kernel import exact_bundle_diagnostics, file_declarations, write_bundle


_POLICY_PATH = "mrd/documentation/01-reference-standard.mrd.json"
_REGISTRY_PATH = "mrd/documentation/02-reference-registry.mrd.json"
_CORE_SCHEMA = "contracts/mrd/v1/mrd.schema.json"
_POLICY_SCHEMA = "contracts/documentation/reference/v1/standard.schema.json"
_REGISTRY_SCHEMA = "contracts/documentation/reference/v1/registry.schema.json"
_PUBLICATION_SCHEMA = "contracts/documentation/reference/v1/publication.schema.json"
_MANIFEST_SCHEMA = "contracts/documentation/reference/v1/manifest.schema.json"
_PUBLICATION = "publication/documentation-reference-standard.json"
_PUBLICATION_ARCHITECTURE = "mrd/documentation/03-publication-architecture.mrd.json"
_PUBLICATION_FAMILY_REGISTRY = "mrd/documentation/04-publication-family-registry.mrd.json"
_PUBLICATION_FAMILY_SCHEMA = "contracts/publication/family/v1/registry.schema.json"

_EXPECTED_REFERENCES = {
    "mcp-2026": "normative_external",
    "google-developer-style": "prescriptive_external",
    "sentry-mcp": "implementation_reference",
    "github-mcp": "implementation_reference",
    "azure-mcp": "implementation_reference",
    "playwright-mcp": "implementation_reference",
    "atlassian-rovo-mcp": "implementation_reference",
    "figma-mcp": "implementation_reference",
    "aws-labs-mcp": "implementation_reference",
    "cloudflare-mcp": "implementation_reference",
}


class DocumentationReferenceRepository:
    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()

    def load(self) -> dict[str, dict[str, Any]]:
        documents: dict[str, dict[str, Any]] = {}
        for relative in (_POLICY_PATH, _REGISTRY_PATH):
            path = self.root / relative
            try:
                document = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as error:
                raise ValueError(f"unable to load documentation reference MRD {relative}: {error}") from error
            doc_id = document.get("_mrd", {}).get("id")
            if not isinstance(doc_id, str):
                raise ValueError(f"documentation reference MRD has no id: {relative}")
            if doc_id in documents:
                raise ValueError(f"duplicate documentation reference MRD id: {doc_id}")
            documents[doc_id] = document
        return documents

    def validate(self) -> dict[str, Any]:
        try:
            documents = self.load()
        except ValueError as error:
            return _result([_diag("REFERENCE_SOURCE_INVALID", str(error))])
        return self.validate_documents(documents)

    def validate_documents(self, documents: dict[str, dict[str, Any]]) -> dict[str, Any]:
        diagnostics: list[dict[str, str]] = []
        checks = {key: "pass" for key in ("schema", "authority", "harvest_binding", "pinning", "lifecycle", "provenance")}
        policy = documents.get("KIS-DOC-CON-POL-001")
        registry = documents.get("KIS-DOC-SEM-REG-001")
        if policy is None or registry is None:
            return _result([_diag("REFERENCE_MRD_SET_INVALID", "documentation reference policy and registry MRDs are required")], checks)

        for document, schema_relative, label in (
            (policy, _POLICY_SCHEMA, "documentation reference policy"),
            (registry, _REGISTRY_SCHEMA, "documentation reference registry"),
        ):
            diagnostics.extend(_schema_diagnostics(self.root, _CORE_SCHEMA, document, f"{label} envelope"))
            diagnostics.extend(_schema_diagnostics(self.root, schema_relative, document.get("content"), label))
        if diagnostics:
            checks["schema"] = "fail"

        registry_content = registry.get("content", {})
        known_mrd_ids = set(documents)
        for path in self.root.glob("mrd/**/*.mrd.json"):
            try:
                candidate = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            candidate_id = candidate.get("_mrd", {}).get("id")
            if isinstance(candidate_id, str):
                known_mrd_ids.add(candidate_id)
        for doc_id, document in documents.items():
            provenance = document.get("_mrd", {}).get("provenance", {})
            expected_fingerprint = "sha256:" + canonical_hash(provenance.get("sources", []))
            if provenance.get("source_fingerprint") != expected_fingerprint:
                diagnostics.append(_diag("REFERENCE_PROVENANCE_FINGERPRINT_MISMATCH", f"provenance fingerprint mismatch: {doc_id}"))
                checks["provenance"] = "fail"
            for source in provenance.get("sources", []):
                if source.get("kind") != "repo_path":
                    continue
                resolved = resolve_repo_file(self.root, source.get("locator"))
                if resolved is None:
                    diagnostics.append(_diag("REFERENCE_SOURCE_UNRESOLVED", f"unresolved repository provenance source: {doc_id} -> {source.get('locator')}"))
                    checks["provenance"] = "fail"
                elif hashlib.sha256(canonical_source_bytes(resolved)).hexdigest() != source.get("sha256"):
                    diagnostics.append(_diag("REFERENCE_SOURCE_HASH_MISMATCH", f"repository provenance hash mismatch: {doc_id} -> {source.get('locator')}"))
                    checks["provenance"] = "fail"
            for dependency in document.get("_mrd", {}).get("dependencies", []):
                target_id = dependency.get("mrd_id")
                if target_id and target_id not in known_mrd_ids:
                    diagnostics.append(_diag("REFERENCE_DEPENDENCY_UNRESOLVED", f"unresolved MRD dependency: {doc_id} -> {target_id}"))
                    checks["provenance"] = "fail"
                source = dependency.get("source")
                if source and resolve_repo_file(self.root, source) is None:
                    diagnostics.append(_diag("REFERENCE_SOURCE_UNRESOLVED", f"unresolved repository source: {doc_id} -> {source}"))
                    checks["provenance"] = "fail"

        references = registry_content.get("references", [])
        evidence_records = {item.get("id"): item for item in registry_content.get("evidence_records", []) if isinstance(item, dict)}
        by_id = {item.get("id"): item for item in references if isinstance(item, dict)}
        if set(by_id) != set(_EXPECTED_REFERENCES):
            diagnostics.append(_diag("REFERENCE_BASELINE_MISMATCH", "reference registry must contain the approved ten-source baseline"))
            checks["authority"] = "fail"
        for source_id, expected_role in _EXPECTED_REFERENCES.items():
            source = by_id.get(source_id)
            if source is None:
                continue
            if source.get("role") != expected_role:
                diagnostics.append(_diag("REFERENCE_ROLE_MISMATCH", f"reference {source_id} must use role {expected_role}"))
                checks["authority"] = "fail"
            if source.get("role") != "canonical_kis" and source.get("may_define_kis_facts") is not False:
                diagnostics.append(_diag("REFERENCE_AUTHORITY_PROMOTION_FORBIDDEN", f"non-canonical reference cannot define KIS facts: {source_id}"))
                checks["authority"] = "fail"
            lifecycle = source.get("lifecycle", {})
            if lifecycle.get("state") == "active" and source.get("pin") is None:
                diagnostics.append(_diag("REFERENCE_PIN_REQUIRED", f"active reference must be pinned: {source_id}"))
                checks["pinning"] = "fail"
            pin = source.get("pin") or {}
            if pin.get("kind") == "research_evidence_sha256":
                evidence = evidence_records.get(pin.get("revision"))
                if evidence is None or evidence.get("sha256") != pin.get("value"):
                    diagnostics.append(_diag("REFERENCE_EVIDENCE_PIN_MISMATCH", f"research evidence pin is not bound to a registered evidence record: {source_id}"))
                    checks["pinning"] = "fail"
            if lifecycle.get("state") == "superseded" and not lifecycle.get("superseded_by"):
                diagnostics.append(_diag("REFERENCE_SUPERSESSION_INVALID", f"superseded reference must identify its replacement: {source_id}"))
                checks["lifecycle"] = "fail"

        harvest_sources: dict[str, dict[str, Any]] = {}
        try:
            harvest = load_harvest_registry(self.root)
            harvest_sources = {item["id"]: item for item in harvest["sources"]}
        except ValueError as error:
            diagnostics.append(_diag("HARVEST_REGISTRY_INVALID", str(error)))
            checks["harvest_binding"] = "fail"
        for source in references:
            harvest_id = source.get("harvest_source_id")
            if not harvest_id:
                continue
            harvest_source = harvest_sources.get(harvest_id)
            if harvest_source is None:
                diagnostics.append(_diag("REFERENCE_HARVEST_BINDING_MISSING", f"unknown harvest source id: {harvest_id}"))
                checks["harvest_binding"] = "fail"
                continue
            pin = source.get("pin") or {}
            expected_hash = harvest_source.get("content_sha256")
            if expected_hash and pin.get("kind") == "content_sha256" and pin.get("value") != expected_hash:
                diagnostics.append(_diag("REFERENCE_HARVEST_PIN_MISMATCH", f"reference pin differs from harvest source: {source.get('id')}"))
                checks["harvest_binding"] = "fail"
        return _result(diagnostics, checks)


def validate_documentation_reference_publication(
    repository: DocumentationReferenceRepository,
) -> dict[str, Any]:
    try:
        config = _load_json(repository.root / _PUBLICATION, "documentation reference publication")
    except ValueError as error:
        return _verification([_diag("REFERENCE_PUBLICATION_INVALID", str(error))])
    diagnostics = _schema_diagnostics(
        repository.root,
        _PUBLICATION_SCHEMA,
        config,
        "documentation reference publication",
    )
    return _verification(diagnostics)


def build_documentation_reference_standard(
    repository: DocumentationReferenceRepository,
    output: Path,
    *,
    replace: bool = False,
) -> dict[str, Any]:
    validation = repository.validate()
    if validation["status"] != "valid":
        raise ValueError(f"documentation reference standard is invalid: {validation['diagnostics']}")
    documents = repository.load()
    config = _load_json(repository.root / _PUBLICATION, "documentation reference publication")
    publication_diagnostics = _schema_diagnostics(repository.root, _PUBLICATION_SCHEMA, config, "documentation reference publication")
    if publication_diagnostics:
        raise ValueError(f"documentation reference publication is invalid: {publication_diagnostics}")
    files = _build_files(documents, config)
    manifest = _build_manifest(repository, documents, config, files, validation)
    manifest_diagnostics = _schema_diagnostics(repository.root, _MANIFEST_SCHEMA, manifest, "documentation reference build manifest")
    if manifest_diagnostics:
        raise ValueError(f"documentation reference build manifest is invalid: {manifest_diagnostics}")
    write_bundle(Path(output), files, manifest, replace=replace)
    return manifest


def verify_documentation_reference_standard(
    repository: DocumentationReferenceRepository,
    output: Path,
) -> dict[str, Any]:
    diagnostics: list[dict[str, str]] = []
    validation = repository.validate()
    if validation["status"] != "valid":
        diagnostics.extend(validation["diagnostics"])
        return _verification(diagnostics)
    output = Path(output)
    manifest_path = output / "manifest.json"
    if not manifest_path.is_file():
        return _verification([_diag("GENERATED_MANIFEST_MISSING", "manifest.json is missing")])
    try:
        actual_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return _verification([_diag("GENERATED_MANIFEST_INVALID", str(error))])
    manifest_schema_diagnostics = _schema_diagnostics(repository.root, _MANIFEST_SCHEMA, actual_manifest, "documentation reference build manifest")
    if manifest_schema_diagnostics:
        diagnostics.extend(manifest_schema_diagnostics)
    documents = repository.load()
    config = _load_json(repository.root / _PUBLICATION, "documentation reference publication")
    publication_schema_diagnostics = _schema_diagnostics(repository.root, _PUBLICATION_SCHEMA, config, "documentation reference publication")
    if publication_schema_diagnostics:
        diagnostics.extend(publication_schema_diagnostics)
    expected_files = _build_files(documents, config)
    expected_manifest = _build_manifest(repository, documents, config, expected_files, validation)
    if actual_manifest != expected_manifest:
        diagnostics.append(_diag("GENERATED_MANIFEST_MISMATCH", "manifest differs from deterministic current inputs"))
    diagnostics.extend(
        exact_bundle_diagnostics(
            output,
            expected_files,
            expected_manifest,
            code_prefix=None,
        )
    )
    return _verification(diagnostics)


def _build_files(documents: dict[str, dict[str, Any]], config: dict[str, Any]) -> dict[str, bytes]:
    policy = documents["KIS-DOC-CON-POL-001"]["content"]
    registry = documents["KIS-DOC-SEM-REG-001"]["content"]
    return {
        "000-index.md": _render_index(config).encode("utf-8"),
        "001-specification.md": _render_specification(config, policy, registry).encode("utf-8"),
        "002-reference-catalogue.md": _render_catalogue(registry).encode("utf-8"),
        "data/reference-registry.json": _json_bytes(registry),
    }


def _build_manifest(
    repository: DocumentationReferenceRepository,
    documents: dict[str, dict[str, Any]],
    config: dict[str, Any],
    files: dict[str, bytes],
    validation: dict[str, Any],
) -> dict[str, Any]:
    inputs = []
    for relative in (
        _POLICY_PATH,
        _REGISTRY_PATH,
        _PUBLICATION,
        _PUBLICATION_ARCHITECTURE,
        _PUBLICATION_FAMILY_REGISTRY,
        _PUBLICATION_FAMILY_SCHEMA,
        _CORE_SCHEMA,
        _POLICY_SCHEMA,
        _REGISTRY_SCHEMA,
        _PUBLICATION_SCHEMA,
        _MANIFEST_SCHEMA,
        "publication/harvest-sources.json",
        "src/kis_mcp_doc/canonical.py",
        "src/kis_mcp_doc/publication_kernel.py",
        "src/kis_mcp_doc/documentation_reference.py",
    ):
        payload = canonical_source_bytes(repository.root / relative)
        inputs.append({"path": relative, "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)})
    declarations = file_declarations(files)
    return {
        "contract": {"name": "documentation-reference-standard-build", "version": 1},
        "specification": {key: config[key] for key in ("title", "version", "status", "layout_profile")},
        "inputs": inputs,
        "input_set_sha256": canonical_hash(inputs),
        "validation": validation,
        "files": declarations,
        "bundle_sha256": canonical_hash(declarations),
    }


def _render_index(config: dict[str, Any]) -> str:
    return "\n".join([
        "<!-- GENERATED -- DO NOT EDIT -->",
        f"# {config['title']} — documentation index",
        "",
        "This generated collection is a review projection. The documentation MRDs and referenced canonical sources remain authoritative.",
        "",
        "- [Specification](001-specification.md)",
        "- [Reference catalogue](002-reference-catalogue.md)",
        "- [Machine-readable reference registry](data/reference-registry.json)",
        "- [Build manifest](manifest.json)",
        "",
    ])


def _render_specification(config: dict[str, Any], policy: dict[str, Any], registry: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED -- DO NOT EDIT -->",
        f"# {config['title']}",
        "",
        '<div id="enable-section-numbers" />',
        "",
        config["subtitle"],
        "",
        "This specification governs how documentation references can influence KIS documentation. It keeps source authority separate from presentation guidance and implementation evidence.",
        "",
        normative_keywords_statement(),
        "",
        "## Authority model",
        "",
    ]
    for item in policy["authority_model"]:
        permission = "may define KIS facts" if item["may_define_kis_facts"] else "MUST NOT define KIS facts"
        lines.append(f"- **`{item['role']}`:** {item['domain']}; {permission}.")
    lines.extend(["", "## Documentation output classes", ""])
    for item in policy["output_classes"]:
        label = item["class"].replace("human_readable", "human-readable").replace("_", " ")
        lines.extend([f"### {label.capitalize()}", "", item["purpose"], "", item["source_rule"], ""])
    lines.extend(["## Reference registry", "", registry["refresh_policy"], "", registry["licensing_policy"], "", "## Conflict behavior", ""])
    lines.append("When a reference conflicts with a canonical owner, KIS surfaces the conflict and keeps the canonical owner unchanged. Unsupported authority promotion and active unpinned references fail validation.")
    lines.extend(["", "## Requirements", ""])
    for rule in policy["requirements"]:
        lines.extend([f"### {rule['rule_id']}", "", rule["statement"], ""])
    lines.extend(["## Source and authority", "", "This page is generated from `KIS-DOC-CON-POL-001` and `KIS-DOC-SEM-REG-001`. It has no write-back authority.", ""])
    return "\n".join(lines)


def _render_catalogue(registry: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED -- DO NOT EDIT -->",
        "# Documentation reference catalogue",
        "",
        "Each entry has a bounded role. Only the applicable canonical owner can define a KIS fact.",
        "",
        "| Reference | Role | Permitted use | Pin | Lifecycle |",
        "|---|---|---|---|---|",
    ]
    for source in registry["references"]:
        uses = ", ".join(f"`{item}`" for item in source["permitted_uses"])
        pin = source["pin"]
        pin_text = "none" if pin is None else f"`{pin['kind']}` at `{pin['revision']}`"
        lines.append(f"| {source['name']} | `{source['role']}` | {uses} | {pin_text} | `{source['lifecycle']['state']}` |")
    lines.extend(["", "## Licensing and refresh", "", registry["licensing_policy"], "", registry["refresh_policy"], ""])
    return "\n".join(lines)


def _schema_diagnostics(root: Path, schema_relative: str, instance: object, label: str) -> list[dict[str, str]]:
    try:
        schema = _load_json(root / schema_relative, f"{label} schema")
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda error: tuple(str(part) for part in error.absolute_path))
    except (ValueError, Exception) as error:
        return [_diag("REFERENCE_SCHEMA_INVALID", str(error))]
    diagnostics = []
    for error in errors:
        location = "/".join(str(part) for part in error.absolute_path) or "$"
        diagnostics.append(_diag("REFERENCE_SCHEMA_VALIDATION_FAILED", f"{label} invalid at {location}: {error.message}"))
    return diagnostics


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"unable to load {label}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def _diag(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _result(diagnostics: list[dict[str, str]], checks: dict[str, str] | None = None) -> dict[str, Any]:
    if checks is None:
        checks = {key: "pass" for key in ("schema", "authority", "harvest_binding", "pinning", "lifecycle", "provenance")}
    if diagnostics and "fail" not in checks.values():
        checks["provenance"] = "fail"
    return {"status": "invalid" if diagnostics else "valid", "checks": checks, "diagnostics": diagnostics}


def _verification(diagnostics: list[dict[str, str]]) -> dict[str, Any]:
    return {"status": "invalid" if diagnostics else "valid", "diagnostics": diagnostics}
