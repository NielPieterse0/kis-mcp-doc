from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .publication_kernel import (
    bundle_manifest_fields,
    exact_bundle_diagnostics,
    file_declarations,
    write_bundle,
)

_POLICY = "prescriptives/documentation/01-reference-standard.mrd.json"
_REGISTRY = "prescriptives/documentation/04-publication-family-registry.mrd.json"
_GENERATOR = "src/kis_mcp_doc/human_docs.py"
_ADAPTERS = "src/kis_mcp_doc/publication_adapters.py"
_OUTPUT_CLASS = "human_documentation"


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _docs(root: Path, family: dict[str, Any]) -> dict[str, dict[str, Any]]:
    base = root / family["mrd_root"]
    documents = [_load_json(path) for path in sorted(base.glob("*.mrd.json"))]
    return {doc["_mrd"]["id"]: doc for doc in documents}


def _config(root: Path, family: dict[str, Any]) -> dict[str, Any]:
    config = _load_json(root / family["publication_config"])
    policy = _load_json(root / _POLICY)
    classes = {item["class"] for item in policy["content"]["output_classes"]}
    if _OUTPUT_CLASS not in classes:
        raise ValueError("human_documentation output class is not governed")
    reference = config.get("documentation_reference", {})
    if reference.get("output_class") != _OUTPUT_CLASS:
        raise ValueError("human documentation publication must declare human_documentation output class")
    if set(family.get("output_classes", [])) != {_OUTPUT_CLASS}:
        raise ValueError("human documentation family must register only human_documentation")
    return config


def _source_declarations(root: Path, family: dict[str, Any]) -> list[dict[str, Any]]:
    paths = [
        root / _POLICY,
        root / _REGISTRY,
        root / family["publication_config"],
        root / _GENERATOR,
        root / _ADAPTERS,
    ]
    paths.extend(sorted((root / family["mrd_root"]).glob("*.mrd.json")))
    declarations: list[dict[str, Any]] = []
    for path in paths:
        payload = path.read_bytes()
        declarations.append({
            "path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
        })
    return declarations


def _header(title: str, subtitle: str) -> list[str]:
    return ["<!-- GENERATED — DO NOT EDIT -->", f"# {title}", "", subtitle, ""]


def _sentence_case_label(value: str) -> str:
    text = value.replace("_", " ").strip()
    return text[:1].upper() + text[1:] if text else text


def _spec_link(config: dict[str, Any]) -> str:
    spec = Path(config["specification"])
    return f"../{spec.parent.name}/{spec.name}"


