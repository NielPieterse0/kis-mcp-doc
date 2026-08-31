from __future__ import annotations

import fnmatch
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

_GOV = "prescriptives/governance/01-repository-governance.json"
_REGISTRY = "prescriptives/governance/02-prescriptive-artefact-registry.json"
_GRAMMAR = "prescriptives/governance/03-directory-grammar.json"
_RULE_SCHEMA = "contracts/governance/v1/governed-rule.schema.json"
_ROLES = {"prescriptive", "implementation", "derived_generated", "verification", "evidence"}
_REQUIRED_SLOT_FIELDS = {
    "slot_id", "patterns", "purpose", "permitted_artefact_types", "prohibited_artefact_types",
    "allowed_semantic_roles", "authority_constraints", "allowed_relationships", "editability",
    "generation_status", "lifecycle", "retention", "verification", "origin",
}
_MRD_SPEC_CONCERNS = {
    "classification", "applicability", "ownership", "layering", "dependencies",
    "provenance", "lifecycle", "validation",
}
_UUID_RE = re.compile(r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def _normalized_statement(value: str) -> str:
    return " ".join(value.casefold().split())


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _tracked_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            capture_output=True, check=True, timeout=10,
        )
        return sorted(path for item in result.stdout.split(b"\0") if item for path in [item.decode("utf-8")] if (root / path).is_file())
    except (OSError, subprocess.SubprocessError, UnicodeDecodeError):
        ignored = {".git", ".venv", ".pytest_cache", ".ruff_cache", "__pycache__", "build", ".temp"}
        return sorted(
            p.relative_to(root).as_posix()
            for p in root.rglob("*")
            if p.is_file() and not any(part in ignored or part.endswith(".egg-info") for part in p.relative_to(root).parts)
        )


def _match(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3]
        return path == prefix or path.startswith(prefix + "/")
    return fnmatch.fnmatchcase(path, pattern)


def _is_transient(path: str, grammar: dict[str, Any]) -> bool:
    parts = path.split("/")
    for pattern in grammar.get("transient_non_governed", []):
        pattern = str(pattern)
        if "/" in pattern and _match(path, pattern):
            return True
        if "/" not in pattern and any(fnmatch.fnmatchcase(part, pattern) for part in parts):
            return True
    return False


def _artifact_kind(path: str) -> str:
    if path == "AGENTS.md": return "repository_authority"
    if path.startswith("prescriptives/governance/"): return "governance_prescriptive"
    if path.startswith("prescriptives/") and path.endswith(".mrd.json"): return "mrd"
    if path.startswith("contracts/"): return "contract"
    if path.startswith("publication/"): return "publication_configuration"
    if path.startswith("src/"): return "implementation"
    if path.startswith("scripts/"): return "script"
    if path.startswith("tests/"): return "test"
    if path.startswith("evidence/"): return "evidence"
    if path.startswith("generated/"): return "generated_projection"
    if path.startswith("tooling/"): return "tooling"
    if path == ".github/CODEOWNERS": return "platform_prescriptive"
    if path.startswith(".github/workflows/"): return "platform_verification"
    if path == ".github/pull_request_template.md": return "generated_human_surface"
    if path == ".github/dependabot.yml": return "repository_configuration"
    if path.startswith(".work/changes/"): return "change_record"
    if path in {"README.md", "CONTRIBUTING.md", "SECURITY.md"}: return "generated_human_surface"
    if path in {"pyproject.toml", "uv.lock", ".editorconfig", ".gitattributes", ".gitignore"}: return "repository_configuration"
    return "unknown"


def enforcement_projection(governance: dict[str, Any]) -> dict[str, Any]:
    entries = []
    for rule in governance.get("rules", []):
        verification = rule["verification"]
        entries.append({
            "rule_id": rule["rule_id"],
            "authoritative_owner": rule["authoritative_owner"],
            "method": verification["method"],
            "implementation": rule["implementation"],
            "validator": verification["validator"],
            "entry_point": verification["entry_point"],
            "execution_point": verification["execution_point"],
            "expected_result": verification["expected_result"],
            "failure_code": verification["failure_code"],
            "negative_fixture": verification["negative_fixture"],
            "residual_review": verification["residual_review"],
            "evidence": rule["evidence"],
        })
    return {
        "schema_version": 1,
        "projection": "repository_governance_enforcement_register",
        "authority": "derived_non_authoritative",
        "generated_from": _GOV,
        "entries": entries,
    }


