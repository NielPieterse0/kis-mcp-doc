from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

from .canonical import canonical_hash

_ARCHITECTURE_PATH = "prescriptives/documentation/03-publication-architecture.mrd.json"
_REGISTRY_PATH = "prescriptives/documentation/04-publication-family-registry.mrd.json"
_REGISTRY_SCHEMA = "contracts/publication/family/v1/registry.schema.json"
_CORE_MRD_SCHEMA = "contracts/mrd/v1/mrd.schema.json"
_DOCUMENTATION_POLICY = "prescriptives/documentation/01-reference-standard.mrd.json"


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def _diag(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _safe_relative_path(relative: str) -> Path:
    if not relative or "\\" in relative:
        raise ValueError(f"publication bundle path must be a normalized relative path: {relative!r}")
    path = Path(*relative.split("/"))
    if (
        path.is_absolute()
        or ".." in path.parts
        or "." in path.parts
        or path.as_posix() != relative
    ):
        raise ValueError(f"publication bundle path must be a normalized relative path: {relative!r}")
    return path


def _registered_path(relative: str, prefix: str) -> Path:
    path = _safe_relative_path(relative)
    if len(path.parts) < 2 or path.parts[0] != prefix:
        raise ValueError(f"registered path must stay under {prefix}/: {relative}")
    return path


def file_declarations(files: dict[str, bytes]) -> list[dict[str, Any]]:
    declarations: list[dict[str, Any]] = []
    for relative, payload in sorted(files.items()):
        _safe_relative_path(relative)
        if not isinstance(payload, bytes):
            raise TypeError(f"publication bundle payload must be bytes: {relative}")
        declarations.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
            }
        )
    return declarations


def bundle_manifest_fields(files: dict[str, bytes]) -> dict[str, Any]:
    declarations = file_declarations(files)
    return {"bundle_sha256": canonical_hash(declarations)}


