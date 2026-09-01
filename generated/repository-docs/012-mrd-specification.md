<!-- GENERATED — DO NOT EDIT -->
# MRD Specification

The MRD Specification is a distinct prescriptive domain: it defines conforming MRDs, not repository-wide governance.

The catalog contains **47** MRD types across **12** functional classes. Repositories select the minimum sufficient set; they do not instantiate the catalog by default.

## Specification sections

| Concern | Purpose | Rules |
|---|---|---:|
| `classification` | Define the stable functional vocabulary used to classify KIS MRDs without coupling classification to repository layout. | 5 |
| `applicability` | Select the minimum sufficient governed MRD set for the actual repository need rather than instantiating the full catalog by default. | 6 |
| `ownership` | Ensure every governed fact has one canonical owner and every non-owning artifact preserves authority through explicit typed relationships instead of restating truth. | 6 |
| `layering` | Define authority ordering for MRD dependencies. | 3 |
| `dependencies` | Make all authority dependencies explicit, stable, resolvable, and acyclic. | 6 |
| `provenance` | Preserve authority direction and distinguish authored prescription from derived implementation views and captured evidence. | 8 |
| `lifecycle` | Define minimal lifecycle and mutability rules for each record mode. | 6 |
| `validation` | Define MRD structural and semantic conformance checks, stable result semantics, and blocking failure codes. | 5 |

## Core contracts

- Selection: not_applicable by default; select only the minimum sufficient governed artefacts.
- Ownership: exactly 1 current canonical owner per governed fact; non-owners reference rather than redefine.
- Dependencies must resolve, obey authority-layer direction, contain no duplicate edges, and remain acyclic.
- Provenance distinguishes prescriptive, descriptive, and meta records and preserves direct, derived, and inferred fact quality.
- Generated human documentation and META projections remain downstream and non-authoritative.

## Validation modes

- `schema`: JSON Schema rejects structurally invalid authority before semantic checks.
- `validator`: Deterministic semantic validation emits stable machine-readable reason codes.
- `workflow`: KIS/kis-op governed workflow prevents prohibited state transitions or unadmitted mutation.
- `generator`: Deterministic generation and stale-output verification enforce one-way source-to-view behavior.
- `review`: Human or agent review is required where semantic adequacy cannot be proven deterministically.

