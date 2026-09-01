<!-- GENERATED — DO NOT EDIT -->
# Runtime, dependencies, and public repository

Understand the executable environment, dependency baseline, and public-repository controls that affect operation and contribution.

## Runtime and dependencies

- Governed Windows Python minimum: `3.11`; package requirement: `>=3.11`.
- Preferred Windows launcher: `py.exe -3.11` with Authenticode trust required.
- `uv` managed Python and Python downloads are disabled for canonical verification; offline canonical verification is enabled.
- Runtime dependencies: `jsonschema>=4.23`.
- Development dependencies: `pytest>=8.3`.
- Defender exclusions, Smart App Control bypasses, and execution-policy weakening are prohibited by the runtime policy.

## Public repository posture

- Status: public documentation engineering and proving ground.
- Verification command: `pwsh -NoProfile -File scripts/verify.ps1`.
- License posture: No project-wide open-source license has been granted. Public visibility does not grant reuse, modification, or redistribution rights.
- Security reporting: Use GitHub private vulnerability reporting when available. Do not disclose vulnerabilities, credentials, tokens, private data, or exploit details in public issues or pull requests.

## Repository controls

| Control | Value |
|---|---|
| `default_branch` | `main` |
| `main_protected` | `true` |
| `required_check` | `verify` |
| `merge_strategy` | `merge_commit_only` |
| `delete_branch_on_merge` | `false` |
| `actions_default_permission` | `read` |
| `pages_source` | `github_actions` |

