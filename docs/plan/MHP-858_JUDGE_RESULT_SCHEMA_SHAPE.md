# MHP-858: Judge Result Schema Shape

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6C: Worker Contracts / E2
**Depends on**: MHP-857 (Worker Task JSONL)
**Protocol**: AWJ Stack + E-Chain 54

## Context

The E-chain (§6) defines the Judge gate formula:

```text
G_schema * G_scope * G_runtime * G_test * G_evidence * G_arch = 1
```

Each gate must pass for Judge acceptance. This MHP defines the JSON schema for Judge verification results.

## Judge Output Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://moodify.local/schemas/judge_result.schema.json",
  "title": "MAP Judge Gate Result",
  "type": "object",
  "required": ["task_id", "verdict", "gates", "summary"],
  "properties": {
    "task_id": {
      "type": "string",
      "description": "Worker task ID being judged."
    },
    "verdict": {
      "type": "string",
      "enum": ["accept", "reject", "needs_architect_review"],
      "description": "Overall Judge verdict for this Worker output."
    },
    "gates": {
      "type": "object",
      "required": ["schema", "scope", "runtime", "test", "evidence", "arch"],
      "properties": {
        "schema": {
          "type": "object",
          "required": ["passed", "detail"],
          "properties": {
            "passed": {"type": "boolean"},
            "detail": {"type": "string", "maxLength": 200}
          }
        },
        "scope": {
          "type": "object",
          "required": ["passed", "detail"],
          "properties": {
            "passed": {"type": "boolean"},
            "detail": {"type": "string", "maxLength": 200},
            "files_checked": {"type": "array", "items": {"type": "string"}},
            "violations": {"type": "array", "items": {"type": "string"}}
          }
        },
        "runtime": {
          "type": "object",
          "required": ["passed", "detail"],
          "properties": {
            "passed": {"type": "boolean"},
            "detail": {"type": "string", "maxLength": 200},
            "commands_run": {"type": "array", "items": {"type": "object", "properties": {
              "command": {"type": "string"},
              "exit_code": {"type": "integer"},
              "output_summary": {"type": "string", "maxLength": 500}
            }}}
          }
        },
        "test": {
          "type": "object",
          "required": ["passed", "detail"],
          "properties": {
            "passed": {"type": "boolean"},
            "detail": {"type": "string", "maxLength": 200},
            "test_summary": {"type": "string", "maxLength": 300}
          }
        },
        "evidence": {
          "type": "object",
          "required": ["passed", "detail"],
          "properties": {
            "passed": {"type": "boolean"},
            "detail": {"type": "string", "maxLength": 200},
            "artifacts_found": {"type": "array", "items": {"type": "string"}},
            "artifacts_missing": {"type": "array", "items": {"type": "string"}}
          }
        },
        "arch": {
          "type": "object",
          "required": ["passed", "detail"],
          "properties": {
            "passed": {"type": "boolean"},
            "detail": {"type": "string", "maxLength": 200},
            "diff_risk": {"type": "string", "enum": ["low", "medium", "high"]},
            "files_changed": {"type": "array", "items": {"type": "string"}}
          }
        }
      }
    },
    "summary": {
      "type": "string",
      "maxLength": 500,
      "description": "Human-readable summary of the Judge decision."
    },
    "review_required": {
      "type": "boolean",
      "description": "True if Architect must review before merge."
    },
    "merge_policy": {
      "type": "string",
      "enum": ["auto_merge", "squash_merge", "no_merge"],
      "description": "Merge action if verdict is accept."
    }
  }
}
```

## Gate Pass Conditions

| Gate | Pass Condition | Fail Example |
|------|---------------|-------------|
| `schema` | All JSON outputs parse; required fields present | Missing `task_id` in output |
| `scope` | All modified files in `allowed_files`; zero in `forbidden_files` | Worker touched `mrs_engine.py` |
| `runtime` | All `proof_commands` exit 0 | `pytest` returned exit code 1 |
| `test` | Specified tests pass | `test_v01_pipeline.py` had a failure |
| `evidence` | All `expected_outputs` have corresponding artifacts | Missing `manifest.json` |
| `arch` | Diff risk is low OR Architect has approved | 200+ line change without review |

## Judge Verdict Logic

```python
def judge(gates: dict) -> str:
    if all(g["passed"] for g in gates.values()):
        return "accept"
    if gates["arch"]["diff_risk"] == "high" or not gates["scope"]["passed"]:
        return "reject"
    return "needs_architect_review"
```

## Integration with Existing Protocol

The Judge schema extends `scripts/aep_worker_protocol.py` by adding scope, test, evidence, and arch gates beyond the existing `task_id`/`loop`/`schema` check.

## Acceptance Criteria

- [x] Judge output schema defined with 6 gates.
- [x] Each gate has pass/fail conditions.
- [x] Verdict logic is explicit (accept/reject/needs_architect_review).
- [x] Compatible with existing `aep_worker_protocol.py` validate flow.
