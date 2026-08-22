# 01 — Current Audio Capability Map

**W01-P05 · 2026-08-17 · Capability Reality Gate（硬规则 §3：先出地图，再改管线）**

| Capability | Current implementation | Runtime verified | Canon class | Input | Output | Failure behavior | Decision |
|---|---|---|---|---|---|---|---|
| FFmpeg/ffprobe 解码 | 系统工具（LA 4.4.2 / 杭州 8.0.1） | ✓（双节点部署） | CANONICAL_AVAILABLE | 音频文件 | PCM/元数据 | PROCESS_TIMEOUT | 复用（audio_io 走 ffmpeg） |
| v01 analyze | `v01_analyzer.analyze()` | ✓（测试+云端 v01 模式） | CANONICAL_AVAILABLE | wav 路径 | metrics（loudness/peak/dynamics/spectral） | INPUT_INVALID（不可解码） | 接入 ANALYZE 阶段 |
| v01 diagnose | `v01_diagnostics.diagnose()` | ✓ | CANONICAL_AVAILABLE | metrics | DiagnosisReport | — | 接入 JUDGE 阶段输入 |
| v01 presets | `v01_presets`（warm_vocal/clean_master/wide_space） | ✓ | CANONICAL_AVAILABLE | preset 名 | 处理链参数 | — | PROFILE 阶段（版本化封装） |
| v01 pipeline | `v01_pipeline.process_audio()` | ✓ | CANONICAL_AVAILABLE | 路径+preset | ProcessResult+输出文件 | INPUT_INVALID | RENDER 阶段实现基底（同步包装） |
| processing chain | `processing/pedalboard_chain.MoodifyDSPChain` + operators | ✓（测试） | CANONICAL_AVAILABLE | PCM+参数 | PCM | PROCESS_CRASH | INTERVENE 参数化 |
| algorithmic review | `data_factory/algorithmic_review` | ✓（10/10 pilot） | CANONICAL_AVAILABLE | 前后指标 | 技术排名 | — | VERIFY 比较验证 |
| auditory 模块 | `auditory/`（decode/analysis/events） | ✓（测试） | INTERNAL_AVAILABLE | 音频 | 事件/证据 | — | 可选增强（不进 P05 主线） |
| stems 分离 | `stems/service.py`（lalal） | 部分（audiolla 部署 LA，无自动调用） | EXTERNAL_AVAILABLE | 音频 | stems | EXTERNAL_API_* | STEM 阶段 adapter 接入（默认 BYPASS） |
| reconstruction 系列 | `reconstruction/`（objective/pipeline/blind） | ✓（golden 本地） | INTERNAL_AVAILABLE | 音频+findings | A/B/C 方案/记录 | — | 与 P05 主线并行（经典重建域），不混入 |
| intervention 原语 | `intervention/`（3 原语） | ✓（负对照 5/5） | EXPERIMENTAL_AVAILABLE | PCM+参数 | PCM | — | 可选 INTERVENE 参数源（P07 评估） |
| era_diagnostic | `era_diagnostic/` | ✓（测试） | INTERNAL_AVAILABLE | 音频 | 年代发现 | — | 经典重建域，不进 P05 主线 |
| identity_guard | `identity_guard/` | ✓（测试） | INTERNAL_AVAILABLE | 前后音频 | 六维 veto | — | VERIFY 可选门（重建域） |
| data_factory cases | `data_factory/` | ✓（pilot 10/10） | CANONICAL_AVAILABLE | 曲目 | case 记录 | — | 历史批处理；P05 主线不依赖 |
| audiolla 容器 | LA docker | ✓（健康，无自动调用） | EXTERNAL_AVAILABLE | 音频 | 分离结果 | EXTERNAL_API_* | STEM adapter 后端 |
| Demucs | 未下载权重 | 否 | UNAVAILABLE | — | — | — | 不引入 |

## 关键结论

1. **主线可用**：v01 analyze→diagnose→process（preset）+ FFmpeg + algorithmic_review 构成 One Song 主链的最小可用基底。
2. **STEM 默认 BYPASS**：audiolla 已部署但无自动调用证据；P05 提供 adapter 契约，默认关闭（§7 禁止无条件分轨）。
3. **不塞历史代码**：MAMSE/era/identity/reconstruction 全部不进 P05 主线（硬规则 §3）；保留为 INTERNAL/EXPERIMENTAL 域。
4. **REAL TIME 无能力**：无 GPU 推理、无 Demucs——P05 不引入。

## 决策

- P05 管线 = v01 三件套（analyze/diagnose/process）+ FFmpeg + algorithmic_review + stems adapter（可选）+ P03/P04 契约（register/complete）。
- 管线为同步 runner（单 worker 语义，P04 lease 在阶段边界检查）。
