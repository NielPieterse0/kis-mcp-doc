from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .governance import canonical_hash, canonical_source_bytes


class WorkManagementRepository:
    def __init__(self, root: Path, mrd_root: Path | None = None) -> None:
        self.root = Path(root).resolve()
        self.mrd_root = (mrd_root or self.root / "mrd" / "work-management").resolve()
        self.schema_path = self.root / "contracts" / "mrd" / "v1" / "mrd.schema.json"

    def load(self) -> dict[str, dict[str, Any]]:
        docs: dict[str, dict[str, Any]] = {}
        for path in sorted(self.mrd_root.glob("*.mrd.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            doc_id = doc.get("_mrd", {}).get("id")
            if not isinstance(doc_id, str) or not doc_id:
                raise ValueError(f"MRD missing stable id: {path}")
            if doc_id in docs:
                raise ValueError(f"duplicate MRD id: {doc_id}")
            docs[doc_id] = doc
        return docs

    def validate(self) -> dict[str, Any]:
        diagnostics: list[dict[str, str]] = []
        try:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema)
            docs = self.load()
        except Exception as error:
            return {"status":"invalid","diagnostics":[{"code":"WORK_MRD_LOAD_INVALID","message":str(error)}]}
        for doc_id, doc in docs.items():
            for error in sorted(validator.iter_errors(doc), key=lambda e: tuple(str(x) for x in e.absolute_path)):
                diagnostics.append({"code":"WORK_MRD_SCHEMA_INVALID","message":f"{doc_id}: {error.message}"})
        ids=set(docs)
        for doc_id,doc in docs.items():
            for dep in doc["_mrd"]["dependencies"]:
                if "mrd_id" in dep and dep["mrd_id"] not in ids:
                    diagnostics.append({"code":"WORK_MRD_DEPENDENCY_UNRESOLVED","message":f"{doc_id}: {dep['mrd_id']}"})
                if "source" in dep:
                    rel=dep["source"][5:]
                    if not (self.root/rel).is_file():
                        diagnostics.append({"code":"WORK_MRD_SOURCE_UNRESOLVED","message":f"{doc_id}: {rel}"})
            sources=doc["_mrd"]["provenance"]["sources"]
            expected="sha256:"+canonical_hash(sources)
            if doc["_mrd"]["provenance"]["source_fingerprint"] != expected:
                diagnostics.append({"code":"WORK_MRD_FINGERPRINT_MISMATCH","message":doc_id})
            for source in sources:
                if source["kind"]=="repo_path":
                    path=self.root/source["locator"][5:]
                    if not path.is_file() or hashlib.sha256(canonical_source_bytes(path)).hexdigest()!=source.get("sha256"):
                        diagnostics.append({"code":"WORK_MRD_SOURCE_HASH_MISMATCH","message":f"{doc_id}: {source['locator']}"})
        return {"status":"invalid" if diagnostics else "valid","diagnostics":diagnostics}


def _page_name(index: int, doc: dict[str, Any]) -> str:
    slug="-".join(x for x in ''.join(c.lower() if c.isalnum() else '-' for c in doc['_mrd']['title']).split('-') if x)
    return f"{index:03d}-{slug}.md"


def _inline_value(value: Any) -> str | None:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (str, int, float)):
        return str(value)
    if isinstance(value, list) and all(isinstance(item, (str, int, float, bool)) for item in value):
        return ", ".join(str(item) for item in value) if value else "None"
    return None


def _human_name(value: str) -> str:
    return value.replace("_", " ").strip().capitalize()


def _code_list(values: list[Any]) -> str:
    return ", ".join(f"`{value}`" for value in values) if values else "None"


def _text_list(values: list[Any]) -> str:
    return ", ".join(str(value) for value in values) if values else "None"


