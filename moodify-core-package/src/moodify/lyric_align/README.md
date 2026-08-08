# Lyric Temporal Alignment（歌词时间对齐）

任务：DSK-MFY-LYRIC-TEMPORAL-ALIGNMENT-001（Phase A-F）
边界：MSE（见 `docs/architecture/MSE_ARCHITECTURE.md`）
日期：2026-08-08

## 定位

用户上传最终音频并粘贴正确歌词 → 自动生成同步滚动歌词与词级时间轴，无需手动打点。
**最终音频是时间权威；歌词文本是文字与顺序权威**。MusicXML/MIDI 仅作可选先验（未实现）。

## 用法

```bash
# case 命令（PPE 生命周期内）
python -m moodify case lyrics-align <project_dir> <case_id> \
    --audio <song> --lyrics <lyrics.txt> --language fr [--backend heuristic|whisperx]

# API（Phase F）
POST /api/v1/lyric-alignments   # 详见 docs/api/LYRIC_ALIGN_API.md

# 直接调用
python - <<'EOF'
from moodify.lyric_align.pipeline import run_alignment
run_alignment("song.wav", "lyrics.txt", "out", "fr", "heuristic")
EOF
```

## 产物（`<case_root>/05_lyric_align/`）

- `alignment.json` / `qc_report.json` / `manifest.json`
- `lyrics.lrc` / `lyrics.enhanced.lrc` / `lyrics_bilingual.lrc` / `lyrics.srt` / `lyrics.ass`
- `evidence/`：归一化音频、活跃区间、backend_raw、demucs 人声干（可选）

## Hash 绑定（manifest.json）

`audio_sha256` / `lyrics_sha256` / `translation_sha256`（可选）/ `score_sha256` / `midi_sha256`（Phase C 未实现恒 null）/ `backend_sha256` / `backend_raw_sha256` / `config_sha256` / `alignment_sha256`（canonical JSON）。

## 质量门（QualityGate，`configs/default.json` 为唯一阈值来源）

PUBLISHABLE 仅当：非 heuristic、无时间倒置、无行重叠超容差、覆盖率 ≥ 0.92、未对齐 token 比 ≤ 0.05、词均值置信度 ≥ 0.72、行最小置信度 ≥ 0.55、确定性双跑中位边界差 ≤ 80ms。阈值暂行，待验证集校准。

## 已知局限（禁止据此宣称生产就绪）

- **Phase B 失败分类未实现**：melisma/垫音/即兴/器乐间隙/弱音素/行边界漂移的自动分类需要标注数据集；当前仅质量门能暴露低置信行与边界漂移。
- **Phase C 乐谱先验未实现**（规格标注 Optional）：MusicXML/MIDI 适配器与时间扭曲；API 入参返回 NOT_IMPLEMENTED。
- **Phase E 验证集待采集**：10 类曲目清单已建（`verification_set.json`），人工锚点与音频资产未收集，阈值未校准。
- **WhisperX 后端**：需服务端 `pip install -e 'moodify[ml]'`（whisperx>=3.3,<4 + demucs>=4,<5）；未安装时抛出可操作错误。
- **双跑 delta**：whisperx 后端会执行两次对齐以计算确定性指标（成本约 ×2）。
- ffmpeg/ffprobe 需可用（Windows 下自动探测 winget/Program Files 安装）。
