# 给 Codex 的执行命令：SoX 音色精修（替代 Audacity）

**案例：** 《Vieillir et devenir nouveau avec toi》
**来源：** `E:\moodify\pre-music\Vieillir et devenir nouveau avec toi\Vieillir et devenir nouveau avec toi.wav`
**执行器：** SoX v14.4.2（已安装，确定性命令行工具）
**输出：** `E:\moodify\pre-music\Vieillir et devenir nouveau avec toi\moodify_delivery_v3\final\`

> 背景：Nama（Ecasound 生态，Unix-only）与 Phosphor（合成器 DAW，无音频导入/导出）均不可用。
> SoX 是替代 Audacity 的干预实验室执行器：Moodify 决策与验证，SoX 执行工艺。

---

## 0. 工艺假设（与 Audacity 版一致）

> 抒情慢歌，人声是核心。目标终混：人声清晰靠前、伴奏有空气感、低频稳而不糊、动态自然。

| 指标 | 目标 |
|---|---|
| presence 2-5k 归一化 delta | **≥ +0.02**（与 V2 同级或更高） |
| low_mid 120-250 归一化 delta | **≤ -0.01**（去糊） |
| crest factor | 保持 ≥ 12 dB（不重压缩） |
| 响度 | **-14 LUFS** |
| true peak | **≤ -1.0 dBTP** |
| 无新增削波 | clipping = 0 |

## 1. SoX 命令链（在 Git Bash 或 PowerShell 执行）

```bash
SOX="/c/Users/Administrator/AppData/Local/Microsoft/WinGet/Packages/ChrisBagwell.SoX_Microsoft.Winget.Source_8wekyb3d8bbwe/sox-14.4.2/sox.exe"
SRC="E:/moodify/pre-music/Vieillir et devenir nouveau avec toi/Vieillir et devenir nouveau avec toi.wav"
OUT="E:/moodify/pre-music/Vieillir et devenir nouveau avec toi/moodify_delivery_v3/final"
mkdir -p "$OUT"

# 1) 中低频去糊：220Hz -2dB(Q1.2) + 400Hz -1dB(Q1.0)，80Hz 以下不动
# 2) 人声存在感：3.2k +1.5dB、5k +2dB、7k +0.5dB（山丘曲线）
# 3) 空气感：11k 高频 shelf +1.5dB（用 treble 效果近似）
"$SOX" "$SRC" "$OUT/V4_curve_eq.wav" \
  equalizer 220 1.2 -2 \
  equalizer 400 1.0 -1 \
  equalizer 3200 0.9 1.5 \
  equalizer 5000 1.0 2 \
  equalizer 7000 0.9 0.5 \
  treble 1.5 11000 0.7

# 4) 动态保留：不压缩。若 -14 LUFS 峰值超 -1dBTP，用 compand 只压峰值：
#    "$SOX" ... compand 0.01,0.3 -60,-60,-45,-30,-25,-25,-21,-21,-18,-18,-14,-14,-11,-11,-8,-8,-5,-5,-2,-2  -2 0.2

# 5) 响度与安全：
#    SoX norm 不支持 LUFS；用 gain 迭代 + stat 校准，或先用 loudnorm 思路：
#    - 测量当前 RMS：sox file -n stat
#    - gain = 目标RMS - 当前RMS（-14 LUFS ≈ RMS -15 附近，K加权后校准）
"$SOX" "$OUT/V4_curve_eq.wav" -n stat 2>&1 | grep "RMS.*amplitude"
# 记录 RMS_A，计算增益 G = (-14.0 - K) - RMS_A（K≈-1.0 加权补偿，用试听校准）
# 应用增益 + 峰值保护：
"$SOX" "$OUT/V4_curve_eq.wav" "$OUT/V4_gain.wav" gain G
# 若峰值 > -1dBFS，整体降到 -1dBFS 峰值：
"$SOX" "$OUT/V4_gain.wav" "$OUT/V4_normalized.wav" gain -n -1

# 6) 最终导出 24bit：
"$SOX" "$OUT/V4_normalized.wav" --bits 24 --rate 48000 "$OUT/V4_AudacityFree_Final.wav"
```

**精确响度替代方案（推荐）：** 用 Python 做最终响度（已含 BS.1770 实现）：

```bash
python - <<'EOF'
# 读 V4_curve_eq.wav → 用 moodify.auditory.metrics.integrated_lufs 校准增益 → 写 24bit
EOF
```

## 2. 验证门禁（Moodify 听觉系统，与 Audacity 版相同）

```bash
# 在 run_v2_v3_compare.py 基础上加入 CANDIDATE-V4-SOX，跑 after scan + compare
```

1. presence 归一化 delta **≥ +0.02**；low_mid **≤ -0.01**；crest delta **≥ -3.0**；
2. 无 NEW_CLIPPING / STEREO_PHASE_RISK_INCREASED；
3. 响度 -14 ±0.5 LUFS、true peak ≤ -1.0 dBTP；
4. technical = IMPROVED 或 NEUTRAL 且无 BLOCKING；
5. **与 V2 差异必须大于 V3 与 V2 的差异**（不许精修回同一个声音）。

## 3. 交付物

```text
moodify_delivery_v3/final/
├── V4_AudacityFree_Final.wav       # 24bit 48k
├── V4_Listening_320k.mp3           # ffmpeg 转
├── sox_operations.json             # 实际执行的完整命令链
└── v4_matched_comparison.txt       # Moodify 归一化对比
```

注册学习循环（intervention execution_mode = **SCRIPTED_TOOL**）：

```bash
python -m moodify case intervention register ... --candidate-id CANDIDATE-V4 \
  --application SoX --method SCRIPTED_TOOL --file intervention.json
```

## 4. 禁止

- ❌ 不压缩换响度（crest < 10 = 失败）；不推到 -10 以下；
- ❌ 不做全频段等量提升（=V1 的错）；不以听感代替门禁；不覆盖源文件。
