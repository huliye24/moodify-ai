# Moodify 核心引擎 — 完整产品意图

## 一句话

**把 AI 生成的原始音乐当作"波场"，进行二次编译/情绪显影，产出听感更好的成品音乐。**

---

## 1. 产品定位

Moodify 是一个 **AI 音乐后期处理引擎**。它不做音乐生成，而是做音乐的"暗房显影"——接收 AI（Suno/Udio）生成的原始音频，诊断其五维波场状态，自动匹配情绪工艺卡，经过 DSP 处理链，输出情绪表达更准确、听感更专业的成品音频。

类比：AI 音乐生成 = 胶片相机拍出底片，Moodify = 暗房把底片显影成照片。

---

## 2. 核心工作流（六阶段流水线）

```
输入: AI原始音频 (.wav/.mp3) + 目标情绪
  │
  ▼
Phase 1: 诊断 — 提取18参数WaveState + 缺陷分类 + 健康分 + 工艺卡匹配
  │
  ▼
Phase 2: 源分离 — Demucs将音频分离为人声/鼓/贝斯/其他 stem
  │
  ▼
Phase 3: 分层增强 — 对每个stem应用EQ/压缩/谐波/混响（基于工艺卡参数）
  │
  ▼
Phase 4: 空间重构 — M/S处理 + 立体声宽度 + 深度重建
  │
  ▼
Phase 5: 再合成 — Stem混合 + 增益平衡 + 交叉淡化
  │
  ▼
Phase 6: 情绪显影+母带 — 平台自适应响度 + 限幅 + 最终质检
  │
  ▼
输出: 成品音频 + 体检报告(前后对比) + EDSR情绪显影成功率
```

---

## 3. 五维波场模型（理论基础）

AI音乐的"波场"包含五个维度：

| 维度 | 参数 | 含义 |
|------|------|------|
| Spectrum 频谱 | S1-S5 (SubPresence, BassWarmth, MidClarity, AirBand, SpectralTilt) | 频率能量分布 |
| Dynamics 动态 | D1-D4 (LRA, ChorusImpact, MicroDynamics, PLR) | 响度起伏与冲击力 |
| Space 空间 | SP1-SP4 (Correlation, ForeBackSep, RT60Consist, WidthHealth) | 立体声场与深度 |
| Layers 层级 | L1-L4 (VocalSNR, BassClarity, DrumDetect, LayerCount) | 声部清晰度与分离度 |
| Emotion 情绪 | E1-E4 (Direction, Richness, FatigueRisk, SectionCont) | 情绪表达质量 |

---

## 4. 八种标准情绪工艺

每种情绪对应一组完整的DSP参数链（15参数 × min/rec/max + 风险警告 + 禁忌症）：

| 代码 | 情绪 | 核心DSP特征 |
|------|------|-------------|
| GA | 温柔觉醒 | 温暖人声+2.5dB低频+轻压缩(2:1)+短混响(1.2s)+柔和高频 |
| SE | 神圣空灵 | 轻盈人声+克制低频+极轻压缩(1.5:1)+宏大混响(3.5s)+开放高频 |
| UD | 都市危险 | 紧张人声+压迫低频+重度压缩(5:1)+工业谐波+紧致空间 |
| LW | 孤独留白 | 内省人声+中性低频+保留动态+深远混响(2.0s)+暗调高频 |
| HL | 治愈温暖 | 温暖人声+饱满低频+柔和压缩+温暖谐波+柔光高频 |
| DR | 黑暗浪漫 | 性感人声+深沉低频+中等压缩(3:1)+暗色谐波+深邃混响(1.8s) |
| WL | 废土机械 | 锋利人声+冲击低频+极限压缩(6:1)+重度失真+极干空间 |
| CN | 电影感 | 叙事人声+宽广低频+保留动态+史诗混响(2.5s)+影院高频 |

---

## 5. 当前已完成（A-C-D轨道）

以下模块**已经存在且可用**，不要重写：

