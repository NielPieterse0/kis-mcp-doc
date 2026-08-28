# Security Policy

## Reporting a vulnerability

Use GitHub private vulnerability reporting when available. Do not disclose vulnerabilities, credentials, tokens, private data, or exploit details in public issues or pull requests.

Include the affected revision/file, credible impact, smallest safe reproduction, known preconditions, and suggested containment when available.

## Repository boundary

Credentials and secrets belong outside the repository. Generated documentation, evidence, and publication artifacts must not contain usable credentials, private keys, tokens, cookies, or machine-local secret state.

Before public release, review repository history and public refs for accidental secret exposure. A clean current tree alone is not sufficient evidence.