def _mrd_specification_pages(config: dict[str, Any], docs: dict[str, dict[str, Any]]) -> tuple[dict[str, bytes], dict[str, Any]]:
    by_concern = {doc["content"]["concern"]: doc for doc in docs.values()}
    classification = by_concern["classification"]
    applicability = by_concern["applicability"]
    ownership = by_concern["ownership"]
    provenance = by_concern["provenance"]
    lifecycle = by_concern["lifecycle"]
    validation = by_concern["validation"]
    spec = _spec_link(config)
    overview = _header(config["title"], config["subtitle"])
    overview += [
        "Use these pages to understand and author conforming MRDs. Repository-wide Governance remains a separate authority and is documented in the Repository Documentation bundle.",
        "",
        "## Start here", "",
        "- [Classify and select MRDs](002-classify-and-select.md)",
        "- [Model authority and relationships](003-authority-and-relationships.md)",
        "- [Represent provenance and lifecycle](004-provenance-and-lifecycle.md)",
        "- [Validate MRD conformance](005-conformance.md)",
        "- [MRD examples](006-examples.md)",
        f"- [MRD Specification]({spec}) for normative requirements and exact reference material",
    ]
    classify = _header("Classify and select MRDs", classification["content"]["purpose"])
    classify += [
        f"The MRD catalog contains **{classification['content']['catalog_policy']['expected_class_count']}** functional classes and **{classification['content']['catalog_policy']['expected_type_count']}** types.", "",
        "Choose the minimum sufficient type set for the governed need. Classification describes what an MRD does, not where the repository stores it.", "",
        "## Selection order", "",
    ]
    classify += [f"{i}. {step}." for i, step in enumerate(applicability["content"]["selection_contract"]["selection_order"], start=1)]
    classify += ["", f"Use the [MRD Specification]({spec}) for the complete applicability catalog."]

    authority = _header("Model authority and relationships", ownership["content"]["purpose"])
    contract = ownership["content"]["ownership_contract"]
    authority += [
        "MRDs represent ownership and typed relationships without making repository-wide Governance part of the MRD format itself.", "",
        f"- Canonical owner count represented by the MRD model: **{contract['canonical_owner_count']}**.",
        f"- Non-owner posture: `{contract['non_owner_posture']}`.",
        f"- Derived posture: `{contract['derived_posture']}`.", "",
        "## Relationship vocabulary", "",
    ]
    authority += [f"- `{item['code']}` ? {item['meaning']}" for item in ownership["content"]["relationship_catalog"]]
    authority += ["", f"Use the [MRD Specification]({spec}) for exact dependency and layering constraints."]

    lineage = _header("Represent provenance and lifecycle", provenance["content"]["purpose"])
    lineage += ["## Record modes", ""]
    lineage += [f"- `{item['mode']}` ? {item['meaning']}" for item in provenance["content"]["record_modes"]]
    lineage += ["", "## Lifecycle by record mode", ""]
    for machine in lifecycle["content"]["lifecycles"]:
        transitions = ", ".join(f"`{x['from']}` ? `{x['to']}`" for x in machine["transitions"])
        lineage += [f"### {machine['record_mode'].title()}", "", f"States: {', '.join(f'`{x}`' for x in machine['states'])}.", "", f"Transitions: {transitions}.", ""]
    lineage += [f"Use the [MRD Specification]({spec}) for provenance source, fact-quality, and lifecycle constraints."]

    conformance = _header("Validate MRD conformance", validation["content"]["purpose"])
    conformance += [
        "MRD conformance validation checks the MRD model and its declared relationships. Repository Governance separately governs when and how repository changes are admitted, reviewed, and evidenced.", "",
        "## Conformance checks", "",
    ]
    conformance += [f"- `{name}`" for name in validation["content"]["result_contract"]["checks"]]
    conformance += ["", "## Stable failure codes", ""]
    conformance += [f"- `{code}`" for code in validation["content"]["reason_codes"]]
    conformance += ["", f"Use the [MRD Specification]({spec}) for the exact result contract and enforcement bindings."]

    examples = _header("MRD examples", "These examples explain the MRD model without adding normative authority.")
    examples += [
        "## Example: define a governed fact in an MRD", "",
        "1. Identify the governed need and select the minimum sufficient MRD class and type.",
        "2. Assign the stable opaque MRD identity separately from class, type, layer, path, and Git revision.",
        "3. Declare typed dependencies and provenance sources.",
        "4. Use the record-mode lifecycle vocabulary for status and supersession.",
        "5. Run MRD conformance validation and resolve stable reason codes before publication.", "",
        f"For exact requirements, use the [MRD Specification]({spec}).",
    ]
    files = {
        "000-index.md": ("\n".join(overview) + "\n").encode(),
        "002-classify-and-select.md": ("\n".join(classify) + "\n").encode(),
        "003-authority-and-relationships.md": ("\n".join(authority) + "\n").encode(),
        "004-provenance-and-lifecycle.md": ("\n".join(lineage) + "\n").encode(),
        "005-conformance.md": ("\n".join(conformance) + "\n").encode(),
        "006-examples.md": ("\n".join(examples) + "\n").encode(),
    }
    traceability = {
        "output_class": _OUTPUT_CLASS,
        "topics": [
            {"page": "002-classify-and-select.md", "source_mrds": [classification["_mrd"]["id"], applicability["_mrd"]["id"]]},
            {"page": "003-authority-and-relationships.md", "source_mrds": [ownership["_mrd"]["id"], by_concern["dependencies"]["_mrd"]["id"], by_concern["layering"]["_mrd"]["id"]]},
            {"page": "004-provenance-and-lifecycle.md", "source_mrds": [provenance["_mrd"]["id"], lifecycle["_mrd"]["id"]]},
            {"page": "005-conformance.md", "source_mrds": [validation["_mrd"]["id"]]},
            {"page": "006-examples.md", "source_mrds": [classification["_mrd"]["id"], provenance["_mrd"]["id"], validation["_mrd"]["id"]]},
        ],
    }
    files["data/source-traceability.json"] = _json_bytes(traceability)
    return files, traceability

