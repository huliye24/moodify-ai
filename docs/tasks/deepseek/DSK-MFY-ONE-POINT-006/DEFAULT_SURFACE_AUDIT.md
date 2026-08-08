# Default Surface Audit — DSK-MFY-ONE-POINT-006

## Audit Scope

Every element that appears in the default `refine prepare` output surface (result.json, summary.md, summary.html, CLI stdout).

## Audit Method

For each element: Is it necessary for the operator to complete their task? Does it use only the 12 canonical words? Could an internal acronym or score stack be removed without losing truth?

## Findings

### result.json

| Element | Judgment |
|---|---|
| schema_version | Keep — required for machine parsing |
| spec_identity (SHA-256) | Keep — traceability anchor |
| status | Keep — 1 of 4 canonical states |
| essence, protect, allow, avoid, action, entrust, owner | Keep — machine contract; `avoid` is nested under Protect on the human surface |
| evidence_path | Keep — where to find depth |
| created_at | Keep — provenance |
| case_id | Keep — technical traceability |
| warnings | Keep — honest disclosure |
| gate_summary | Keep — PROGRESSIVE access to technical gates |

### summary.md / summary.html

| Element | Judgment |
|---|---|
| Essence heading + description | Keep |
| Protect list + nested Avoid clause | Keep |
| Allow description | Keep |
| Separate Avoid heading | Remove — it would create a sixth narrative centre |
| Action description (no acronyms) | Keep |
| Entrust + owner | Keep |
| Status | Keep |
| Evidence link line | Keep |
| Internal acronyms (WSE/MSE/PPE/MRS) | ABSENT — passing |
| Score walls, dashboards, metric stacks | ABSENT — passing |

### summary.html

| Element | Judgment |
|---|---|
| Semantic HTML (h1, h2, p, li, hr) | Keep — accessible structure |
| System font stack | Keep — no design dependency |
| Max-width 640px, generous line-height | Keep — readable |
| Light background, dark text | Keep — accessible contrast |
| No JavaScript, no charts, no widgets | Clean — passing |
| No decorative dashboards | Clean — passing |

### CLI stdout

| Element | Judgment |
|---|---|
| Status (1 of 4) | Keep |
| Essence, Owner, Action, Entrust summaries | Keep |
| Warnings (when present) | Keep |
| Gate acronyms, score lists, metric dumps | ABSENT — passing |

## Verdict

Default surface passes: 0 internal acronyms, 5 canonical concepts, no false claims, no score walls, no technology self-promotion. All technical depth preserved in evidence/.