def _natural_list(values: list[Any], *, code: bool=False, bold: bool=False) -> str:
    items = []
    for value in values:
        text = str(value)
        if code:
            text = f"`{text}`"
        elif bold:
            text = f"**{text}**"
        items.append(text)
    if not items:
        return "none"
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _markdown_cell(value: Any) -> str:
    if value is None or value == "":
        return "None"
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _append_table(lines: list[str], headers: list[str], rows: list[list[Any]]) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        lines.append("| " + " | ".join(_markdown_cell(value) for value in row) + " |")
    lines.append("")


def _source_and_authority(doc: dict[str, Any]) -> list[str]:
    return [
        "## Source and authority",
        "",
        f"This page projects `{doc['_mrd']['id']}` version `{doc['_mrd']['version']}`. The MRD remains authoritative; this generated page has no write-back authority.",
        "",
    ]


def _render_domain_model(content: dict[str, Any]) -> list[str]:
    lines = [
        "Work Management defines the fields and controlled vocabularies used to describe a work record. The model keeps command data separate from observed evidence so that a generated view cannot silently become a second source of truth.",
        "",
        "## Field model",
        "",
        "Work Management uses three authority directions. **Command** fields are changed through Work Management. **Evidence** fields are observed or projected from their owning source. **Handoff** fields start in Work Management and later become governed repository-change facts.",
        "",
    ]
    direction_labels = {
        "command": "Command fields",
        "evidence": "Evidence fields",
        "handoff": "Handoff fields",
    }
    for direction in ("command", "evidence", "handoff"):
        fields = [item for item in content["fields"] if item["direction"] == direction]
        if not fields:
            continue
        lines.extend([f"### {direction_labels[direction]}", ""])
        rows = []
        for field in fields:
            scope = "all record types" if field["applicable_record_types"] == ["*"] else _text_list(field["applicable_record_types"])
            details = [
                f"ID `{field['id']}`",
                f"provider `{field['provider_type']}`",
                "KIS-managed" if field["managed"] else "provider-managed",
                f"applies to {scope}",
            ]
            if field["required_contexts"]:
                details.append(f"required for {_code_list(field['required_contexts'])}")
            if field["vocabulary"]:
                details.append(f"vocabulary `{field['vocabulary']}`")
            meaning = f"{field['definition']} {field['population']}"
            rows.append([
                field["name"],
                meaning,
                f"`{field['authority']}`",
                f"`{field['direction']}`",
                "; ".join(details),
            ])
        _append_table(lines, ["Field", "Meaning", "Authority", "Direction", "Details"], rows)

    lines.extend([
        "## Authority rules",
        "",
        "These rules prevent field ownership from drifting between Work Management, repository change governance, GitHub, Actions, and generated documentation:",
        "",
    ])
    lines.extend(f"- {rule}" for rule in content["rules"])
    lines.append("")

    lines.extend([
        "## Controlled vocabularies",
        "",
        "Single-select fields use the following governed values. The display label is what readers see; the token is the stable machine value.",
        "",
    ])
    for vocabulary in content["vocabularies"]:
        lines.extend([
            f"### {_human_name(vocabulary['id'])} values",
            "",
            vocabulary["definition"],
            "",
        ])
        rows = [
            [value["label"], f"`{value['token']}`", value["definition"]]
            for value in vocabulary["values"]
        ]
        _append_table(lines, ["Value", "Token", "Meaning"], rows)
    return lines


