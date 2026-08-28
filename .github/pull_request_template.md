## Outcome

Describe the bounded repository outcome.

## Scope

- Work item / governed change:
- Canonical sources changed:
- Generated surfaces changed:

## Verification

- [ ] `pwsh -NoProfile -File scripts/verify.ps1` passes on this exact head.
- [ ] `git diff --check` passes.
- [ ] No GitHub issue auto-closing keyword is present in this PR or its commits.

## Security and authority

- [ ] No credentials, private data, machine-local secret state, or unsafe generated material is introduced.
- [ ] Generated documentation remains downstream of its canonical source and was not hand-edited as authority.
