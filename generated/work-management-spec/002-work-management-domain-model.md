<!-- GENERATED — DO NOT EDIT -->
# Work Management domain model

<div id="enable-section-numbers" />

[Previous: Specification](001-specification.md) | [Next: Work lifecycle](003-work-lifecycle.md) | [Index](000-index.md)

<span id="mrd-urn-uuid-a0e914e6-64b0-561f-ad39-393287ce71c5"></span>

Work Management describes each work record through a single field model with explicit authority direction. The important distinction is not where a field is displayed, but which system may change it and whether the value is commanded, observed, or handed off to another authority.

## Authority directions

**Command** fields are changed through Work Management operations. **Evidence** fields are observed or projected from their canonical owner. **Handoff** fields begin as Work Management planning data and later become repository-change evidence when change governance takes authority.

The current model contains 14 command fields, 13 evidence fields, and 2 handoff fields.

A generated specification can explain or index those fields, but it cannot turn an evidence field into command data or become a second owner of any value.

## Authority rules

- Every managed field has one authority and one direction.
- Project-native evidence is observed, not redefined by generated documentation.

## Exact field and vocabulary reference

The complete managed-field catalog and every controlled-vocabulary value are exact lookup data. See the [Work field and vocabulary reference](020-work-field-and-vocabulary-reference.md).

## Source and authority

This page projects `urn:uuid:a0e914e6-64b0-561f-ad39-393287ce71c5` version `1.0.0`. The MRD remains authoritative; this generated page has no write-back authority.
