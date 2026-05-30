# MHP-007-A：Moodify Inspector 可视化对比工具 — 设计规格

> 日期：2026-05-30
> 来源：ChatGPT
> 定位：本地辅助分析脚本，不是 GUI
> 比喻：v01_pipeline = 手，v01_inspector = 眼睛

---

## 核心设计

```bash
python scripts/v01_inspector.py \
  --before original.wav \
  --after processed.wav \
  --output-dir inspector_reports/demo
```

输出 7 个文件：report.md + metrics_comparison.json + 5 张 PNG 图。

## 指标

基础信息 + 动态指标（peak/rms/crest/dynamic_range）+ 空间指标（correlation/mid_side_ratio）+ 频谱指标（6 bands + centroid/rolloff/flatness）

## 图像

waveform_before_after / spectrum_overlay / spectrum_delta / spectrogram_before / spectrogram_after / band_energy_comparison

## 约束

不新增依赖、不做 GUI、不做实时播放、不修改 src/moodify/

## 验收

7 个输出文件 + JSON 含 before/after/delta + report.md 含 checklist + 104 tests green
