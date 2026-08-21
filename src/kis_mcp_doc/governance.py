from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


CONCERNS = ("classification", "layering", "dependencies", "provenance", "lifecycle", "validation")


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class GovernanceRepository:
    def __init__(self, root: Path, mrd_root: Path) -> None:
        self.root = Path(root).resolve()
        self.mrd_root = Path(mrd_root).resolve()
        self.schema_path = self.root / "contracts" / "mrd" / "v1" / "mrd.schema.json"
        self.content_schema_path = self.root / "contracts" / "governance" / "v1" / "content.schema.json"

    def load(self) -> dict[str, dict[str, Any]]:
        documents: dict[str, dict[str, Any]] = {}
        for path in sorted(self.mrd_root.glob("*.mrd.json")):
            document = json.loads(path.read_text(encoding="utf-8"))
            doc_id = document.get("_mrd", {}).get("id")
            if not isinstance(doc_id, str) or not doc_id:
                raise ValueError(f"MRD missing stable id: {path}")
            if doc_id in documents:
                raise ValueError(f"duplicate MRD id: {doc_id}")
            documents[doc_id] = document
        return documents

    def validate(self) -> dict[str, Any]:
        try:
            documents = self.load()
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
            return self._result([self._diagnostic("schema", "MRD_SCHEMA_INVALID", str(error), "$", None)])
        return self.validate_documents(documents)

    def validate_documents(self, documents: dict[str, dict[str, Any]]) -> dict[str, Any]:
        diagnostics: list[dict[str, Any]] = []
        concerns = self._concern_owners(documents, diagnostics)
        self._validate_schema(documents, diagnostics)
        self._validate_rule_ids(documents, diagnostics)
        self._validate_classification(documents, concerns, diagnostics)
        self._validate_layering(documents, concerns, diagnostics)
        self._validate_dependencies(documents, concerns, diagnostics)
        self._validate_provenance(documents, concerns, diagnostics)
        self._validate_lifecycle(documents, concerns, diagnostics)
        return self._result(diagnostics)

    def _concern_owners(self, documents: dict[str, dict[str, Any]], diagnostics: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        owners: dict[str, dict[str, Any]] = {}
        for doc_id, document in documents.items():
            concern = document.get("content", {}).get("concern")
            if concern not in CONCERNS:
                diagnostics.append(self._diagnostic("classification", "MRD_GOVERNANCE_CONCERN_MISSING", f"{doc_id} does not declare one of the six governance concerns", f"{doc_id}.content.concern", doc_id))
                continue
            if concern in owners:
                diagnostics.append(self._diagnostic("classification", "MRD_GOVERNANCE_CONCERN_DUPLICATE", f"multiple MRDs own concern {concern}", f"{doc_id}.content.concern", doc_id))
                continue
            owners[concern] = document
        for concern in CONCERNS:
            if concern not in owners:
                diagnostics.append(self._diagnostic("classification", "MRD_GOVERNANCE_CONCERN_MISSING", f"no MRD owns concern {concern}", "$.content.concern", None))
        return owners

    def _validate_schema(self, documents: dict[str, dict[str, Any]], diagnostics: list[dict[str, Any]]) -> None:
        try:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
            content_schema = json.loads(self.content_schema_path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            Draft202012Validator.check_schema(content_schema)
            validator = Draft202012Validator(schema)
            content_validator = Draft202012Validator(content_schema)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            diagnostics.append(self._diagnostic("schema", "MRD_SCHEMA_INVALID", f"unable to load MRD schema: {error}", str(self.schema_path), None))
            return
        for doc_id, document in documents.items():
            errors = sorted(validator.iter_errors(document), key=lambda item: tuple(str(p) for p in item.absolute_path))
            content_errors = sorted(content_validator.iter_errors(document.get("content", {})), key=lambda item: tuple(str(p) for p in item.absolute_path))
            for error in errors:
                location = "/".join(str(p) for p in error.absolute_path) or "$"
                diagnostics.append(self._diagnostic("schema", "MRD_SCHEMA_INVALID", error.message, location, doc_id))
            for error in content_errors:
                suffix = "/".join(str(p) for p in error.absolute_path)
                location = "content" if not suffix else f"content/{suffix}"
                diagnostics.append(self._diagnostic("schema", "MRD_SCHEMA_INVALID", error.message, location, doc_id))

    def _validate_rule_ids(
        self,
        documents: dict[str, dict[str, Any]],
        diagnostics: list[dict[str, Any]],
    ) -> None:
        owners: dict[str, str] = {}
        for doc_id, document in documents.items():
            for index, rule in enumerate(document.get("content", {}).get("rules", [])):
                rule_id = rule.get("rule_id")
                if not isinstance(rule_id, str):
                    continue
                previous = owners.get(rule_id)
                if previous is not None:
                    diagnostics.append(
                        self._diagnostic(
                            "schema",
                            "MRD_RULE_ID_DUPLICATE",
                            f"rule id {rule_id} is owned by both {previous} and {doc_id}",
                            f"{doc_id}.content.rules[{index}].rule_id",
                            doc_id,
                        )
                    )
                else:
                    owners[rule_id] = doc_id

    def _validate_classification(self, documents: dict[str, dict[str, Any]], concerns: dict[str, dict[str, Any]], diagnostics: list[dict[str, Any]]) -> None:
        owner = concerns.get("classification")
        if owner is None:
            return
        content = owner.get("content", {})
        classes = {entry.get("code") for entry in content.get("classes", [])}
        catalog = content.get("type_catalog", [])
        pairs = {(entry.get("class"), entry.get("type")) for entry in catalog}
        codes = [entry.get("code") for entry in catalog]
        expected = content.get("catalog_policy", {}).get("expected_type_count")
        if expected != len(catalog) or len(set(codes)) != len(codes):
            diagnostics.append(self._diagnostic("classification", "MRD_CATALOG_COUNT_MISMATCH", f"catalog declares {expected} types but resolves to {len(catalog)} entries and {len(set(codes))} unique codes", "classification.content.type_catalog", owner["_mrd"]["id"]))
        for doc_id, document in documents.items():
            envelope = document.get("_mrd", {})
            cls, typ = envelope.get("class"), envelope.get("type")
            if cls not in classes:
                diagnostics.append(self._diagnostic("classification", "MRD_CLASS_UNKNOWN", f"unknown MRD class {cls!r}", f"{doc_id}._mrd.class", doc_id))
            if (cls, typ) not in pairs:
                diagnostics.append(self._diagnostic("classification", "MRD_TYPE_INVALID", f"invalid class/type pair {cls}-{typ}", f"{doc_id}._mrd.type", doc_id))
            parts = doc_id.split("-")
            if len(parts) < 5 or parts[-3] != cls or parts[-2] != typ:
                diagnostics.append(self._diagnostic("classification", "MRD_ID_CLASS_TYPE_MISMATCH", f"id {doc_id} does not encode class/type {cls}-{typ}", f"{doc_id}._mrd.id", doc_id))

    def _validate_layering(self, documents: dict[str, dict[str, Any]], concerns: dict[str, dict[str, Any]], diagnostics: list[dict[str, Any]]) -> None:
        owner = concerns.get("layering")
        if owner is None:
            return
        layers = {entry.get("code") for entry in owner.get("content", {}).get("layers", [])}
        for doc_id, document in documents.items():
            if document.get("_mrd", {}).get("layer") not in layers:
                diagnostics.append(self._diagnostic("layering", "MRD_LAYER_INVALID", f"unknown layer {document.get('_mrd', {}).get('layer')!r}", f"{doc_id}._mrd.layer", doc_id))

    def _validate_dependencies(self, documents: dict[str, dict[str, Any]], concerns: dict[str, dict[str, Any]], diagnostics: list[dict[str, Any]]) -> None:
        graph: dict[str, set[str]] = {doc_id: set() for doc_id in documents}
        for doc_id, document in documents.items():
            source_layer = document.get("_mrd", {}).get("layer")
            seen: set[tuple[str, str, str]] = set()
            for index, dependency in enumerate(document.get("_mrd", {}).get("dependencies", [])):
                target_kind = "mrd" if "mrd_id" in dependency else "source"
                target = dependency.get("mrd_id") or dependency.get("source")
                edge = (target_kind, str(target), str(dependency.get("relationship")))
                if edge in seen:
                    diagnostics.append(self._diagnostic("dependencies", "MRD_DEPENDENCY_DUPLICATE", f"duplicate dependency {edge}", f"{doc_id}._mrd.dependencies[{index}]", doc_id))
                    continue
                seen.add(edge)
                if target_kind == "source":
                    if self._resolve_repo_file(target) is None:
                        diagnostics.append(self._diagnostic("dependencies", "MRD_DEPENDENCY_UNRESOLVED", f"canonical source dependency does not resolve inside repository: {target}", f"{doc_id}._mrd.dependencies[{index}]", doc_id))
                    continue
                if target not in documents:
                    diagnostics.append(self._diagnostic("dependencies", "MRD_DEPENDENCY_UNRESOLVED", f"MRD dependency does not resolve: {target}", f"{doc_id}._mrd.dependencies[{index}]", doc_id))
                    continue
                graph[doc_id].add(str(target))
                target_layer = documents[str(target)].get("_mrd", {}).get("layer")
                if self._layer_number(source_layer) is not None and self._layer_number(target_layer) is not None and self._layer_number(source_layer) < self._layer_number(target_layer):
                    diagnostics.append(self._diagnostic("dependencies", "MRD_DEPENDENCY_LAYER_VIOLATION", f"{doc_id} at {source_layer} cannot depend on {target} at {target_layer}", f"{doc_id}._mrd.dependencies[{index}]", doc_id))
        cycle = self._find_cycle(graph)
        if cycle:
            diagnostics.append(self._diagnostic("dependencies", "MRD_DEPENDENCY_CYCLE", " -> ".join(cycle), "$._mrd.dependencies", cycle[0]))

    def _validate_provenance(self, documents: dict[str, dict[str, Any]], concerns: dict[str, dict[str, Any]], diagnostics: list[dict[str, Any]]) -> None:
        owner = concerns.get("provenance")
        if owner is None:
            return
        content = owner.get("content", {})
        qualities = {entry.get("quality") for entry in content.get("fact_qualities", [])}
        source_kinds = {entry.get("kind") for entry in content.get("source_kinds", [])}
        for doc_id, document in documents.items():
            envelope = document.get("_mrd", {})
            provenance = envelope.get("provenance", {})
            quality = provenance.get("fact_quality")
            if quality not in qualities:
                diagnostics.append(self._diagnostic("provenance", "MRD_SOURCE_UNRESOLVED", f"unknown fact quality {quality!r}", f"{doc_id}._mrd.provenance.fact_quality", doc_id))
            if envelope.get("record_mode") == "prescriptive" and quality == "inferred":
                diagnostics.append(self._diagnostic("provenance", "MRD_NORMATIVE_INFERENCE_PROHIBITED", "inferred facts cannot be active prescriptive authority", f"{doc_id}._mrd.provenance.fact_quality", doc_id))
            sources = provenance.get("sources", [])
            if provenance.get("source_fingerprint") != "sha256:" + canonical_hash(sources):
                diagnostics.append(self._diagnostic("provenance", "MRD_SOURCE_FINGERPRINT_MISMATCH", "provenance source fingerprint does not match canonical source set", f"{doc_id}._mrd.provenance.source_fingerprint", doc_id))
            source_ids: set[str] = set()
            for index, source in enumerate(sources):
                source_id, kind = source.get("source_id"), source.get("kind")
                if source_id in source_ids or kind not in source_kinds:
                    diagnostics.append(self._diagnostic("provenance", "MRD_SOURCE_UNRESOLVED", f"invalid or duplicate provenance source {source_id!r} ({kind!r})", f"{doc_id}._mrd.provenance.sources[{index}]", doc_id))
                source_ids.add(str(source_id))
                if kind == "repo_path":
                    locator = source.get("locator", "")
                    if self._resolve_repo_file(locator) is None:
                        diagnostics.append(self._diagnostic("provenance", "MRD_SOURCE_UNRESOLVED", f"repo provenance source does not resolve inside repository: {locator}", f"{doc_id}._mrd.provenance.sources[{index}]", doc_id))
                if kind == "external_reference" and not source.get("sha256"):
                    diagnostics.append(self._diagnostic("provenance", "MRD_SOURCE_UNRESOLVED", "external provenance source must carry a SHA-256 fingerprint", f"{doc_id}._mrd.provenance.sources[{index}]", doc_id))

    def _validate_lifecycle(self, documents: dict[str, dict[str, Any]], concerns: dict[str, dict[str, Any]], diagnostics: list[dict[str, Any]]) -> None:
        owner = concerns.get("lifecycle")
        if owner is None:
            return
        states_by_mode = {entry.get("record_mode"): set(entry.get("states", [])) for entry in owner.get("content", {}).get("lifecycles", [])}
        for doc_id, document in documents.items():
            envelope = document.get("_mrd", {})
            mode, status = envelope.get("record_mode"), envelope.get("status")
            if mode not in states_by_mode:
                diagnostics.append(self._diagnostic("lifecycle", "MRD_RECORD_MODE_INVALID", f"unknown record mode {mode!r}", f"{doc_id}._mrd.record_mode", doc_id))
            elif status not in states_by_mode[mode]:
                diagnostics.append(self._diagnostic("lifecycle", "MRD_STATUS_INVALID", f"status {status!r} is invalid for record mode {mode!r}", f"{doc_id}._mrd.status", doc_id))
            if envelope.get("class") == "EVD" and mode != "descriptive":
                diagnostics.append(self._diagnostic("lifecycle", "MRD_EVD_RECORD_MODE_INVALID", "EVD records must be descriptive", f"{doc_id}._mrd.record_mode", doc_id))
            if envelope.get("class") == "META" and mode != "meta":
                diagnostics.append(self._diagnostic("lifecycle", "MRD_META_RECORD_MODE_INVALID", "META records must use meta record mode", f"{doc_id}._mrd.record_mode", doc_id))
            for target in envelope.get("supersedes", []):
                if target not in documents:
                    diagnostics.append(self._diagnostic("lifecycle", "MRD_SUPERSESSION_UNRESOLVED", f"supersedes target does not resolve: {target}", f"{doc_id}._mrd.supersedes", doc_id))
            replacement = envelope.get("superseded_by")
            if replacement is not None and replacement not in documents:
                diagnostics.append(self._diagnostic("lifecycle", "MRD_SUPERSESSION_UNRESOLVED", f"superseded_by target does not resolve: {replacement}", f"{doc_id}._mrd.superseded_by", doc_id))

    def _resolve_repo_file(self, locator: object) -> Path | None:
        if not isinstance(locator, str) or not locator.startswith("repo:"):
            return None
        relative = locator[5:]
        if not relative:
            return None
        candidate = (self.root / relative).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError:
            return None
        return candidate if candidate.is_file() else None

    @staticmethod
    def _layer_number(value: object) -> int | None:
        if isinstance(value, str) and len(value) == 2 and value[0] == "L" and value[1].isdigit():
            return int(value[1])
        return None

    @staticmethod
    def _find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
        visiting: set[str] = set()
        visited: set[str] = set()
        stack: list[str] = []
        def visit(node: str) -> list[str] | None:
            if node in visiting:
                start = stack.index(node)
                return stack[start:] + [node]
            if node in visited:
                return None
            visiting.add(node); stack.append(node)
            for target in sorted(graph.get(node, ())):
                cycle = visit(target)
                if cycle:
                    return cycle
            stack.pop(); visiting.remove(node); visited.add(node)
            return None
        for node in sorted(graph):
            cycle = visit(node)
            if cycle:
                return cycle
        return None

    @staticmethod
    def _diagnostic(check: str, code: str, message: str, location: str, mrd_id: str | None) -> dict[str, Any]:
        return {"check": check, "code": code, "message": message, "location": location, "mrd_id": mrd_id}

    @staticmethod
    def _result(diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
        failed = {item["check"] for item in diagnostics}
        checks = {name: ("fail" if name in failed else "pass") for name in ("classification", "layering", "dependencies", "provenance", "lifecycle", "schema")}
        return {"status": "invalid" if diagnostics else "valid", "checks": checks, "diagnostics": diagnostics}