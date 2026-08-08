# Lyric Alignment 验证集（DSK-MFY-LYRIC-TEMPORAL-ALIGNMENT-001, Phase E）

日期：2026-08-08
状态：**清单已建，音频资产与人工锚点待采集**（本机无可用音频资产，采集列为后续独立任务）

## 目的

Publish 门槛阈值（0.92/0.05/0.72/0.55/80ms）是**暂行值**，必须在带人工锚点的标注验证集上校准。禁止以单曲成功推断生产就绪（任务规格 Forbidden claims）。

## 曲目清单（10 类）

| ID | 类别 | 语言 | 要求 |
|---|---|---|---|
| VS-001 | 法语长元音民谣 | fr | 长元音/连音 |
| VS-002 | 法语密集歌词流行 | fr | 高密度歌词 |
| VS-003 | 中文流行 | zh | 字符级对齐 |
| VS-004 | 双语歌曲 | mixed | 行级翻译对应 |
| VS-005 | 主唱+垫音 | mixed | 垫音分离 |
| VS-006 | 重度混响 | mixed | 混响鲁棒性 |
| VS-007 | 失真人声 | mixed | 失真鲁棒性 |
| VS-008 | 安静前奏+长器乐间奏 | mixed | 活动区间检测 |
| VS-009 | 重复副歌 | mixed | 重复行结构 |
| VS-010 | AI 人声伪影 | mixed | 伪影鲁棒性 |

机器清单：`moodify-core-package/src/moodify/lyric_align/verification_set.json`（status=pending，anchors=null）。

## 锚点格式（每曲）

```json
{
  "track_id": "VS-001",
  "line_anchors": [{"line_index": 0, "start_s": 0.0, "end_s": 4.2}],
  "word_anchors": [{"line_index": 0, "word_index": 1, "start_s": 0.8}]
}
```

人工逐行/逐词标注时间锚点，仅用于评估，不进入用户工作流（规格 Phase E 要求）。

## 采集与校准计划（后续任务）

1. 选取 10 首真实歌曲（每类 1 首），存入私有资产库（不入仓库）。
2. 人工标注行/词锚点，双人复核，记录分歧。
3. 运行 heuristic + whisperx 后端，产出边界误差分布（中位数/95 分位）。
4. 按误差分布校准 QualityGate 阈值，更新 `configs/default.json`。
5. 输出校准报告并提交（`docs/verification/lyric_align_calibration_report.md`）。

## 已知局限（Phase B 分类、Phase C 乐谱先验）

- melisma/垫音/即兴/器乐间隙/弱音素/行边界漂移的**自动分类**未实现——需标注数据；当前仅质量门可发现边界漂移与低置信行。
- MusicXML/MIDI 乐谱先验（Phase C，规格标注 Optional）未实现；score_asset_id/midi_asset_id 入参返回 NOT_IMPLEMENTED。
