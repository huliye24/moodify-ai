# DSK-MFY-PPE-HARDENING-005｜PPE 基线从 Function 到 Form 的五轮加固

**日期：2026-08-01**  
**执行 Worker：DeepSeek（用户手动发送执行命令）**  
**任务所有者、独立 Judge 与最终放行人：Codex / 授权用户**  
**基线结论：PPE-01～04 已 `PASS_WITH_WARNINGS`，本任务不得篡改该历史事实**  
**目标：把一次成功运行转化为可重复、可失败、可恢复、可理解、可继承的生产形式**

## 1. 哲学与工程命题

本任务遵循：

```text
E:\软件建造的哲学\POSC_002_Function_Is_Not_Form_Edition_0.1.pdf
```

核心命题：第一次成功只证明通路存在；工程建造要求把成功所依赖的条件、边界、失败、判断与责任保存为他人可以进入的形式。

本任务不增加声音处理功能。它只把 2026-08-01 的 PPE 合成案例冒烟加固成一个可独立运行和审计的基线层。

## 2. 已知事实与必须复核的问题

只读基线：

```text
E:\moodify\outputs\ppe_2026-08-01\01_COMMAND_CHECKLIST.md
E:\moodify\outputs\ppe_2026-08-01\02_PRODUCTION_GATES_DRAFT.md
E:\moodify\outputs\ppe_2026-08-01\03_EXECUTION_REPORT.md
E:\moodify\outputs\ppe_2026-08-01\evidence.yaml
E:\moodify\outputs\ppe_2026-08-01\ledger\ledger.duckdb
E:\moodify\outputs\ppe_2026-08-01\failure_isolation\ledger\ledger.duckdb
```

当前已知：

1. `case create → case validate → assets hash → evidence compile → report build` 已成功。
2. 隔离资产哈希失配会返回失败，并追加进入 DuckDB。
3. 仓库原始 `demo/assets/source.txt` 未被修改。
4. 合成案例没有音频 MeasurementRecord；这是显式警告，不得补成推测值。
5. 独立 `.venv` 在线安装曾超时；成功仍部分依赖本机已有 Python 3.12 环境。
6. `rule validate` 曾输出 `checks.human_approval=true` 且 `approval_id=null`，语义容易被误解。
7. 缺少批准文件时 `rule promote` 正确返回非零，但向操作者泄漏完整 Python traceback。
8. 现有 `rule promote` 在完整校验和文件写入之前把 approval 加入数据库，必须检查非法转换或写入失败是否留下部分状态。

## 3. 角色与最终权力

### DeepSeek

DeepSeek 是本任务的受限实施 Worker。它负责事实审计、最小代码修改、测试、失败注入、运行证据和交接文件。它不得宣布最终验收通过。

### Codex

Codex 独立读取 diff、重跑测试、复核账本、验证越权情况并作出 `ACCEPT / REWORK / HOLD`。DeepSeek 的 `READY_FOR_CODEX_REVIEW` 只表示提交验收，不表示通过。

### 人类

只有授权人类可以作声音审美、真实音频权利和生产规则晋级决定。任何自动分数或 Worker 都不得替代。

## 4. 修改边界

允许修改：

```text
E:\moodify\moodify-bridge\src\moodify_bridge\
E:\moodify\moodify-bridge\tests\
E:\moodify\moodify-bridge\README.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-PPE-HARDENING-005\
E:\moodify\outputs\deepseek_validation\DSK-MFY-PPE-HARDENING-005\
```

只读，不得修改：

```text
E:\moodify\moodify-bridge\demo\
E:\moodify\outputs\ppe_2026-08-01\
E:\软件建造的哲学\POSC_002_Function_Is_Not_Form_Edition_0.1.pdf
```

禁止：

- 修改 Core、Runtime、DSP、Preset、MRS、历史实验、真实音频或客户资产；
- 修改现有 DuckDB schema/migrations，除非先停止并请求 Codex 重新授权；
- 覆盖、删除或“清理”任何既有运行产物；
- 安装/升级依赖、联网、调用 DeepSeek API 或其他外部服务；
- Git reset/clean/stash/rebase/checkout discard/commit/push/切换分支；
- 以删除测试、放宽断言、吞掉异常或伪造日志获得绿色结果；
- 把工具链通过写成声音改善、商业可交付或生产规则已获批准。

所有现有 dirty/untracked 文件均属于用户。不得还原或整理与本任务无关的改动。