def _render_lifecycle(content: dict[str, Any]) -> list[str]:
    state_by_token = {state["token"]: state["label"] for state in content["states"]}
    lines = [
        "A work item moves through explicit states. Project-visible states describe the shared work queue, while internal states such as Review, Verification, and Documentation describe delivery activity without creating new GitHub Project status values.",
        "",
        "## State model",
        "",
    ]
    _append_table(
        lines,
        ["State", "Meaning", "GitHub Project status", "Token"],
        [[state["label"], state["definition"], "Yes" if state["project_status"] else "No", f"`{state['token']}`"] for state in content["states"]],
    )

    lines.extend([
        "## Transitions",
        "",
        "Transitions are explicit. A work item **MUST** move only to a destination listed for its current state. On Hold and Deferred also require a Review Trigger.",
        "",
    ])
    transition_rows = []
    for source, targets in content["transitions"].items():
        requirement = content["transition_requirements"].get(source, [])
        transition_rows.append([
            state_by_token.get(source, _human_name(source)),
            ", ".join(state_by_token.get(target, _human_name(target)) for target in targets) if targets else "No transitions",
            _text_list(requirement),
        ])
    _append_table(lines, ["From", "Allowed next states", "Additional requirement"], transition_rows)

    readiness = content["readiness"]
    lines.extend([
        "## Readiness and claims",
        "",
        "Before a work item can enter Ready, it **MUST** satisfy all configured readiness requirements:",
        "",
        f"- The source issue contains {_natural_list(readiness['required_issue_sections'], bold=True)}.",
        f"- The Project record contains {_natural_list(readiness['required_project_fields'], bold=True)}.",
    ])
    if readiness["requires_dependencies_understood"]:
        lines.append("- Dependencies are understood.")
    lines.extend([
        "",
        f"Execution claims use the **{content['claim']['execution_owner_field']}** field. Claims {'expire automatically' if content['claim']['auto_expiry'] else 'do not expire automatically'}.",
        "",
        f"At intake, the alias `{next(iter(content['intake_aliases']))}` is normalized to `{next(iter(content['intake_aliases'].values()))}`.",
        "",
        "## Delivery and completion",
        "",
        "Delivery is tracked separately from the work state. The configured delivery-stage sequence is:",
        "",
        _code_list(content["delivery"]["stages"]),
        "",
        f"The **{content['delivery']['stage_field']}** field stores that stage. **{content['delivery']['change_id_field']}**, **{content['delivery']['complexity_field']}**, and **{content['delivery']['risk_triggers_field']}** connect the work record to repository change governance. The sequence starts its governed change at `{content['delivery']['change_created_stage']}` and reaches `{content['delivery']['complete_stage']}` when delivery is complete.",
        "",
        f"Completion targets `{content['completion']['terminal_state']}`. The current configuration {'requires' if content['completion']['require_no_active_claim_after_close'] else 'does not require'} the execution claim to be absent after close.",
        "",
        "## Completion and activation guards",
        "",
        "Guards reject or qualify transitions when required evidence is missing or inconsistent:",
        "",
    ])
    _append_table(
        lines,
        ["Guard", "Applies when", "Rule", "Result", "Reason"],
        [[f"`{guard['id']}`", f"`{guard['condition']}`", guard["definition"], f"`{guard['disposition']}` to `{guard['target']}`", f"`{guard['reason_code']}`"] for guard in content["guards"]],
    )
    return lines


def _render_operations(content: dict[str, Any]) -> list[str]:
    mutation_rule = content["mutation_rule"].replace("apply=true", "`apply=true`")
    lines = [
        "Work Management exposes a bounded set of operations for intake, claiming, state changes, verification, and post-merge commissioning. Each operation has a defined effect and implementation surface so callers can distinguish reads from mutations and evidence collection.",
        "",
        "## Mutation safety",
        "",
        mutation_rule,
        "",
        "## Operations",
        "",
    ]
    _append_table(
        lines,
        ["Operation", "Purpose", "Effect", "Implementation surface"],
        [[f"{_human_name(op['id'])} (`{op['id']}`)", op["definition"], f"`{op['effect']}`", f"`{op['implementation_surface']}`"] for op in content["operations"]],
    )
    lines.extend([
        "## Result envelope",
        "",
        "Operation results use a common envelope so readers and tools can identify when the observation was made, what target was resolved, where the evidence came from, the operation result, and any valid next action.",
        "",
    ])
    lines.extend(f"- `{item}`" for item in content["result_envelope"])
    lines.extend([
        "",
        "## Typed errors",
        "",
        "Failures use bounded error categories rather than unstructured provider text:",
        "",
    ])
    lines.extend(f"- `{item}`" for item in content["typed_errors"])
    lines.extend([
        "",
        "## Verification domains",
        "",
        "Source verification and live verification are separate evidence domains. A successful repository check does not by itself prove the post-merge runtime surface.",
        "",
    ])
    _append_table(
        lines,
        ["Domain", "Field", "Meaning"],
        [[f"`{item['id']}`", item["field"], item["definition"]] for item in content["verification_domains"]],
    )
    return lines


