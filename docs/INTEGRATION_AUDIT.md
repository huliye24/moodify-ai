# Integration Audit — CLI ↔ API ↔ Console ↔ Runtime

**Date**: 2026-06-04
**Protocol**: NEM-18 / Harden-6 / V2 (Integration Audit)
**Node**: NEM-MOODIFY-STUDIO-OS-001

---

## 1. Four-Interface Coverage Matrix

| Subsystem | Module | CLI | API | Console | Runtime |
|-----------|--------|-----|-----|---------|---------|
| Operator Jobs | operator_console.py | ✅ create/list/plan/run/show | ✅ CRUD + attach + deliver | ✅ 4 views (Queue, Jobs, Reports, Delivery) | ✅ run_daily engine |
| Studio | studio.py | — | ✅ clients/projects/orders | ✅ 1 view | — |
| Scheduler | scheduler.py | — | ✅ requests/leases/runs | ✅ 1 view | — |
| Calibration | mrs_calibration.py | — | ✅ sample-sets/reviews/thresholds | ✅ 1 view | — |
| Craft | craft_memory.py | ✅ craft/writeback | ✅ records | ✅ 1 view | ✅ writeback on delivery |
| Config | config.py | ✅ load_config | ✅ load_config | — | ✅ RuntimeConfig |
| Runner | runner.py | ✅ run/cli | ✅ via run_operator_job | ✅ "Run" button | ✅ run_daily + templates |
| Registry | registry.py | ✅ register | ✅ via plan_operator_runtime | — | ✅ input discovery |
| Queue | queue.py | ✅ plan | ✅ via plan_operator_runtime | — | ✅ task queue |
| Utils | utils.py | — | — | — | ✅ I/O, hashing |
| CLI | cli.py | ✅ 40+ subcommands | — | — | — |
| API | operator_api.py | — | ✅ 45+ routes | — | — |
| Console HTML | operator_console.html | — | — | ✅ 8 views | — |

## 2. Console View → API Contract Verification

| View | JS Render Function | API Endpoint(s) Called | Contract Tested? |
|------|--------------------|------------------------|-------------------|
| Queue | renderQueue | GET /operator/jobs | ✅ test_console_interaction |
| Job Detail | renderJobDetail | GET /operator/jobs/{id}/detail | ✅ test_console_interaction |
| Reports | renderReports | GET /operator/jobs/{id}/reports | ✅ test_console_interaction |
| Delivery | renderDelivery | GET /operator/deliveries | ✅ test_console_interaction |
| Craft | renderCraft | GET /craft/records | ✅ test_console_interaction |
| Studio | renderStudio | GET /studio/clients | ✅ test_console_interaction |
| Scheduler | renderScheduler | GET /scheduler/requests | ✅ test_console_interaction |
| Calibration | renderCalibration | GET /calibration/reviews | ✅ test_console_interaction |

**All 8 Console views call contract-tested API endpoints.** ✅

## 3. Run Operator Job — Reachability

| Interface | Path | Tested? |
|-----------|------|---------|
| CLI | `python3 -m moodify_runtime.cli operator-run --job-id JOB_XXX --live` | ✅ test_operator_job_runner |
| API | POST /operator/jobs/{job_id}/run | ✅ test_api_contract |
| Console | "Run" button → api('POST', `/operator/jobs/${id}/run`) | ✅ HTML verification |
| Runtime | run_operator_job(...) | ✅ 10 unit tests + 3 real audio |

**run_operator_job --live is reachable from all three interfaces.** ✅

## 4. Gaps & Decisions

| # | Gap | Decision |
|---|-----|----------|
| 1 | Studio has API but no CLI commands | Intentional: Studio is admin-console-only |
| 2 | Scheduler has API but no CLI commands | Intentional: Scheduler is API-driven (cloud workers) |
| 3 | Calibration has API but no CLI commands | Intentional: Calibration needs UI review forms |
| 4 | Craft has API + CLI but no Console interaction test | ✅ Verified in MHP-054 |
| 5 | No /operator/compact endpoint in Console HTML | Added MHP-066: /operator/compact API endpoint |

## 5. API Route Count

| Prefix | Routes | Test Coverage |
|--------|--------|---------------|
| /health | 1 | ✅ test_api_system |
| /studio-os/status | 1 | ✅ test_api_system (includes storage health) |
| /operator/* | 13 | ✅ test_api_jobs + test_api_contract |
| /studio/* | 10 | ✅ test_api_studio |
| /scheduler/* | 6 | ✅ test_api_scheduler |
| /calibration/* | 6 | ✅ test_api_calibration |
| /craft/* | 1 | ✅ test_console_interaction |
| /openapi.json | 1 | ✅ test_api_system |
| /operator (HTML) | 1 | ✅ test_api_system |
| **Total** | **40** | **All contract-tested** |

---

**Audit Result**: All 4 interfaces aligned. 0 accidental gaps. 40 routes, 8 console views, all contract-tested. System is production-coherent.
