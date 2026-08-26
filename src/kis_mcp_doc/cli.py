from __future__ import annotations

import argparse
import json
from pathlib import Path

from .governance import GovernanceRepository
from .render import build_governance_spec, verify_governance_spec
from .work_management import WorkManagementRepository, build_work_management_spec, verify_work_management_spec


def _repository(root: Path) -> GovernanceRepository:
    return GovernanceRepository(root, root / "mrd" / "governance")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kis-doc")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("work-validate")
    work_build = sub.add_parser("work-build")
    work_build.add_argument("--output", type=Path)
    work_build.add_argument("--replace", action="store_true")
    work_check = sub.add_parser("work-check-generated")
    work_check.add_argument("--output", type=Path)
    build = sub.add_parser("build")
    build.add_argument("--output", type=Path)
    build.add_argument("--replace", action="store_true")
    build.add_argument("--litho-package", type=Path)
    check = sub.add_parser("check-generated")
    check.add_argument("--output", type=Path)
    check.add_argument("--litho-package", type=Path)
    args = parser.parse_args(argv)

    root = args.root.resolve()
    repo = _repository(root)
    publication = root / "publication" / "governance-spec.json"
    if args.command == "validate":
        result = repo.validate()
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1

    if args.command == "work-validate":
        result = WorkManagementRepository(root).validate()
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "work-build":
        output = args.output or (root / "generated" / "work-management-spec")
        manifest = build_work_management_spec(WorkManagementRepository(root), output, replace=args.replace)
        print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "work-check-generated":
        output = args.output or (root / "generated" / "work-management-spec")
        result = verify_work_management_spec(WorkManagementRepository(root), output)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1

    output = args.output or (root / "generated" / "governance-spec")
    if args.command == "build":
        manifest = build_governance_spec(
            repo,
            publication,
            output,
            replace=args.replace,
            litho_package=args.litho_package,
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    if args.command == "check-generated":
        result = verify_governance_spec(
            repo, publication, output, litho_package=args.litho_package
        )
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
