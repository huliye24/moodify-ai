# MSP/0.2 Compare — Layer B Evidence Pack

**Schema:** `moodify.sound/0.2`（compare 作业）+ `moodify.msp_report/0.2`（EXPERIMENTAL — freeze gate: 本证据包 + 确定性重放证明）
**Generated:** 2026-10-02，core `1.0.0-rc.1`，branch `codex/professional-finishing-layer-20260920`
**证明目标（设计提案 §6 Layer B）：** 响度对齐 A/B 黄金 case + `judgment_boundary.layer2_comparison = EXECUTED`

## Contents

| Path | What it is |
|---|---|
| `jobs/*.json` | 两个 compare 作业原文（路径相对 job 文件解析） |
| `cases/<case_ref>/`、`cases/<case_cand>/` | 每次 compare 产生的两个独立 1.0 case bundle（报告的构建输入） |
| `cases/compare_*/report.{json,md,html}` | compare 报告三件套（L2 对比层 + contact-sheet） |
| `cases/compare_*/delta_spectrum_{linear,log}.png` | Δ 频谱图（响度对齐后，数值 STFT 差值渲染） |
| `clipped.wav` | 候选 B 音频本体（**未入库**：`*.wav` 被 gitignore；sha256 `cfa6b727…e0f3a41`，与 msp02_analysis_001 负对照同源同 hash） |

`cases/*/scan/` 的 npz/PNG 为可再生产物，未入库；小型指针/摘要 JSON 已入库。重跑 job 即复原。

## Pairs

| compare dir | Reference | Candidate | 响度对齐 | 关键 delta | 判断 |
|---|---|---|---|---|---|
| `compare_5778e539a783_9e58d8f2a4b8` | `demo/input/example.mp3`（golden 参考） | Mix Graph v0.1 golden 渲染输出（同源 clean_master 图） | +0.25 dB（有效） | LUFS −0.25 · true peak −0.25 · crest +0.08 · clipping 0→0 · 全部变化微小 | NO_TECHNICAL_BLOCKERS，无发现，无草案节点 |
| `compare_2f2f6900e718_9752b39842c0` | `demo/input/example.mp3` | `clipped.wav`（+12 dB 削波负对照） | −10.08 dB（有效） | LUFS +10.08 · true peak +4.55（→+2.72 dBFS 越界）· **crest 12.37→4.74（Δ−7.63，动态坍塌）** · clipping 0→1,113,410 | REMEDIATION_REQUIRED；BLOCKING CLIPPING_PRESENT + limiter 草案节点（削波仍只出 note） |

两对报告的边界均为 **L1 EXECUTED · L2 EXECUTED · L3–L5 NOT_PROMISED**。

## Determinism proof

两个 compare 目录在生成后执行 `moodify report <compare>/report.json` 二次渲染：report.md 与 report.html 逐字节一致（sha256 前后相等，2026-10-02 本机验证；重渲染经由 write_report_bundle → write_compare_bundle 路由，覆盖三根图像装载）。

## Reproduce

```bash
cd moodify-core-package
# 负对照音频本体（*.wav 不入库；与 msp02_analysis_001 的负对照同 hash）：
ffmpeg -y -i demo/input/example.mp3 -af "volume=12dB" -ar 48000 -ac 2 \
  artifacts/msp02_compare_001/clipped.wav
for j in job_pair_finishing_ab job_pair_clipped; do
  PYTHONPATH=src python -m moodify.release_cli protocol process ../artifacts/msp02_compare_001/jobs/$j.json
done
```

Same core version + same profile + same sources → 相同报告内容（`generated_at` 与 case 随机 ID 除外；delta 数值、渲染、case 输入全量确定性）。Pair A 的归一化增益 +0.25 dB 与 `artifacts/mix_graph_v01/golden/README.md` 记录的 −0.25 LU 响度差自洽，构成跨证据包交叉印证。

## Fact boundary

- 本包证明：**L2 相对测量链路**（配对校验 → 响度对齐 → delta → Δ 频谱图 → 渲染）的确定性与 fail-closed 行为；**不证明**任何 delta 是「更好」或「更差」——显著性阈值属 Layer C 校准，报告内 `visibility_note` 明示。
- 削波负对照验证的是「绝对发现 + 相对 delta」在同一报告中的协同呈现（BLOCKING 发现照常来自候选自身指标，参考不改变 plan/finding），**不是**修复效果证据。
- `compared_review_required` 不得当作 `verified`；L3–L5 判断仍不承诺。
- Pair B 的 CLIPPING 证据链：候选 case bundle 的 `clipping_sample_count`（L1 绝对规则）+ 对比层 `clipping_sample_count 0→1,113,410`（L2 相对描述），两处独立成立。
