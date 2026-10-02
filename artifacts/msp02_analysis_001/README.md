# MSP/0.2 Analysis — Layer A Evidence Pack

**Schema:** `moodify.sound/0.2`（analyze 作业）+ `moodify.msp_report/0.2`（EXPERIMENTAL — freeze gate: 本证据包 + 确定性重放证明）
**Generated:** 2026-10-02，core `1.0.0-rc.1`，branch `codex/professional-finishing-layer-20260920`
**Provenance:** scan profile `MFY-WSE-SCAN-PROFILE-001`（params sha256 `f0ff177d…de45f1`），judgment rules v1.0，ffmpeg 8.1.1

## Contents

| Path | What it is |
|---|---|
| `jobs/*.json` | The four 0.2 analyze jobs exactly as executed |
| `cases/<case_id>/report.json` | `moodify.msp_report/0.2` 报告权威（schema 校验通过） |
| `cases/<case_id>/report.md` / `report.html` | 确定性文本渲染 + 单文件显示屏（inline CSS、base64 频谱、无 JS/CDN） |
| `cases/<case_id>/{case,measurements,evidence,judgment_rules,auditory_report}.json` | 底层 1.0 case bundle（报告的构建输入，fail-closed 依赖） |
| `negative_control_clipped.wav` | 负对照音频本体（**未入库**：`*.wav` 被 .gitignore 排除；sha256 见下，可用同命令重生成） |

`cases/*/scan/` 中的 npz（~7 MB/case）与频谱 PNG（~3 MB/case）为可再生产物，未入库；scan 内的小型指针/摘要 JSON（metrics.json、scan_manifest.json、timeline_metrics.jsonl）已入库。重跑 job 即复原未入库部分。

## Cases

| case_id | Source | Duration | Findings | workflow_decision | Draft plan |
|---|---|---|---|---|---|
| `case_10bdb3da…` | `demo/input/example.mp3`（golden 参考） | 174.6 s | 无（51 项测量全 VALID） | NO_TECHNICAL_BLOCKERS | 空 |
| `case_06375100…` | `artifacts/mix_graph_v01/golden/example_mixgraph_8eec7960.wav`（Mix Graph v0.1 golden 渲染输出） | 174.6 s | 无（51 项全 VALID） | NO_TECHNICAL_BLOCKERS | 空 |
| `case_5fe1d78c…` | `07Music/albums/Control Theory.mp3`（真实成品曲） | 204.6 s | 无（51 项全 VALID） | NO_TECHNICAL_BLOCKERS | 空 |
| `case_9ff518d2…` | `negative_control_clipped.wav`（example.mp3 +12 dB 增益，故意削波） | 174.6 s | CLIPPING_PRESENT（BLOCKING，1,113,410 samples）+ TRUE_PEAK_MARGIN_EXCEEDED（WARNING，+2.72 dBFS） | REMEDIATION_REQUIRED | limiter 草案节点（ceiling −1.0 dBFS，reversible）；削波只出 note 不出节点 |

## Determinism proof

四个 case 在生成后均执行 `moodify report <report.json>` 二次渲染：report.md 与 report.html 逐字节一致（sha256 前后相等，2026-10-02 本机验证）。

## Reproduce

```bash
cd moodify-core-package
for j in job_example_mp3 job_mixgraph_golden job_control_theory job_negative_control; do
  PYTHONPATH=src python -m moodify.release_cli protocol process ../artifacts/msp02_analysis_001/jobs/$j.json
done
# 负对照音频本体（*.wav 不入库）：
ffmpeg -y -i demo/input/example.mp3 -af "volume=12dB" -ar 48000 -ac 2 \
  artifacts/msp02_analysis_001/negative_control_clipped.wav
```

Same core version + same profile + same source → same report.json contents（`generated_at` 时间戳除外；md/html 渲染与 case 输入全量确定性）。

## Fact boundary

- 本包只证明 **L1 技术测量** 与协议/报告/渲染链路本身的确定性；不证明听感质量、身份保留或商业就绪。
- 负对照验证的是「绝对规则 → 发现 → 保守草案计划」的映射行为（limiter 只映射 true-peak 余量问题；削波按设计不可自动修复），**不是** limiter 实际修复效果的证据。
- 三个干净 case 的 `PARTIAL` overall 状态来自 1.0 听觉报告中 `musical_structure` 分区状态为 UNKNOWN（结构分析不在本链路能力内，见能力表 ABSENT 行），**不是**测量失败；四 case 的 51 项测量均为 VALID。
- `analyzed_review_required` 不得当作 `verified`；`plan.status` 恒为 `DRAFT_PLAN_NOT_EXECUTED`。
