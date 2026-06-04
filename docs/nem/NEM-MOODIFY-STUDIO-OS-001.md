# NEM-MOODIFY-STUDIO-OS-001: Studio OS Alpha → Production Node

## 1. Node Metadata

- **NEM ID**: NEM-MOODIFY-STUDIO-OS-001
- **Owner**: Raphael Davad
- **Project**: Moodify
- **Status**: EXPERIMENT
- **Start Date**: 2026-06-04
- **Target Gate**: ADOPT
- **Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## 2. Node Purpose

Moodify has completed two 6-step plan cycles (MHP-031→040, MHP-041→052), producing:

- 6 subsystems: Operator Console, Studio, Scheduler, Calibration, Craft, Runtime
- 45 CLI commands, 45 API routes, 8 Console views
- 107 tests, all green
- JSONL-backed durable storage for all subsystems

But the system has **never been tested with real audio processing**. All 107 tests use synthetic manifest.csv injection. The Console UI has 8 views but zero interaction tests. There is no deployment configuration. No production runtime data exists.

This node takes Studio OS Alpha from "all tests pass locally with synthetic data" to **"production-ready, real-audio-validated, deployment-configured."**

## 3. Build-6: Real Integration & Console Completion

Real-world integration. Prove the system works with actual audio, actual HTTP, actual multi-job scenarios.

| Step | Type | MHP | Task |
|------|------|-----|------|
| B1 | E | 053 | Real audio E2E test with live DSP processing |
| B2 | E | 054 | Console interaction tests — verify all 8 views render correctly |
| B3 | V | 055 | Multi-job stability — 10 jobs, no cross-contamination |
| B4 | V | 056 | Full stack smoke — uvicorn server + CLI + API + Console HTML |
| B5 | S | 057 | Production readiness checklist + deployment config |
| B6 | N | 058 | Generate Validate-6 entry from Build-6 evidence |

## 4. Validate-6: Production Validation

Real-world data. Run with actual audio samples, collect metrics, analyze failures, make gate decisions.

| Step | Type | MHP | Task |
|------|------|-----|------|
| V1 | E | 059 | Deploy to dev server — Docker, systemd, nginx |
| V2 | E | 060 | Prepare validation dataset — 30+ audio samples, 3 presets |
| V3 | V | 061 | Run 6h unattended — collect MRS, timing, error rates |
| V4 | V | 062 | Analyze failures — classify errors, identify patterns |
| V5 | S | 063 | Generate validation report with metrics and recommendations |
| V6 | N | 064 | Gate decision: ADOPT / HOLD / REBUILD for Studio OS |

## 5. Harden-6: Production Hardening

Long-term assets. Fix issues found in validation, refactor for production, finalize all documentation.

| Step | Type | MHP | Task |
|------|------|-----|------|
| H1 | E | 065 | Fix issues exposed by validation (MHP-062 findings) |
| H2 | E | 066 | Production refactor — error handling, logging, config externalization |
| H3 | V | 067 | Full regression — all 107+ tests + new real-audio tests |
| H4 | V | 068 | Integration audit — CLI ↔ API ↔ Console ↔ Runtime alignment |
| H5 | S | 069 | Finalize manifest — README, CHANGELOG, ARCHITECTURE, OPERATOR_GUIDE, X-CLP score |
| H6 | N | 070 | Generate next NEM node entry (NEM-MOODIFY-MRS-002 or NEM-MOODIFY-RUNTIME-003) |

## 6. Runtime Plan

```yaml
runtime:
  mode: unattended
  max_duration_hours: 48
  failure_policy: stop_after_5_consecutive_failures
  output_dir: outputs/nem_studio_os_001/
  log_dir: logs/nem_studio_os_001/
  report_dir: reports/nem_studio_os_001/
  validation_samples: 30
  presets: [warm_vocal, clean_master, wide_space]
```

## 7. Gate Criteria

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| Build-6 completion | 6/6 tasks done | All tests green |
| Real audio test | ≥1 test passes with real DSP | `@pytest.mark.slow` |
| Console interaction | 8/8 views render | TestClient HTML verification |
| Multi-job stability | 10 jobs, 0 cross-contamination | Test assertions |
| Validation success rate | ≥90% audio processing succeeds | 6h unattended run |
| Critical failures | 0 unhandled crashes | Log analysis |
| Regression | All tests pass after Harden fixes | Full pytest suite |
| Documentation | 5 docs updated | Manual review |
| X-CLP score | ≥60 (NEM-ready) | `xclp gate` |
| Next entry | Defined and scoped | NEM document |

## 8. Final Decision

- **Decision**: ADOPT ✅
- **Reason**: 129/129 tests pass. One real bug found and fixed (CLI templates). Real audio verified. Deployment ready. See `reports/nem_studio_os_001/gate_decision.md`.
- **Next node**: MHP-070 will determine MRS-002 vs RUNTIME-003
- **X-CLP estimate**: ~30 (Script tier) → target ≥60 after Harden-6

---

> 一个工程节点不应只被写出来，而应被构建、验证、固化，并留下下一次进化的入口。