class RepositoryGovernanceRepository:
    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()

    def role_matches(self, path: str, governance: dict[str, Any] | None = None) -> list[str]:
        governance = governance or _load(self.root / _GOV)
        return [str(rule.get("role")) for rule in governance.get("classification_rules", []) if _match(path, str(rule.get("pattern", "")))]

    def role_for(self, path: str, governance: dict[str, Any] | None = None) -> str | None:
        matches = self.role_matches(path, governance)
        return matches[0] if len(matches) == 1 else None

    def slot_matches(self, path: str, grammar: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        grammar = grammar or _load(self.root / _GRAMMAR)
        return [slot for slot in grammar.get("slots", []) if any(_match(path, str(pattern)) for pattern in slot.get("patterns", []))]

    def validate(self) -> dict[str, Any]:
        diagnostics: list[dict[str, str]] = []
        try:
            governance = _load(self.root / _GOV)
            registry = _load(self.root / _REGISTRY)
            grammar = _load(self.root / _GRAMMAR)
            rule_schema = _load(self.root / _RULE_SCHEMA)
            files = [path for path in _tracked_files(self.root) if not _is_transient(path, grammar)]
        except (OSError, ValueError, json.JSONDecodeError) as error:
            return self._result([self._diag("REPOSITORY_GOVERNANCE_LOAD_FAILED", str(error), "governance")])
        self._validate_governance(governance, rule_schema, diagnostics)
        self._validate_roles(governance, files, diagnostics)
        self._validate_directory_grammar(grammar, governance, files, diagnostics)
        self._validate_registry(registry, governance, grammar, files, diagnostics)
        self._validate_normative_restatement(governance, files, diagnostics)
        self._validate_boundary(files, diagnostics)
        self._validate_mrd_identity(diagnostics)
        return self._result(diagnostics)

    def _validate_governance(self, governance: dict[str, Any], rule_schema: dict[str, Any], diagnostics: list[dict[str, str]]) -> None:
        declared_roles = {item.get("role") for item in governance.get("semantic_roles", [])}
        if declared_roles != _ROLES or len(governance.get("semantic_roles", [])) != len(_ROLES):
            diagnostics.append(self._diag("REPOSITORY_ROLE_CATALOG_INVALID", "semantic role catalogue must define the five repository roles exactly once", _GOV))
        if governance.get("authority", {}).get("canonical_owner") != governance.get("id"):
            diagnostics.append(self._diag("REPOSITORY_CANONICAL_OWNER_INVALID", "Governance must identify itself as the canonical repository-wide owner", _GOV))
        validator = Draft202012Validator(rule_schema)
        rules = governance.get("rules", [])
        ids: set[str] = set(); fixtures: set[str] = set()
        test_path = self.root / "tests" / "test_repository_governance.py"
        test_source = test_path.read_text(encoding="utf-8") if test_path.exists() else ""
        for index, rule in enumerate(rules):
            errors = sorted(validator.iter_errors(rule), key=lambda e: tuple(str(p) for p in e.absolute_path))
            if errors:
                diagnostics.append(self._diag("REPOSITORY_RULE_SCHEMA_INVALID", errors[0].message, f"{_GOV}#rules/{index}")); continue
            rid = rule["rule_id"]
            if rid in ids:
                diagnostics.append(self._diag("REPOSITORY_RULE_ID_DUPLICATE", f"duplicate governed rule id: {rid}", _GOV))
            ids.add(rid)
            if rule["authoritative_owner"] != governance.get("id"):
                diagnostics.append(self._diag("REPOSITORY_RULE_OWNER_INVALID", f"rule {rid} is not owned by canonical Governance", _GOV))
            verification = rule["verification"]; fixture = verification["negative_fixture"]
            if fixture in fixtures or f"def {fixture}(" not in test_source:
                diagnostics.append(self._diag("REPOSITORY_NEGATIVE_FIXTURE_MISSING", f"rule {rid} does not resolve to a unique failing fixture", _GOV))
            fixtures.add(fixture)
            residual = verification.get("residual_review")
            if verification["method"] == "deterministic" and residual is not None:
                diagnostics.append(self._diag("REPOSITORY_REVIEW_POLICY_INVALID", f"deterministic rule {rid} cannot require residual human review", _GOV))
            if verification["method"] == "deterministic_plus_residual_review":
                required = set(governance.get("validation_policy", {}).get("residual_review_required_fields", []))
                if not isinstance(residual, dict) or not required.issubset(residual):
                    diagnostics.append(self._diag("REPOSITORY_REVIEW_POLICY_INVALID", f"residual review for {rid} is not fully bounded and justified", _GOV))
        for rule in rules:
            rid = rule.get("rule_id", "<unknown>")
            implementation_paths = [item.get("artifact") for item in rule.get("implementation", []) if isinstance(item, dict)]
            verification = rule.get("verification", {})
            evidence = rule.get("evidence", {})
            reference_paths = implementation_paths + [verification.get("validator"), verification.get("execution_point")]
            evidence_location = evidence.get("location")
            if isinstance(evidence_location, str):
                reference_paths.append(evidence_location.split("::", 1)[0])
            unresolved = [path for path in reference_paths if not isinstance(path, str) or not path or not (self.root / path).is_file()]
            validator_path = verification.get("validator")
            failure_code = verification.get("failure_code")
            if isinstance(validator_path, str) and (self.root / validator_path).is_file() and isinstance(failure_code, str):
                if failure_code not in (self.root / validator_path).read_text(encoding="utf-8"):
                    unresolved.append(f"{validator_path}::{failure_code}")
            if unresolved:
                diagnostics.append(self._diag("REPOSITORY_RULE_ASSURANCE_REFERENCE_INVALID", f"rule {rid} has unresolved assurance references: {', '.join(map(str, unresolved))}", _GOV))
            lifecycle = rule.get("lifecycle", {})
            status = lifecycle.get("status")
            superseded_by = lifecycle.get("superseded_by")
            supersedes = lifecycle.get("supersedes", [])
            if (status == "superseded") != isinstance(superseded_by, str) or any(target not in ids or target == rid for target in supersedes):
                diagnostics.append(self._diag("REPOSITORY_GOVERNANCE_VOCABULARY_INVALID", f"rule {rid} has invalid lifecycle or supersession references", _GOV))
        order = governance.get("validation_policy", {}).get("order", [])
        if not order or order[-1] != "human_review" or "deterministic_validator" not in order:
            diagnostics.append(self._diag("REPOSITORY_REVIEW_POLICY_INVALID", "validation policy must place human review after deterministic validation", _GOV))
        ranks = governance.get("evidence_model", {}).get("conformance_evidence_precedence", [])
        if [item.get("rank") for item in ranks] != list(range(1, len(ranks) + 1)) or len({item.get("class") for item in ranks}) != len(ranks):
            diagnostics.append(self._diag("REPOSITORY_EVIDENCE_PRECEDENCE_INVALID", "conformance evidence precedence must be unique and contiguous", _GOV))
        constructs = governance.get("governed_vocabulary", {}).get("constructs", [])
        names = {item.get("name") for item in constructs}
        if names != {"principle","policy","rule","requirement","implementation","verification","evidence","projection"}:
            diagnostics.append(self._diag("REPOSITORY_GOVERNANCE_VOCABULARY_INVALID", "governed construct vocabulary is incomplete", _GOV))
        nonnormative = {item["name"] for item in constructs if item.get("normative") is False}
        for relation in governance.get("governed_vocabulary", {}).get("relationships", []):
            if relation.get("authority_effect") not in {"none", "subordinate_no_override", "lifecycle_only"}:
                diagnostics.append(self._diag("REPOSITORY_GOVERNANCE_VOCABULARY_INVALID", "unknown authority effect in relationship vocabulary", _GOV))
            if relation.get("name") in {"implements","verifies","evidences","projects"} and not set(relation.get("from", [])).issubset(nonnormative):
                diagnostics.append(self._diag("REPOSITORY_GOVERNANCE_VOCABULARY_INVALID", "non-normative relationship originates from a normative construct", _GOV))
        if (self.root / "prescriptives" / "governance" / "04-enforcement-register.json").exists():
            diagnostics.append(self._diag("REPOSITORY_ENFORCEMENT_PROJECTION_INVALID", "enforcement register must not be independently authored under prescriptives", "prescriptives/governance/04-enforcement-register.json"))

    def _validate_roles(self, governance: dict[str, Any], files: list[str], diagnostics: list[dict[str, str]]) -> None:
        for path in files:
            matches = self.role_matches(path, governance)
            if len(matches) != 1 or matches[0] not in _ROLES:
                diagnostics.append(self._diag("REPOSITORY_ROLE_RESOLUTION_INVALID", f"persistent artefact must resolve to exactly one semantic role; {path} resolved {matches}", path))

    def _validate_directory_grammar(self, grammar: dict[str, Any], governance: dict[str, Any], files: list[str], diagnostics: list[dict[str, str]]) -> None:
        slot_ids: set[str] = set()
        for slot in grammar.get("slots", []):
            missing = sorted(_REQUIRED_SLOT_FIELDS - set(slot))
            sid = str(slot.get("slot_id", ""))
            if not sid or sid in slot_ids or missing:
                diagnostics.append(self._diag("REPOSITORY_SLOT_CONTRACT_INVALID", f"slot {sid!r} is duplicated or incomplete: {missing}", _GRAMMAR))
            slot_ids.add(sid)
            origin = slot.get("origin", {})
            if origin.get("kind") not in {"github_issue", "governed_change", "repository_obligation"} or not origin.get("locator"):
                diagnostics.append(self._diag("REPOSITORY_SLOT_ORIGIN_MISSING", f"slot {sid} lacks a governed demonstrated-need origin", _GRAMMAR))
            if not slot.get("permitted_artefact_types") or not slot.get("allowed_semantic_roles"):
                diagnostics.append(self._diag("REPOSITORY_SLOT_CONTRACT_INVALID", f"slot {sid} must declare permitted types and roles", _GRAMMAR))
            if "derived_generated" in set(slot.get("allowed_semantic_roles", [])) and slot.get("authority_constraints", {}).get("write_back") is not False:
                diagnostics.append(self._diag("GENERATED_AUTHORITY_PROHIBITED", f"generated slot must explicitly prohibit write-back: {sid}", _GRAMMAR))
        for path in files:
            slots = self.slot_matches(path, grammar)
            if len(slots) != 1:
                code = "REPOSITORY_DIRECTORY_UNKNOWN" if not slots else "REPOSITORY_SLOT_RESOLUTION_INVALID"
                diagnostics.append(self._diag(code, f"persistent artefact must resolve to exactly one legal slot; {path} resolved {[s.get('slot_id') for s in slots]}", path)); continue
            slot = slots[0]; role = self.role_for(path, governance); kind = _artifact_kind(path)
            if role not in set(slot.get("allowed_semantic_roles", [])):
                diagnostics.append(self._diag("REPOSITORY_SLOT_ROLE_PROHIBITED", f"{path} role {role!r} is not legal in slot {slot['slot_id']}", path))
            if kind not in set(slot.get("permitted_artefact_types", [])) or kind in set(slot.get("prohibited_artefact_types", [])):
                diagnostics.append(self._diag("REPOSITORY_SLOT_ARTEFACT_PROHIBITED", f"{path} kind {kind!r} is not legal in slot {slot['slot_id']}", path))
            constraints = slot.get("authority_constraints", {})
            if role in {"derived_generated","verification","evidence"} and constraints.get("canonical_owner_required") is True:
                diagnostics.append(self._diag("REPOSITORY_SLOT_AUTHORITY_INVALID", f"non-prescriptive role cannot be required to own normative authority: {path}", path))
            if role == "derived_generated" and constraints.get("write_back") is not False:
                diagnostics.append(self._diag("GENERATED_AUTHORITY_PROHIBITED", f"generated slot must explicitly prohibit write-back: {slot['slot_id']}", _GRAMMAR))
        reserved = grammar.get("reserved_workspace", {})
        if reserved.get("path") != ".work" or any(reserved.get(key) is not False for key in ("canonical_authority", "published", "required_as_product_input")) or reserved.get("promotion_requires_grammar_amendment") is not True:
            diagnostics.append(self._diag("REPOSITORY_WORKSPACE_POLICY_INVALID", ".work must remain disposable/non-authoritative and require grammar amendment before promotion", _GRAMMAR))

    def _validate_registry(self, registry: dict[str, Any], governance: dict[str, Any], grammar: dict[str, Any], files: list[str], diagnostics: list[dict[str, str]]) -> None:
        entries = registry.get("entries", []); by_path: dict[str, dict[str, Any]] = {}; fact_owners: dict[str, str] = {}
        required = {"identity","title","purpose","semantic_role","artefact_kind","canonical_path","authoritative_owner","governing_artefact","scope_in","scope_out","status","record_mode","editability","provenance","relationships","fact_ids","human_projection"}
        relationship_contracts = {item.get("registry_key"): item for item in grammar.get("relationship_contracts", []) if isinstance(item, dict)}
        for entry in entries:
            path = entry.get("canonical_path")
            if not isinstance(path, str) or path in by_path:
                diagnostics.append(self._diag("PRESCRIPTIVE_REGISTRY_PATH_DUPLICATE", f"registry path is missing or duplicated: {path!r}", _REGISTRY)); continue
            by_path[path] = entry
            missing = sorted(required - set(entry))
            if missing:
                diagnostics.append(self._diag("PRESCRIPTIVE_REGISTRY_ENTRY_INCOMPLETE", f"registry entry {path} is missing: {', '.join(missing)}", path))
            projection = entry.get("human_projection", {})
            if projection.get("disposition") not in {"projected","not_published"} or (projection.get("disposition") == "not_published" and not projection.get("reason")):
                diagnostics.append(self._diag("PRESCRIPTIVE_HUMAN_PROJECTION_MISSING", f"prescriptive entry has no governed human projection disposition: {path}", path))
            for relationship_key, targets in entry.get("relationships", {}).items():
                contract = relationship_contracts.get(relationship_key)
                if contract is None or not isinstance(targets, list):
                    diagnostics.append(self._diag("REPOSITORY_RELATIONSHIP_INVALID", f"unregistered repository relationship {relationship_key!r} on {path}", path)); continue
                semantic = contract.get("semantic_relationship")
                for target in targets:
                    target_role = self.role_for(target, governance) if isinstance(target, str) and target in files else None
                    target_slots = self.slot_matches(target, grammar) if isinstance(target, str) else []
                    if target_role not in set(contract.get("target_roles", [])) or len(target_slots) != 1 or semantic not in set(target_slots[0].get("allowed_relationships", [])):
                        diagnostics.append(self._diag("REPOSITORY_RELATIONSHIP_INVALID", f"{relationship_key} from {path} has illegal or unresolved target {target!r}", path))
            for fact_id in entry.get("fact_ids", []):
                previous = fact_owners.get(str(fact_id))
                if previous is not None:
                    diagnostics.append(self._diag("PRESCRIPTIVE_FACT_OWNER_DUPLICATE", f"fact {fact_id} is owned by both {previous} and {path}", path))
                else: fact_owners[str(fact_id)] = path
        for path in files:
            if self.role_for(path, governance) == "prescriptive" and path not in by_path:
                diagnostics.append(self._diag("PRESCRIPTIVE_ARTEFACT_UNREGISTERED", f"prescriptive artefact is not registered: {path}", path))
        for path in by_path:
            if path not in files:
                diagnostics.append(self._diag("PRESCRIPTIVE_REGISTRY_PATH_MISSING", f"registered prescriptive artefact does not exist: {path}", path))
            elif self.role_for(path, governance) != "prescriptive":
                diagnostics.append(self._diag("PRESCRIPTIVE_REGISTRY_ROLE_INVALID", f"registered artefact is not classified prescriptive: {path}", path))

    def _validate_normative_restatement(self, governance: dict[str, Any], files: list[str], diagnostics: list[dict[str, str]]) -> None:
        canonical_statements = {_normalized_statement(rule["statement"]): rule["rule_id"] for rule in governance.get("rules", [])}
        rule_ids = set(canonical_statements.values())
        for path in files:
            if path in {_GOV, _REGISTRY} or self.role_for(path, governance) != "prescriptive":
                continue
            try:
                text = (self.root / path).read_text(encoding="utf-8-sig")
            except (OSError, UnicodeDecodeError):
                continue
            normalized_text = _normalized_statement(text)
            duplicate = next((rid for statement, rid in canonical_statements.items() if statement in normalized_text), None)
            reused_id = next((rid for rid in rule_ids if rid in text), None)
            if duplicate or reused_id:
                diagnostics.append(self._diag("REPOSITORY_NORMATIVE_RESTATEMENT_PROHIBITED", f"non-owning prescriptive artefact restates canonical repository rule {duplicate or reused_id}", path))

    def _validate_boundary(self, files: list[str], diagnostics: list[dict[str, str]]) -> None:
        governance_files = [p for p in files if p.startswith("prescriptives/governance/")]
        if any(p.endswith(".mrd.json") for p in governance_files):
            diagnostics.append(self._diag("REPOSITORY_GOVERNANCE_BOUNDARY_INVALID", "repository Governance cannot contain MRD Specification records", "prescriptives/governance"))
        expected_governance = {"prescriptives/governance/01-repository-governance.json","prescriptives/governance/02-prescriptive-artefact-registry.json","prescriptives/governance/03-directory-grammar.json"}
        if set(governance_files) != expected_governance:
            diagnostics.append(self._diag("REPOSITORY_GOVERNANCE_BOUNDARY_INVALID", "Governance domain contains unexpected authority artefacts", "prescriptives/governance"))
        spec_paths = sorted(self.root.glob("prescriptives/mrd-specification/*.mrd.json"))
        concerns = []
        for path in spec_paths:
            try: concerns.append(_load(path).get("content", {}).get("concern"))
            except (OSError, ValueError, json.JSONDecodeError): continue
        if set(concerns) != _MRD_SPEC_CONCERNS or len(concerns) != len(_MRD_SPEC_CONCERNS):
            diagnostics.append(self._diag("REPOSITORY_GOVERNANCE_BOUNDARY_INVALID", "MRD Specification must own exactly its eight conformance concerns and no repository Governance concern", "prescriptives/mrd-specification"))

    def _validate_mrd_identity(self, diagnostics: list[dict[str, str]]) -> None:
        ids: set[str] = set(); legacy: set[str] = set()
        for path in sorted(self.root.glob("prescriptives/**/*.mrd.json")):
            try: doc = _load(path)
            except (OSError, ValueError, json.JSONDecodeError): continue
            env = doc.get("_mrd", {}); identity = env.get("id"); relative = path.relative_to(self.root).as_posix()
            if not isinstance(identity, str) or not _UUID_RE.fullmatch(identity) or identity in ids or env.get("canonical_path") != relative:
                diagnostics.append(self._diag("MRD_IDENTITY_METADATA_INVALID", f"MRD stable identity/path metadata is invalid: {relative}", relative))
            ids.add(str(identity))
            aliases = env.get("legacy_ids", [])
            if not isinstance(aliases, list) or identity in aliases or any(alias in legacy for alias in aliases):
                diagnostics.append(self._diag("MRD_IDENTITY_METADATA_INVALID", f"MRD legacy identity migration aliases are invalid: {relative}", relative))
            legacy.update(str(alias) for alias in aliases)
            binding = env.get("revision_binding", {})
            if binding.get("mode") != "external_git_provider_evidence" or binding.get("git_revision") is not None or binding.get("change_identity_source") != "github_issue_and_pull_request":
                diagnostics.append(self._diag("MRD_IDENTITY_METADATA_INVALID", f"MRD revision/change provenance binding is invalid: {relative}", relative))

    @staticmethod
    def _diag(code: str, message: str, location: str) -> dict[str, str]:
        return {"code": code, "message": message, "location": location}

    @staticmethod
    def _result(diagnostics: list[dict[str, str]]) -> dict[str, Any]:
        return {"status": "invalid" if diagnostics else "valid", "diagnostics": diagnostics}