def write_bundle(
    output: Path,
    files: dict[str, bytes],
    manifest: dict[str, Any],
    *,
    replace: bool = False,
) -> None:
    output = Path(output)
    if "manifest.json" in files:
        raise ValueError("manifest.json is owned by the publication bundle writer")
    if output.exists() and not replace:
        raise FileExistsError(f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.", suffix=".tmp", dir=output.parent))
    backup: Path | None = None
    try:
        for relative, payload in sorted(files.items()):
            target = staging / _safe_relative_path(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
        (staging / "manifest.json").write_bytes(_json_bytes(manifest))

        if output.exists():
            backup = output.parent / f".{output.name}.{uuid.uuid4().hex}.bak"
            os.replace(output, backup)
        try:
            os.replace(staging, output)
        except Exception:
            if backup is not None and backup.exists() and not output.exists():
                os.replace(backup, output)
                backup = None
            raise
        if backup is not None and backup.exists():
            shutil.rmtree(backup, ignore_errors=True)
            backup = None
    except Exception:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        if backup is not None and backup.exists() and not output.exists():
            os.replace(backup, output)
        raise


def _bundle_code(code_prefix: str | None, suffix: str) -> str:
    return f"{code_prefix}_{suffix}" if code_prefix else suffix


def bundle_diagnostics(
    output: Path,
    expected_files: dict[str, bytes],
    expected_manifest: dict[str, Any],
    *,
    code_prefix: str | None = "PUBLICATION",
    normalizer: Callable[[str, bytes], bytes] | None = None,
) -> list[dict[str, str]]:
    output = Path(output)
    diagnostics: list[dict[str, str]] = []
    expected_payloads = dict(expected_files)
    expected_payloads["manifest.json"] = _json_bytes(expected_manifest)
    expected_paths = set(expected_payloads)
    actual_paths = (
        {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
        if output.is_dir()
        else set()
    )
    if actual_paths != expected_paths:
        diagnostics.append(
            _diag(
                _bundle_code(code_prefix, "GENERATED_FILE_SET_MISMATCH"),
                "generated publication file inventory differs from deterministic expected output",
            )
        )
    for relative, expected in sorted(expected_payloads.items()):
        path = output / _safe_relative_path(relative)
        if not path.is_file():
            diagnostics.append(
                _diag(_bundle_code(code_prefix, "GENERATED_FILE_MISSING"), f"generated file missing: {relative}")
            )
            continue
        actual = path.read_bytes()
        if normalizer is not None:
            expected = normalizer(relative, expected)
            actual = normalizer(relative, actual)
        if actual != expected:
            diagnostics.append(
                _diag(
                    _bundle_code(code_prefix, "GENERATED_FILE_CONTENT_MISMATCH"),
                    f"generated file differs from deterministic expected output: {relative}",
                )
            )
    return diagnostics


def exact_bundle_diagnostics(
    output: Path,
    expected_files: dict[str, bytes],
    expected_manifest: dict[str, Any],
    *,
    code_prefix: str | None = "PUBLICATION",
) -> list[dict[str, str]]:
    return bundle_diagnostics(
        output,
        expected_files,
        expected_manifest,
        code_prefix=code_prefix,
    )


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"unable to load {label}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _schema_errors(root: Path, schema_relative: str, instance: object) -> list[str]:
    schema = _load_json(root / schema_relative, f"schema {schema_relative}")
    Draft202012Validator.check_schema(schema)
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '$'}: {error.message}"
        for error in sorted(
            Draft202012Validator(schema).iter_errors(instance),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
    ]


def _resolve_entrypoint(value: str) -> Callable[..., Any]:
    module_name, separator, attribute = value.partition(":")
    if not separator or not module_name or not attribute:
        raise ValueError(f"invalid adapter entrypoint: {value}")
    module = importlib.import_module(module_name)
    target = getattr(module, attribute)
    if not callable(target):
        raise TypeError(f"adapter entrypoint is not callable: {value}")
    return target


def _validate_adapter_signature(target: Callable[..., Any], phase: str) -> None:
    signature = inspect.signature(target)
    if phase == "build":
        signature.bind(Path("."), {}, replace=False)
    else:
        signature.bind(Path("."), {})


def _phase_result(family_id: str, phase: str, result: object) -> dict[str, Any]:
    if (
        not isinstance(result, dict)
        or result.get("status") not in {"valid", "invalid"}
        or not isinstance(result.get("diagnostics"), list)
    ):
        return {
            "status": "invalid",
            "diagnostics": [_diag(
                "PUBLICATION_FAMILY_ADAPTER_RESULT_INVALID",
                f"{family_id}.{phase} must return status and diagnostics",
            )],
        }
    return result


class PublicationFamilyRegistry:
    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.path = self.root / _REGISTRY_PATH

    def load(self) -> dict[str, Any]:
        return _load_json(self.path, "publication family registry")

    def validate(self) -> dict[str, Any]:
        diagnostics: list[dict[str, str]] = []
        try:
            registry = self.load()
        except ValueError as error:
            return {"status": "invalid", "diagnostics": [_diag("PUBLICATION_FAMILY_REGISTRY_INVALID", str(error))]}

        try:
            architecture = _load_json(self.root / _ARCHITECTURE_PATH, "publication architecture MRD")
            for error in _schema_errors(self.root, _CORE_MRD_SCHEMA, architecture):
                diagnostics.append(_diag("PUBLICATION_ARCHITECTURE_MRD_SCHEMA_INVALID", error))
            for error in _schema_errors(self.root, _CORE_MRD_SCHEMA, registry):
                diagnostics.append(_diag("PUBLICATION_FAMILY_MRD_SCHEMA_INVALID", error))
            for error in _schema_errors(self.root, _REGISTRY_SCHEMA, registry):
                diagnostics.append(_diag("PUBLICATION_FAMILY_REGISTRY_SCHEMA_INVALID", error))
        except (ValueError, OSError, TypeError) as error:
            diagnostics.append(_diag("PUBLICATION_FAMILY_REGISTRY_SCHEMA_INVALID", str(error)))
            architecture = {}

        if architecture.get("_mrd", {}).get("id") != "KIS-DOC-CON-POL-002":
            diagnostics.append(_diag("PUBLICATION_ARCHITECTURE_ID_INVALID", "publication architecture MRD must be KIS-DOC-CON-POL-002"))
        if registry.get("_mrd", {}).get("id") != "KIS-DOC-SEM-REG-002":
            diagnostics.append(_diag("PUBLICATION_FAMILY_REGISTRY_ID_INVALID", "publication family registry MRD must be KIS-DOC-SEM-REG-002"))
        architecture_protocol = architecture.get("content", {}).get("adapter_protocol", {}).get("version")
        registry_protocol = registry.get("content", {}).get("adapter_protocol_version")
        if architecture_protocol != 1 or registry_protocol != architecture_protocol:
            diagnostics.append(_diag(
                "PUBLICATION_ADAPTER_PROTOCOL_VERSION_INVALID",
                "publication adapter protocol version must resolve to version 1 in architecture and registry",
            ))

        architecture_provenance = architecture.get("_mrd", {}).get("provenance", {})
        if architecture_provenance.get("source_fingerprint") != "sha256:" + canonical_hash(architecture_provenance.get("sources", [])):
            diagnostics.append(
                _diag("PUBLICATION_ARCHITECTURE_PROVENANCE_FINGERPRINT_MISMATCH", "publication architecture provenance fingerprint differs from its source set")
            )

        provenance = registry.get("_mrd", {}).get("provenance", {})
        if provenance.get("source_fingerprint") != "sha256:" + canonical_hash(provenance.get("sources", [])):
            diagnostics.append(
                _diag("PUBLICATION_FAMILY_PROVENANCE_FINGERPRINT_MISMATCH", "publication family registry provenance fingerprint differs from its source set")
            )

        try:
            policy = _load_json(self.root / _DOCUMENTATION_POLICY, "documentation reference policy")
            governed_output_classes = {
                item.get("class") for item in policy.get("content", {}).get("output_classes", [])
            }
        except ValueError as error:
            diagnostics.append(_diag("PUBLICATION_OUTPUT_CLASS_AUTHORITY_INVALID", str(error)))
            governed_output_classes = set()

        known_mrd_ids: set[str] = set()
        for path in self.root.glob("prescriptives/**/*.mrd.json"):
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            doc_id = doc.get("_mrd", {}).get("id")
            if isinstance(doc_id, str):
                known_mrd_ids.add(doc_id)

        seen_ids: set[str] = set()
        seen_outputs: set[str] = set()
        families = registry.get("content", {}).get("families", [])
        if not isinstance(families, list):
            families = []
        for family in families:
            if not isinstance(family, dict):
                continue
            family_id = family.get("id")
            output = family.get("output")
            if isinstance(family_id, str):
                if family_id in seen_ids:
                    diagnostics.append(_diag("PUBLICATION_FAMILY_ID_DUPLICATE", f"duplicate publication family id: {family_id}"))
                seen_ids.add(family_id)
            if isinstance(output, str):
                if output in seen_outputs:
                    diagnostics.append(_diag("PUBLICATION_FAMILY_OUTPUT_DUPLICATE", f"duplicate publication output: {output}"))
                seen_outputs.add(output)
                try:
                    _registered_path(output, "generated")
                except ValueError as error:
                    diagnostics.append(_diag("PUBLICATION_FAMILY_OUTPUT_INVALID", str(error)))
            semantic_owner = family.get("semantic_owner")
            if semantic_owner not in known_mrd_ids:
                diagnostics.append(_diag("PUBLICATION_FAMILY_SEMANTIC_OWNER_UNRESOLVED", f"semantic owner does not resolve: {semantic_owner}"))
            mrd_root = family.get("mrd_root")
            try:
                mrd_path = _registered_path(mrd_root, "prescriptives") if isinstance(mrd_root, str) else None
            except ValueError as error:
                diagnostics.append(_diag("PUBLICATION_FAMILY_MRD_ROOT_INVALID", str(error)))
                mrd_path = None
            if mrd_path is None or not (self.root / mrd_path).is_dir():
                diagnostics.append(_diag("PUBLICATION_FAMILY_MRD_ROOT_UNRESOLVED", f"MRD root does not resolve: {mrd_root}"))
            publication_config = family.get("publication_config")
            try:
                config_path = _registered_path(publication_config, "publication") if isinstance(publication_config, str) else None
            except ValueError as error:
                diagnostics.append(_diag("PUBLICATION_FAMILY_CONFIG_INVALID", str(error)))
                config_path = None
            if config_path is None or not (self.root / config_path).is_file():
                diagnostics.append(_diag("PUBLICATION_FAMILY_CONFIG_UNRESOLVED", f"publication config does not resolve: {publication_config}"))
            output_classes = family.get("output_classes", [])
            if isinstance(output_classes, list):
                for output_class in output_classes:
                    if output_class not in governed_output_classes:
                        diagnostics.append(_diag("PUBLICATION_OUTPUT_CLASS_UNGOVERNED", f"publication output class is not governed: {output_class}"))
            adapters = family.get("adapter", {})
            if isinstance(adapters, dict):
                for phase in ("validate", "build", "verify"):
                    entrypoint = adapters.get(phase)
                    if not isinstance(entrypoint, str):
                        continue
                    try:
                        target = _resolve_entrypoint(entrypoint)
                    except (ImportError, AttributeError, TypeError, ValueError) as error:
                        diagnostics.append(_diag("PUBLICATION_FAMILY_ADAPTER_UNRESOLVED", f"{family_id}.{phase}: {error}"))
                        continue
                    try:
                        _validate_adapter_signature(target, phase)
                    except (TypeError, ValueError) as error:
                        diagnostics.append(_diag(
                            "PUBLICATION_FAMILY_ADAPTER_SIGNATURE_INVALID",
                            f"{family_id}.{phase}: {error}",
                        ))
        return {"status": "invalid" if diagnostics else "valid", "diagnostics": diagnostics}

    def family(self, family_id: str) -> dict[str, Any]:
        for family in self.load().get("content", {}).get("families", []):
            if family.get("id") == family_id:
                return family
        raise KeyError(family_id)


def _run_registered_phase(
    root: Path,
    phase: str,
    *,
    family_ids: list[str] | None = None,
) -> dict[str, Any]:
    registry = PublicationFamilyRegistry(root)
    registry_result = registry.validate()
    if registry_result["status"] != "valid":
        return {"status": "invalid", "registry": registry_result, "families": {}}
    registered_families = registry.load()["content"]["families"]
    selected = set(family_ids) if family_ids is not None else None
    if selected is not None:
        registered_ids = {family["id"] for family in registered_families}
        unknown = sorted(selected - registered_ids)
        if unknown:
            return {
                "status": "invalid",
                "registry": registry_result,
                "families": {},
                "diagnostics": [_diag("PUBLICATION_FAMILY_UNKNOWN", f"unknown publication family: {family_id}") for family_id in unknown],
            }
    results: dict[str, Any] = {}
    for family in registered_families:
        if selected is not None and family["id"] not in selected:
            continue
        adapter = _resolve_entrypoint(family["adapter"][phase])
        try:
            phase_result = adapter(Path(root).resolve(), family)
            results[family["id"]] = _phase_result(family["id"], phase, phase_result)
        except Exception as error:
            results[family["id"]] = {
                "status": "invalid",
                "diagnostics": [_diag("PUBLICATION_FAMILY_ADAPTER_FAILED", f"{family['id']}.{phase}: {error}")],
            }
    valid = all(result.get("status") == "valid" for result in results.values())
    return {"status": "valid" if valid else "invalid", "registry": registry_result, "families": results}


def validate_registered_publications(root: Path, *, family_ids: list[str] | None = None) -> dict[str, Any]:
    return _run_registered_phase(root, "validate", family_ids=family_ids)


def verify_registered_publications(root: Path, *, family_ids: list[str] | None = None) -> dict[str, Any]:
    return _run_registered_phase(root, "verify", family_ids=family_ids)


def build_registered_publication(
    root: Path,
    family_id: str,
    *,
    replace: bool = False,
) -> dict[str, Any]:
    registry = PublicationFamilyRegistry(root)
    registry_result = registry.validate()
    if registry_result["status"] != "valid":
        return {
            "status": "invalid",
            "registry": registry_result,
            "family": family_id,
            "diagnostics": [_diag(
                "PUBLICATION_FAMILY_REGISTRY_INVALID",
                "publication family registry is invalid",
            )],
        }
    try:
        family = registry.family(family_id)
    except KeyError:
        return {
            "status": "invalid",
            "registry": registry_result,
            "family": family_id,
            "diagnostics": [_diag(
                "PUBLICATION_FAMILY_UNKNOWN",
                f"unknown publication family: {family_id}",
            )],
        }
    adapter = _resolve_entrypoint(family["adapter"]["build"])
    try:
        manifest = adapter(Path(root).resolve(), family, replace=replace)
    except Exception as error:
        return {
            "status": "invalid",
            "registry": registry_result,
            "family": family_id,
            "diagnostics": [_diag(
                "PUBLICATION_FAMILY_ADAPTER_FAILED",
                f"{family_id}.build: {error}",
            )],
        }
    if not isinstance(manifest, dict):
        return {
            "status": "invalid",
            "registry": registry_result,
            "family": family_id,
            "diagnostics": [_diag(
                "PUBLICATION_FAMILY_ADAPTER_RESULT_INVALID",
                f"{family_id}.build must return a manifest object",
            )],
        }
    return {
        "status": "valid",
        "registry": registry_result,
        "family": family_id,
        "diagnostics": [],
        "manifest": manifest,
    }
