# MOOD AGENTS 018 — Capability Model

**Authority:** MOOD-AGENTS-018 TASK.md Phase F

## Canonical capabilities

| Slug | Definition |
|---|---|
| `audio-analysis` | Input audio, output auditable analysis results. |
| `research` | Organize research material and produce structured summaries. |
| `documentation` | Draft protocol documents, READMEs, change logs. |
| `code-assistance` | Assist in implementation. Cannot become governance authority. |
| `proof-verification` | Verify submission evidence format / integrity. Does **not** approve. |
| `curation` | Organize content. Does **not** assign reputation. |
| `task-assistance` | Plan and track tasks. |
| `node-operations` | Support node operations (NOT chain settlement). |
| `other` | Specialized. Requires explicit human review of the capability text. |

## Forbidden capabilities

- ❌ `super-intelligence`
- ❌ `all-purpose`
- ❌ `guaranteed-profit`
- ❌ `autonomous-governance`

These are rejected at registration (operator-controlled; capability set is
selected from the canonical list above).