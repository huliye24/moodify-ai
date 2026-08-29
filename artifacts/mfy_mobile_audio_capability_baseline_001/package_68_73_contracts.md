# 68–73 包契约设计(只设计,不实现)— MFY_MOBILE_AUDIO_CAPABILITY_BASELINE_001

总路线:`67 基线 → 68 可观测+bit-transparent → 69 端侧 DSP Runtime → 70 设备感知渲染 → 71 Preserve-Identity MVP → 72 多设备盲听 → 73 Play 试点`

## 共享设计原则

1. **旁路优先**:任何不确定/设备能力不足/过载/身份风险 → BYPASS 或 HUMAN_REQUIRED,不降级硬跑
2. **证据链**:每包必须产出 Measurement Record + Evidence Artifact + 失败记录,复用 core contracts
3. **回滚**:每包改动必须以 feature/开关形式可整体关闭,恢复原播放路径
4. **实验≠生产**:68-73 期间所有能力标 EXPERIMENTAL,人类听感门通过前不得声称"更好听"
5. **分轨后置**:分轨是 71 之后的可选增强;实时播放不依赖分轨

---

## 包 68 — 音频路径可观测与 bit-transparent 基线

**目的**:证明播放链路上输入→输出字节可验证,建立观测点。

- **接口边界**:
  - 新增 `PlaybackProbe`(Android 侧):输入 URI 字节 sha256 记录;ExoPlayer AudioSink 输出格式回调(采样率/声道/位深)记录
  - 新增 `AudioPathRecord`: {input_sha256, input_format, output_format, route, codec, cache_hit}
  - 不动 PlaybackManager 主逻辑;仅挂观测
- **失败状态**:sha256 不匹配 / 输出格式回读失败 → `OBSERVATION_INCOMPLETE`(记录,不阻断播放)
- **证据**:bit-transparent 验证矩阵(本地 FLAC/WAV/MP3 各 3 首,设备扬声器+有线)
- **回滚**:移除观测代码即可恢复原路径(零行为变更设计)
- **验收门**:本地文件播放 100% bit-transparent(输入字节==ExoPlayer 解码输入),输出格式可回读
- **工作树先行实现观察(2026-08-16 20:16,未提交,67 续作复核时记录)**:权威工作树已出现 68 草案——`InputMetadataExtractor.kt`(MediaExtractor 只读 staging 元数据)、`PlaybackPath.kt`(PlaybackPathRecord, schema `mfy-playback-path-v1`,offloadStatus 如实标 UNKNOWN)、`PlaybackPathObserver.kt`(offload/underrun/route/spatializer 观测,AudioFocus 有意不观测)、`BypassEquivalenceTest.kt`(WAV/FLAC 字节精确 + MP3/AAC 有效 PCM 断言)、fixtures tone.wav/flac/mp3/aac。**68 应以该先行实现为输入**:契约名 PlaybackProbe/AudioPathRecord 与先行命名 PlaybackPathRecord 不一致,68 包需对齐命名与验收门;先行实现声称 FLAC 解码字节==源 PCM,其设备侧断言需在 68 真机门复验;输入字节 sha256 观测点(Bit-transparent 关键)先行实现尚未覆盖。

## 包 69 — 可旁路、实时安全的端侧 DSP Runtime

**目的**:在播放链插入一个**可整体旁路**的实时 DSP 层(无 EQ/响度/AI 效果——只搭运行时骨架)。

- **接口边界**:
  - `AudioDspGraph`:单一 Media3 AudioProcessor 链,输入格式协商(44.1/48k 统一处理策略,不盲目升采样),headroom 安全(process 前 -x dBFS 保护),平滑参数(无爆音)
  - `BypassSwitch`:runtime 状态旁路;过载/异常 50ms 内自动切旁路
  - 首版只放"无操作(identity) processor"证明管线安全
- **失败状态**:过载/underrun/异常 → 自动旁路 + `DSP_BYPASSED` 记录;DSP 线程 crash 不影响播放
- **证据**:旁路/生效 A/B 波形一致性(processor 为空操作时输出==输入);underrun 统计;延迟测量
- **回滚**:BypassSwitch 默认 ON;移除 graph 即恢复原路径
- **验收门**:空操作 processor 下输出与输入 bit-identical;旁路切换无卡顿

## 包 70 — 设备/输出路由自适应渲染

**目的**:只读取系统可观测能力(不映射型号),决策输出 profile。

