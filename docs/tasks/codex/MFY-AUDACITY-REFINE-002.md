# 给 Codex 的执行命令：Audacity 音色精修（超越 V2）

**案例：** 《Vieillir et devenir nouveau avec toi》
**来源：** `E:\moodify\pre-music\Vieillir et devenir nouveau avec toi\Vieillir et devenir nouveau avec toi.wav`
**基底：** 建议用 `V2_Gentle_Master.wav` 或直接原始 WAV（二选一，见 §3）
**输出：** `E:\moodify\pre-music\Vieillir et devenir nouveau avec toi\moodify_delivery_v3\final\`
**执行者：** Codex（在 Audacity GUI 中手动执行，不要求自动化）

---

## 0. 背景（来自 Moodify 听觉审计）

- V1（Audacity gentle）：响度 +1dB，响度归一化后全部频段变化 <1dB —— **等于没处理**；
- V2（Moodify 整轨 EQ）：presence +3.0dB、air +2.1dB、low_mid -0.7dB —— **第一次真实音色变化**，但响度 -15 偏柔和、曲线是固定模板；
- V3（Deep Ear）：分析/检测能力升级了，但最终处理决策只有 DC 修复、首尾淡化、响度校准 —— **没有形成新的音色工艺**，结果与 V2 Audacity 版几乎相同（PCM 差 -60dB，频谱像素差 mean <1/255）。

**结论：精修的价值不在"分析得更深"，而在"执行不同的工艺假设"。**
Audacity 的定位是**干预实验室执行器**：Moodify 负责决策与验证，你负责用 Audacity 的曲线 EQ 把工艺做出来。

---

## 1. 工艺假设（本次要验证的）

> 这首歌是抒情慢歌，人声是核心。目标终混：**人声清晰靠前、伴奏有空气感、低频稳而不糊、动态保持自然**。

具体目标（Moodify 可测）：

| 指标 | 目标 | 依据 |
|---|---|---|
| presence 2-5k 归一化 delta | **≥ +0.02**（与 V2 的 +0.0416 同级或更高） | 人声清晰度 |
| low_mid 120-250 归一化 delta | **≤ -0.01**（负向，去糊） | V2 已证有效 |
| crest factor | 保持 ≥ 12 dB（不重压缩） | 抒情慢歌动态是特色 |
| 响度 | **-14 LUFS**（streaming 标准；V1 -13.2 偏响、V2 -15 偏柔） | 行业实践 |
| true peak | **≤ -1.0 dBTP** | 安全 |
| 无新增削波 | clipping count = 0 | 硬门禁 |

## 2. Audacity 操作链（按顺序执行）

在 Audacity 中打开源音频（建议先 `效果 → 均衡 → Filter Curve EQ`，全程用**曲线绘制**而非固定预设）。

### 步骤 1｜中低频去糊（与 V2 同向，更精细）
- `Filter Curve EQ`，在 **220Hz** 处降 **-2.0 dB**，Q 宽（±1.5 oct），平滑曲线；
- 400Hz 处 **-1.0 dB** 过渡；
- **不要动 80Hz 以下**（低频是这首歌的基底，V2 验证过 sub 保持）。

### 步骤 2｜人声存在感（核心工艺，与 V2 差异化）
- **3.2kHz**：+1.5 dB；
- **5kHz**：+2.0 dB（presence 峰）；
- **7kHz**：+0.5 dB（平滑回落）；
- 曲线从 2.5k 到 7k 呈"山丘"，不要做成陡峭峰（避免齿音/刺耳）。

### 步骤 3｜空气感
- **11kHz** 起 High-Shelf：**+1.5 dB**，斜率高（平滑）；
- 听感检查：不应出现"嘶嘶"或"玻璃碎"感；若有，降到 +1.0 dB。

### 步骤 4｜动态（保持自然）
- **不压缩**。若 -14 LUFS 目标下峰值超 -1 dBTP，用 `效果 → 限制器`（Limiter）：
  - 阈值 **-1 dB**、release 100ms、仅抓峰值瞬态；
  - 若 Limiter 触发超过 2dB 的衰减，说明 EQ 增益过大，回退 EQ 而不是压动态。

### 步骤 5｜响度与安全
- `效果 → 响度归一化`（Loudness Normalization）：目标 **-14 LUFS**（选 LUFS 模式）；
- 最后 `效果 → 标准化` 峰值 **-1.0 dB**（若响度归一化后峰值已低于 -1 则跳过）；
- 导出：**48kHz / 24bit WAV**（`文件 → 导出音频`，格式 WAV，编码 Signed 24-bit PCM）。

## 3. 基底选择

- **方案 A（推荐）：以原始 WAV 为基底** —— 全程在 Audacity 完成，结果与 V2 完全独立，可直接对比"V2 固定 EQ vs Audacity 曲线精修"哪个更好；
- 方案 B：以 V2_Gentle_Master 为基底 —— 在已有 presence 提升上叠加，省一步 EQ，但会继承 V2 的 -15 响度。

**选 A。** 独立性对"工艺对比"更有价值。

## 4. 验证门禁（必须全部通过才能称为交付）

**用 Moodify 听觉系统验证（不是人耳"感觉一下"）：**

```bash
python -m moodify.learning.run_real_song  # 已有 before scan；替换候选路径
```

或手动跑对比：

```bash
# 1) 注册干预 + after 扫描 + 对比（候选路径改为你的输出）
python -m moodify.learning.run_v2_v3_compare   # 参考脚本，加入 V4 候选
```

**门禁清单：**

1. `comparison_report.json` 中：
   - presence_2000_5000_hz 归一化 delta **≥ +0.02**；
   - low_mid_120_250_hz 归一化 delta **≤ -0.01**；
   - crest_factor_db delta **≥ -3.0**（动态未损伤）；
   - 无 `NEW_CLIPPING` / `STEREO_PHASE_RISK_INCREASED` 风险标志；
2. 响度 -14 ±0.5 LUFS，true peak ≤ -1.0 dBTP；
3. **technical_assessment = IMPROVED 或 NEUTRAL 且无 BLOCKING 风险**；
4. 人工听感：与 V2 盲听对比，人声清晰度、低频干净度、整体开阔感至少有一项可辨提升；
5. 与 V2 的差异**必须大于 V3 与 V2 的差异**（即不能又精修回同一个声音——PCM 差异应明显大于 -60dB dither 级）。

## 5. 交付物

```text
moodify_delivery_v3/final/
├── ..._V4_Audacity_Curve_Final.wav        # 24bit 48k
├── ..._V4_Listening_320k.mp3              # 试听
├── audacity_operations.json               # 你实际执行的步骤/参数（供干预记录）
└── v4_matched_comparison.txt              # Moodify 响度归一化对比摘要
```

并注册到学习循环：

```bash
python -m moodify case intervention register ...  --candidate-id CANDIDATE-V4 \
  --application Audacity --method EXTERNAL_GUI_PROCESSING --file intervention.json
```

## 6. 禁止

- ❌ 不压缩动态来"听起来更响"（crest < 10 视为失败）；
- ❌ 不把响度推到 -10 以下（V3 的 Deep Ear 教训）；
- ❌ 不做"全频段等量提升"（那是 V1 的错，等于没做）；
- ❌ 不以"听感不错"代替门禁验证（必须跑 Moodify 对比）；
- ❌ 不覆盖原始 WAV 或任何既有候选。

---

**执行完成后，把 `audacity_operations.json` 和验证输出交给 Claude A，由 Moodify 完成 V4 候选注册、学习记录与人工听感评估。**