- **A: 诊断引擎** (`src/moodify/diagnosis/engine.py`) — 完整18参数提取，FFT-based，支持quick/full模式
- **A: 数据模型** (`src/moodify/data_types.py`) — WaveState, WaveStateDiagnosis, CraftCardV2等完整数据结构
- **A: 缺陷分类器** (`src/moodify/diagnosis/defect_classifier.py`) — 自动检测HRI过高、动态压平、人声缺失等缺陷
- **A: 健康评分器** (`src/moodify/diagnosis/health_scorer.py`) — WHS(0-100) + EDS计算
- **A: 质量门禁** (`src/moodify/diagnosis/quality_gate.py`) — 三质量门Gate1/2/3
- **C: 工艺链知识库** (`src/moodify/knowledge/craft_chains.py`) — 8情绪×15参数的完整数据集
- **C: 工艺卡匹配器** (`src/moodify/knowledge/craft_chain_match.py`) — 基于缺陷自动匹配最佳工艺卡
- **C: 情绪目标库** (`src/moodify/knowledge/emotion_targets.py`) — 情绪名称解析+目标映射
- **C: 风险模型** (`src/moodify/knowledge/risk_model.py`) — 处理风险量化评估
- **D: 工作流引擎** (`src/moodify/orchestration/workflow_engine.py`) — 六阶段编排框架(Phase1完成,Phase2-6为桩)
- **D: 状态转移引擎** (`src/moodify/orchestration/state_transfer.py`) — WaveState转换+Δ计算
- **D: FastAPI服务** (`src/moodify/api/main.py`) — REST API接口

---

## 6. 必须完成的工作（B轨道 + 集成）

### 6.1 B1: DSP处理引擎 — **最高优先级**

位置: `src/moodify/processing/`

**当前状态**: `operators.py` 已有5个基础算子(EQ/Compressor/Reverb/StereoEnhancer/Limiter)，但使用FFT和scipy手写实现，音质和专业性不足。

**需要完成**:
1. 安装并集成 `pedalboard` (Spotify Audio Library) 作为DSP后端
   - 替代手写EQ使用 pedalboard.PeakFilter/ShelfFilter
   - 替代手写Compressor使用 pedalboard.Compressor
   - 替代手写Reverb使用 pedalboard.Reverb
   - 新增 pedalboard.Chorus, Phaser, Distortion, Delay
2. 实现 `MoodifyDSPChain` 类，接收工艺卡参数 → 构造pedalboard chain → 处理音频
3. 确保所有参数从工艺卡的min/rec/max范围正确映射到pedalboard参数
4. 输出与输入同shape/samplerate，不改变音频长度
5. 批量处理优化：对大文件使用流式处理避免OOM

### 6.2 B2: 源分离集成

位置: Phase 2 of workflow_engine.py

**需要完成**:
1. 集成Demucs (facebookresearch/demucs) 进行4-stem源分离(vocals/drums/bass/other)
2. 实现fallback: Demucs不可用时自动降级为full-mix模式
3. 分离后的stems传递给Phase 3分层增强

### 6.3 B3: 空间重构

位置: Phase 4 of workflow_engine.py

**需要完成**:
1. 实现M/S空间宽度调节
2. 实现立体声深度重建（基于Haas effect + 早期反射模拟）
3. 实现单声道兼容性检查

### 6.4 B4: 母带处理链

位置: Phase 6 of workflow_engine.py

**需要完成**:
1. 平台自适应响度标准化：
   - Spotify: -14 LUFS integrated
   - YouTube: -14 LUFS
   - Apple Music: -16 LUFS
2. 砖墙限幅器（True Peak ≤ -1 dBTP）
3. 最终质量检查：削波检测、响度验证、频谱完整性
4. 输出格式：44.1kHz/16bit WAV + 320kbps MP3

### 6.5 B5: CLI完善

位置: `src/moodify/cli.py`

**需要完成**:
1. `moodify analyze <file>` — 输出完整18参数诊断报告（JSON/表格/雷达图文本版）
2. `moodify process <file> "<emotion>"` — 一键六阶段处理
3. `moodify batch <dir> "<emotion>"` — 批量处理目录
4. `moodify emotions` — 列出8种情绪+描述
5. `moodify compare <raw> <processed>` — A/B对比报告
6. `moodify serve` — 启动FastAPI服务
7. 所有命令支持 `--output-dir`, `--platform`, `--verbose`, `--dry-run`

### 6.6 B6: API服务完善

位置: `src/moodify/api/main.py`

