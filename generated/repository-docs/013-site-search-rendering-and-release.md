<!-- GENERATED — DO NOT EDIT -->
# Site, search, rendering, and release

Follow the repository bundle from registered publication family to reader-facing GitHub Pages output.

The publication-family registry selects reader-facing families with `publish_to_site`. Site, public search, and the Pages release use that same selection; registration alone never implies public exposure.

## Delivery surfaces

| Surface | Current configuration |
|---|---|
| Site | `KIS Documentation` at base path `/kis-mcp-doc`; search index `generated/documentation-search/search-index.json` |
| Search | default result limit `10`; minimum token length `2` |
| Release | hosting `github-pages`; site output `generated/documentation-site` |

## Deterministic flow

1. A family adapter validates and builds its own semantic bundle.
2. The shared publication kernel verifies exact file inventory, bytes, and family manifests.
3. The documentation site composes only `publish_to_site=true` families into routes and navigation.
4. Search indexes the same public family set.
5. The release builder packages the generated site and release metadata for GitHub Pages.

Rendering is downstream presentation. It does not interpret new canonical facts or write changes back to source authority.

