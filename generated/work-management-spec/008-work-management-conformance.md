<!-- GENERATED — DO NOT EDIT -->
# Work Management conformance

<div id="enable-section-numbers" />

[Previous: Provider and command-plane boundary](007-provider-and-command-plane-boundary.md) | [Index](000-index.md)

<span id="mrd-urn-uuid-68adde2d-be01-5184-8193-9ebb62f8d434"></span>

A Work Management implementation conforms to this specification only when its source MRDs, dependencies, evidence, generated views, and lifecycle behavior pass the checks below. These checks keep human-readable documentation aligned with machine-readable authority.

## Conformance requirements

1. MRD envelopes validate against the KIS MRD core schema.
2. All MRD dependencies resolve and preserve one-owner authority.
3. Harvested source hashes match the pinned canonical snapshot.
4. Generated specification is byte deterministic.
5. Generated output is stale/tamper detectable.
6. Lifecycle transitions and selection rules are reproduced exactly from canonical contracts.
7. Unavailable live Project evidence remains explicit and does not become inferred authority.

## Source and authority

This page projects `urn:uuid:68adde2d-be01-5184-8193-9ebb62f8d434` version `1.0.0`. The MRD remains authoritative; this generated page has no write-back authority.
