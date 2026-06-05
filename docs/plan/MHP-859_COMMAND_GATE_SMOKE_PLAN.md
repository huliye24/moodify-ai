# MHP-859: Command Gate Smoke Plan

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6C: Worker Contracts / V3
**Depends on**: MHP-857 (Worker JSONL), MHP-858 (Judge Schema)
**Protocol**: AWJ Stack + E-Chain 54

## Context

The Judge `G_runtime` gate requires that all proof commands exit 0. This MHP defines the canonical smoke command set for every MAP Build task — the commands a Worker must run and a Judge must verify before accepting any AEP.

## MAP Command Gate — Canonical Commands

### v01 Core Pipeline

```bash
# Unit tests (must always pass)
PYTHONPATH=/home/ubuntu/moodify-mainline:/home/ubuntu/moodify-mainline/moodify-core-package/src \
  python3 -m pytest -q moodify-core-package/tests/test_v01_pipeline.py

# API smoke (must always pass)
PYTHONPATH=/home/ubuntu/moodify-mainline:/home/ubuntu/moodify-mainline/moodify-core-package/src \
  python3 -m pytest -q moodify-core-package/tests/test_api_v01.py
```

### CLI Smoke (one preset, fast)

```bash
PYTHONPATH=/home/ubuntu/moodify-mainline:/home/ubuntu/moodify-mainline/moodify-core-package/src \
  python3 -m moodify.cli v01-process \
    moodify-core-package/tests/baseline/test_audio/vocal_folk.wav \
    --preset clean_master --output-dir /tmp/map_command_gate_test
```

### CLI Smoke (all 3 presets)

```bash
for preset in clean_master warm_vocal wide_space; do
  PYTHONPATH=/home/ubuntu/moodify-mainline:/home/ubuntu/moodify-mainline/moodify-core-package/src \
    python3 -m moodify.cli v01-process \
      moodify-core-package/tests/baseline/test_audio/vocal_folk.wav \
      --preset $preset --output-dir /tmp/map_command_gate_test/$preset
done
```

### Schema Validation

```bash
python3 -m json.tool schemas/map_chain_report.schema.json >/dev/null

python3 -c "
import json
from jsonschema import validate
with open('schemas/map_chain_report.schema.json') as f: s = json.load(f)
# validate against a known-good report
with open('/tmp/map_command_gate_test/clean_master/vocal_folk_clean_master_report.json') as f: r = json.load(f)
validate(r, s)
print('schema valid')
"
```

### Artifact Existence Check

```bash
test -f /tmp/map_command_gate_test/clean_master/vocal_folk_clean_master.wav && echo "WAV: ok"
test -f /tmp/map_command_gate_test/clean_master/vocal_folk_clean_master_report.json && echo "JSON: ok"
test -f /tmp/map_command_gate_test/clean_master/vocal_folk_clean_master_report.pdf && echo "PDF: ok"
test -f /tmp/map_command_gate_test/clean_master/vocal_folk_before_spectrum.png && echo "BEFORE: ok"
test -f /tmp/map_command_gate_test/clean_master/vocal_folk_clean_master_after_spectrum.png && echo "AFTER: ok"
```

## Command Gate Matrix

| Gate Level | Commands | Time Budget | When Required |
|-----------|----------|-------------|---------------|
| **L1: Unit** | `pytest test_v01_pipeline.py` | < 10s | Every Worker AEP |
| **L2: API** | `pytest test_api_v01.py` | < 10s | Every Worker AEP |
| **L3: CLI Single** | `v01-process --preset clean_master` | < 30s | Implementation MHPs |
| **L4: CLI All** | `v01-process` × 3 presets | < 60s | Build Gate MHPs |
| **L5: Schema** | `jsonschema.validate(report)` | < 5s | Schema/contract MHPs |
| **L6: Artifacts** | `test -f` × 5 artifacts | < 1s | Delivery MHPs |

## Judge Recipe

```python
# The Judge script for each Worker AEP runs this:
def command_gate(task: dict) -> GateResult:
    commands = task["proof_commands"]
    results = []
    for cmd in commands:
        exit_code, output = run_command(cmd)
        results.append({"command": cmd, "exit_code": exit_code, "output_summary": output[:500]})
    all_passed = all(r["exit_code"] == 0 for r in results)
    return GateResult(
        passed=all_passed,
        detail=f"{sum(1 for r in results if r['exit_code']==0)}/{len(results)} commands passed",
        commands_run=results,
    )
```

## Acceptance Criteria

- [x] 6 canonical command gate levels defined (L1–L6).
- [x] Each level has time budget and when-required policy.
- [x] Judge recipe is defined.
- [x] All commands are idempotent and safe to re-run.
