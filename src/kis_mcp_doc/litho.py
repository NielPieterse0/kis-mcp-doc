from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .governance import canonical_source_bytes


_SCHEMA = "contracts/documentation/litho/v1/package.schema.json"


def load_litho_evidence(repository_root: Path, package_root: Path) -> dict[str, Any]:
    repository_root = Path(repository_root).resolve()
    package_root = Path(package_root).resolve()
    manifest_path = package_root / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        schema = json.loads((repository_root / _SCHEMA).read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"unable to load Litho evidence package: {error}") from error

    errors = sorted(
        Draft202012Validator(schema).iter_errors(manifest),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        error = errors[0]
        location = "/".join(str(part) for part in error.absolute_path) or "$"
        raise ValueError(f"Litho evidence package invalid at {location}: {error.message}")

    pages: list[dict[str, Any]] = []
    seen: set[str] = set()
    for declaration in sorted(manifest["files"], key=lambda item: item["path"]):
        relative = _portable_relative_path(declaration["path"])
        if relative in seen:
            raise ValueError(f"duplicate Litho evidence path: {relative}")
        seen.add(relative)
        path = (package_root / Path(*relative.split("/"))).resolve()
        try:
            path.relative_to(package_root)
        except ValueError as error:
            raise ValueError(f"Litho evidence path escapes package: {relative}") from error
        if not path.is_file():
            raise ValueError(f"Litho evidence file missing: {relative}")
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != declaration["sha256"] or len(payload) != declaration["bytes"]:
            raise ValueError(f"Litho evidence hash or byte count mismatch: {relative}")
        if path.suffix.casefold() != ".md":
            raise ValueError(f"Litho evidence file must be Markdown: {relative}")
        content = payload.decode("utf-8")
        _reject_machine_local_paths(content, relative)
        pages.append({**declaration, "title": _title(content, relative), "content": content})

    assertions, diagnostics, canonical_sources = _evaluate_assertions(
        repository_root,
        seen,
        manifest.get("assertions", []),
    )
    return {
        "contract": manifest["contract"],
        "provider": manifest["provider"],
        "target": manifest["target"],
        "evidence_class": manifest["evidence_class"],
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "pages": pages,
        "assertions": assertions,
        "diagnostics": diagnostics,
        "canonical_sources": canonical_sources,
    }


def _evaluate_assertions(
    repository_root: Path,
    evidence_paths: set[str],
    assertions: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    normalized: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    canonical_by_path: dict[str, dict[str, Any]] = {}
    seen_ids: set[str] = set()
    for assertion in sorted(assertions, key=lambda item: item["id"]):
        assertion_id = assertion["id"]
        if assertion_id in seen_ids:
            raise ValueError(f"duplicate Litho assertion id: {assertion_id}")
        seen_ids.add(assertion_id)
        source_path = _portable_relative_path(assertion["source_path"])
        if source_path not in evidence_paths:
            raise ValueError(
                f"Litho assertion source is not a declared evidence page: {source_path}"
            )
        canonical_source = assertion["canonical_source"]
        canonical_path, relative = _resolve_repo_json(repository_root, canonical_source)
        try:
            canonical_document = json.loads(canonical_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ValueError(
                f"Litho assertion canonical source is not readable JSON: {canonical_source}"
            ) from error
        canonical_value = _resolve_json_pointer(
            canonical_document,
            assertion["json_pointer"],
        )
        payload = canonical_source_bytes(canonical_path)
        canonical_by_path[relative] = {
            "path": relative,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
        }
        record = dict(assertion)
        record["source_path"] = source_path
        normalized.append(record)
        if assertion["observed_value"] != canonical_value:
            diagnostics.append({
                "code": "EXTERNAL_EVIDENCE_CONTRADICTS_CANONICAL",
                "assertion_id": assertion_id,
                "source_path": source_path,
                "canonical_source": canonical_source,
                "json_pointer": assertion["json_pointer"],
                "observed_value": assertion["observed_value"],
                "canonical_value": canonical_value,
            })
    return normalized, diagnostics, [canonical_by_path[key] for key in sorted(canonical_by_path)]


def _resolve_repo_json(repository_root: Path, locator: str) -> tuple[Path, str]:
    if not locator.startswith("repo:"):
        raise ValueError(f"Litho assertion canonical source must use repo: locator: {locator}")
    relative = _portable_relative_path(locator[5:])
    path = (repository_root / Path(*relative.split("/"))).resolve()
    try:
        path.relative_to(repository_root)
    except ValueError as error:
        raise ValueError(f"Litho assertion canonical source escapes repository: {locator}") from error
    if not path.is_file() or path.suffix.casefold() != ".json":
        raise ValueError(f"Litho assertion canonical JSON source is unavailable: {locator}")
    return path, relative


def _resolve_json_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    current = document
    for token in pointer.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        try:
            if isinstance(current, list):
                current = current[int(token)]
            elif isinstance(current, dict):
                current = current[token]
            else:
                raise KeyError(token)
        except (KeyError, IndexError, ValueError) as error:
            raise ValueError(f"Litho assertion JSON pointer does not resolve: {pointer}") from error
    return current


def _reject_machine_local_paths(content: str, relative: str) -> None:
    patterns = (
        r"(?i)\b[A-Z]:[\\/]",
        r"(?i)(?<![A-Za-z0-9])/(?:home|Users|tmp|var/tmp)/",
        r"\\\\[^\\\s]+\\[^\\\s]+",
    )
    if any(re.search(pattern, content) for pattern in patterns):
        raise ValueError(
            f"Litho evidence contains a machine-local absolute path: {relative}"
        )


def _portable_relative_path(value: str) -> str:
    candidate = value.replace("\\", "/")
    parts = candidate.split("/")
    if (
        not candidate
        or candidate.startswith("/")
        or len(candidate) > 1 and candidate[1] == ":"
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise ValueError(f"Litho evidence path must be portable and relative: {value}")
    return "/".join(parts)


def _title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        if line.startswith("# ") and line[2:].strip():
            return line[2:].strip()
    return Path(fallback).stem
