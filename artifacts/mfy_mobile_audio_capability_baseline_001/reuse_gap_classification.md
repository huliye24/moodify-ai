# 复用/缺口分类 — MFY_MOBILE_AUDIO_CAPABILITY_BASELINE_001

**审计对象**: `E:\moodify-worktrees\moodify-3.0-external-audio` HEAD `f6316612`
分类: KEEP / ADAPT / BUILD / HUMAN_REQUIRED。实验能力不得写成生产事实。

## KEEP(直接复用,生产级已接线)

| 能力 | 位置 | 说明 |
|---|---|---|
| Media3 ExoPlayer 播放栈 | apps/android/.../PlaybackManager.kt | queue/A-B/后台/缓存全就绪 |
| MediaSessionService | apps/android/.../PlaybackService.kt | 后台播放 + 锁屏控制 |
| 512MB LRU 缓存 + prefetch | apps/android/.../PlaybackAudioCache.kt | 缓存边界清晰 |
| 本地 URI 接收 + persistable 权限 | apps/android/.../MainActivity.kt | QQ 分享入口已通 |
| WSE 扫描链(FAST/STANDARD/DEEP) | core/auditory/service.py + profiles.py | FAST 档适合移动端预分析 |
| measurement_registry 白名单 | core/configs/measurement_registry_v1.yaml | 12 项 judgment_eligible |
| 8 类 P0 事件 | core/auditory/events/models.py | 时间定位,防审美结论 |
| judgment 15 阈值 + 增量门 | core/auditory/judgment.py | before/after 保护 |
| authority fail-closed | core/authority/pipeline.py | 非 MACHINE_DECIDED → HUMAN_REQUIRED |
| A/B/C 计划生成 + guardrails | core/data_factory/plan_generator.py | P01-P15 工艺卡 |
| intervention + pedalboard 链 | core/data_factory/intervention.py + processing/pedalboard_chain.py | 24-bit PCM 输出 |
| algorithmic_review 冻结公式 | core/data_factory/algorithmic_review.py | SOURCE/A/B/C 排名 |
| comparison before/after delta | core/auditory/comparison.py | 增量证据 |
| case 契约全套 | core/contracts/ | production_case/evidence_artifact/machine_finding |
| node JobQueue | core/node/queue.py | SQLite, 6h lease, retry 3 |

## ADAPT(可复用但需改造/重新接线)

| 能力 | 位置 | 改造内容 |
|---|---|---|
| A/B 双按钮 NowPlayingScreen | apps/android/.../ui/screens/NowPlayingScreen.kt | 死代码未接线;需接入 73 的极简播放页 |
| MiniPlayer / PlaybackBar 组件 | apps/android/.../ui/components/ | 完整拖拽手势已写,未接线;73 可复用 |
| plan_generator 目标函数 | core/data_factory/plan_generator.py | 现为通用"干预实验室"目标;68-71 需重建导向目标(带宽/底噪/单声道限制) |
| algorithmic_review 评分公式 | core/data_factory/algorithmic_review.py | 从"目标情绪达成"改为"重建保真度 + 身份保持" |
| PersonalLibraryStore | apps/android/.../data/PersonalLibraryStore.kt | 现仅存元数据;73 本地库需加 sha256/指纹索引 |
| TokenStore / BaseUrlStore | apps/android/.../data/ | Keystore 底座已有;73 需定义"用户自有文件"鉴权模型 |

## BUILD(不存在,需新建)

| 能力 | 所属包 | 说明 |
|---|---|---|
| 音频路径观测点(输入字节校验/输出格式回读) | 68 | bit-transparent 基线;当前播放链路零观测 |
| 端侧 DSP Runtime(可旁路、实时安全) | 69 | 现输出路径是干净委托栈,可整块插入 AudioProcessor;但无运行时框架 |
| 设备能力探针(采样率/帧缓冲/路由/codec) | 68/70 | 现无 AudioManager/AudioTrack 任何代码 |
| 设备感知渲染决策(自适应 profile) | 70 | 现无 device→profile 机制;禁止型号硬编码 |
| Preserve-Identity 干预 MVP | 71 | 现无 DO_NOT_TOUCH/ARTISTIC_INTENT;judgment 增量门是最接近的保护 |
| 多设备盲听验证设施 | 72 | 现无盲听评审设施 |
| 自适应播放器试点 | 73 | 现 HomeScreen 是目录播放,无"本地→重建→Play"流 |
| 本地音乐库(扫描/指纹/sha256 索引) | 73 | 现仅 intent 分享单曲 |
| SAF 文件选择器 | 73 | 现仅被动接收分享 |

## HUMAN_REQUIRED(人类听感/审美裁决,机器不可单独批准)

| 事项 | 位置 | 说明 |
|---|---|---|
| 审美批准 / 原作身份裁决 | core/authority/scope_contract.py | 禁止 perceptual preference / artistic quality 结论 |
| "是否更好听" claim | — | DeepSeek 不拥有;任何 PASS 结论需人类听感门 |
| 阈值放宽 / 设备参数上线 | — | 未测量参数禁止映射 |
| 私人音频授权 | — | 68-73 测试素材需合法自有音频 |

## 分轨现状(71 之后的可选增强,不是 68-73 前置)

- 3.0 权威分支:无 stems/demucs;仅 HPSS(EXPERIMENTAL,未接线)
- E:\moodify(android-2.0 分支,已部署 LA):LALAL `/api/v1/stems/*` 10 轨异步分离,实测通过,按分钟计费
- Audiolla(LA,补丁包 66):镜像含 demucs 但未启用;5 处理引擎已通过 smoke/async
- **结论**:实时播放成立不依赖分轨;分轨(如需)走离线质量门,失败回 full-mix

## 66 真实状态记录(只读)

- Audiolla 已部署 LA 103.144.246.242:Docker 29.1.3 + Compose 2.40.3,镜像 psyb0t/audiolla@sha256:1b76f692...(2026-07-31,~1GB),容器 moodify-audiolla healthy,127.0.0.1:18080 绑定,5 引擎(librosa-analyze/pedalboard-chain/sox-transform/fx-chain/matchering),Bearer token 鉴权(/etc/moodify/audiolla/.env),/data 持久化(uid 1000)
- 验证:healthz ✓,未授权 401 ✓,staging/analyze/transparent master/retrieve ✓,async job(pending→running→completed,0.78s)✓,matchering reference mode ✓,40s WAV 资源测试 ✓;容器重启后 data 保留 ✓
- 已知:SSH 22 端口间歇性被重置(服务器侧网络波动,服务器健康,网站/API 全 200);66 最终报告待 SSH 稳定后补交 artifacts/audiolla_cloud_deploy_001/
- 未验证:完整歌曲(仅 40s);未接入任何生产链(按 66 边界)
