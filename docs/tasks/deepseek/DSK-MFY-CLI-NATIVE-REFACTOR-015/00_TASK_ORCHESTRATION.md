# DSK-MFY-CLI-NATIVE-REFACTOR-015｜Moodify AI-Native CLI 产品重构

## 0. 状态与前置条件

状态：`PLANNED_FOR_DEEPSEEK`。

前置任务：`DSK-MFY-DAW-BACKENDS-014` 已完成并经 Codex 验收，或其冻结的 CLI DAW 合同已经可用。若前置未满足，只能完成 Stage 0/1 与兼容设计，不得伪造集成 PASS。

本任务不是改名、包装 argparse，也不是删除 GUI。它要把 Moodify 重构为以 CLI、声明式项目、机器可读输出和证据为产品本体的 AI-native 音乐系统。

## 1. 产品定义

> Moodify 是面向人类与 AI Agent 的原生 CLI 音乐决策、制作与证据系统；GUI、Web、App 都是 CLI/API 之上的可选客户端。

```text
Human / AI Agent
        ↓
Moodify CLI + JSON Protocol
        ↓
Application Orchestrator
        ↓
Canonical Music Project + Decision Model
        ↓
Audio / MIDI / Score / Lyrics / Evidence Ports
        ↓
Replaceable Engines and External Adapters
```

Moodify 必须拥有：项目事实、音乐资产身份、决策记录、处理计划、运行证据、版本与修订历史。第三方工具只能是可替换执行器。

## 2. 重构原则

1. CLI-first，不等于 shell-script-first：核心必须是可测试的 Python application API，CLI 是稳定适配器。
2. JSON-first：每个命令支持稳定 schema、稳定退出码和机器可读结果；人类文本只是 presentation。
3. Project-first：零散文件操作迁移为 canonical project 下的 asset/run/revision。
4. Plan-before-apply：分析、决策、计划和执行分离；危险或有损动作必须可预览。
5. Evidence-by-default：每次执行记录输入、配置、版本、argv、hash、输出、指标和失败。
6. Backend-neutral：Audio/MIDI/Score/Lyrics 后端通过 ports/adapters 接入。
7. Strangler migration：新 façade 包住旧能力，逐步替换；禁止一次性重写和大规模搬目录。
8. Backward compatible：旧命令先进入兼容层并给出结构化 deprecation，不得突然失效。
9. 无界面依赖：核心命令不能依赖窗口、鼠标、焦点、弹窗和默认音频设备。
10. AI-safe：严格输入校验、权限/路径边界、幂等键、dry-run、取消、超时和可恢复状态。

## 3. 工作边界

允许新增/修改：

```text
E:\moodify\moodify-core-package\src\moodify\app\
E:\moodify\moodify-core-package\src\moodify\domain\
E:\moodify\moodify-core-package\src\moodify\ports\
E:\moodify\moodify-core-package\src\moodify\adapters\
E:\moodify\moodify-core-package\src\moodify\cli_v2\
E:\moodify\moodify-core-package\src\moodify\cli.py
E:\moodify\moodify-core-package\tests\test_cli_v2*.py
E:\moodify\moodify-core-package\tests\cli_v2\
E:\moodify\docs\architecture\AI_NATIVE_CLI_ARCHITECTURE.md
E:\moodify\docs\architecture\CLI_V2_COMMAND_CONTRACT.md
E:\moodify\docs\architecture\CANONICAL_MUSIC_PROJECT.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-CLI-NATIVE-REFACTOR-015\
E:\moodify\outputs\deepseek_validation\DSK-MFY-CLI-NATIVE-REFACTOR-015\
```

既有实现原则上只读；只有 `cli.py` 可做最小路由接线。若确需修改其他既有文件，先记录 `SCOPE_CHANGE_REQUEST.md`，本任务停止为 `HOLD` 等待 Codex。

禁止：真实歌曲处理；删除/移动既有模块；改变旧产物语义；隐式联网/安装；修改全局配置；复制第三方源码/二进制；Git reset/clean/stash/checkout/commit/push/切分支；覆盖用户 dirty/untracked 文件。

## 4. Stage 0｜仓库与能力审计

编码前读取适用 `AGENTS.md`，记录 Git/dirty 状态，盘点现有 CLI、DSP、转录、MIDI、Score、Lyrics、Spectral Evidence、MRS/Runtime/Bridge 的入口、合同、依赖和测试。

交付：

- `00_IMPLEMENTATION_AUDIT.md`
- `01_CAPABILITY_INVENTORY.md`
- `02_COMMAND_COMPATIBILITY_MATRIX.md`
- `03_DEPENDENCY_AND_IMPORT_MAP.md`
- `04_RISK_REGISTER.md`

必须识别循环依赖、重复模型、隐式全局状态、非确定输出、GUI/人工依赖、无稳定错误码和无证据路径。Stage 0 Gate 未 PASS 禁止编码。

## 5. Stage 1｜冻结产品与领域合同

