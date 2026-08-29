# DSK-MFY-AUDITORY-SCAN-001 — Golden Case 复现脚本

用仓库合成资产跑完整证据循环（不依赖任何版权音乐）。

## 1. 生成合成源与候选

```bash
python -m pytest tests/auditory/test_golden.py -q
```

或手动：

```bash
python - <<'EOF'
import numpy as np, soundfile as sf
from pathlib import Path

out = Path("outputs/auditory_golden")
out.mkdir(parents=True, exist_ok=True)
sr = 48000
t = np.arange(sr * 12) / sr
# 类音乐信号：低频基底 + 中频 + 高频空气 + 少量噪声
src = (0.25 * np.sin(2*np.pi*55*t) + 0.2 * np.sin(2*np.pi*220*t)
       + 0.15 * np.sin(2*np.pi*880*t) + 0.05 * np.sin(2*np.pi*6000*t)
       + 0.01 * np.random.default_rng(7).standard_normal(len(t)))
src = np.stack([src, src * 0.98], axis=1).astype(np.float32)
# 候选 = 源 + 人声区 presence 提升（模拟外部精修）
cand = src + 0.08 * np.sin(2*np.pi*4000*t)[:, None]
sf.write(out / "golden_source.wav", src, sr)
sf.write(out / "golden_candidate.wav", np.clip(cand, -1, 1).astype(np.float32), sr)
EOF
```

## 2. 完整 CLI 证据循环

```bash
python -m moodify project init outputs/auditory_golden/proj --title golden
python -m moodify asset import outputs/auditory_golden/proj outputs/auditory_golden/golden_source.wav
python -m moodify case create outputs/auditory_golden/proj \
  --spec '{"title":"golden","essence":"synthetic music-like","desired_change":"vocal presence",\
           "must_preserve":[],"must_avoid":[],\
           "preservation_acknowledgement":{"acknowledged":true,"by":"golden","reason":"synthetic"}}' \
  --owner golden --asset-id <ASSET_ID>
python -m moodify case scan outputs/auditory_golden/proj <CASE_ID> \
  --stage before --input outputs/auditory_golden/golden_source.wav
python -m moodify case candidate register outputs/auditory_golden/proj <CASE_ID> \
  --candidate-id GOLDEN-001 --input outputs/auditory_golden/golden_candidate.wav
python -m moodify case scan outputs/auditory_golden/proj <CASE_ID> \
  --stage after --input outputs/auditory_golden/golden_candidate.wav --candidate-id GOLDEN-001
python -m moodify case compare outputs/auditory_golden/proj <CASE_ID> \
  --candidate-id GOLDEN-001 --plan outputs/auditory_golden/plan.json
```

## 3. 预期产物（case 目录）

```
cases/<CASE_ID>/
├── 01_before_scan/    spectrum_linear.png, spectrum_log.png, metrics.json,
│                      timeline_metrics.jsonl, analysis_data.npz, scan_manifest.json
├── 03_processing/candidates/GOLDEN-001.json
├── 04_after_scan/     (同上)
└── 05_comparison/     metrics_delta.json, delta_spectrum_linear.png,
                       delta_spectrum_log.png, comparison_contact_sheet.png,
                       comparison_report.json, judgment_rules.json, comparison_manifest.json
```

## 4. 判定（对照）

- `comparison_report.json` 中 `human_listening_required: true`、`artistic_approval_granted: false`
- plan 有 presence 目标时：`technical_assessment: IMPROVED`、`workflow_decision: PASS_TO_LISTENING`
- 无 plan 时：`UNCERTAIN / INCONCLUSIVE`