def _render_selection(content: dict[str, Any]) -> list[str]:
    eligible = content["eligible_states"]
    eligible_text = _natural_list(eligible, code=True)
    lines = [
        "Selection is deterministic. Work Management first applies the eligibility rules for the active profile, then ranks only the candidates that remain.",
        "",
        "## Selection procedure",
        "",
        f"1. Keep only candidates whose state is {eligible_text}.",
        "2. Apply the active profile's rules in their declared order. These rules check source shape, open state, project scope, required metadata, claims, approval, dependency evidence, and blockers as applicable to that profile.",
        "3. Exclude any candidate that fails a rule and return the rule's stable reason code.",
        f"4. Rank the remaining candidates by {_code_list(content['ranking'])}.",
        "",
        f"Priority order is {_code_list(content['priority_order'])}. Effort order is {_code_list(content['effort_order'])}. Dependency evidence is classified as {_code_list(content['dependency_evidence'])}.",
        "",
        "## Selection inputs",
        "",
    ]
    _append_table(
        lines,
        ["Input", "Project field"],
        [[_human_name(key), value] for key, value in content["fields"].items()],
    )
    lines.extend([
        "## Selection profiles",
        "",
        "Profiles reuse the same rule catalog but apply different subsets and preserve profile-specific failure reasons where the source contract requires them.",
        "",
    ])
    profile_rows = []
    for name, profile in content["profiles"].items():
        overrides = "; ".join(f"`{key}` maps to `{value}`" for key, value in profile["reason_overrides"].items()) or "None"
        profile_rows.append([_human_name(name), _code_list(profile["rules"]), overrides])
    _append_table(lines, ["Profile", "Rules in order", "Reason overrides"], profile_rows)
    lines.extend([
        "## Rule catalog",
        "",
    ])
    _append_table(
        lines,
        ["Rule", "Kind", "Requirement", "Failure reason"],
        [[f"`{rule['id']}`", f"`{rule['kind']}`", rule["definition"], f"`{rule['reason_code']}`" if rule["reason_code"] is not None else "None"] for rule in content["rules"]],
    )
    return lines


