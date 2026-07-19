# Registry

Machine-readable JSON registry contracts are canonical in this repository. The requested conceptual contracts are represented as JSON files to avoid duplicate YAML authorities:

- `architectural_boundaries.json` for architectural-boundary candidates.
- `investigations.json` for registered investigation workspaces. Repository topology validation derives the complete set of canonical investigation workspaces from this registry and verifies each workspace's required scaffold.
- `terminology.json` for terminology authority pointers.
- `classifications.json` for classification contracts.

Legacy lifecycle indexes remain as JSON-only companions: `protocol_versions.json`, `retained_classifications.json`, and `candidate_invariants.json`.

`retained_classifications.json` indexes canonical retained-classification artifacts; the artifact itself remains authoritative for per-system outputs, lineage, and freshness.
