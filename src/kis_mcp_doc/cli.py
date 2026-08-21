from __future__ import annotations

import argparse
import json
from pathlib import Path

from .governance import GovernanceRepository
from .render import build_governance_spec, verify_governance_spec


def _repository(root: Path) -> GovernanceRepository:
    return GovernanceRepository(root, root / "mrd" / "governance")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kis-doc")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    build = sub.add_parser("build")
    build.add_argument("--output", type=Path)
    build.add_argument("--replace", action="store_true")
    check = sub.add_parser("check-generated")
    check.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    root = args.root.resolve()
    repo = _repository(root)
    publication = root / "publication" / "governance-spec.json"
    if args.command == "validate":
        result = repo.validate()
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1

    output = args.output or (root / "generated" / "governance-spec")
    if args.command == "build":
        manifest = build_governance_spec(
            repo,
            publication,
            output,
            replace=args.replace,
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    if args.command == "check-generated":
        result = verify_governance_spec(repo, publication, output)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
