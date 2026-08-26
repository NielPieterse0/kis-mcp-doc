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

_POLICY = "mrd/documentation/01-reference-standard.mrd.json"
_REGISTRY = "mrd/documentation/04-publication-family-registry.mrd.json"
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


def _spec_link(config: dict[str, Any]) -> str:
    spec = Path(config["specification"])
    return f"../{spec.parent.name}/{spec.name}"


def _governance_pages(config: dict[str, Any], docs: dict[str, dict[str, Any]]) -> tuple[dict[str, bytes], dict[str, Any]]:
    ownership = docs["KIS-KNOW-CON-POL-002"]["content"]
    lifecycle = docs["KIS-KNOW-WRK-STM-001"]["content"]
    workflow = docs["KIS-KNOW-WRK-WFL-001"]["content"]
    validation = docs["KIS-KNOW-EVL-TST-001"]["content"]
    spec = _spec_link(config)
    overview = _header(config["title"], config["subtitle"])
    overview += [
        "Use these pages when you need to apply governance, not when you need the normative contract.",
        "The generated documentation explains canonical Governance MRDs without becoming a second authority.",
        "",
        "## Start here",
        "",
        "- [Understand authority and ownership](002-understand-authority.md)",
        "- [Apply governance to a change](003-apply-governance.md)",
        "- [Understand MRD lifecycle](004-mrd-lifecycle.md)",
        "- [Troubleshoot governance failures](005-troubleshooting.md)",
        "- [Governance examples](006-examples.md)",
        f"- [Governance Specification]({spec}) for normative rules and exact reference material",
    ]
    authority = _header("Understand authority and ownership", ownership["purpose"])
    contract = ownership["ownership_contract"]
    authority += [
        "A governed fact has one current canonical owner. Other artifacts may explain or project that fact, but they do not become another owner.",
        "",
        "## Working rule",
        "",
        f"- Canonical owner count: **{contract['canonical_owner_count']}**.",
        f"- Non-owner posture: `{contract['non_owner_posture']}`.",
        f"- Derived posture: `{contract['derived_posture']}`.",
        f"- Conflict posture: `{contract['conflict_posture']}`.",
        "",
        f"For the complete relationship vocabulary and normative requirements, see the [Governance Specification]({spec}).",
    ]
    applying = _header("Apply governance to a change", workflow["purpose"])
    applying += ["Follow the canonical phases in order. A phase can stop the change when its declared stop condition is met.", ""]
    for phase in sorted(workflow["phases"], key=lambda item: item["order"]):
        applying += [f"## {phase['order']}. {phase['name'].replace('_', ' ').title()}", ""]
        applying += [f"- {action}." for action in phase["required_actions"]]
        if phase["stop_when"]:
            applying += ["", "Stop here when:"] + [f"- {condition}." for condition in phase["stop_when"]]
        applying += [""]
    applying += [f"Use the [Governance Specification]({spec}) when you need exact MUST/SHOULD/MAY requirements or rule identifiers."]

    life = _header("Understand MRD lifecycle", lifecycle["purpose"])
    life += ["The lifecycle depends on the MRD record mode.", ""]
    for machine in lifecycle["lifecycles"]:
        transitions = ", ".join(f"`{item['from']}` → `{item['to']}`" for item in machine["transitions"])
        life += [f"## {machine['record_mode'].title()}", "", f"States: {', '.join(f'`{state}`' for state in machine['states'])}.", "", f"Allowed transitions: {transitions}.", ""]
    life += [f"See the [Governance Specification]({spec}) for lifecycle requirements and lineage rules."]

    trouble = _header("Troubleshoot governance failures", "Use canonical stop conditions and validation evidence to decide what must be fixed before work continues.")
    trouble += ["## Common blocking situations", ""]
    stops = [condition for phase in workflow["phases"] for condition in phase["stop_when"]]
    trouble += [f"- {condition}." for condition in stops]
    trouble += ["", "## Validation evidence", "", "Validation uses stable reason codes. Do not infer past a blocking diagnostic.", ""]
    trouble += [f"- `{code}`" for code in validation["reason_codes"]]
    trouble += ["", f"Use the [Governance Specification]({spec}) to resolve a reason code against its normative validation contract."]

    examples = _header("Governance examples", "These examples illustrate the canonical workflow; they do not add governance semantics.")
    examples += [
        "## Example: govern a repository change",
        "",
        "1. Resolve repository authority and the active change scope.",
        "2. Select only the MRDs required by the governed needs.",
        "3. Resolve dependencies, ownership, and typed relationships.",
        "4. Run structural and semantic governance validation.",
        "5. Execute only inside the admitted scope.",
        "6. Generate the review surface from validated authority.",
        "7. Verify generated output and report remaining gaps or diagnostics.",
        "",
        "If any canonical phase declares a blocking stop condition, stop the example at that phase rather than inferring authority.",
        "",
        f"For exact requirements behind each phase, use the [Governance Specification]({spec}).",
    ]
    files = {
        "000-index.md": ("\n".join(overview) + "\n").encode(),
        "002-understand-authority.md": ("\n".join(authority) + "\n").encode(),
        "003-apply-governance.md": ("\n".join(applying) + "\n").encode(),
        "004-mrd-lifecycle.md": ("\n".join(life) + "\n").encode(),
        "005-troubleshooting.md": ("\n".join(trouble) + "\n").encode(),
        "006-examples.md": ("\n".join(examples) + "\n").encode(),
    }
    traceability = {
        "output_class": _OUTPUT_CLASS,
        "topics": [
            {"page": "002-understand-authority.md", "source_mrds": ["KIS-KNOW-CON-POL-002"]},
            {"page": "003-apply-governance.md", "source_mrds": ["KIS-KNOW-WRK-WFL-001"]},
            {"page": "004-mrd-lifecycle.md", "source_mrds": ["KIS-KNOW-WRK-STM-001"]},
            {"page": "005-troubleshooting.md", "source_mrds": ["KIS-KNOW-WRK-WFL-001", "KIS-KNOW-EVL-TST-001"]},
            {"page": "006-examples.md", "source_mrds": ["KIS-KNOW-WRK-WFL-001"]},
        ],
    }
    files["data/source-traceability.json"] = _json_bytes(traceability)
    return files, traceability