def _render_authority_policy(content: dict[str, Any]) -> list[str]:
    lines = [
        "Authority determines which system may change a fact. Reconciliation then compares provider state with those owners and reports drift instead of choosing a new truth. Generated documentation stays downstream of every canonical source.",
        "",
        "## Authority principles",
        "",
    ]
    lines.extend(f"- {item}" for item in content["principles"])
    lines.extend(["", "## Change-governance handoff", ""])
    change = content["change_governance"]
    lines.append(f"Work Management carries change-planning data into repository governance, but repository change governance owns the governed change facts once a change exists. This projection uses change-governance schema version `{change['schema_version']}`.")
    lines.append("")
    complexity_rows = []
    for name, value in change["complexities"].items():
        complexity_rows.append([
            _human_name(name),
            value["description"],
            _text_list(value["artifacts"]),
            _text_list(value["base_reviews"]),
            value["max_verifications"],
        ])
    _append_table(lines, ["Complexity", "Meaning", "Artifacts", "Base reviews", "Max verifications"], complexity_rows)
    lines.extend([
        f"Supported review types: {_code_list(change['review_types'])}.",
        "",
        "### Risk triggers",
        "",
    ])
    risk_rows = [[_human_name(name), value["description"], _code_list(value["reviews"])] for name, value in change["risk_triggers"].items()]
    _append_table(lines, ["Risk trigger", "When it applies", "Required review"], risk_rows)

    schema = content["github_project_schema"]
    lines.extend([
        "## GitHub Project schema",
        "",
        f"The configured Project schema belongs to portfolio `{schema['portfolio_id']}` and uses schema version `{schema['schema_version']}`. Fields and allowed single-select options are explicit so provider drift can be detected.",
        "",
    ])
    _append_table(
        lines,
        ["Field", "Type", "Options"],
        [[field["name"], f"`{field['type']}`", _text_list(field["options"]) if field["options"] else "Not applicable"] for field in schema["fields"]],
    )
    lines.extend([
        "### Project views",
        "",
        "Views are derived navigation surfaces over the same Project data. Their filters and visible fields do not create new authority.",
        "",
    ])
    view_rows = []
    for view in schema["views"]:
        grouping_parts = []
        if view["group_by"]:
            grouping_parts.append(f"group by {_text_list(view['group_by'])}")
        if view["vertical_group_by"]:
            grouping_parts.append(f"vertical group by {_text_list(view['vertical_group_by'])}")
        if view["sort_by"]:
            grouping_parts.append(f"sort by {_text_list(view['sort_by'])}")
        grouping = "; ".join(grouping_parts) or "None"
        view_rows.append([view["name"], view["purpose"], f"`{view['layout']}`", view["filter"], grouping, _text_list(view["visible_fields"])])
    _append_table(lines, ["View", "Purpose", "Layout", "Filter", "Grouping / sort", "Visible fields"], view_rows)

    bindings = content["project_bindings"]
    lines.extend([
        "## Project bindings",
        "",
        f"Project integration is {'enabled' if bindings['enabled'] else 'disabled'} for portfolio `{bindings['portfolio_id']}` under schema version `{bindings['schema_version']}`.",
        "",
        "### Backend bindings",
        "",
    ])
    _append_table(
        lines,
        ["Binding", "Provider", "Owner", "Owner type", "Project"],
        [[item["binding_id"], f"`{item['provider']}`", item["owner"], item["owner_type"], item["project_number"]] for item in bindings["backend_bindings"]],
    )
    lines.extend(["### Managed projects", ""])
    _append_table(
        lines,
        ["Project ID", "Display name", "Repository", "Local root", "Backend"],
        [[item["project_id"], item["display_name"], item["repository"], f"`{item['local_root']}`", item["backend_binding"]] for item in bindings["managed_projects"]],
    )
    lines.extend(["### Features and gates", ""])
    _append_table(lines, ["Feature", "Mode"], [[_human_name(key), f"`{value}`"] for key, value in bindings["features"].items()])
    _append_table(lines, ["Gate", "Strength"], [[_human_name(key), f"`{value}`"] for key, value in bindings["gates"].items()])
    lines.extend([
        f"Evidence collection is bounded to `{bindings['evidence']['max_file_bytes']}` bytes per file and `{bindings['evidence']['max_total_bytes']}` bytes in total.",
        "",
    ])
    return lines