## 5. 必读文件

开始编码前完整读取：

```text
E:\moodify\moodify-bridge\README.md
E:\moodify\moodify-bridge\pyproject.toml
E:\moodify\moodify-bridge\src\moodify_bridge\cli.py
E:\moodify\moodify-bridge\src\moodify_bridge\schemas.py
E:\moodify\moodify-bridge\src\moodify_bridge\serialization.py
E:\moodify\moodify-bridge\src\moodify_bridge\services.py
E:\moodify\moodify-bridge\src\moodify_bridge\store.py
E:\moodify\moodify-bridge\tests\test_schemas.py
E:\moodify\moodify-bridge\tests\test_store_workflow.py
E:\moodify\moodify-bridge\tests\test_metrics.py
E:\moodify\docs\tasks\deepseek\DSK-MFY-THICKNESS-001\00_MASTER_TASK.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-THICKNESS-001\NEXT_HARDENING_TASKS_2026-07-30.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-PPE-HARDENING-005\02_CODEX_ACCEPTANCE_MATRIX.md
```

同时查找并遵守适用的 `AGENTS.md`，记录分支、HEAD、`git status --short`、Python 路径与依赖版本。

## 6. 目标形态

新增一个统一 PPE 基线入口，推荐接口：

```powershell
py -3.12 -m moodify_bridge.cli ppe run demo/case.yaml --output-dir NEW_RUN_DIR
```

如仓库事实证明另一命名更一致，可以调整，但必须在 Batch 0 说明并保持单一入口。

一次成功运行至少生成：

```text
NEW_RUN_DIR/
  run_manifest.json
  environment.json
  command_results.jsonl
  gate_results.json
  evidence.yaml
  ledger/ledger.duckdb
  reports/case.md
  reports/case.html
  FINAL_STATUS.txt
```

要求：

- `--output-dir` 必须是显式的新目录；非空目录默认拒绝，不覆盖历史。
- 输入和 demo 资产只读；运行前后 SHA-256 必须一致。
- 每一步保存命令/动作名、开始结束 UTC、退出码/状态、错误代码和产物路径。
- `FINAL_STATUS` 只能为 `PASS`、`PASS_WITH_WARNINGS` 或 `FAIL`。
- 任一阻断闸门 FAIL 时最终状态必须 FAIL，不能被其他指标抵消。
- 中途失败仍要尽可能生成失败 manifest；不得把部分结果冒充成功。
- 两个全新目录重复运行后，排除时间、UUID、绝对输出路径等声明过的易变字段，其规范化结果必须一致。

## 7. 六闸门数据契约

实现版本化、严格验证的 GateResult；可以作为 Pydantic 模型或等价严格结构，但不得只输出自由文本。

固定闸门 ID：

```text
input_complete
identity_consistent
measurement_available
candidates_comparable
human_approved
report_complete
```

每项至少包含：

```text
schema_version
gate_id
status: PASS | WARN | FAIL
blocking: boolean
reason_code
message
evidence_paths
checked_at
checker_version
```

本合成案例的预期边界：

- 没有音频测量时 `measurement_available=WARN`，不得填充伪测量。
- 没有候选音频比较时 `candidates_comparable=WARN`，不得伪造比较结果。
- 没有生产晋级请求时，`human_approved` 必须表达“NOT_APPLICABLE/PENDING 的语义映射”，不得误报已批准。若状态枚举保持三值，应使用 WARN + 稳定 reason code。
- 身份哈希不匹配必须为阻断 FAIL。
- 报告缺失或产物引用不存在必须为阻断 FAIL。

## 8. 五批串行执行

### Batch 0｜事实冻结与最小设计

1. 记录环境、Git 和基线哈希。
2. 运行现有 10 项测试、Ruff、Mypy，记录真实结果。
3. 重现两个已知语义问题。
4. 写 `00_IMPLEMENTATION_AUDIT.md`：数据流、写入边界、错误模型、确定性字段和最小修改文件。

Gate：未完成事实审计不得编码；若基线测试失败或只读文件已变化，立即 HOLD。

### Batch A｜正确性：闸门与批准语义

1. 实现六闸门结构和聚合规则。
2. 消除 `human_approval=true / approval_id=null` 的歧义；字段必须明确区分“需要批准”和“已有批准”。
3. 保持历史兼容或明确记录兼容策略，并增加回归测试。
4. 检查 `rule promote` 的操作顺序：缺失/无效批准、错误规则版本、非法状态转换、写入失败均不得产生规则文件或 ledger 的部分晋级状态。

