<!-- GENERATED — DO NOT EDIT -->
# Understand MRD lifecycle

Define minimal lifecycle and mutability rules for each record mode.

The lifecycle depends on the MRD record mode.

## Prescriptive

States: `draft`, `active`, `superseded`.

Allowed transitions: `draft` → `active`, `active` → `superseded`.

## Descriptive

States: `created`, `retained`.

Allowed transitions: `created` → `retained`.

## Meta

States: `generated`, `replaced`.

Allowed transitions: `generated` → `replaced`.

See the [Governance Specification](../governance-spec/001-specification.md) for lifecycle requirements and lineage rules.
