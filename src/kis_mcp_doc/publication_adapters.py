from __future__ import annotations

from pathlib import Path
from typing import Any

from .documentation_reference import (
    DocumentationReferenceRepository,
    build_documentation_reference_standard,
    validate_documentation_reference_publication,
    verify_documentation_reference_standard,
)
from .governance import GovernanceRepository
from .render import build_governance_spec, validate_governance_publication, verify_governance_spec
from .work_management import (
    WorkManagementRepository,
    build_work_management_spec,
    validate_work_management_publication,
    verify_work_management_spec,
)


def _family_output(root: Path, family: dict[str, Any], output: Path | None) -> Path:
    return Path(output) if output is not None else root / family["output"]


def _combined_validation(
    semantic: dict[str, Any],
    publication: dict[str, Any],
    *additional: dict[str, Any],
) -> dict[str, Any]:
    results = (semantic, publication, *additional)
    diagnostics = [item for result in results for item in result.get("diagnostics", [])]
    invalid = any(result.get("status") != "valid" for result in results)
    return {
        "status": "invalid" if invalid else "valid",
        "diagnostics": diagnostics,
        "semantic": semantic,
        "publication": publication,
    }


def _validate_output_classes(family: dict[str, Any], required: set[str]) -> dict[str, Any]:
    actual = set(family.get("output_classes", []))
    if actual != required:
        return {
            "status": "invalid",
            "diagnostics": [{
                "code": "PUBLICATION_FAMILY_OUTPUT_CLASS_MISMATCH",
                "message": f"registered output classes must equal {sorted(required)}",
            }],
        }
    return {"status": "valid", "diagnostics": []}


def validate_governance(root: Path, family: dict[str, Any]) -> dict[str, Any]:
    repository = GovernanceRepository(root, root / family["mrd_root"])
    return _combined_validation(
        repository.validate(),
        validate_governance_publication(repository, root / family["publication_config"]),
        _validate_output_classes(family, {"human_readable_specification", "generated_reference"}),
    )


def build_governance(root: Path, family: dict[str, Any], *, output: Path | None = None, replace: bool = False) -> dict[str, Any]:
    repository = GovernanceRepository(root, root / family["mrd_root"])
    return build_governance_spec(
        repository,
        root / family["publication_config"],
        _family_output(root, family, output),
        replace=replace,
    )


def verify_governance(root: Path, family: dict[str, Any]) -> dict[str, Any]:
    repository = GovernanceRepository(root, root / family["mrd_root"])
    return verify_governance_spec(repository, root / family["publication_config"], root / family["output"])


def validate_work_management(root: Path, family: dict[str, Any]) -> dict[str, Any]:
    repository = WorkManagementRepository(root, root / family["mrd_root"])
    return _combined_validation(
        repository.validate(),
        validate_work_management_publication(repository),
        _validate_output_classes(family, {"human_readable_specification", "generated_reference"}),
    )


def build_work_management(root: Path, family: dict[str, Any], *, output: Path | None = None, replace: bool = False) -> dict[str, Any]:
    repository = WorkManagementRepository(root, root / family["mrd_root"])
    return build_work_management_spec(repository, _family_output(root, family, output), replace=replace)


def verify_work_management(root: Path, family: dict[str, Any]) -> dict[str, Any]:
    repository = WorkManagementRepository(root, root / family["mrd_root"])
    return verify_work_management_spec(repository, root / family["output"])


def validate_documentation_reference(root: Path, family: dict[str, Any]) -> dict[str, Any]:
    repository = DocumentationReferenceRepository(root)
    return _combined_validation(
        repository.validate(),
        validate_documentation_reference_publication(repository),
        _validate_output_classes(family, {"human_readable_specification", "generated_reference"}),
    )


def build_documentation_reference(root: Path, family: dict[str, Any], *, output: Path | None = None, replace: bool = False) -> dict[str, Any]:
    return build_documentation_reference_standard(
        DocumentationReferenceRepository(root),
        _family_output(root, family, output),
        replace=replace,
    )


def verify_documentation_reference(root: Path, family: dict[str, Any]) -> dict[str, Any]:
    return verify_documentation_reference_standard(DocumentationReferenceRepository(root), root / family["output"])
