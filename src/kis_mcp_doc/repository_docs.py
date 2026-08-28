from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .canonical import canonical_hash
from .publication_kernel import (
    bundle_manifest_fields,
    exact_bundle_diagnostics,
    file_declarations,
    write_bundle,
)

_POLICY = "mrd/documentation/05-repository-human-bundle.mrd.json"
_REGISTRY = "mrd/documentation/04-publication-family-registry.mrd.json"
_CONFIG = "publication/repository-docs.json"
_GENERATOR = "src/kis_mcp_doc/repository_docs.py"
_OUTPUT_CLASS = "human_documentation"
_EXCLUDED_PARTS = {".git", ".work", ".venv", ".temp", ".pytest_cache", "__pycache__", "generated"}
_EXCLUDED_PREFIXES = (
    "mrd/work-management/",
    "contracts/work-management/",
    "evidence/work-management/",
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def _is_repository_source(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    normalized = relative.as_posix()
    if any(part in _EXCLUDED_PARTS for part in relative.parts):
        return False
    if any(normalized.startswith(prefix) for prefix in _EXCLUDED_PREFIXES):
        return False
    return path.is_file()


def _repository_sources(root: Path) -> list[Path]:
    return sorted(
        (path for path in root.rglob("*") if _is_repository_source(path, root)),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def _artifact_kind(relative: str) -> str:
    path = Path(relative)
    if relative == "AGENTS.md":
        return "repository_authority"
    if relative.startswith("mrd/"):
        return "machine_readable_record"
    if relative.startswith("contracts/"):
        return "contract_or_schema"
    if relative.startswith("publication/"):
        return "publication_configuration"
    if relative.startswith("src/"):
        return "implementation"
    if relative.startswith("tests/"):
        return "verification"
    if relative.startswith("scripts/") or relative.startswith(".github/"):
        return "automation"
    if path.name in {"pyproject.toml", "uv.lock"} or relative.startswith("tooling/"):
        return "build_or_runtime_configuration"
    if path.suffix.lower() in {".md"}:
        return "human_surface"
    return "repository_artifact"


def _authority(relative: str, kind: str) -> tuple[str, str, str]:
    if relative == "AGENTS.md":
        return "AGENTS.md", "repository", "self"
    if kind == "machine_readable_record":
        return relative, "mrd", "self"
    if kind == "contract_or_schema":
        return relative, "contract", "self"
    if kind in {"implementation", "verification", "automation", "build_or_runtime_configuration"}:
        return relative, "executable", "AGENTS.md"
    if kind == "publication_configuration":
        return relative, "configuration", _REGISTRY
    if kind == "human_surface":
        return "publication/public-repository.json", "generated_projection", "publication/public-repository.json"
    return relative, "repository", "AGENTS.md"


def _artifact_record(root: Path, path: Path) -> dict[str, Any]:
    relative = path.relative_to(root).as_posix()
    payload = path.read_bytes()
    kind = _artifact_kind(relative)
    owner, authority, governing = _authority(relative, kind)
    title = path.name
    logical_version = None
    source_fingerprint = None
    status = "current"
    if path.suffix.lower() == ".json":
        try:
            value = _load_json(path)
            header = value.get("_mrd", {}) if isinstance(value.get("_mrd"), dict) else value
            title = str(header.get("title") or title)
            logical_version = header.get("version") if isinstance(header.get("version"), str) else None
            status = header.get("status") if isinstance(header.get("status"), str) else status
            provenance = header.get("provenance", {}) if isinstance(header.get("provenance"), dict) else {}
            source_fingerprint = provenance.get("source_fingerprint") if isinstance(provenance.get("source_fingerprint"), str) else None
        except (OSError, ValueError, json.JSONDecodeError):
            pass
    return {
        "identity": f"repo:{relative}",
        "title": title,
        "artefact_kind": kind,
        "repository": "NielPieterse0/kis-mcp-doc",
        "canonical_path": relative,
        "source_of_truth": owner,
        "status": status,
        "record_mode": "prescriptive" if kind in {"repository_authority", "machine_readable_record", "contract_or_schema"} else "descriptive",
        "editability": "generated_only" if kind == "human_surface" else "source_editable",
        "logical_version": logical_version,
        "exact_git_revision": None,
        "content_hash": "sha256:" + hashlib.sha256(payload).hexdigest(),
        "source_fingerprint": source_fingerprint,
        "baseline_release_identity": None,
        "owner": owner,
        "authority": authority,
        "governing_artefact": governing,
        "provenance": {"kind": "repository_file", "observed": True},
        "sources": [relative],
        "related_artefacts": [],
        "dependencies": [],
        "generated_from": [],
        "validation_relationships": [],
        "implementation_relationships": [],
        "publication_relationships": [],
        "supersedes": [],
        "superseded_by": None,
        "migration_trace": [],
        "summary": None,
        "scope_in": [],
        "scope_out": [],
        "keywords": sorted({kind, path.suffix.lower().lstrip(".") or "file"}),
        "change_classification": None,
        "impact_relationships": [],
        "freshness": {"mode": "content_hash", "drift_checked_by": "repository-docs manifest"},
    }


def _mrd_relationships(root: Path, records: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    relations: list[dict[str, Any]] = []
    id_to_path: dict[str, str] = {}
    for relative, record in records.items():
        if record["artefact_kind"] != "machine_readable_record":
            continue
        value = _load_json(root / relative)
        mrd_id = value.get("_mrd", {}).get("id")
        if isinstance(mrd_id, str):
            id_to_path[mrd_id] = relative
    for relative, record in records.items():
        if record["artefact_kind"] != "machine_readable_record":
            continue
        value = _load_json(root / relative)
        for dependency in value.get("_mrd", {}).get("dependencies", []):
            if not isinstance(dependency, dict):
                continue
            target = None
            if isinstance(dependency.get("mrd_id"), str):
                target = id_to_path.get(dependency["mrd_id"])
            source = dependency.get("source")
            if target is None and isinstance(source, str) and source.startswith("repo:"):
                candidate = source[5:]
                if candidate in records:
                    target = candidate
            if target:
                relations.append({
                    "source": relative,
                    "target": target,
                    "type": dependency.get("relationship", "references"),
                    "intent": "declared_mrd_dependency",
                    "evidence": relative,
                    "fact_quality": "observed",
                })
    return relations


def _publication_relationships(root: Path, records: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    registry = _load_json(root / _REGISTRY)
    relations: list[dict[str, Any]] = []
    generated: list[dict[str, Any]] = []
    for family in registry.get("content", {}).get("families", []):
        config = family.get("publication_config")
        output = family.get("output")
        if isinstance(config, str) and config in records:
            relations.append({
                "source": config,
                "target": _REGISTRY,
                "type": "registered_by",
                "intent": family["id"],
                "evidence": _REGISTRY,
                "fact_quality": "observed",
            })
        if isinstance(output, str):
            generated.append({
                "identity": f"generated-family:{family['id']}",
                "title": family["title"],
                "artefact_kind": "generated_publication_family",
                "repository": "NielPieterse0/kis-mcp-doc",
                "canonical_path": output,
                "source_of_truth": config,
                "status": "derived",
                "record_mode": "descriptive",
                "editability": "generated_only",
                "logical_version": None,
                "exact_git_revision": None,
                "content_hash": None,
                "source_fingerprint": None,
                "baseline_release_identity": None,
                "owner": family.get("semantic_owner"),
                "authority": "generated_projection",
                "governing_artefact": _REGISTRY,
                "provenance": {"kind": "publication_registry_declaration", "observed": True},
                "sources": [config, _REGISTRY],
                "related_artefacts": [],
                "dependencies": [],
                "generated_from": [config],
                "validation_relationships": [],
                "implementation_relationships": [],
                "publication_relationships": [{"target": _REGISTRY, "type": "registered_by", "intent": family["id"]}],
                "supersedes": [],
                "superseded_by": None,
                "migration_trace": [],
                "summary": None,
                "scope_in": [],
                "scope_out": [],
                "keywords": ["generated", "publication", family["id"]],
                "change_classification": None,
                "impact_relationships": [],
                "freshness": {"mode": "family_manifest", "drift_checked_by": "publications-check-generated"},
            })
    return relations, generated


def repository_model(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    records = {
        path.relative_to(root).as_posix(): _artifact_record(root, path)
        for path in _repository_sources(root)
    }
    relations = _mrd_relationships(root, records)
    publication_relations, generated = _publication_relationships(root, records)
    relations.extend(publication_relations)
    for relative, record in records.items():
        governing = record["governing_artefact"]
        if governing != relative and governing in records:
            relations.append({
                "source": relative,
                "target": governing,
                "type": "governed_by",
                "intent": "authority_direction",
                "evidence": "repository classification policy",
                "fact_quality": "derived_from_path_policy",
            })
    for relation in relations:
        source_record = records.get(relation["source"])
        if source_record is None:
            continue
        link = {"target": relation["target"], "type": relation["type"], "intent": relation["intent"]}
        source_record["related_artefacts"].append(link)
        if relation["intent"] == "declared_mrd_dependency":
            source_record["dependencies"].append(link)
        if relation["type"] == "registered_by":
            source_record["publication_relationships"].append(link)
    artefacts = list(records.values()) + generated
    return {
        "schema_version": 1,
        "repository": "NielPieterse0/kis-mcp-doc",
        "revision_binding": {
            "mode": "external_git_manifest",
            "exact_git_revision": None,
            "reason": "containing Git commit identity is bound outside tracked generated content to avoid circular identity",
        },
        "artefacts": sorted(artefacts, key=lambda item: item["identity"]),
        "relationships": sorted(relations, key=lambda item: (item["source"], item["type"], item["target"])),
    }


def _header(title: str, subtitle: str) -> list[str]:
    return ["<!-- GENERATED — DO NOT EDIT -->", f"# {title}", "", subtitle, ""]


def _pages(root: Path, config: dict[str, Any], model: dict[str, Any]) -> dict[str, bytes]:
    counts: dict[str, int] = {}
    for artefact in model["artefacts"]:
        counts[artefact["artefact_kind"]] = counts.get(artefact["artefact_kind"], 0) + 1
    index = _header(config["title"], config["subtitle"])
    index += [
        "This bundle explains the current kis-mcp-doc repository from its governed machine and executable sources. It is a derived view and never writes back to authority.",
        "",
        "## Start here",
        "",
        "- [Architecture and authority](001-architecture-and-authority.md)",
        "- [Repository map](002-repository-map.md)",
        "- [Publication and generated documentation](003-publication-and-generated-documentation.md)",
        "- [Verification and operations](004-verification-and-operations.md)",
        "- [Artefact metadata and relationships](005-artefact-metadata-and-relationships.md)",
        "- [Coverage and freshness](006-coverage-and-freshness.md)",
    ]
    authority = _header("Architecture and authority", "Understand where repository truth lives and how generated documentation relates to it.")
    authority += [
        "`AGENTS.md` defines repository operating authority. Canonical facts then remain in the applicable MRDs, contracts, schemas, configuration, implementation, tests, and automation.",
        "",
        "Generated documentation is a one-way projection. Change the owning source and regenerate; do not edit generated pages as authority.",
        "",
        "## Repository role",
        "",
        "kis-mcp-doc is the engineering and proving ground for KIS Governance and Knowledge/Docs capabilities. Parent KIS remains platform authority until a capability is formally adopted there.",
        "",
        "## Work Management boundary",
        "",
        "Work Management remains a separate documentation and specification family. This repository bundle describes the kis-mcp-doc product and publication system without merging Work Management semantics into it.",
    ]
    repo_map = _header("Repository map", "Use the repository by authority and responsibility instead of treating every file as equivalent.")
    repo_map += ["## Current artefact classes", "", "| Artefact class | Count |", "|---|---:|"]
    repo_map += [f"| `{kind}` | {count} |" for kind, count in sorted(counts.items())]
    repo_map += [
        "",
        "## Main areas",
        "",
        "- `mrd/`: governed machine-readable domain authority.",
        "- `contracts/`: schemas and machine-enforceable contracts.",
        "- `src/kis_mcp_doc/`: generators, validators, publication, site, search, release, and repository behavior.",
        "- `publication/`: publication-family and delivery configuration.",
        "- `tests/`: executable conformance and regression evidence.",
        "- `scripts/` and `.github/`: local and provider automation.",
        "- `generated/`: deterministic downstream outputs; never source authority.",
    ]
    publication = _header("Publication and generated documentation", "The publication registry is the single family inventory for generated specifications and human documentation.")
    registry = _load_json(root / _REGISTRY)
    publication += ["## Registered families", "", "| Family | Output | Classes |", "|---|---|---|"]
    for family in registry["content"]["families"]:
        publication.append(f"| `{family['id']}` | `{family['output']}` | {', '.join(family['output_classes'])} |")
    publication += [
        "",
        "The shared publication kernel validates family registration, dispatches adapters, writes complete bundles atomically, and compares exact generated inventories and bytes for drift.",
        "",
        "The documentation site and static search derive routes from this same registry. The release package then bundles the verified site for GitHub Pages.",
    ]
    verification = _header("Verification and operations", "Use executable evidence to decide whether repository documentation and generated surfaces are current.")
    verification += [
        "## Canonical verification",
        "",
        "Run `pwsh -File scripts/verify.ps1` for the repository-wide gate. It runs tests, governance and publication validation, generated-output checks, search/site/release checks, public-repository hygiene, and whitespace verification.",
        "",
        "## Development rule",
        "",
        "During implementation, run focused affected checks. Before publication, the governed change workflow performs its required scope and verification checks; the pull request owns full exact-head provider verification.",
        "",
        "## Runtime safety",
        "",
        "Local Windows verification uses `scripts/runtime-preflight.ps1` and the governed Python runtime policy before dependency synchronization or tests.",
    ]
    metadata = _header("Artefact metadata and relationships", "Use the generated inventory for stable discovery, lineage, graph traversal, and future impact analysis.")
    metadata += [
        "Each observed source artefact records stable repository identity, canonical path, source-of-truth direction, status, record mode, editability, content hash, owner, authority class, governing artefact, provenance class, and freshness evidence.",
        "",
        "Relationships are typed and evidence-bearing. Declared MRD dependencies are observed facts. Path-derived governance links are explicitly marked as derived from repository policy instead of being presented as source-declared facts.",
        "",
        "Generated publication families are virtual graph nodes declared from the canonical publication registry. They retain their semantic owner and source configuration without becoming authority.",
        "",
        "See [artefact-inventory.json](data/artefact-inventory.json) and [relationship-graph.json](data/relationship-graph.json) for the machine-readable projection.",
    ]
    freshness = _header("Coverage and freshness", "A repository bundle is complete only when its declared source set and generated output agree.")
    freshness += [
        f"The current source inventory contains **{sum(counts.values())}** source or declared generated-family artefacts.",
        "",
        "## Freshness model",
        "",
        "- Every source file is content-hashed in the repository-docs manifest.",
        "- The artefact inventory repeats per-artefact content hashes for direct trace and comparison.",
        "- Exact generated-file inventory and bytes are checked by `publications-check-generated`.",
        "- Site, search, and release verification independently reject stale downstream bundles.",
        "- Exact containing Git revision is bound externally through Git/provider evidence rather than embedded into tracked generated content, avoiding a circular commit identity.",
        "",
        "## Coverage exclusions",
        "",
        "Historical `.work` records, temporary/runtime state, virtual environments, caches, and generated outputs are not re-ingested as current repository source authority. Work Management remains a separate publication family.",
    ]
    return {
        "000-index.md": ("\n".join(index) + "\n").encode("utf-8"),
        "001-architecture-and-authority.md": ("\n".join(authority) + "\n").encode("utf-8"),
        "002-repository-map.md": ("\n".join(repo_map) + "\n").encode("utf-8"),
        "003-publication-and-generated-documentation.md": ("\n".join(publication) + "\n").encode("utf-8"),
        "004-verification-and-operations.md": ("\n".join(verification) + "\n").encode("utf-8"),
        "005-artefact-metadata-and-relationships.md": ("\n".join(metadata) + "\n").encode("utf-8"),
        "006-coverage-and-freshness.md": ("\n".join(freshness) + "\n").encode("utf-8"),
    }


def _expected_bundle(root: Path, family: dict[str, Any]) -> tuple[dict[str, bytes], dict[str, Any]]:
    root = Path(root).resolve()
    config = _load_json(root / _CONFIG)
    if config.get("documentation_reference", {}).get("output_class") != _OUTPUT_CLASS:
        raise ValueError("repository documentation must declare human_documentation output class")
    if set(family.get("output_classes", [])) != {_OUTPUT_CLASS}:
        raise ValueError("repository documentation family must register only human_documentation")
    model = repository_model(root)
    files = _pages(root, config, model)
    files["data/artefact-inventory.json"] = _json_bytes({
        "schema_version": model["schema_version"],
        "repository": model["repository"],
        "revision_binding": model["revision_binding"],
        "artefacts": model["artefacts"],
    })
    files["data/relationship-graph.json"] = _json_bytes({
        "schema_version": 1,
        "repository": model["repository"],
        "relationships": model["relationships"],
    })
    source_files = []
    for path in _repository_sources(root):
        relative = path.relative_to(root).as_posix()
        payload = path.read_bytes()
        source_files.append({"path": relative, "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)})
    coverage = {
        "schema_version": 1,
        "source_files": len(source_files),
        "artefacts": len(model["artefacts"]),
        "relationships": len(model["relationships"]),
        "excluded_source_classes": ["historical_change_records", "runtime_state", "generated_outputs", "work_management_human_consolidation"],
    }
    files["data/coverage-report.json"] = _json_bytes(coverage)
    manifest = {
        "contract": {"name": "kis-repository-human-documentation", "version": 1},
        "family_id": family["id"],
        "output_class": _OUTPUT_CLASS,
        "generator": {"name": "kis-mcp-doc", "algorithm": "repository-docs-v1"},
        "source_fingerprint": "sha256:" + canonical_hash(source_files),
        "inputs": {"source_files": source_files},
        "coverage": coverage,
        "files": file_declarations(files),
        **bundle_manifest_fields(files),
    }
    return files, manifest


def validate_repository_docs(root: Path, family: dict[str, Any]) -> dict[str, Any]:
    try:
        policy = _load_json(Path(root) / _POLICY)
        if policy.get("_mrd", {}).get("id") != "KIS-DOC-CON-POL-003":
            raise ValueError("repository human bundle policy must be KIS-DOC-CON-POL-003")
        _expected_bundle(Path(root), family)
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as error:
        return {"status": "invalid", "diagnostics": [{"code": "REPOSITORY_DOCUMENTATION_INVALID", "message": str(error)}]}
    return {"status": "valid", "diagnostics": []}


def build_repository_docs(root: Path, family: dict[str, Any], *, output: Path | None = None, replace: bool = False) -> dict[str, Any]:
    validation = validate_repository_docs(root, family)
    if validation["status"] != "valid":
        raise ValueError(validation["diagnostics"][0]["message"])
    files, manifest = _expected_bundle(Path(root), family)
    target = Path(output) if output is not None else Path(root) / family["output"]
    write_bundle(target, files, manifest, replace=replace)
    return manifest


def verify_repository_docs(root: Path, family: dict[str, Any]) -> dict[str, Any]:
    validation = validate_repository_docs(root, family)
    if validation["status"] != "valid":
        return validation
    try:
        files, manifest = _expected_bundle(Path(root), family)
        diagnostics = exact_bundle_diagnostics(Path(root) / family["output"], files, manifest, code_prefix="REPOSITORY_DOCUMENTATION")
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as error:
        diagnostics = [{"code": "REPOSITORY_DOCUMENTATION_VERIFY_FAILED", "message": str(error)}]
    return {"status": "invalid" if diagnostics else "valid", "diagnostics": diagnostics}
