# Moodify

AI 音乐二次处理与情绪声波工程系统。

## Status

- **Version**: v0.1.0-alpha.1
- **Mainline**: v01
- **CLI**: `analyze` / `process` 默认走 v01 主线
- **API**: `/process` 走 `v01_pipeline`
- **Tests**: 20 v01 tests, 104 total tests, all green

## What Moodify Does

```text
导入音频 → 频谱分析 → 诊断报告 → DSP 预设处理 → 导出优化 WAV
```

## Install

```bash
cd moodify-core-package
pip install -e .
```

Requires Python 3.10+.

## CLI Quickstart

```bash
# List presets
moodify presets

# Spectrum analysis
moodify analyze song.wav
# → outputs/song_spectrum.png

# Process with a preset
moodify process song.wav --preset warm_vocal
# → outputs/song_warm_vocal.wav
# → outputs/song_warm_vocal_report.json
```

## API Quickstart

```bash
# Start server
moodify serve
# → http://localhost:8000/docs

# Health check
curl http://localhost:8000/health
# → {"status":"ok","version":"0.1.0","mode":"v01","mainline":"v01_pipeline"}

# List presets
curl http://localhost:8000/presets

# Process audio
curl -X POST http://localhost:8000/process \
  -F "audio=@song.wav" \
  -F "preset=warm_vocal" \
  -o processed.wav
```

## Presets

| Preset | Name | Description |
|--------|------|-------------|
| `warm_vocal` | 温暖人声 | 增强人声温度、厚度和亲密感 |
| `clean_master` | 干净母带 | 透明母带处理，清理频谱，增强稳定性 |
| `wide_space` | 宽阔空间 | 增强空间感和听觉宽度 |

每个 preset = 15 个 pedalboard DSP 参数（EQ / 压缩 / 混响 / 谐波 / 高频搁架）。

## Outputs

```text
outputs/
├── song_spectrum.png          # 频谱图
├── song_warm_vocal.wav        # 处理后的音频
└── song_warm_vocal_report.json # 诊断报告
```

## Tests

```bash
# v0.1.0 mainline only
pytest -m v01
# → 20 passed

# Full test suite
pytest
# → 104 passed
```

## Architecture

### v01 mainline (6 files)

```text
v01_types.py          — AudioMetrics / DiagnosisReport / ProcessResult
v01_presets.py        — 3 presets × 15 DSP params
v01_analyzer.py       — FFT spectrum → AudioMetrics + PNG
v01_diagnostics.py    — rule-based DiagnosisReport
v01_exporter.py       — 16-bit WAV + peak clamp
v01_pipeline.py       — import → analyze → diagnose → process → export
```

### Legacy (preserved, not wired to v0.1.0)

```text
diagnosis/       — 18-param DiagnosisEngine + defect classifier + health scorer
orchestration/   — 6-phase WorkflowOrchestrator (938 lines)
knowledge/       — 8 emotion × 15 param craft chains
processing/      — pedalboard DSP chain + spectral chain + operators

CLI access:
  moodify legacy-analyze <file>
  moodify legacy-process <file> <emotion>
```

### Experimental (preserved, not wired to v0.1.0)

```text
evaluation/    — batch AI evaluation + judges
calibration/   — online D-value calibration
physics/       — B-matrix experiments
llm/           — DeepSeek client + RAG prompts
optimizer/     — 5D strength space search
safety/        — parameter projection + bounds
memory/        — SQLite + JSONL history
```

## Development Rules

- 不要删除旧系统（diagnosis / orchestration / knowledge / physics / calibration / llm / optimizer / safety / memory）
- 不要把 `WorkflowOrchestrator` 接回 v0.1.0 `/process`
- 不要修改 v01 API 契约（3 个 preset，不是 8 个 emotion）
- 不要在 v0.1.0 阶段做 GUI
- `pytest` 始终跑全量，`pytest -m v01` 用于快速检查主线

## Links

- Repository: https://github.com/huliye24/moodify-o3is
- Latest tag: `v0.1.0-alpha.1`
- Project snapshot: `docs/PROJECT_SNAPSHOT_v0.1.0-alpha.1.md`

## License

Proprietary — 文川院 / Moodify 声音实验室 · 影焰实验室
