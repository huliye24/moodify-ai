# Golden Runtime Case — DSK-MFY-RUNTIME-INTEGRATION-001

One complete real production case driven through the formal CLI v2.

## Case
- case_id: MFY-CASE-5030DEA8F22D
- final state: COMPLETED
- source fixture: `moodify-core-package/tests/baseline/test_audio/vocal_folk.wav`
- source_sha256: `34b94987959122b7...`
- plan_hash: `ce0f39451f8a58fb...`
- approval: `APR-85bc53a1b459` by huliye24
- engine: native 1.0.0
- execution: `MFY-EXEC-ea2290afad74`
- verification: `VERIFY-4f1e13050945` (PASS)
- moodify_version: 0.1.0

## State path (from case_final.json transitions)
```
- -> CREATED  (2026-08-01T14:28:19Z)
CREATED -> SOURCE_REGISTERED  (2026-08-01T14:28:19Z)
SOURCE_REGISTERED -> SPECIFIED  (2026-08-01T14:28:19Z)
SPECIFIED -> ANALYZED  (2026-08-01T14:28:28Z)
ANALYZED -> PLANNED  (2026-08-01T14:28:28Z)
PLANNED -> TECHNICALLY_VALIDATED  (2026-08-01T14:28:28Z)
TECHNICALLY_VALIDATED -> AWAITING_ARTISTIC_APPROVAL  (2026-08-01T14:28:29Z)
AWAITING_ARTISTIC_APPROVAL -> APPROVED  (2026-08-01T14:28:29Z)
APPROVED -> EXECUTING  (2026-08-01T14:28:30Z)
EXECUTING -> EXECUTED  (2026-08-01T14:28:38Z)
EXECUTED -> VERIFYING  (2026-08-01T14:28:39Z)
VERIFYING -> VERIFIED  (2026-08-01T14:28:39Z)
VERIFIED -> PACKAGED  (2026-08-01T14:28:39Z)
PACKAGED -> COMPLETED  (2026-08-01T14:28:39Z)
```

## Artifacts
- `cli_transcript.json` — every CLI request and response
- `case_final.json` — persisted case state incl. execution + verification records
- `evidence/` — the formal evidence package (verified and internally consistent)
- `output/processed_audio.wav` — the executed output
- `source_manifest.json` — fixture identity
