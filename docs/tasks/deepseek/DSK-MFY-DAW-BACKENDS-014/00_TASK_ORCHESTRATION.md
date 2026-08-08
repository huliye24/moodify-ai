# DSK-MFY-DAW-BACKENDS-014｜Moodify CLI DAW Engine 最小闭环

## 0. 状态

`PLANNED_FOR_DEEPSEEK`。本版本覆盖此前“REAPER 主力自动化 DAW”方案；CLI-first 是 P0 架构约束。

## 1. 目标

建立无需 GUI、鼠标、窗口焦点和人工点击的 Moodify CLI DAW：

```text
Moodify Decision & Evidence System
└── MoodifyCLIDAWEngine                 唯一主入口与事实所有者
    ├── NativeDSPBackend                默认执行器
    ├── FFmpegBackend                   无界面基础渲染
    ├── OptionalHeadlessEngineBackend   审计后选择，不先入为主
    └── Export/Handoff Adapters
        ├── ReaperProjectExporter       非主执行路径
        ├── ArdourProjectExporter       非主执行路径
        ├── AudacityMacroExporter       非主执行路径
        └── AuditionHumanHandoff        人工频谱精修
```

任务必须完成 CLI DAW 的最小可信闭环：声明式工程、时间线、多轨混合、处理图、离线渲染、证据、回读验证。不得把“调用一个 GUI DAW”包装成 CLI DAW。

## 2. 先审计，后选型

编码前读取适用 `AGENTS.md`、Git/dirty 状态、现有 DSP/CLI/证据合同，并盘点本机 Python、FFmpeg、ffprobe、Pedalboard、SoX、Rubber Band、FluidSynth 等可用组件。

新增 `00_IMPLEMENTATION_AUDIT.md`，回答：

- 哪些现有能力可复用，哪些缺失；
- 候选无界面引擎是否真正支持非交互批处理、Windows、离线渲染、多轨、自动化、插件及稳定退出码；
- 许可证、维护状态、打包体积和可复现性；
- 为什么选择或拒绝候选；
- 第一阶段是否仅用 NativeDSP + FFmpeg 即可形成可信闭环。

禁止仅因软件自称 DAW 就纳入。GUI 应用即使带启动参数，也只能算兼容适配器，除非证明全流程无需界面。

## 3. 边界

允许新增/修改：

```text
E:\moodify\moodify-core-package\src\moodify\cli_daw\
E:\moodify\moodify-core-package\tests\test_cli_daw*.py
E:\moodify\moodify-core-package\src\moodify\cli.py
E:\moodify\docs\architecture\CLI_DAW_ENGINE.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-DAW-BACKENDS-014\
E:\moodify\outputs\deepseek_validation\DSK-MFY-DAW-BACKENDS-014\
```

禁止改动真实音乐资产与既有 DSP/MRS/Score 合同；禁止复制第三方二进制或源码；禁止联网安装、静默接受许可、下载插件；禁止 Git reset/clean/stash/checkout/commit/push/切分支。用户既有修改不得覆盖。

测试只能使用生成的短音频夹具。源文件始终只读，所有运行写入全新目录。

## 4. Stage 0｜冻结合同与 Gate

先写并冻结：

- `CLI_DAW_PROJECT_SCHEMA.md`：project、track、clip、bus、send、master、marker、tempo；
- `PROCESSING_GRAPH_CONTRACT.md`：trim、gain、pan、fade、EQ、compressor、limiter、resample、mix；
- `AUTOMATION_CONTRACT.md`：时间单位、插值、边界、冲突规则；
- `RENDER_EVIDENCE_CONTRACT.md`：输入/配置/工具/输出 hash、命令 argv、版本、指标和日志；
- `CAPABILITY_AND_FALLBACK_POLICY.md`：支持、降级、拒绝及错误码；
- `HEADLESS_ENGINE_EVALUATION.md`：候选矩阵和选型结论。

Stage 0 Gate 未 PASS 禁止进入编码。

## 5. Stage 1｜CLI DAW 核心模型

实现严格类型：

```text
CLIDAWProject
Track / Clip / Bus / Send / Master
ProcessingNode / AutomationLane
RenderRequest / RenderResult / RenderEvidence
EngineCapabilities / EngineProbe
```

必须支持：

- WAV 源引用与 hash；
- sample-accurate 或明确记录精度的时间线；
- 多轨 gain/pan/mute/solo；
- clip trim、offset、fade；
- bus/master 路由；
- 确定性处理图；
- 工程 schema version 与严格校验；
- 不支持的节点 fail closed，不能静默跳过。

项目 JSON/YAML 是事实源，不允许外部 DAW 工程成为唯一事实源。

## 6. Stage 2｜NativeDSP + FFmpeg 无界面渲染

实现 `NativeDSPBackend` 与 `FFmpegBackend`，优先复用已有模块，不复制 DSP 业务逻辑。

要求：

- 全程使用参数数组启动子进程，禁止 shell 字符串拼接；
- probe 记录可执行文件绝对路径、版本和能力；
- 生成可审计 render plan；
- 渲染 stems、buses、master；
- 输出 WAV、manifest、日志、hash、响度/峰值/时长等可机器验证指标；
- 超时、取消、非零退出、输出缺失、hash 不符均显式失败；
- 同输入、同配置、同版本双运行结果和证据应一致；若编码器存在字节级非确定性，必须定义并验证内容级等价，不得掩盖。

可选 headless 引擎只有在 Stage 0 证据充分且本机已存在时才做最小 adapter；缺失不得阻塞核心闭环。

## 7. Stage 3｜唯一 CLI

至少实现：

```powershell
py -3.11 -m moodify daw engines
py -3.11 -m moodify daw validate --project PROJECT.json
py -3.11 -m moodify daw plan --project PROJECT.json --output-dir NEW_DIR
py -3.11 -m moodify daw render --project PROJECT.json --engine native --output-dir NEW_DIR
py -3.11 -m moodify daw verify RUN_DIR
```

CLI 必须可在没有桌面会话的终端运行，支持稳定退出码和 JSON 结果。不得弹窗，不得等待窗口，不得依赖默认音频设备。

旧 CLI 保持兼容。错误至少区分：schema invalid、engine unavailable、capability unsupported、render failed、verification failed。

REAPER/Ardour/Audacity/Audition 本任务只保留 exporter/handoff capability declaration；未实现返回 `NOT_IMPLEMENTED`。不得将 GUI 自动化列为 PASS。

## 8. Stage 4｜验证与交付

必须验证：

- mono/stereo、多采样率、不同 bit depth；
- clip offset/trim/fade、gain/pan/mute/solo；
- 双轨混合、bus/master；
- 非法路由、循环路由、未知节点、缺失源；
- 特殊字符与 Unicode 路径；
- 超时、非零退出、中断、半成品清理；
- 双运行与源 hash 不变；
- CLI help/smoke、相关回归、lint/type check。

交付 `HANDOFF.md`、验证命令、测试结果、产物树、限制与源 hash。最终状态只能为 `READY_FOR_CODEX_REVIEW`、`REWORK`、`HOLD`，然后停止等待 Codex 独立验收。

## 9. P0 Gate

以下任一不成立不得 PASS：无 GUI/鼠标/窗口依赖；原音频只读且 hash 不变；输出只进新目录；项目合同是事实源；命令参数数组化；缺失能力显式失败；无隐式联网/安装；稳定退出码；证据可回读；旧 CLI 不回归；不伪造人工听感结论。
