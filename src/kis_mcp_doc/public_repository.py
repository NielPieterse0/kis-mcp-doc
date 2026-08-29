from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT_CONFIG = Path("publication/public-repository.json")
CLOSING = re.compile(
    r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+"
    r"(?:#\d+|[\w.-]+/[\w.-]+#\d+|https://github\.com/[^\s]+/issues/\d+)",
    re.IGNORECASE,
)
SENSITIVE_PARTS = {".venv", ".temp", "__pycache__", "quarantine"}
SENSITIVE_NAMES = {".env", "credentials.json", "secrets.json", "id_rsa", "id_ed25519"}


def load_public_repository_config(root: Path) -> dict:
    return json.loads((root / ROOT_CONFIG).read_text(encoding="utf-8"))


def _readme(config: dict) -> str:
    return f"""# {config['project_name']}

{config['description']}

**Repository status:** {config['status']}. Repository authority and execution rules are defined in [`{config['authority_file']}`]({config['authority_file']}).

**License:** {config['license_notice']}

## What this repository provides

- governed Governance and Work Management MRDs and contracts;
- deterministic human-readable specifications, task documentation, reference data, search, and documentation-site output;
- stale/tamper detection and exact generated-output verification;
- GitHub Pages and deterministic release-asset publication paths.

## Documentation

The governed reader-facing documentation site is published at {config['documentation_url']}

The repository keeps canonical facts in MRDs, contracts, schemas, configuration, code, and tests. Human-readable documentation is generated from those sources and is never a write-back authority.

## Repository structure

`prescriptives/` contains canonical machine-readable domain records. `contracts/` contains schemas and contracts. `publication/` contains publication configuration. `src/` contains deterministic generators and validators. `generated/` contains derived publication output. `tests/` and `scripts/` contain verification controls.

## Verify locally

Use PowerShell {config['minimum_powershell_major']} or later and run:

```powershell
{config['verification_command']}
```

The command verifies locked dependencies, tests, governance, generated documentation, publication/search/site/release integrity, public-repository hygiene, and whitespace without permitting generated views to become authority.

## Contributing and security

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the governed change path and [`SECURITY.md`](SECURITY.md) for private vulnerability reporting.
"""


def _contributing(config: dict) -> str:
    return f"""# Contributing

Repository authority, change boundaries, and execution rules are defined in [`{config['authority_file']}`]({config['authority_file']}).

## Change workflow

- Start from the current `main` branch and use an isolated change branch/worktree.
- Keep each change bounded to one approved work item or governed scope.
- Run `{config['verification_command']}` before review.
- Require the exact pull-request head to pass the `verify` status check before merge.
- Do not bypass failed, missing, stale, or mismatched verification evidence.

## Issue completion authority

Do not use GitHub auto-closing keywords such as `Fixes #123`, `Closes #123`, or `Resolves #123` in pull-request bodies or commit messages. Work Management retains completion authority.

## Documentation authority

Do not hand-edit generated Markdown. Change the owning MRD, contract, configuration, code, or generator and regenerate the derived surface.

## Security

Follow [`SECURITY.md`](SECURITY.md). Never commit credentials, tokens, private keys, machine-local runtime state, caches, quarantine payloads, or unreviewed external-source material.
"""


def _security(config: dict) -> str:
    return f"""# Security Policy

## Reporting a vulnerability

{config['security_reporting']}

Include the affected revision/file, credible impact, smallest safe reproduction, known preconditions, and suggested containment when available.

## Repository boundary

Credentials and secrets belong outside the repository. Generated documentation, evidence, and publication artifacts must not contain usable credentials, private keys, tokens, cookies, or machine-local secret state.

Before public release, review repository history and public refs for accidental secret exposure. A clean current tree alone is not sufficient evidence.
"""


def _pull_request_template(config: dict) -> str:
    return f"""## Outcome

Describe the bounded repository outcome.

## Scope

- Work item / governed change:
- Canonical sources changed:
- Generated surfaces changed:

## Verification

- [ ] `{config['verification_command']}` passes on this exact head.
- [ ] `git diff --check` passes.
- [ ] No GitHub issue auto-closing keyword is present in this PR or its commits.

## Security and authority

- [ ] No credentials, private data, machine-local secret state, or unsafe generated material is introduced.
- [ ] Generated documentation remains downstream of its canonical source and was not hand-edited as authority.
"""
def public_repository_outputs(root: Path) -> dict[Path, str]:
    config = load_public_repository_config(root)
    return {
        Path("README.md"): _readme(config),
        Path("CONTRIBUTING.md"): _contributing(config),
        Path("SECURITY.md"): _security(config),
        Path(".github/pull_request_template.md"): _pull_request_template(config),
    }


def build_public_repository_surfaces(root: Path) -> list[str]:
    written: list[str] = []
    for relative, text in public_repository_outputs(root).items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        written.append(relative.as_posix())
    return written


def verify_public_repository_surfaces(root: Path) -> dict:
    findings: list[str] = []
    outputs = public_repository_outputs(root)
    declared = set(load_public_repository_config(root).get("generated_files", []))
    owned = {relative.as_posix() for relative in outputs}
    if declared != owned:
        findings.append("generated_files must exactly match generator-owned public surfaces")
    for relative, expected in outputs.items():
        target = root / relative
        if not target.is_file():
            findings.append(f"missing generated public surface: {relative.as_posix()}")
            continue
        actual = target.read_text(encoding="utf-8")
        if actual != expected:
            findings.append(f"stale generated public surface: {relative.as_posix()}")
    return {"status": "valid" if not findings else "invalid", "findings": findings}


def _tracked_files(root: Path) -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    return [Path(item.decode()) for item in raw.split(b"\0") if item]


def _check_tracked_state(root: Path) -> list[str]:
    findings: list[str] = []
    for relative in _tracked_files(root):
        lowered = {part.lower() for part in relative.parts}
        if lowered & SENSITIVE_PARTS or relative.name.lower() in SENSITIVE_NAMES:
            findings.append(f"tracked sensitive/local-state path: {relative.as_posix()}")
    return findings


def _check_pr_text(root: Path) -> list[str]:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not Path(event_path).is_file():
        return []
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    pull = event.get("pull_request")
    if not pull:
        return []
    findings: list[str] = []
    if CLOSING.search(pull.get("body") or ""):
        findings.append("pull-request body contains a GitHub issue-closing keyword")
    base, head = pull["base"]["sha"], pull["head"]["sha"]
    messages = subprocess.check_output(
        ["git", "log", "--format=%B%x00", f"{base}..{head}"], cwd=root, text=True
    )
    if CLOSING.search(messages):
        findings.append("pull-request commit history contains a GitHub issue-closing keyword")
    return findings
def validate_public_repository(root: Path) -> dict:
    config = load_public_repository_config(root)
    findings = verify_public_repository_surfaces(root)["findings"]
    findings.extend(_check_tracked_state(root))
    findings.extend(_check_pr_text(root))
    if int(config.get("minimum_powershell_major", 0)) < 7:
        findings.append("minimum_powershell_major must be at least 7")
    controls = config.get("repository_controls", {})
    if controls.get("required_check") != "verify":
        findings.append("repository_controls.required_check must be verify")
    return {"status": "valid" if not findings else "invalid", "findings": findings}
