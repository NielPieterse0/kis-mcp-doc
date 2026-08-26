<!-- GENERATED — DO NOT EDIT -->
# Apply governance to a change

Prescribe how kis-op applies the governance model when inspecting, planning, changing, validating, and presenting governed repository work.

Follow the canonical phases in order. A phase can stop the change when its declared stop condition is met.

## 1. Resolve Authority

- load repository authority and active change scope.
- identify canonical owners relevant to the request.

Stop here when:
- required authority cannot be resolved.

## 2. Select Applicable Mrds

- classify the actual governed needs.
- apply the 47-type applicability contract.
- select the minimum sufficient MRD set.

Stop here when:
- a required need has no representable type and no governed extension path.

## 3. Resolve Relationships

- bind dependencies and typed relationships.
- detect duplicate ownership and authority conflicts.

Stop here when:
- required dependency or canonical owner is unresolved.

## 4. Validate Governance

- run structural and semantic governance validation.
- surface stable reason codes for blocking failures.

Stop here when:
- blocking governance validation fails.

## 5. Execute Bounded Change

- work only inside the admitted change scope.
- preserve parent KIS trust and Git authority.
- avoid unrelated documentation or platform expansion.

Stop here when:
- requested mutation exceeds admitted scope or authority.

## 6. Generate Review Surface

- generate the HRD specification from validated MRDs.
- preserve provenance and deterministic source bindings.

Stop here when:
- source validation or deterministic generation fails.

## 7. Verify And Report

- verify generated output is current and untampered.
- report completion, gaps, deferrals, and diagnostics against the requested scope.

Use the [Governance Specification](../governance-spec/001-specification.md) when you need exact MUST/SHOULD/MAY requirements or rule identifiers.
