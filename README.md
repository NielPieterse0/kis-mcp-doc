# KIS MCP Documentation

Governed, deterministic documentation generation for KIS Governance and Work Management.

**Repository status:** public documentation engineering and proving ground. Repository authority and execution rules are defined in [`AGENTS.md`](AGENTS.md).

**License:** No project-wide open-source license has been granted. Public visibility does not grant reuse, modification, or redistribution rights.

## What this repository provides

- governed Governance and Work Management MRDs and contracts;
- deterministic human-readable specifications, task documentation, reference data, search, and documentation-site output;
- stale/tamper detection and exact generated-output verification;
- GitHub Pages and deterministic release-asset publication paths.

## Documentation

The governed reader-facing documentation site is published at https://nielpieterse0.github.io/kis-mcp-doc/

The repository keeps canonical facts in MRDs, contracts, schemas, configuration, code, and tests. Human-readable documentation is generated from those sources and is never a write-back authority.

## Repository structure

`prescriptives/` contains canonical machine-readable domain records. `contracts/` contains schemas and contracts. `publication/` contains publication configuration. `src/` contains deterministic generators and validators. `generated/` contains derived publication output. `tests/` and `scripts/` contain verification controls.

## Verify locally

Use PowerShell 7 or later and run:

```powershell
pwsh -NoProfile -File scripts/verify.ps1
```

The command verifies locked dependencies, tests, governance, generated documentation, publication/search/site/release integrity, public-repository hygiene, and whitespace without permitting generated views to become authority.

## Contributing and security

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the governed change path and [`SECURITY.md`](SECURITY.md) for private vulnerability reporting.
