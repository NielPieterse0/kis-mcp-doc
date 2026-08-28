from __future__ import annotations

import argparse
import json
from pathlib import Path

from .documentation_reference import (
    DocumentationReferenceRepository,
    build_documentation_reference_standard,
    verify_documentation_reference_standard,
)
from .governance import GovernanceRepository
from .documentation_site import build_documentation_site, validate_documentation_site, verify_documentation_site
from .documentation_search import build_documentation_search, search_documentation, validate_documentation_search, verify_documentation_search
from .documentation_release import build_documentation_release, validate_documentation_release, verify_documentation_release
from .publication_kernel import (
    build_registered_publication,
    validate_registered_publications,
    verify_registered_publications,
)
from .public_repository import (
    build_public_repository_surfaces,
    validate_public_repository,
    verify_public_repository_surfaces,
)
from .render import build_governance_spec, verify_governance_spec
from .work_management import (
    WorkManagementRepository,
    build_work_management_spec,
    verify_work_management_spec,
)


def _repository(root: Path) -> GovernanceRepository:
    return GovernanceRepository(root, root / "mrd" / "governance")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kis-doc")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("site-validate")
    sub.add_parser("search-validate")
    sub.add_parser("release-validate")
    sub.add_parser("public-validate")
    sub.add_parser("public-build")
    sub.add_parser("public-check-generated")
    release_build = sub.add_parser("release-build")
    release_build.add_argument("--output", type=Path)
    release_build.add_argument("--replace", action="store_true")
    release_check = sub.add_parser("release-check-generated")
    release_check.add_argument("--output", type=Path)
    search_build = sub.add_parser("search-build")
    search_build.add_argument("--output", type=Path)
    search_build.add_argument("--replace", action="store_true")
    search_check = sub.add_parser("search-check-generated")
    search_check.add_argument("--output", type=Path)
    search_query = sub.add_parser("search")
    search_query.add_argument("query")
    search_query.add_argument("--limit", type=int)
    site_build = sub.add_parser("site-build")
    site_build.add_argument("--output", type=Path)
    site_build.add_argument("--replace", action="store_true")
    site_check = sub.add_parser("site-check-generated")
    site_check.add_argument("--output", type=Path)
    publications_validate = sub.add_parser("publications-validate")
    publications_validate.add_argument("--family", action="append")
    publications_build = sub.add_parser("publications-build")
    publications_build.add_argument("--family", required=True)
    publications_build.add_argument("--replace", action="store_true")
    publications_check = sub.add_parser("publications-check-generated")
    publications_check.add_argument("--family", action="append")
    sub.add_parser("references-validate")
    references_build = sub.add_parser("references-build")
    references_build.add_argument("--output", type=Path)
    references_build.add_argument("--replace", action="store_true")
    references_check = sub.add_parser("references-check-generated")
    references_check.add_argument("--output", type=Path)
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
    if args.command == "public-build":
        print(json.dumps({"files": build_public_repository_surfaces(root)}, indent=2, sort_keys=True))
        return 0
    if args.command == "public-check-generated":
        result = verify_public_repository_surfaces(root)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "public-validate":
        result = validate_public_repository(root)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "release-validate":
        result = validate_documentation_release(root)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "release-build":
        manifest = build_documentation_release(root, args.output, replace=args.replace)
        print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "release-check-generated":
        result = verify_documentation_release(root, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "search-validate":
        result = validate_documentation_search(root)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "search-build":
        manifest = build_documentation_search(root, args.output, replace=args.replace)
        print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "search-check-generated":
        result = verify_documentation_search(root, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "search":
        print(json.dumps(search_documentation(root, args.query, limit=args.limit), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "site-validate":
        result = validate_documentation_site(root)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "site-build":
        manifest = build_documentation_site(root, args.output, replace=args.replace)
        print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "site-check-generated":
        result = verify_documentation_site(root, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "publications-validate":
        result = validate_registered_publications(root, family_ids=args.family)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "publications-build":
        result = build_registered_publication(
            root,
            args.family,
            replace=args.replace,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "publications-check-generated":
        result = verify_registered_publications(root, family_ids=args.family)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "validate":
        result = repo.validate()
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "references-validate":
        result = DocumentationReferenceRepository(root).validate()
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "references-build":
        output = args.output or (root / "generated" / "documentation-reference-standard")
        manifest = build_documentation_reference_standard(
            DocumentationReferenceRepository(root), output, replace=args.replace
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "references-check-generated":
        output = args.output or (root / "generated" / "documentation-reference-standard")
        result = verify_documentation_reference_standard(
            DocumentationReferenceRepository(root), output
        )
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1

    if args.command == "work-validate":
        result = WorkManagementRepository(root).validate()
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "valid" else 1
    if args.command == "work-build":
        output = args.output or (root / "generated" / "work-management-spec")
        manifest = build_work_management_spec(
            WorkManagementRepository(root), output, replace=args.replace
        )
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
