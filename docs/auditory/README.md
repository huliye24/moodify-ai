# Moodify Auditory Scan Runtime（DSK-MFY-AUDITORY-SCAN-001）

Moodify 是听觉智能系统。本组件是它的感官捕获层：扫描、测量、比较、验证和
技术判断。**它不修改声音**——外部应用（如 Audacity）负责改变声音，Moodify
负责观察与裁决。

## 1. 两张频谱图各显示什么

- `spectrum_linear.png`：线性频率轴，直观展示频段能量随时间的分布，适合看
  低频与整体形状。
- `spectrum_log.png`：对数频率轴，与人耳感知更接近，高频细节（空气感、
  齿音、泛音）更可读。

## 2. 为什么需要两种频率视图

线性视图会压缩高频细节（20Hz-24kHz 中高频只占很小一段）；对数视图放大
高频但会压缩低频。听感判断通常需要对数视图，工程诊断常用线性视图。两张都
要，是因为单一视图会掩盖另一类问题。

## 3. 为什么图像本身不能证明"变好"

频谱图亮 ≠ 更好。响度提升会让所有频段都变亮；更亮可能是削波、更糊或更刺。
本组件用**数值测量**（STFT 数据）比较，图像只作为人工复核证据。

## 4. 为什么响度归一化是频谱比较的前提

一个更响的候选会让大多数频段看起来更亮——这是响度差，不是音色改善。
`compute_deltas` 同时产出：

- 原始 delta（after - before）
- 响度归一化 delta（把 after 调整到 before 的 integrated LUFS 后重算频段比例）

纯响度变化 → 原始 delta 大、归一化 delta 接近零；真实音色变化 → 归一化
delta 在对应频段显著。

## 5. 处理计划如何定义"预期改善"

`processing_plan.json` 的 `technical_goals` 声明每个目标的指标、方向、最小
有意义变化；`guardrails` 声明不可违反的约束（如不新增削波）。对比结果只有在
计划存在时才判定"达到目标"；**没有计划的对比只能描述变化，不能声称改善**。

## 6. 技术验证与艺术审批的区别

- `technical_assessment`：IMPROVED / NEUTRAL / DEGRADED / UNCERTAIN /
  INVALID_COMPARISON —— 只基于测量。
- `workflow_decision`：PASS_TO_LISTENING / NEEDS_REWORK / REJECT_TECHNICAL /
  INCONCLUSIVE / INVALID。
- 每个报告固定包含 `human_listening_required: true` 和
  `artistic_approval_granted: false`。**技术成功永远不会自动批准作品**。

## 7. 如何运行 before 扫描

```bash
python -m moodify case scan <project_dir> <case_id> \
  --stage before --input <source.wav>
```

## 8. 如何注册 Audacity 候选

```bash
python -m moodify case candidate register <project_dir> <case_id> \
  --candidate-id CANDIDATE-001 --input <candidate.wav> \
  --application Audacity --method EXTERNAL_GUI_PROCESSING
```

（不要求 Audacity CLI、不要求 mod-script-pipe、不自动化 Audacity。）

## 9. 如何运行 after 扫描

```bash
python -m moodify case scan <project_dir> <case_id> \
  --stage after --input <candidate.wav> --candidate-id CANDIDATE-001
```

## 10. 如何比较

```bash
python -m moodify case compare <project_dir> <case_id> \
  --candidate-id CANDIDATE-001 --plan <processing_plan.json>
```

## 11. 如何解读风险标志

`risk_flags` 全部是技术观察（NEW_CLIPPING、TRUE_PEAK_MARGIN_REDUCED、
EXCESSIVE_LOUDNESS_INCREASE、STEREO_PHASE_RISK_INCREASED 等），阈值版本化
记录在 `05_comparison/judgment_rules.json`。BLOCKING 级直接
REJECT_TECHNICAL；WARNING 级只提示人工注意。信号指标**不能**推导出
"好听/有情感/有音乐性"。

## 12. 如何检查证据

- 每个扫描目录的 `scan_manifest.json` 记录全部产物哈希；
- `05_comparison/comparison_manifest.json` 记录对比产物哈希；
- `manifests.verify_manifest_hashes()` 可复核；哈希不一致 → 失败关闭。

## 13. 已知限制

- LUFS 为自研 BS.1770 实现（48kHz K-weighting 系数），与商业仪表可能差
  0.1-0.3 LU；
- true peak 为 4x 过采样近似，非完全 inter-sample 精确；
- delta 频谱图为降采样视图（256 log/线性 bins），用于人工复核而非计量；
- 仅支持 Windows + ffmpeg/ffprobe 8.x（PATH 或 WinGet 安装）；
- 无 plan 时只产出 UNCERTAIN/INCONCLUSIVE（保守设计）；
- 立体声指标对 mono 输入置 null，不虚构。

## 架构位置

```
Moodify 分析 → Processing Plan → 外部处理（Audacity）→ 候选注册
  → After 扫描 → 对比 → 技术判断 → 人工听音与艺术审批
```

本组件不是"AI 音乐后处理工具"的附属品，而是 Moodify 听觉观察与验证
基础设施的一部分。
