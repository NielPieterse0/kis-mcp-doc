from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .canonical import canonical_hash
from .repository_governance import RepositoryGovernanceRepository, enforcement_projection
from .publication_kernel import (
    bundle_manifest_fields,
    exact_bundle_diagnostics,
    file_declarations,
    write_bundle,
)

_POLICY = "prescriptives/documentation/05-repository-human-bundle.mrd.json"
_REGISTRY = "prescriptives/documentation/04-publication-family-registry.mrd.json"
_GOVERNANCE_REGISTRY = "prescriptives/governance/02-prescriptive-artefact-registry.json"
_CONFIG = "publication/repository-docs.json"
_GENERATOR = "src/kis_mcp_doc/repository_docs.py"
_OUTPUT_CLASS = "human_documentation"
_EXCLUDED_PARTS = {".git", ".work", ".venv", ".temp", ".pytest_cache", ".ruff_cache", "__pycache__", "generated"}
_EXCLUDED_PART_SUFFIXES = (".egg-info",)
_EXCLUDED_PREFIXES = (
    "prescriptives/work-management/",
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
    if any(part.endswith(_EXCLUDED_PART_SUFFIXES) for part in relative.parts):
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
    if relative.startswith("prescriptives/"):
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
        return relative, "prescriptive_record", "self"
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
                "semantic_role": "derived_generated",
                "governance_slot": "generated",
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


def _governance_registry_relationships(root: Path, records: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    registry = _load_json(root / _GOVERNANCE_REGISTRY)
    relations: list[dict[str, Any]] = []
    for entry in registry.get("entries", []):
        source = entry.get("canonical_path")
        if source not in records:
            continue
        for relationship_type, targets in entry.get("relationships", {}).items():
            for target in targets:
                if target in records:
                    relations.append({
                        "source": source,
                        "target": target,
                        "type": relationship_type,
                        "intent": "governed_repository_relationship",
                        "evidence": _GOVERNANCE_REGISTRY,
                        "fact_quality": "declared",
                    })
    return relations


def repository_model(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    records = {
        path.relative_to(root).as_posix(): _artifact_record(root, path)
        for path in _repository_sources(root)
    }
    governance_repository = RepositoryGovernanceRepository(root)
    for relative, record in records.items():
        slots = governance_repository.slot_matches(relative)
        record["semantic_role"] = governance_repository.role_for(relative)
        record["governance_slot"] = slots[0]["slot_id"] if len(slots) == 1 else None
    relations = _mrd_relationships(root, records)
    relations.extend(_governance_registry_relationships(root, records))
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
        "- [Repository Governance](007-repository-governance.md)",
        "- [Directory Grammar](008-directory-grammar.md)",
        "- [Rule assurance and enforcement](009-rule-assurance-and-enforcement.md)",
        "- [Prescriptive coverage](010-prescriptive-coverage.md)",
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
        "- `prescriptives/`: governed prescriptive authority, organized by current justified domain.",
        "- `contracts/`: schemas and machine-enforceable contracts.",
        "- `src/kis_mcp_doc/`: generators, validators, publication, site, search, release, and repository behavior.",
        "- `publication/`: publication-family and delivery configuration.",
        "- `tests/`: executable conformance and regression evidence.",
        "- `scripts/` and `.github/`: local and provider automation.",
        "- `generated/`: deterministic downstream outputs; never source authority.",
    ]
    publication = _header("Publication and generated documentation", "The publication registry is the single family inventory for generated specifications and human documentation.")
    registry = _load_json(root / _REGISTRY)
    publication += ["## Registered families", "", "| Family | Output | Classes | Published to Pages |", "|---|---|---|---|"]
    for family in registry["content"]["families"]:
        pages = "Yes" if family["publish_to_site"] else "No — standalone family"
        publication.append(f"| `{family['id']}` | `{family['output']}` | {', '.join(family['output_classes'])} | {pages} |")
    publication += [
        "",
        "The shared publication kernel validates every registered family, dispatches adapters, writes complete bundles atomically, and compares exact generated inventories and bytes for drift.",
        "",
        "The `publish_to_site` decision is explicit for every family. The documentation site, public search index, and GitHub Pages release include only families marked `true`; standalone families remain generated and verified but are not reader-facing Pages content.",
    ]
    verification = _header("Verification and operations", "Use executable evidence to decide whether repository documentation and generated surfaces are current.")
    verification += [
        "## Canonical verification",
        "",
        "Run `pwsh -File scripts/verify.ps1` for the repository-wide gate. It runs tests, governance and publication validation, generated-output checks, search/site/release checks, public-repository hygiene, and whitespace verification.",
        "",
        "The gate verifies both semantics and bytes: publication-family validation requires an explicit Pages decision, regression tests enforce the public-family boundary, and generated-output checks reconstruct publication, search, site, and release artefacts and fail on any stale or mismatched tracked output.",
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
    governance_source = _load_json(root / "prescriptives/governance/01-repository-governance.json")
    grammar_source = _load_json(root / "prescriptives/governance/03-directory-grammar.json")
    prescriptive_registry = _load_json(root / "prescriptives/governance/02-prescriptive-artefact-registry.json")
    governance_page = _header("Repository Governance", "Canonical repository-wide authority is projected here without write-back authority.")
    governance_page += [
        "Repository Governance is distinct from the MRD Specification. Governance controls repository-wide authority, ownership, placement, assurance, evidence precedence, change application, and verification policy; the MRD Specification defines what a conforming MRD is.", "",
        "## Governed construct vocabulary", "", "| Construct | Normative | Meaning |", "|---|---|---|",
    ]
    for item in governance_source["governed_vocabulary"]["constructs"]:
        governance_page.append(f"| `{item['name']}` | {'Yes' if item['normative'] else 'No'} | {item['meaning']} |")
    governance_page += ["", "## Relationship law", "", "| Relationship | From | To | Authority effect |", "|---|---|---|---|"]
    for item in governance_source["governed_vocabulary"]["relationships"]:
        governance_page.append(f"| `{item['name']}` | {', '.join(item['from'])} | {', '.join(item['to'])} | `{item['authority_effect']}` |")
    governance_page += ["", "## Conformance evidence precedence", "", "Normative ownership and observed implementation state are separate planes. Lower-precedence evidence cannot override fresher higher-precedence conformance evidence.", "", "| Rank | Evidence class | Examples |", "|---:|---|---|"]
    for item in governance_source["evidence_model"]["conformance_evidence_precedence"]:
        governance_page.append(f"| {item['rank']} | `{item['class']}` | {', '.join(item['examples'])} |")
    governance_page += ["", "## Validation policy", "", governance_source["validation_policy"]["review_policy"], "", "Validation order: " + " -> ".join(f"`{x}`" for x in governance_source["validation_policy"]["order"]) + ".", ""]
    governance_page += ["## Governed rules", "", "| Rule | Scope | Origin | Method | Failure code |", "|---|---|---|---|---|"]
    for rule in governance_source["rules"]:
        governance_page.append(f"| `{rule['rule_id']}` | {', '.join(rule['scope']['applies_to'])} | `{rule['rationale']['origin']['id']}` | `{rule['verification']['method']}` | `{rule['verification']['failure_code']}` |")
    governance_page.append("")

    grammar_page = _header("Repository Structure Definition and Directory Grammar", "This generated structure definition projects the canonical Directory Grammar. Every persistent governed artefact has exactly one legal slot; unknown or ambiguous placement fails closed.")
    grammar_page += [grammar_source["placement_law"], "", "## Slot contracts", "", "| Slot | Patterns | Purpose | Permitted / prohibited types | Roles | Authority | Relationships | Editability / lifecycle | Verification | Origin |", "|---|---|---|---|---|---|---|---|---|---|"]
    for slot in grammar_source["slots"]:
        authority_text = ", ".join(f"{k}={v}" for k, v in sorted(slot["authority_constraints"].items()))
        grammar_page.append(
            f"| `{slot['slot_id']}` | {'; '.join(f'`{x}`' for x in slot['patterns'])} | {slot['purpose']} | "
            f"{', '.join(slot['permitted_artefact_types'])} / {', '.join(slot['prohibited_artefact_types']) or 'none'} | "
            f"{', '.join(slot['allowed_semantic_roles'])} | {authority_text} | {', '.join(slot['allowed_relationships'])} | "
            f"`{slot['editability']}` / `{slot['lifecycle']}` / `{slot['retention']}` | `{slot['verification']['entry_point']}` | `{slot['origin']['id']}` |"
        )
    grammar_page += ["", "## Relationship contracts", "", "| Registry key | Semantic relationship | Direction | Source roles | Target roles |", "|---|---|---|---|---|"]
    for relationship in grammar_source.get("relationship_contracts", []):
        grammar_page.append(
            f"| `{relationship['registry_key']}` | `{relationship['semantic_relationship']}` | `{relationship['direction']}` | "
            f"{', '.join(f'`{role}`' for role in relationship['source_roles'])} | {', '.join(f'`{role}`' for role in relationship['target_roles'])} |"
        )
    grammar_page += ["", "## Reserved workspace", "", "`.work` is disposable/non-product authority. It is not published, cannot be required as product input, and cannot be promoted into persistent product structure without amending the Directory Grammar first.", ""]

    assurance_page = _header("Rule assurance and enforcement", "Every mandatory Repository Governance rule closes the loop from authority through implementation, verification, fixture, evidence, and residual review where justified.")
    assurance_page += ["| Rule | Implementation | Validator / execution | Negative fixture | Evidence | Residual review |", "|---|---|---|---|---|---|"]
    for rule in governance_source["rules"]:
        v = rule["verification"]; residual = v["residual_review"]
        review = "None" if residual is None else f"{residual['reviewer_capability']}: {residual['bounded_question']} — {residual['justification']}"
        assurance_page.append(f"| `{rule['rule_id']}` | {', '.join(x['artifact'] + '::' + x['control'] for x in rule['implementation'])} | `{v['validator']}` via `{v['execution_point']}` | `{v['negative_fixture']}` | `{rule['evidence']['location']}` at `{rule['evidence']['evaluated_revision']}` | {review} |")
    assurance_page += ["", "The machine-readable [enforcement register](data/enforcement-register.json) is generated from the canonical rules above. It is not independently authored authority.", ""]

    coverage_page = _header("Prescriptive coverage", "Every registered prescriptive artefact has a governed human-projection disposition.")
    coverage_page += ["| Identity | Canonical path | Owner | Projection disposition | Projection route |", "|---|---|---|---|---|"]
    for entry in prescriptive_registry["entries"]:
        projection = entry["human_projection"]
        route = projection.get("location") or projection.get("reason", "")
        coverage_page.append(f"| `{entry['identity']}` | `{entry['canonical_path']}` | `{entry['authoritative_owner']}` | `{projection['disposition']}` | `{route}` |")
    coverage_page.append("")

    return {
        "000-index.md": ("\n".join(index) + "\n").encode("utf-8"),
        "001-architecture-and-authority.md": ("\n".join(authority) + "\n").encode("utf-8"),
        "002-repository-map.md": ("\n".join(repo_map) + "\n").encode("utf-8"),
        "003-publication-and-generated-documentation.md": ("\n".join(publication) + "\n").encode("utf-8"),
        "004-verification-and-operations.md": ("\n".join(verification) + "\n").encode("utf-8"),
        "005-artefact-metadata-and-relationships.md": ("\n".join(metadata) + "\n").encode("utf-8"),
        "006-coverage-and-freshness.md": ("\n".join(freshness) + "\n").encode("utf-8"),
        "007-repository-governance.md": ("\n".join(governance_page) + "\n").encode("utf-8"),
        "008-directory-grammar.md": ("\n".join(grammar_page) + "\n").encode("utf-8"),
        "009-rule-assurance-and-enforcement.md": ("\n".join(assurance_page) + "\n").encode("utf-8"),
        "010-prescriptive-coverage.md": ("\n".join(coverage_page) + "\n").encode("utf-8"),
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
    governance_source = _load_json(root / "prescriptives/governance/01-repository-governance.json")
    grammar_source = _load_json(root / "prescriptives/governance/03-directory-grammar.json")
    prescriptive_registry = _load_json(root / "prescriptives/governance/02-prescriptive-artefact-registry.json")
    files["data/governance-rules.json"] = _json_bytes({"schema_version": 1, "authority": "derived_non_authoritative", "generated_from": "prescriptives/governance/01-repository-governance.json", "rules": governance_source["rules"]})
    files["data/enforcement-register.json"] = _json_bytes(enforcement_projection(governance_source))
    files["data/directory-grammar.json"] = _json_bytes({"schema_version": 1, "authority": "derived_non_authoritative", "generated_from": "prescriptives/governance/03-directory-grammar.json", "slots": grammar_source["slots"], "placement_law": grammar_source["placement_law"]})
    files["data/prescriptive-coverage.json"] = _json_bytes({"schema_version": 1, "authority": "derived_non_authoritative", "generated_from": "prescriptives/governance/02-prescriptive-artefact-registry.json", "entries": [{"identity": x["identity"], "canonical_path": x["canonical_path"], "authoritative_owner": x["authoritative_owner"], "human_projection": x["human_projection"]} for x in prescriptive_registry["entries"]]})
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
        if policy.get("_mrd", {}).get("id") != "urn:uuid:0e84ae43-f74a-5065-a5e2-b21e105376b8":
            raise ValueError("repository human bundle policy must be urn:uuid:0e84ae43-f74a-5065-a5e2-b21e105376b8")
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