def _work_pages(config: dict[str, Any], docs: dict[str, dict[str, Any]]) -> tuple[dict[str, bytes], dict[str, Any]]:
    lifecycle = docs["KIS-WORK-WRK-STM-001"]["content"]
    operations = docs["KIS-WORK-WRK-WFL-001"]["content"]
    boundary = docs["KIS-WORK-CTR-SVC-001"]["content"]
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
        ops += [f"## {operation['id'].replace('_', ' ').title()}", "", operation["definition"], "", f"Implementation surface: `{operation['implementation_surface']}`. Effect: `{operation['effect']}`.", ""]
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
            {"page": "002-work-lifecycle.md", "source_mrds": ["KIS-WORK-WRK-STM-001"]},
            {"page": "003-work-operations.md", "source_mrds": ["KIS-WORK-WRK-WFL-001"]},
            {"page": "004-complete-work.md", "source_mrds": ["KIS-WORK-WRK-STM-001"]},
            {"page": "005-troubleshooting.md", "source_mrds": ["KIS-WORK-WRK-STM-001", "KIS-WORK-WRK-WFL-001", "KIS-WORK-CTR-SVC-001"]},
            {"page": "006-examples.md", "source_mrds": ["KIS-WORK-WRK-STM-001", "KIS-WORK-WRK-WFL-001"]},
        ],
    }
    files["data/source-traceability.json"] = _json_bytes(traceability)
    return files, traceability


def _expected_bundle(root: Path, family: dict[str, Any], kind: str) -> tuple[dict[str, bytes], dict[str, Any]]:
    config = _config(root, family)
    documents = _docs(root, family)
    if kind == "governance":
        files, traceability = _governance_pages(config, documents)
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
