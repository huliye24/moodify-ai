# Canonical Music Project v1

`project.json` is the current canonical manifest. Required top-level fields are:

- `schema_version`, `project_id`, `title`;
- `assets`, `decisions`, `plans`, `runs`;
- `revisions`, `evidence`, `metadata`.

An asset records a stable UUID, kind, resolved reference path, SHA-256, role and metadata. A path is a locator, not identity. Moodify validates the recorded hash before rendering and again during run verification.

A plan records a UUID, intent, explicit processing steps, dry-run state and warnings. The v1 accepted processing step is bounded gain only. A run records its plan, terminal status, output directory, source hashes, artifacts, evidence path and errors.

Writes use a temporary sibling file, flush and atomic replacement. Existing source audio remains read-only. Schema migrations must be explicit and must preserve historical interpretation; an unknown schema version fails closed.