def _work_pages(config: dict[str, Any], docs: dict[str, dict[str, Any]]) -> tuple[dict[str, bytes], dict[str, Any]]:
    lifecycle = docs["urn:uuid:7f58b5b4-9808-5c06-bbed-75a8526685f3"]["content"]
    operations = docs["urn:uuid:3bab4e5b-4c6d-5c21-811c-a7f6cb02ac93"]["content"]
    boundary = docs["urn:uuid:2f2b1233-37fe-580c-bc75-26a38e9aa7fe"]["content"]
    spec = _spec_link(config)
    overview = _header(config["title"], config["subtitle"])
    overview += [
        "Use these pages to operate the governed Work system. Exact state, field, and provider contracts remain in the Work Management Specification and generated reference.",
        "",
        "## Start here",
        "",
        "- [Move work through its lifecycle](002-work-lifecycle.md)",
        "- [Use Work Management operations](003-work-operations.md)",
        "- [Complete governed work](004-complete-work.md)",
        "- [Troubleshoot work state](005-troubleshooting.md)",
        "- [Work Management examples](006-examples.md)",
        f"- [Work Management Specification]({spec}) for normative and exact reference material",
    ]
    life = _header("Move work through its lifecycle", lifecycle["purpose"])
    life += ["Work Status and Delivery Stage are separate dimensions. Change one only through its owning authority.", "", "## Work states", ""]
    for state in lifecycle["states"]:
        life += [f"- **{state['label']}** (`{state['token']}`): {state['definition']}"]
    life += ["", "## Before work becomes Ready", ""]
    life += [f"- Required Project fields: {', '.join(lifecycle['readiness']['required_project_fields'])}."]
    life += [f"- Required issue sections: {', '.join(lifecycle['readiness']['required_issue_sections'])}."]
    life += ["- Dependencies must be understood." if lifecycle["readiness"]["requires_dependencies_understood"] else "- Dependency understanding is not required."]
    life += ["", f"See the [Work Management Specification]({spec}) for every allowed transition and guard."]
    ops = _header("Use Work Management operations", operations["purpose"])
    ops += ["Choose the operation that matches the intended lifecycle action; mutation authority is bounded by the command plane.", ""]
    for operation in operations["operations"]:
        ops += [f"## {_sentence_case_label(operation['id'])}", "", operation["definition"], "", f"Implementation surface: `{operation['implementation_surface']}`. Effect: `{operation['effect']}`.", ""]
    ops += [f"For operation contracts and typed errors, use the [Work Management Specification]({spec})."]

    complete = _header("Complete governed work", "Completion is evidence-gated; merge is not the same as Done.")
    complete += [
        "A change can move through repository delivery, merge, documentation reconciliation, and commissioning before Work reaches Done.",
        "",
        "## Delivery stages",
        "",
        " → ".join(f"`{stage}`" for stage in lifecycle["delivery"]["stages"]),
        "",
        "## Completion checks",
        "",
        f"- Terminal Work state: `{lifecycle['completion']['terminal_state']}`.",
        "- Required post-merge documentation reconciliation must be complete when its guard applies.",
        "- Source verification and live verification remain separate evidence domains.",
        "",
        f"See the [Work Management Specification]({spec}) for exact completion guards.",
    ]
    trouble = _header("Troubleshoot work state", "Use guards, authority, and typed errors instead of forcing a state transition.")
    trouble += ["## Guards", ""]
    for guard in lifecycle["guards"]:
        trouble += [f"- `{guard['id']}` → `{guard['reason_code']}`: {guard['definition']}"]
    trouble += ["", "## Provider boundary", "", boundary["provider_contract"]["live_observation"], ""]
    trouble += ["Typed errors:"] + [f"- `{error}`" for error in operations["typed_errors"]]
    trouble += ["", f"Use the [Work Management Specification]({spec}) for exact field authority and recovery semantics."]

    examples = _header("Work Management examples", "These examples compose canonical operations and states; they do not create new transitions or authority.")
    examples += [
        "## Example: take and complete ready work",
        "",
        "1. Confirm the item satisfies Ready metadata and dependency requirements.",
        "2. Use `take_next_work` or `claim_work` to establish the execution claim.",
        "3. Perform the governed repository change while Work remains evidence-linked to its delivery stage.",
        "4. Run source verification for the exact delivery identity.",
        "5. After merge, complete required documentation reconciliation and any required commissioning.",
        "6. Use `complete_work` only after the completion guards are satisfied.",
        "",
        "If a guard rejects a transition, resolve its reason code instead of forcing the state.",
        "",
        f"For exact transitions, guards, fields, and operation contracts, use the [Work Management Specification]({spec}).",
    ]

    files = {
        "000-index.md": ("\n".join(overview) + "\n").encode(),
        "002-work-lifecycle.md": ("\n".join(life) + "\n").encode(),
        "003-work-operations.md": ("\n".join(ops) + "\n").encode(),
        "004-complete-work.md": ("\n".join(complete) + "\n").encode(),
        "005-troubleshooting.md": ("\n".join(trouble) + "\n").encode(),
        "006-examples.md": ("\n".join(examples) + "\n").encode(),
    }
    traceability = {
        "output_class": _OUTPUT_CLASS,
        "topics": [
            {"page": "002-work-lifecycle.md", "source_mrds": ["urn:uuid:7f58b5b4-9808-5c06-bbed-75a8526685f3"]},
            {"page": "003-work-operations.md", "source_mrds": ["urn:uuid:3bab4e5b-4c6d-5c21-811c-a7f6cb02ac93"]},
            {"page": "004-complete-work.md", "source_mrds": ["urn:uuid:7f58b5b4-9808-5c06-bbed-75a8526685f3"]},
            {"page": "005-troubleshooting.md", "source_mrds": ["urn:uuid:7f58b5b4-9808-5c06-bbed-75a8526685f3", "urn:uuid:3bab4e5b-4c6d-5c21-811c-a7f6cb02ac93", "urn:uuid:2f2b1233-37fe-580c-bc75-26a38e9aa7fe"]},
            {"page": "006-examples.md", "source_mrds": ["urn:uuid:7f58b5b4-9808-5c06-bbed-75a8526685f3", "urn:uuid:3bab4e5b-4c6d-5c21-811c-a7f6cb02ac93"]},
        ],
    }
    files["data/source-traceability.json"] = _json_bytes(traceability)
    return files, traceability