- **接口边界**:
  - `DeviceCapabilityProbe`:AudioManager.getDevices / PROPERTY_OUTPUT_SAMPLE_RATE / FRAMES_PER_BUFFER / 蓝牙 codec(API 可读部分)
  - `RenderProfile`: {sample_rate_strategy(跟随系统,不升采样), channel_strategy, headroom, dsp_enabled(boolean)}
  - `ProfileDecision`:observed 数据 → 版本化规则(未知 → 默认安全 profile 或 BYPASS)
- **失败状态**:能力探测失败/未知 → `DEVICE_CAPABILITY_UNKNOWN` + 安全 profile;禁止用型号名推断参数
- **证据**:设备矩阵(见 device_test_matrix.json)逐项实测记录,observed vs api_reported 分级
- **回滚**:ProfileDecision 默认返回"系统默认"(即旁路)
- **验收门**:≥2 台真机(中端+低端)probe 数据齐全,未知设备不崩溃且走安全 profile

## 包 71 — Preserve-Identity 听觉干预 MVP

**目的**:在 69/70 之上,允许**已批准范围**的干预,核心是 DO_NOT_TOUCH 保护。

- **接口边界**:
  - `IdentityGuard`:contracts 层新契约(仿 machine_finding)——六类风险上限(voice timbre/transient/reverb/stereo/bass/loudness),增量超出 → BLOCKING
  - `InterventionProfile`: {approved_interventions[], identity_limits, guardrail_set} 版本化 scope
  - 决策:`scope_contract` 检查 → plan → IdentityGuard → 输出或 BYPASS;不确定 → HUMAN_REQUIRED
  - 复用 core plan_generator/pedalboard_chain/comparison(改造目标函数,不新建 pipeline)
- **失败状态**:guardrail 失败 → 候选丢弃 + `IDENTITY_RISK`;参数未授权 → 拒绝执行
- **证据**:每案例 case 目录(00_source..06_review 复用现有契约);before/after 增量报告
- **回滚**:InterventionProfile 未批准时恒 BYPASS(默认)
- **验收门**:同一首歌 3 个候选至少 1 个通过全部 guardrail;任何被 BLOCKING 的候选不进入播放

## 包 72 — 多设备、响度匹配盲听验证

**目的**:人类听感门——机器候选必须经盲听验证(不自动通过)。

- **接口边界**:
  - `BlindListeningRecord`: {case_id, device, output_chain, matched_lufs(响度匹配), candidate_a/b, listener_id, preference}
  - 盲听协议:响度匹配(±0.3 LUFS)后 A/B/X 测试;每设备≥2 听者
  - 结果不自动改阈值;只作为案例证据
- **失败状态**:响度不匹配 → 重试;听者结果矛盾 → `BLIND_RESULT_INCONCLUSIVE`
- **证据**:盲听记录 JSON + 设备矩阵回填;结果写入 case 06_human_review(人类 stamp)
- **回滚**:无生产参数变更,纯验证
- **验收门**:≥2 设备 × ≥2 听者完成;结论仅作 evidence,不承诺"更好"

## 包 73 — 一个 Play 的自适应播放器试点

**目的**:最小用户可见流:`Open song → Moodify understands → Safe intervention or bypass → Play`。

- **接口边界**:
  - Android:本地文件选择(SAF)+ 现有 PlaybackManager + 69/70/71 链;HomeScreen 改造为"选择→处理→播放"
  - 隐藏不删:PersonalLibraryStore/TokenStore/云端调用保留但不公开
  - 结果缓存:重建结果与原始文件**不同缓存命名空间**(sha256 键)
  - 不发布 APK 以外的线上变更
- **失败状态**:任何链路失败 → 自动播放原始文件(默认保底)+ `RECONSTRUCTION_BYPASSED` 记录
- **证据**:试点案例记录(每首:输入 sha256、profile、guardrail 结果、盲听链接)
- **回滚**:开关关闭即恢复 3.1 原播放器
- **验收门**:试点设备(1 台中端)上 10 首合法自有歌曲完整走通;全程可旁路

---

## 包间依赖与输入

| 包 | 依赖 | 关键输入 |
|---|---|---|
| 68 | 67 | AudioPathRecord 观测点设计 |
| 69 | 68 | 输出格式回读能力、bit-transparent 基线 |
| 70 | 68 | DeviceCapabilityProbe(复用 68 的格式回读) |
| 71 | 69+70 | DSP graph 骨架 + 设备 profile |
| 72 | 71 | 通过 guardrail 的候选 + 设备矩阵 |
| 73 | 71+72 | 批准的 InterventionProfile + 盲听证据 |

## 包级禁止项

- 68-73 全程:不加 EQ/响度/空间化/AI 效果到播放链;不改发布 APK/线上/秘密;不型号→参数硬映射;不声称"更好听"
- 每个包必须:只读基线不变 + 证据文件 + 失败记录 + 回滚验证
