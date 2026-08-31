<!-- GENERATED — DO NOT EDIT -->
# Represent provenance and lifecycle

Preserve authority direction and distinguish authored prescription from derived implementation views and captured evidence.

## Record modes

- `prescriptive` ? What must be true. Authored, reviewed, and explicitly adopted as governing authority.
- `descriptive` ? What happened or is observed. Captured evidence or records.
- `meta` ? A generated representation, index, or map of other authority.

## Lifecycle by record mode

### Prescriptive

States: `draft`, `active`, `superseded`.

Transitions: `draft` ? `active`, `active` ? `superseded`.

### Descriptive

States: `created`, `retained`.

Transitions: `created` ? `retained`.

### Meta

States: `generated`, `replaced`.

Transitions: `generated` ? `replaced`.

Use the [MRD Specification](../mrd-specification/001-specification.md) for provenance source, fact-quality, and lifecycle constraints.
