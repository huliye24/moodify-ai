# ThinkPad PROCESS Pipeline Verification — Real Entry Points

**Task:** MOODIFY_THINKPAD_HEAVY_LANE_001 (Phase D)
**Date:** 2026-10-05
**Branch:** `feat/thinkpad-heavy-lane-001`
**Principle:** 只走真实产品入口（README / 桌面壳实际调用的 CLI 命令），
不创建旁路脚本；每个阶段的状态如实标注 IMPLEMENTED / PARTIAL / NOT_IMPLEMENTED。

---

## Test material

`local_audio_assets/inputs/`（ignored 目录，不入 Git）：

```text
test_A_10s.wav    10s   stereo 44.1k  合成测试信号（5 层正弦 + pink noise + tremolo/apulsator）
test_B_60s.wav    60s   同上
test_C_180s.wav   180s  同上
```

另备仓库自带真实素材 `moodify-core-package/tests/baseline/test_audio/{piano,electronic,vocal_folk}.wav`
（30/40/45s）用于后续基准扩展。

## Stage-by-stage result（2026-10-05 实测）

| # | Stage | 真实入口 | 实测证据 | 状态 |
|---|---|---|---|---|
| 1 | Input / Import | `moodify protocol validate job.json` | `{"status": "valid"}`，1.0s | **IMPLEMENTED** |
| 2 | Analyze | `moodify protocol process <0.2 analyze job>` | case bundle（report.json/md/html + measurements + evidence），10s 输入 9.5s | **IMPLEMENTED** |
| 3 | Diagnose | `report.json:findings[]`（Studio ②问题 严格投影自此） | 仅 2 种规则（CLIPPING_PRESENT / TRUE_PEAK_MARGIN_EXCEEDED）；仓库自述 18 个真实 case 中 17 个为空 | **PARTIAL** |
| 4 | Plan | `report.json:plan` = `DRAFT_PLAN_NOT_EXECUTED`；Mix Graph 预设派生 `finishing new` | 保守草案（可逆标准算子）；任意 AI 方案执行 = TARGET 未实现 | **PARTIAL** |
| 5 | Process | `moodify protocol process <0.1 job>` → `v01_pipeline.process_audio` | WAV + output sha256 + 参数 + `processed_review_required`，10s 输入 2.2s | **IMPLEMENTED** |
| 6 | Verify | `moodify finishing verify --source --output` | before/after 测量 + deltas + invariants（channels/length/finite），`status: "measured"`，2.9s | **PARTIAL** |
| 7 | Output / Export | 0.1 process 产物；`finishing export`（16-bit PCM, -1 dBFS ceiling） | WAV + evidence.json + 报告三件套；sha256 齐备 | **IMPLEMENTED** |

**Verify 为何是 PARTIAL：** 测量级验证真实存在（前后测量、不变量、哈希、Mix Graph 逐节点
before/after），但**感知/质量结论不存在**——Layer 2 只描述 delta 从不评级，Layer 3–5 为
`NOT_PROMISED`；`review_required: true` 明确要求人工听审。这不是缺陷，是 Canon
（Generated is not finished）的如实状态。

**Plan 为何是 PARTIAL：** `plan.status` 恒为 `DRAFT_PLAN_NOT_EXECUTED`，且只起草保守可逆
算子；执行必须显式另发 process/finishing 作业（绝不自动执行）。「任意 AI 方案的完整执行」
（TASK 002B/002C）在仓库里标为 TARGET — 未实现。

## 实测命令序列（可复现）

```powershell
# 1. validate（0.1）
moodify protocol validate local_audio_assets/job_process_A.json
# 2. analyze（0.2，产物：报告三件套 case bundle）
moodify protocol process  local_audio_assets/job_analyze_A.json
# 3. process（0.1，产物：wav + 哈希 + 诊断 + processed_review_required）
moodify protocol process  local_audio_assets/job_process_A.json
# 4. verify（前后测量证据）
moodify finishing verify --source local_audio_assets/inputs/test_A_10s.wav `
                         --output local_audio_assets/outputs/process_A/test_A_10s_clean_master.wav
# 5. Mix Graph 路径（Plan 执行层的现有真实能力，EXPERIMENTAL）
moodify finishing new    --preset clean_master --source <wav> --out graph.json
moodify finishing render graph.json --output-dir <dir>    # 逐节点 before/after + evidence.json

# 所有 python 子进程带 PYTHONUTF8=1（zh-CN Windows GBK 陷阱，仓库既有约定）
```

## Observed — 两个诊断面（仅记录，不处置）

0.1 `process` 的 JSON 结果内嵌 **v01_pipeline 诊断块**（`issues` / `strengths` /
`suggested_presets`，面向上行 5 段频谱启发式），而 Studio ②问题 严格投影自 **0.2
`report.json:findings`**（2 条规则）。两者是并存的诊断面。仓库已把「诊断权威统一」
标记为 `HUMAN_DECISION_REQUIRED`（不得由 agent 自行接入第二诊断权威）。
本报告只记录事实，不做任何统一动作。

## Not fabricated（明确未演示）

```text
感知级自动验证（"是否更好听"）        NOT_DEMONSTRATED — Layer 3–5 NOT_PROMISED
任意 AI 方案的完整执行（002B/002C）   NOT_IMPLEMENTED — TARGET
精细分离引擎                          NOT_IMPLEMENTED — TARGET
```
