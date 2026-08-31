<!-- GENERATED — DO NOT EDIT -->
# Publication and generated documentation

The publication registry is the single family inventory for generated specifications and human documentation.

## Registered families

| Family | Output | Classes | Published to Pages |
|---|---|---|---|
| `mrd-specification` | `generated/mrd-specification` | human_readable_specification, generated_reference | Yes |
| `work-management-spec` | `generated/work-management-spec` | human_readable_specification, generated_reference | No — standalone family |
| `documentation-reference-standard` | `generated/documentation-reference-standard` | human_readable_specification, generated_reference | Yes |
| `mrd-specification-docs` | `generated/mrd-specification-docs` | human_documentation | Yes |
| `work-management-docs` | `generated/work-management-docs` | human_documentation | No — standalone family |
| `repository-docs` | `generated/repository-docs` | human_documentation | Yes |

The shared publication kernel validates every registered family, dispatches adapters, writes complete bundles atomically, and compares exact generated inventories and bytes for drift.

The `publish_to_site` decision is explicit for every family. The documentation site, public search index, and GitHub Pages release include only families marked `true`; standalone families remain generated and verified but are not reader-facing Pages content.