def _expected_bundle(root: Path, family: dict[str, Any], kind: str) -> tuple[dict[str, bytes], dict[str, Any]]:
    config = _config(root, family)
    documents = _docs(root, family)
    if kind == "mrd-specification":
        files, traceability = _mrd_specification_pages(config, documents)
    elif kind == "work-management":
        files, traceability = _work_pages(config, documents)
    else:
        raise ValueError(f"unknown human documentation kind: {kind}")
    manifest = {
        "contract": {"name": "kis-human-documentation-build", "version": 1},
        "family_id": family["id"],
        "output_class": _OUTPUT_CLASS,
        "generator": {"name": "kis-mcp-doc", "algorithm": "human-docs-v1"},
        "inputs": {"source_files": _source_declarations(root, family)},
        "traceability_topics": len(traceability["topics"]),
        "files": file_declarations(files),
        **bundle_manifest_fields(files),
    }
    return files, manifest


def validate_human_docs_family(root: Path, family: dict[str, Any], kind: str) -> dict[str, Any]:
    try:
        config = _config(root, family)
        documents = _docs(root, family)
        if not documents:
            raise ValueError("human documentation family has no canonical MRD sources")
        if Path(config["source_glob"]).parent.as_posix() != family["mrd_root"]:
            raise ValueError("human documentation source_glob does not match registered MRD root")
        _expected_bundle(root, family, kind)
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as error:
        return {"status": "invalid", "diagnostics": [{"code": "HUMAN_DOCUMENTATION_INVALID", "message": str(error)}]}
    return {"status": "valid", "diagnostics": []}


def build_human_docs_family(
    root: Path,
    family: dict[str, Any],
    kind: str,
    *,
    output: Path | None = None,
    replace: bool = False,
) -> dict[str, Any]:
    validation = validate_human_docs_family(root, family, kind)
    if validation["status"] != "valid":
        raise ValueError(validation["diagnostics"][0]["message"])
    files, manifest = _expected_bundle(root, family, kind)
    target = Path(output) if output is not None else root / family["output"]
    write_bundle(target, files, manifest, replace=replace)
    return manifest


def verify_human_docs_family(root: Path, family: dict[str, Any], kind: str) -> dict[str, Any]:
    validation = validate_human_docs_family(root, family, kind)
    if validation["status"] != "valid":
        return validation
    try:
        files, manifest = _expected_bundle(root, family, kind)
        diagnostics = exact_bundle_diagnostics(
            root / family["output"], files, manifest, code_prefix="HUMAN_DOCUMENTATION"
        )
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as error:
        diagnostics = [{"code": "HUMAN_DOCUMENTATION_VERIFY_FAILED", "message": str(error)}]
    return {"status": "invalid" if diagnostics else "valid", "diagnostics": diagnostics}