def _render_provider_boundary(content: dict[str, Any]) -> list[str]:
    command = content["command_plane"]
    provider = content["provider_contract"]
    lines = [
        "The command plane defines the work states and fields that KIS may change. The provider boundary observes and mutates GitHub Project only through the configured read and write models; provider state does not redefine repository-owned facts.",
        "",
        "## Command-plane model",
        "",
        f"Claims use **{command['claim']['execution_owner_field']}** and {'expire automatically' if command['claim']['auto_expiry'] else 'do not expire automatically'}. The completion policy targets `{command['completion']['terminal_state']}` and {'requires' if command['completion']['require_no_active_claim_after_close'] else 'does not require'} the claim to be absent after close.",
        "",
        f"The command plane exposes these work states: {_code_list(command['work_states'])}. Delivery uses {_code_list(command['delivery_stages'])}.",
        "",
        f"The intake alias `{next(iter(command['intake_aliases']))}` maps to `{next(iter(command['intake_aliases'].values()))}`.",
        "",
        "### Field authority",
        "",
        "Each field keeps the authority and direction defined by the Work Management domain model:",
        "",
    ]
    _append_table(
        lines,
        ["Field", "Authority", "Direction"],
        [[field, f"`{rule['authority']}`", f"`{rule['direction']}`"] for field, rule in command["field_authority"].items()],
    )

    queue = command["queue"]
    readiness = command["readiness"]
    queue_state_label = "state" if len(queue["eligible_states"]) == 1 else "states"
    lines.extend([
        "## Queue and readiness",
        "",
        f"The executable queue accepts {queue_state_label} {_natural_list(queue['eligible_states'], code=True)}. It ranks by {_code_list(queue['ranking'])}, using priority order {_code_list(queue['priority_order'])} and effort order {_code_list(queue['effort_order'])}.",
        "",
        f"Queue inputs come from **{queue['state_field']}**, **{queue['priority_field']}**, **{queue['effort_field']}**, **{queue['created_field']}**, and **{queue['blocked_by_field']}**.",
        "",
        "Before the provider-backed command plane can treat work as Ready, the record **MUST** satisfy its configured readiness requirements:",
        "",
        f"- The source issue contains {_natural_list(readiness['required_issue_sections'], bold=True)}.",
        f"- The Project record contains {_natural_list(readiness['required_project_fields'], bold=True)}.",
    ])
    if readiness["requires_dependencies_understood"]:
        lines.append("- Dependencies are understood.")
    lines.extend([
        "",
        "## State transitions",
        "",
        "The provider-facing command plane uses the same transition graph as the Work lifecycle chapter. The table is repeated here because the provider adapter validates these exact transitions.",
        "",
    ])
    transition_rows=[]
    for source, targets in command["transitions"].items():
        requirement=command["transition_requirements"].get(source, [])
        target_text = _code_list(targets) if targets else "No transitions"
        transition_rows.append([f"`{source}`", target_text, _text_list(requirement)])
    _append_table(lines, ["From", "Allowed next states", "Additional requirement"], transition_rows)

    delivery = command["delivery"]
    lines.extend([
        "## Delivery projection",
        "",
        f"**{delivery['stage_field']}** carries the derived delivery stage. **{delivery['change_id_field']}**, **{delivery['complexity_field']}**, and **{delivery['risk_triggers_field']}** are projected from repository change governance. The change-created stage is `{delivery['change_created_stage']}` and the complete stage is `{delivery['complete_stage']}`.",
        "",
        "## Provider contract",
        "",
        f"The configured Project is `{provider['project']}`. Reads use {provider['read_model']}; writes use {provider['write_model']}.",
        "",
        provider["live_observation"],
        "",
        f"Command-plane schema version: `{command['schema_version']}`.",
        "",
    ])
    return lines


def _render_conformance(content: dict[str, Any]) -> list[str]:
    lines = [
        "A Work Management implementation conforms to this specification only when its source MRDs, dependencies, evidence, generated views, and lifecycle behavior pass the checks below. These checks keep human-readable documentation aligned with machine-readable authority.",
        "",
        "## Conformance requirements",
        "",
    ]
    for index, check in enumerate(content["checks"], start=1):
        lines.append(f"{index}. {check}")
    lines.append("")
    return lines


def _render_generic(content: dict[str, Any]) -> list[str]:
    lines = [content.get("purpose", ""), ""] if content.get("purpose") else []
    for key, value in content.items():
        if key == "purpose":
            continue
        lines.extend([f"## {_human_name(key)}", ""])
        inline = _inline_value(value)
        if inline is not None:
            lines.extend([inline, ""])
        elif isinstance(value, list):
            lines.extend(f"- {_inline_value(item) or str(item)}" for item in value)
            lines.append("")
        elif isinstance(value, dict):
            rows = [[_human_name(str(name)), _inline_value(item) or str(item)] for name, item in value.items()]
            _append_table(lines, ["Name", "Value"], rows)
    return lines