先写文档与 schema：

- `AI_NATIVE_CLI_ARCHITECTURE.md`
- `CLI_V2_COMMAND_CONTRACT.md`
- `CANONICAL_MUSIC_PROJECT.md`
- `PROJECT_SCHEMA.json`
- `COMMAND_RESULT_SCHEMA.json`
- `RUN_EVIDENCE_SCHEMA.json`
- `ERROR_CATALOG.md`
- `MIGRATION_AND_DEPRECATION_POLICY.md`

Canonical project 至少包含：project identity/schema version、assets、relationships、analysis、decisions、plans、runs、artifacts、revisions、approvals、provenance。所有实体使用稳定 ID；路径不是身份。

命令结果统一 envelope：schema_version、command、status、exit_code、project_id、run_id、artifacts、warnings、errors、evidence_path。时间、浮点、枚举、路径和排序必须规范化。

Stage 1 Gate：合同可独立校验、错误码无歧义、旧命令映射清楚、迁移不丢数据。

## 6. Stage 2｜建立新内核骨架

采用清晰依赖方向：

```text
domain ← app ← ports ← adapters
                  ↑
                cli_v2
```

实现但不得过度抽象：

- domain：Project、Asset、Decision、Plan、Run、Artifact、Revision、Evidence 值对象/实体；
- app：用例服务、事务边界、幂等、dry-run、状态机；
- ports：Audio、MIDI、Score、Lyrics、Evidence、Storage、Clock、Hasher 接口；
- adapters：对现有 Moodify 能力做薄适配，禁止复制算法；
- cli_v2：解析、调用 app、JSON/text presentation、稳定退出码。

领域层不得 import CLI、subprocess、GUI 或具体第三方库。应用层不得解析终端字符串。Adapter 的不可用能力必须显式返回 typed error。

## 7. Stage 3｜最小纵向闭环

至少实现以下命令：

```powershell
py -3.11 -m moodify --version --json
py -3.11 -m moodify capabilities --json
py -3.11 -m moodify project init PROJECT_DIR --json
py -3.11 -m moodify project inspect PROJECT_DIR --json
py -3.11 -m moodify asset import PROJECT_DIR INPUT.wav --copy-mode reference --json
py -3.11 -m moodify plan create PROJECT_DIR --intent INTENT.json --dry-run --json
py -3.11 -m moodify run execute PROJECT_DIR --plan-id PLAN_ID --output-dir NEW_DIR --json
py -3.11 -m moodify run verify PROJECT_DIR --run-id RUN_ID --json
```

最小闭环使用合成 WAV 与一个已经存在、风险最低的处理能力：init → import → plan → dry-run → execute → verify → inspect。不得为凑闭环复制 DSP。

要求：

- 默认不覆盖，输出目录必须新建；
- source reference 默认只读并记录 SHA-256；
- `--json` stdout 只能输出一个合法 JSON；日志进入 stderr；
- 相同 idempotency key 不重复执行；
- SIGINT/超时/失败留下可解释状态，不把半成品标记成功；
- `--dry-run` 不产生音频派生物；
- 对机器和人类均提供 help，但 JSON 合同优先。

## 8. Stage 4｜兼容层与能力接入

将现有代表性入口映射进兼容层，至少覆盖：旧 audio transcribe、stem MIDI、spectral evidence、CLI DAW（若前置可用）。

旧命令行为保持；stderr 可给 deprecation，`--json` 给 machine-readable warning。不得在本任务删除旧命令。

Score、Lyrics、MIDI、Audio 后端只建立真实 adapter/capability；尚未完成的返回 `NOT_IMPLEMENTED` 或 `BACKEND_UNAVAILABLE`，不得假接入。

## 9. Stage 5｜验证、迁移演练与交付

必须测试：

- schema round-trip 与旧/新 schema 拒绝策略；
- JSON stdout 纯净、stderr 分离、退出码稳定；
- Unicode/空格/特殊字符路径；
- source hash 不变、路径逃逸和 symlink/junction 防护；
- dry-run、幂等、取消、超时、失败恢复；
- 未知能力、backend unavailable、NOT_IMPLEMENTED；
- 双运行确定性或合同规定的内容级等价；
- 旧 CLI smoke 与相关回归；
- import boundary/cycle test、lint/type check。

在全新验证目录使用合成夹具完成两次纵向运行。交付 `HANDOFF.md`、测试记录、产物树、兼容矩阵、迁移限制、源 hash。最终状态只能是 `READY_FOR_CODEX_REVIEW`、`REWORK` 或 `HOLD`，然后停止等待 Codex 独立验收。

## 10. P0 验收门

以下任一不成立不得 PASS：CLI/JSON 是正式产品合同；domain 不依赖具体工具；project 是事实源；source 只读；输出仅进新目录；无 GUI 依赖；plan 与 apply 分离；证据默认生成；错误 fail closed；旧 CLI 不回归；无隐式联网/安装；无用户修改被覆盖；无伪造人工听感或能力。