**需要完成**:
1. POST `/api/v1/analyze` — 上传音频返回完整诊断JSON
2. POST `/api/v1/process` — 上传音频+情绪返回处理后音频+报告
3. GET `/api/v1/emotions` — 情绪列表
4. GET `/api/v1/craft_cards` — 工艺卡浏览
5. GET `/api/v1/health` — 服务健康检查
6. Swagger文档完善
7. 添加CORS支持
8. 文件上传大小限制(50MB) + 格式验证(WAV/MP3/FLAC)

### 6.7 B7: 安装与部署

**需要完成**:
1. 完善 `pyproject.toml` — 确保 `pip install -e .` 一键安装所有依赖
2. 完善 `requirements.txt` — 包含所有必需依赖及其版本
3. 编写安装脚本 `install.sh`
4. 确保在无GPU环境可运行（Demucs使用CPU模式）

---

## 7. 北极星指标

**EDSR (Emotion Development Success Rate)**:
```
EDSR = Count(用户偏好处理后版本) / Count(总评估数)
```

目标：EDSR ≥ 65%（即处理后版本在A/B盲测中被偏好概率≥65%）

---

## 8. 技术约束

1. **纯Python 3.10+**，不依赖Node.js/Go/Electron
2. **本地优先**，不依赖云API
3. **无GPU可运行**（Demucs CPU模式可接受较慢速度）
4. **内存友好**：4GB RAM环境可处理5分钟以内音频
5. **输出格式**：44.1kHz WAV + 320kbps MP3
6. **依赖管理**：所有依赖写入requirements.txt，版本锁定
7. **不修改已有模块的公共API**（A/C/D轨道代码只读）

---

## 9. 成功标准（交付物检查清单）

- [ ] `pip install -e .` 一键安装成功
- [ ] `moodify analyze song.wav` 输出完整18参数诊断JSON
- [ ] `moodify process song.wav "温柔觉醒"` 端到端运行成功
- [ ] `moodify process song.wav "都市危险"` 端到端运行成功
- [ ] 处理后音频与原始音频的WHS对比有明显提升
- [ ] `moodify serve` API服务正常启动并可访问/docs
- [ ] 批量处理 `moodify batch ./samples "神圣空灵"` 可运行
- [ ] 至少3种情绪工艺可端到端跑通
- [ ] Demucs源分离可用（或优雅降级）
- [ ] 母带响度符合Spotify标准(-14 LUFS)

---

## 10. 项目文件结构

```
/root/moodify-lab/
├── MOODIFY_INTENT.md          # 本文档 — 完整意图
├── src/moodify/               # 核心Python包
│   ├── diagnosis/             # [已完成] 诊断引擎
│   ├── processing/            # [需完成] DSP处理算子 ← 主要工作区
│   ├── knowledge/             # [已完成] 工艺链知识库
│   ├── orchestration/         # [需完成] 六阶段工作流
│   ├── api/                   # [需完成] FastAPI服务
│   ├── data_types.py          # [已完成] 数据结构
│   └── cli.py                 # [需完成] 命令行接口
├── 交接文档/                   # 工川署交接资料（只读参考）
├── pyproject.toml
├── requirements.txt
├── install.sh
└── tests/
```

---

## 11. 执行策略

**24小时工作分解**:

1. **第0-2小时**: 环境搭建 — 安装依赖，验证现有代码可运行，确认A/C/D模块正常
2. **第2-8小时**: B1 DSP引擎 — pedalboard集成，MoodifyDSPChain实现，8情绪链全部可执行
3. **第8-12小时**: B2-B4 — Demucs集成，空间重构，母带处理链
4. **第12-18小时**: B5-B6 — CLI完善，API服务完善，端到端集成测试
5. **第18-22小时**: 端到端测试 — 用测试音频跑通所有8种情绪，修bug
6. **第22-24小时**: 打磨 — 文档，安装脚本，最终验证，生成使用说明

---

## 12. 关键提醒

- **不要重构A/C/D模块** — 它们已经过工川署验收，只读使用
- **遇到理论问题先做工程决策** — 能跑通比理论完美重要
- **每个Phase独立可测试** — 不要等全部做完再验证
- **记录所有安装步骤** — 确保另一个人在新机器上能复现
- **如果某个功能无法在24小时内完美完成，先做能用的版本（MVP），再迭代**
