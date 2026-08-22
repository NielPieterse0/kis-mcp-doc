from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


_REGISTRY = "publication/harvest-sources.json"
_SCHEMA = "contracts/documentation/harvest/v1/registry.schema.json"


def load_harvest_registry(repository_root: Path) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    registry_path = root / _REGISTRY
    schema_path = root / _SCHEMA
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"unable to load harvest source registry: {error}") from error

    errors = sorted(
        Draft202012Validator(schema).iter_errors(registry),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        error = errors[0]
        location = "/".join(str(part) for part in error.absolute_path) or "$"
        raise ValueError(f"harvest source registry invalid at {location}: {error.message}")

    source_ids = [item["id"] for item in registry["sources"]]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("harvest source registry contains duplicate source ids")
    for source in registry["sources"]:
        if source["status"] == "active_reference" and source["pinned_revision"] is None:
            raise ValueError(
                f"active harvest reference must pin a revision: {source['id']}"
            )
    return registry