Gate：语义测试、无批准测试、错误版本测试、非法转换测试全绿。

### Batch B｜失败形式：稳定错误与统一运行器

1. 为用户输入错误提供稳定 reason/error code 和简洁 CLI 消息。
2. 缺失批准、缺失 manifest、无效 YAML、输出目录非空等预期错误不得显示 Python traceback。
3. 实现统一 PPE 入口和完整运行产物。
4. 所有子步骤失败都进入 `command_results.jsonl` 和最终 manifest。

Gate：成功 smoke 与至少四类 CLI 失败 smoke 全部满足退出码、错误码、无 traceback 和无越权写入。

### Batch C｜重复性、故障注入与恢复

1. 在两个全新输出目录运行相同案例，比较规范化产物。
2. 自动化测试资产缺失、哈希失配、报告阶段失败、重复目录、批准缺失/错误版本和非法转换。
3. 证明失败记录不覆盖此前 PASS；重试必须进入新目录并保留失败现场。
4. 证明 demo 源资产、8 月 1 日产物和历史账本哈希不变。

Gate：确定性比较通过；所有故障有稳定分类；没有混合成功/失败状态。

### Batch D｜兼容、继承与交接

1. 运行 bridge 全量测试、Ruff、Mypy，两次成功 smoke 和失败矩阵。
2. 更新 README，给出单入口、产物契约、状态语义、失败恢复和限制。
3. 生成 `VALIDATION_REPORT.md`、`FAILURE_LEDGER.md`、`HANDOFF.md`。
4. 对允许路径执行 diff/文件清单审计；记录未运行项和原因。
5. 最终只可写 `READY_FOR_CODEX_REVIEW`、`REWORK` 或 `HOLD`。

Gate：后来者只读 README/HANDOFF 即可在新目录复现；DeepSeek 完成交接后停止，等待 Codex 独立验收。

## 9. 必须新增或覆盖的测试语义

- GateResult 严格 schema、未知字段拒绝、固定枚举和阻断聚合。
- 无测量、无候选、无晋级请求不会被写成 PASS 伪事实。
- 缺失/无效批准不会改变规则文件、approval 表或规则状态。
- 非法转换不会先写 approval 再失败。
- 预期 CLI 错误无 traceback、退出码非零、错误码稳定。
- 新/非空输出目录行为明确。
- 成功 manifest 引用的文件全部存在且哈希匹配。
- 失败 manifest 不包含虚假成功声明。
- 同输入双运行的规范化结果一致。
- 只读基线运行前后哈希一致。

## 10. DeepSeek 必须交付

```text
docs/tasks/deepseek/DSK-MFY-PPE-HARDENING-005/
  00_IMPLEMENTATION_AUDIT.md
  PROGRESS.md
  VALIDATION_REPORT.md
  FAILURE_LEDGER.md
  HANDOFF.md

outputs/deepseek_validation/DSK-MFY-PPE-HARDENING-005/
  run_a/...
  run_b/...
  failure_matrix/...
  normalized_comparison.json
  readonly_hashes_before.json
  readonly_hashes_after.json
```

代码和测试放入允许的 bridge 目录。不得把生成产物放入 `moodify-bridge/demo` 或覆盖 `outputs/ppe_2026-08-01`。

## 11. 失败与停止规则

出现以下任一情况立即停止并判定 HOLD：

- 只读资产哈希变化；
- 修改允许范围外文件；
- 需要修改数据库 migration/schema 才能继续；
- 无法解释的基线回归；
- 需要联网、安装依赖或真实音频；
- 无法证明失败不会留下部分晋级状态。

失败报告必须包含：批次、命令、退出码、完整错误、已修改文件、只读哈希、Git 状态和唯一安全后续动作。

## 12. 完成定义

DeepSeek 只能在以下全部成立时提交 `READY_FOR_CODEX_REVIEW`：

1. Batch 0/A/B/C/D 全部通过；
2. 统一入口和六闸门成为机器可检查结构；
3. 已知批准语义和 traceback 问题已被测试保护；
4. promotion 不存在已知部分状态路径；
5. 双运行规范化一致；
6. 失败矩阵完整且只读资产哈希不变；
7. 全量测试、Ruff、Mypy 通过；
8. HANDOFF 包含精确复现和 Codex 验收命令。

最终完成权属于 Codex，不属于 Worker。

