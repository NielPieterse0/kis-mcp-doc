<!-- GENERATED — DO NOT EDIT -->
# Governed relationship vocabulary

<div id="enable-section-numbers" />

[Owning specification chapter: Authority, Ownership, and Relationships](004-authority-ownership-and-relationships.md) | [Documentation index](000-index.md)

> **Output class:** `generated_reference`. This page is an exact lookup projection of canonical Governance authority. It has no write-back authority.

Relationships preserve authority by expressing how one governed artifact relates to another without creating duplicate ownership.

| Relationship | Meaning |
|---|---|
| `depends_on` | The source requires the target authority to be valid or interpretable. |
| `validated_by` | The source is structurally or semantically checked by the target contract or validator. |
| `governs` | The source prescribes requirements for the target. |
| `constrains` | The source restricts permitted values or behavior of the target. |
| `selects` | The source chooses among behaviors already permitted by the target authority. |
| `maps_to` | The source translates deterministically to the target representation. |
| `implements` | The source is an implementation of target authority. |
| `evidences` | The source records evidence about the target without becoming its authority. |
| `projects` | The source is a generated view of the target and has no write-back authority. |
| `references` | The source points to the target owner without restating the governed fact as new authority. |
| `supersedes` | The source replaces the target while preserving lineage. |

## Source and authority

This reference projects `KIS-KNOW-CON-POL-002` version `1.0.0`. The MRD remains authoritative.
