<!-- GENERATED — DO NOT EDIT -->
# Publication and generated documentation

The publication registry is the single family inventory for generated specifications and human documentation.

## Registered families

| Family | Output | Classes |
|---|---|---|
| `governance-spec` | `generated/governance-spec` | human_readable_specification, generated_reference |
| `work-management-spec` | `generated/work-management-spec` | human_readable_specification, generated_reference |
| `documentation-reference-standard` | `generated/documentation-reference-standard` | human_readable_specification, generated_reference |
| `governance-docs` | `generated/governance-docs` | human_documentation |
| `work-management-docs` | `generated/work-management-docs` | human_documentation |
| `repository-docs` | `generated/repository-docs` | human_documentation |

The shared publication kernel validates family registration, dispatches adapters, writes complete bundles atomically, and compares exact generated inventories and bytes for drift.

The documentation site and static search derive routes from this same registry. The release package then bundles the verified site for GitHub Pages.
