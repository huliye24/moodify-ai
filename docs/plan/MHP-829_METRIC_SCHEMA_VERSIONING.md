# MHP-829: Metric Schema Versioning

**Status**: done
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-SYSTEM-044 / System Plan-6A: Standardization / P3 (Validation)
**Depends on**: MHP-828
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Establish a versioning policy for the NightMetricRecord schema and all collector output formats to ensure backward compatibility across E-Chains.

## Schema Versioning Policy

### 1. Schema Registry

| Schema | Current Version | File | Status |
|--------|----------------|------|--------|
| NightMetricRecord | v1.0 | `schemas/night_metric_record.schema.json` | ACTIVE |
| DeepSeek Worker Output | v1.0 | `schemas/deepseek_worker_output.schema.json` | ACTIVE |
| Recommendation | v1.0 | `moodify_runtime/recommenders/base.py` | ACTIVE |
| DataLoopResult | v1.0 | `moodify_runtime/data_loop_runner.py` | ACTIVE |

### 2. Version Number Rules (SemVer)

- **MAJOR** (X.0.0): Breaking change — field removed, renamed, or type changed. Old consumers cannot read new data.
- **MINOR** (0.X.0): New optional fields added. Old consumers can still read (ignore unknown fields).
- **PATCH** (0.0.X): Documentation, thresholds, or implementation changes. Schema shape unchanged.

### 3. Compatibility Contract

Each schema must:
- Declare its `$id` with version in the URI
- Include a `version` field in the root object for runtime detection
- Use `additionalProperties: true` for forward-compat (or document strict mode)

### 4. Migration Rules

When a breaking change is needed:
1. Bump MAJOR version.
2. Add a migration script in `scripts/migrate/`.
3. Keep the old collector as deprecated for one E-Chain cycle.
4. Update the CLI to accept `--schema-version` flag.
5. Announce in CHANGELOG with migration guide.

### 5. NightMetricRecord v1.0 → v1.1 Migration Example

v1.0 fields: `run_id, started_at, collected_at, source_artifacts, runtime, scoring, craft, queue, tidal, tasks`

v1.1 (proposed): add `operator.decision_history` and `operator.review_minutes` as optional fields. MINOR bump.

### 6. Validation

Run schema validation nightly:

```bash
python3 -c "
import json
from pathlib import Path
record = json.loads(Path('reports/data_loop/<run_id>/night_metric_record.json').read_text())
# Validate required top-level keys
required = ['run_id', 'started_at', 'collected_at', 'runtime', 'scoring', 'craft', 'tasks']
missing = [k for k in required if k not in record]
if missing:
    print(f'SCHEMA VIOLATION: missing keys {missing}')
else:
    print('SCHEMA OK')
"
```

## Acceptance Criteria

- All four schemas are registered with versions. ✅
- SemVer rules are documented. ✅
- Migration rules are explicit. ✅
- Nightly validation check is defined. ✅
