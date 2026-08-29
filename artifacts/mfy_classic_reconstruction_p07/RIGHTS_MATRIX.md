# P07 Rights Matrix

Processing data != training data != user private data.

| Record | rights_status | processing | training | public demo | retention |
|---|---|---|---|---|---|
| SYNTH_T01..T03 (Gate A) | INTERNAL_TEST_ALLOWED | YES | NO | NO | internal_research_only |

Rules enforced in code (validate_rights):
- INTERNAL_TEST_ALLOWED can never grant training_permission
- rights_status must be OWNED / AUTHORIZED / INTERNAL_TEST_ALLOWED
- processing_permission required to run reconstruction
- training_permission and public_demo_permission DEFAULT NO

Real corpus records must carry explicit grants per track.