def render_document(doc: dict[str, Any]) -> str:
    renderers = {
        "KIS-WORK-SEM-REG-001": _render_domain_model,
        "KIS-WORK-WRK-STM-001": _render_lifecycle,
        "KIS-WORK-WRK-WFL-001": _render_operations,
        "KIS-WORK-DEC-SCR-001": _render_selection,
        "KIS-WORK-CON-POL-001": _render_authority_policy,
        "KIS-WORK-CTR-SVC-001": _render_provider_boundary,
        "KIS-WORK-EVL-TST-001": _render_conformance,
    }
    lines = [
        "<!-- GENERATED — DO NOT EDIT -->",
        f"# {doc['_mrd']['title']}",
        "",
        '<div id="enable-section-numbers" />',
        "",
        "[Specification](001-specification.md) | [Documentation index](000-index.md)",
        "",
    ]
    renderer = renderers.get(doc["_mrd"]["id"], _render_generic)
    lines.extend(renderer(doc["content"]))
    lines.extend(_source_and_authority(doc))
    return "\n".join(lines)


def _live_project_summary(repo: WorkManagementRepository) -> str:
    path = repo.root / "evidence" / "work-management" / "canonical-snapshot.json"
    try:
        observation = json.loads(path.read_text(encoding="utf-8"))["live_project_observation"]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError):
        return "Live GitHub Project evidence is unavailable in the captured evidence set. The specification does not infer missing provider state."
    if observation.get("status") != "observed":
        return "Live GitHub Project evidence is unavailable in the captured evidence set. The specification does not infer missing provider state."
    schema = observation.get("schema_status", {})
    if observation.get("inventory_complete") is True and schema.get("ready") is True:
        return "The captured live GitHub Project evidence is observed. Inventory is complete, and the configured Project schema is ready with no reported field, option, type, or view drift."
    return "The captured live GitHub Project evidence is observed, but the captured inventory or schema status is not fully ready. The detailed evidence remains authoritative for the observed state."


