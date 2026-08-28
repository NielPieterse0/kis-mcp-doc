# Contributing

Repository authority, change boundaries, and execution rules are defined in [`AGENTS.md`](AGENTS.md).

## Change workflow

- Start from the current `main` branch and use an isolated change branch/worktree.
- Keep each change bounded to one approved work item or governed scope.
- Run `pwsh -NoProfile -File scripts/verify.ps1` before review.
- Require the exact pull-request head to pass the `verify` status check before merge.
- Do not bypass failed, missing, stale, or mismatched verification evidence.

## Issue completion authority

Do not use GitHub auto-closing keywords such as `Fixes #123`, `Closes #123`, or `Resolves #123` in pull-request bodies or commit messages. Work Management retains completion authority.

## Documentation authority

Do not hand-edit generated Markdown. Change the owning MRD, contract, configuration, code, or generator and regenerate the derived surface.

## Security

Follow [`SECURITY.md`](SECURITY.md). Never commit credentials, tokens, private keys, machine-local runtime state, caches, quarantine payloads, or unreviewed external-source material.
