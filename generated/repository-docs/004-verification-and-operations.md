<!-- GENERATED — DO NOT EDIT -->
# Verification and operations

Use executable evidence to decide whether repository documentation and generated surfaces are current.

## Canonical verification

Run `pwsh -File scripts/verify.ps1` for the repository-wide gate. It runs tests, governance and publication validation, generated-output checks, search/site/release checks, public-repository hygiene, and whitespace verification.

## Development rule

During implementation, run focused affected checks. Before publication, the governed change workflow performs its required scope and verification checks; the pull request owns full exact-head provider verification.

## Runtime safety

Local Windows verification uses `scripts/runtime-preflight.ps1` and the governed Python runtime policy before dependency synchronization or tests.