def build_work_management_spec(repo: WorkManagementRepository, output: Path, *, replace: bool=False) -> dict[str, Any]:
    validation=repo.validate()
    if validation["status"]!="valid": raise ValueError(f"work-management MRDs invalid: {validation['diagnostics']}")
    docs=list(repo.load().values())
    output=Path(output)
    staging=Path(tempfile.mkdtemp(prefix=f".{output.name}.",suffix=".tmp",dir=output.parent))
    try:
        pages=[]
        for i,doc in enumerate(docs,2):
            name=_page_name(i,doc); text=render_document(doc); (staging/name).write_text(text,encoding="utf-8"); pages.append((name,doc))
        index = [
            "<!-- GENERATED — DO NOT EDIT -->",
            "# KIS Work Management Specification — documentation index",
            "",
            "Start with the [Specification](001-specification.md) for the operating model. The remaining chapters provide the detailed lifecycle, selection, authority, provider, and conformance rules.",
            "",
            "The validated Work Management MRDs remain authoritative. These pages are deterministic review projections and have no write-back authority.",
            "",
            "## Specification pages",
            "",
            "- [Specification](001-specification.md)",
        ] + [f"- [{d['_mrd']['title']}]({n})" for n, d in pages] + [
            "",
            "## Traceability",
            "",
            "- [Build manifest](manifest.json) — exact MRD and generated-file hashes",
            "",
        ]
        (staging/'000-index.md').write_text("\n".join(index),encoding='utf-8')
        root = [
            "<!-- GENERATED — DO NOT EDIT -->",
            "# KIS Work Management Specification",
            "",
            '<div id="enable-section-numbers" />',
            "",
            "Work Management is the governed KIS system for capturing, classifying, selecting, executing, verifying, and closing work across registered projects.",
            "",
            'The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY", and "OPTIONAL" are normative when they appear in all capitals.',
            "",
            "## Overview",
            "",
            "Work Management gives work one shared lifecycle and one explicit authority model. It separates facts that Work Management may change from evidence observed from GitHub, repository change governance, verification, and derived delivery state.",
            "",
            "A GitHub Project provides the shared provider surface, but it does not become the owner of every fact displayed there. Repository change governance remains authoritative for governed change identity, complexity, and risk; GitHub remains authoritative for provider-native source identity and dependency observations; verification systems own their evidence; and Work Management owns its command fields.",
            "",
            _live_project_summary(repo),
            "",
            "## Key concepts",
            "",
            "- **Command data** is changed through Work Management operations, such as status, priority, effort, claims, holds, and deferrals.",
            "- **Evidence data** is observed or projected from its owning source, such as GitHub source identity, repository change facts, verification, and delivery state.",
            "- **Handoff data** begins as Work Management planning data and becomes repository-owned evidence when a governed change takes authority for it.",
            "- **Generated documentation** explains and indexes the governed model. It never writes facts back to Work Management or its sources.",
            "",
            "## How work moves",
            "",
            "1. Capture work and classify it before it enters the executable queue.",
            "2. Admit work to Ready only after the required source sections, Project fields, and dependency evidence are present.",
            "3. Select Ready work deterministically, then establish an execution claim before activation.",
            "4. Track repository delivery and source verification as evidence without replacing the Work lifecycle state.",
            "5. After merge, reconcile any required documentation and live-verification obligations before the configured completion gates allow Done.",
            "",
            "## Detailed specification",
            "",
        ] + [f"- [{d['_mrd']['title']}]({n})" for n, d in pages] + [
            "",
            "## Traceability",
            "",
            "See the [documentation index](000-index.md) and [build manifest](manifest.json) for exact source identities, MRD versions, hashes, and generated-file declarations.",
            "",
        ]
        spec="\n".join(root); (staging/'001-specification.md').write_text(spec,encoding='utf-8'); (staging/'specification.md').write_text(spec,encoding='utf-8')
        files=[]
        for path in sorted(staging.rglob('*')):
            if path.is_file():
                b=path.read_bytes(); files.append({'path':path.relative_to(staging).as_posix(),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
        mrds=[]
        for path in sorted(repo.mrd_root.glob('*.mrd.json')):
            b=canonical_source_bytes(path); d=json.loads(path.read_text(encoding='utf-8')); mrds.append({'id':d['_mrd']['id'],'path':path.relative_to(repo.root).as_posix(),'sha256':hashlib.sha256(b).hexdigest(),'version':d['_mrd']['version']})
        manifest={'contract':{'name':'kis-work-management-spec-build','version':1},'specification':{'title':'KIS Work Management Specification','version':'1.0.0','status':'draft','layout_profile':'mcp-spec'},'inputs':{'mrds':mrds,'source_set_sha256':canonical_hash(mrds)},'validation':validation,'files':files,'bundle_sha256':canonical_hash(files)}
        (staging/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        if output.exists():
            if not replace: raise FileExistsError(output)
            shutil.rmtree(output)
        output.parent.mkdir(parents=True,exist_ok=True); staging.replace(output); return manifest
    except Exception:
        shutil.rmtree(staging,ignore_errors=True); raise


def verify_work_management_spec(repo: WorkManagementRepository, output: Path) -> dict[str, Any]:
    output=Path(output)
    if not (output/'manifest.json').is_file(): return {'status':'invalid','diagnostics':[{'code':'WORK_GENERATED_MANIFEST_MISSING','message':'manifest.json missing'}]}
    temp=output.parent/(output.name+'.verify.tmp')
    if temp.exists(): shutil.rmtree(temp)
    try:
        build_work_management_spec(repo,temp)
        expected={p.relative_to(temp).as_posix():canonical_source_bytes(p) for p in temp.rglob('*') if p.is_file()}
        actual={p.relative_to(output).as_posix():canonical_source_bytes(p) for p in output.rglob('*') if p.is_file()}
        if expected!=actual: return {'status':'invalid','diagnostics':[{'code':'WORK_GENERATED_DRIFT','message':'generated Work Management specification differs from deterministic current output'}]}
        return {'status':'valid','diagnostics':[]}
    finally:
        shutil.rmtree(temp,ignore_errors=True)
