from __future__ import annotations

import fnmatch
import json
import subprocess
from pathlib import Path
from typing import Any

_GOV = "prescriptives/repository-governance/01-repository-governance.json"
_REGISTRY = "prescriptives/repository-governance/02-prescriptive-artefact-registry.json"
_GRAMMAR = "prescriptives/repository-governance/03-directory-grammar.json"
_ENFORCEMENT = "prescriptives/repository-governance/04-enforcement-register.json"
_ROLES = {"prescriptive", "implementation", "derived_generated", "verification", "evidence"}


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
        return sorted(item.decode("utf-8") for item in result.stdout.split(b"\0") if item)
    except (OSError, subprocess.SubprocessError, UnicodeDecodeError):
        ignored = {".git", ".venv", ".pytest_cache", ".ruff_cache", "__pycache__", "build"}
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
        if "/" in pattern:
            if _match(path, pattern):
                return True
        elif any(fnmatch.fnmatchcase(part, pattern) for part in parts):
            return True
    return False


class RepositoryGovernanceRepository:
    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()

    def role_for(self, path: str, governance: dict[str, Any] | None = None) -> str | None:
        governance = governance or _load(self.root / _GOV)
        for rule in governance.get("classification_rules", []):
            if _match(path, str(rule.get("pattern", ""))):
                return str(rule.get("role"))
        return None

    def validate(self) -> dict[str, Any]:
        diagnostics: list[dict[str, str]] = []
        try:
            governance = _load(self.root / _GOV)
            registry = _load(self.root / _REGISTRY)
            grammar = _load(self.root / _GRAMMAR)
            enforcement = _load(self.root / _ENFORCEMENT)
            files = [path for path in _tracked_files(self.root) if not _is_transient(path, grammar)]
        except (OSError, ValueError, json.JSONDecodeError) as error:
            return self._result([self._diag("REPOSITORY_GOVERNANCE_LOAD_FAILED", str(error), "repository-governance")])

        self._validate_roles(governance, files, diagnostics)
        self._validate_directory_grammar(grammar, files, diagnostics)
        self._validate_registry(governance, registry, files, diagnostics)
        self._validate_enforcement(governance, enforcement, diagnostics)
        return self._result(diagnostics)

    def _validate_roles(self, governance: dict[str, Any], files: list[str], diagnostics: list[dict[str, str]]) -> None:
        declared_roles = {item.get("role") for item in governance.get("semantic_roles", [])}
        if declared_roles != _ROLES:
            diagnostics.append(self._diag("REPOSITORY_ROLE_CATALOG_INVALID", "semantic role catalogue must define the five repository roles exactly once", _GOV))
        for path in files:
            role = self.role_for(path, governance)
            if role not in _ROLES:
                diagnostics.append(self._diag("REPOSITORY_ARTEFACT_UNCLASSIFIED", f"persistent artefact has no governed semantic role: {path}", path))

    def _validate_directory_grammar(self, grammar: dict[str, Any], files: list[str], diagnostics: list[dict[str, str]]) -> None:
        top_dirs = set(grammar.get("top_level_directories", []))
        root_files = set(grammar.get("root_files", []))
        closed = {key: set(value) for key, value in grammar.get("closed_subdirectories", {}).items()}
        contract_domains = set(grammar.get("contract_domains", []))
        for path in files:
            parts = path.split("/")
            if len(parts) == 1:
                if path not in root_files:
                    diagnostics.append(self._diag("REPOSITORY_ROOT_FILE_UNKNOWN", f"root artefact is not a legal grammar slot: {path}", path))
                continue
            top = parts[0]
            if top not in top_dirs:
                diagnostics.append(self._diag("REPOSITORY_DIRECTORY_UNKNOWN", f"top-level directory is not legal: {top}", path))
                continue
            if top in closed and len(parts) > 2 and parts[1] not in closed[top]:
                diagnostics.append(self._diag("REPOSITORY_SUBDIRECTORY_UNKNOWN", f"{top}/{parts[1]} is not a legal governed subdirectory", path))
            if top == "contracts" and len(parts) > 2 and parts[1] not in contract_domains:
                diagnostics.append(self._diag("REPOSITORY_SUBDIRECTORY_UNKNOWN", f"contracts/{parts[1]} is not a registered contract domain", path))
            if top == "publication" and len(parts) > 2:
                diagnostics.append(self._diag("REPOSITORY_SUBDIRECTORY_UNKNOWN", "publication configuration must remain directly under publication/ unless the grammar is amended", path))
            if top in {"scripts", "tests", "tooling"} and len(parts) > 2:
                diagnostics.append(self._diag("REPOSITORY_SUBDIRECTORY_UNKNOWN", f"{top}/ has no registered persistent subdirectory class", path))
        reserved = grammar.get("reserved_workspace", {})
        if reserved.get("path") != ".work" or any(reserved.get(key) is not False for key in ("canonical_authority", "published", "required_as_product_input")) or reserved.get("promotion_requires_grammar_amendment") is not True:
            diagnostics.append(self._diag("REPOSITORY_WORKSPACE_POLICY_INVALID", ".work must remain disposable/non-authoritative and require grammar amendment before promotion", _GRAMMAR))

    def _validate_registry(self, governance: dict[str, Any], registry: dict[str, Any], files: list[str], diagnostics: list[dict[str, str]]) -> None:
        entries = registry.get("entries", [])
        by_path: dict[str, dict[str, Any]] = {}
        fact_owners: dict[str, str] = {}
        for entry in entries:
            path = entry.get("canonical_path")
            if not isinstance(path, str) or path in by_path:
                diagnostics.append(self._diag("PRESCRIPTIVE_REGISTRY_PATH_DUPLICATE", f"registry path is missing or duplicated: {path!r}", _REGISTRY))
                continue
            by_path[path] = entry
            for fact_id in entry.get("fact_ids", []):
                previous = fact_owners.get(str(fact_id))
                if previous is not None:
                    diagnostics.append(self._diag("PRESCRIPTIVE_FACT_OWNER_DUPLICATE", f"fact {fact_id} is owned by both {previous} and {path}", path))
                else:
                    fact_owners[str(fact_id)] = path
            required = ("identity", "purpose", "semantic_role", "artefact_kind", "canonical_path", "authoritative_owner", "governing_artefact", "scope_in", "scope_out", "status", "record_mode", "editability", "provenance", "relationships", "fact_ids")
            missing = [key for key in required if key not in entry]
            if missing:
                diagnostics.append(self._diag("PRESCRIPTIVE_REGISTRY_ENTRY_INCOMPLETE", f"registry entry {path} is missing: {', '.join(missing)}", path))
        for path in files:
            if self.role_for(path, governance) == "prescriptive" and path not in by_path:
                diagnostics.append(self._diag("PRESCRIPTIVE_ARTEFACT_UNREGISTERED", f"prescriptive artefact is not registered: {path}", path))
        for path in by_path:
            if path not in files:
                diagnostics.append(self._diag("PRESCRIPTIVE_REGISTRY_PATH_MISSING", f"registered prescriptive artefact does not exist: {path}", path))
            elif self.role_for(path, governance) != "prescriptive":
                diagnostics.append(self._diag("PRESCRIPTIVE_REGISTRY_ROLE_INVALID", f"registered artefact is not classified prescriptive: {path}", path))

    def _validate_enforcement(self, governance: dict[str, Any], enforcement: dict[str, Any], diagnostics: list[dict[str, str]]) -> None:
        rules = {item.get("rule_id"): item for item in governance.get("rules", [])}
        entries = {item.get("rule_id"): item for item in enforcement.get("entries", [])}
        if set(entries) != set(rules):
            diagnostics.append(self._diag("REPOSITORY_ENFORCEMENT_COVERAGE_INVALID", "every repository governance rule must have exactly one enforcement-register entry", _ENFORCEMENT))
        test_source = (self.root / "tests" / "test_repository_governance.py").read_text(encoding="utf-8") if (self.root / "tests" / "test_repository_governance.py").exists() else ""
        for rule_id, entry in entries.items():
            if entry.get("class") == "deterministic":
                fixture = entry.get("negative_fixture")
                if not isinstance(fixture, str) or not fixture or f"def {fixture}(" not in test_source:
                    diagnostics.append(self._diag("REPOSITORY_NEGATIVE_FIXTURE_MISSING", f"deterministic rule {rule_id} does not resolve to a failing fixture", _ENFORCEMENT))
            elif entry.get("class") != "review":
                diagnostics.append(self._diag("REPOSITORY_ENFORCEMENT_CLASS_INVALID", f"rule {rule_id} has unknown enforcement class", _ENFORCEMENT))

    @staticmethod
    def _diag(code: str, message: str, location: str) -> dict[str, str]:
        return {"code": code, "message": message, "location": location}

    @staticmethod
    def _result(diagnostics: list[dict[str, str]]) -> dict[str, Any]:
        return {"status": "invalid" if diagnostics else "valid", "diagnostics": diagnostics}
