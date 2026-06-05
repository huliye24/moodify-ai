# MHP-857: Worker Task JSONL Shape

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6C: Worker Contracts / E1
**Depends on**: MHP-856 (Probe 6B Decision)
**Protocol**: AWJ Stack + E-Chain 54

## Context

The AEP Worker Protocol (`docs/protocol/AEP_WORKER_PROTOCOL.md`) defines a generic contract: architect creates JSONL tasks, workers process one task per call, judge validates outputs. MAP-Chain needs its own JSONL shape for dispatching Build NEM work to Workers.

## Worker Task JSONL Shape

Each line is one bounded MAP Build task:

```json
{
  "task_id": "MAP-BUILD-046-MHP-864-001",
  "echain": "ECHAIN-MOODIFY-MAP-CHAIN-015",
  "nem": "NEM-MOODIFY-MAP-BUILD-046",
  "mhp": "MHP-864",
  "mhp_title": "Implement Scan Result Contract",
  "phase": "Build-6A",
  "type": "implementation",
  "layer": "S",
  "role": "worker",
  "input_files": [
    "moodify-core-package/src/moodify/v01_types.py",
    "moodify-core-package/src/moodify/v01_pipeline.py"
  ],
  "allowed_files": [
    "moodify-core-package/src/moodify/v01_types.py",
    "moodify-core-package/src/moodify/v01_pipeline.py",
    "moodify-core-package/tests/test_v01_pipeline.py"
  ],
  "forbidden_files": [
    "moodify_runtime/mrs_engine.py",
    "moodify_runtime/operator_api.py"
  ],
  "expected_outputs": [
    "ScanResult with 6 new acoustic fields",
    "Updated scan_audio() implementation",
    "Unit test passing"
  ],
  "proof_commands": [
    "python3 -m pytest -q moodify-core-package/tests/test_v01_pipeline.py"
  ],
  "architect_notes": "Add loudness_lufs, transient_ratio, stereo_width, spectral_centroid_hz, dc_offset, clip_count. All optional, default None/0.",
  "priority": 1,
  "depends_on": ["MHP-863"]
}
```

## Field Definitions

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `task_id` | string | yes | Unique task identifier |
| `echain` | string | yes | Parent E-chain ID |
| `nem` | string | yes | Parent NEM ID |
| `mhp` | string | yes | MHP number this task belongs to |
| `mhp_title` | string | yes | Human-readable MHP title |
| `phase` | string | yes | Build phase: Build-6A/6B/6C |
| `type` | string | yes | `implementation`, `test`, `docs`, or `review` |
| `layer` | string | yes | MAP layer: S/A/D/P/V/R/G |
| `role` | string | yes | AWJ role: `worker` or `architect` |
| `input_files` | string[] | yes | Files the Worker must read to understand context |
| `allowed_files` | string[] | yes | WHITELIST: files the Worker CAN modify |
| `forbidden_files` | string[] | yes | BLACKLIST: files the Worker MUST NOT touch |
| `expected_outputs` | string[] | yes | Human-readable deliverables |
| `proof_commands` | string[] | yes | Shell commands that MUST exit 0 for acceptance |
| `architect_notes` | string | no | Additional guidance from Architect |
| `priority` | integer | yes | 1 (highest) to 5 (lowest) |
| `depends_on` | string[] | no | MHPs that must complete first |

## Worker Output Shape

Each Worker returns _exactly_ one JSON object per task:

```json
{
  "task_id": "MAP-BUILD-046-MHP-864-001",
  "status": "done",
  "artifacts": [
    "moodify-core-package/src/moodify/v01_types.py",
    "moodify-core-package/src/moodify/v01_pipeline.py",
    "moodify-core-package/tests/test_v01_pipeline.py"
  ],
  "proof_results": [
    {"command": "python3 -m pytest -q moodify-core-package/tests/test_v01_pipeline.py", "exit_code": 0, "output_summary": "7 passed"}
  ],
  "diff_summary": "3 files changed, +45 -2 lines, v01_types.py ScanResult +6 fields, scan_audio() updated",
  "notes": "All fields default to None. Existing tests pass. No new dependencies."
}
```

## AWJ Control

- **Architect** writes the JSONL task file.
- **Worker** processes ONE task per call. Cannot change `task_id`, `mhp`, `layer`, `allowed_files`, `proof_commands`, or `priority`.
- **Judge** validates: (1) artifacts within `allowed_files`, (2) no artifact in `forbidden_files`, (3) all `proof_commands` exit 0, (4) output is valid JSON.

## Build NEM Task Count

18 Build MHPs × ~2 tasks per MHP = ~36 Worker tasks for Build NEM-046.

## Acceptance Criteria

- [x] JSONL task shape defined with 18 fields.
- [x] Worker output shape defined with 6 fields.
- [x] AWJ control rules explicit.
- [x] Compatible with existing `scripts/aep_worker_protocol.py` validate/select flow.
