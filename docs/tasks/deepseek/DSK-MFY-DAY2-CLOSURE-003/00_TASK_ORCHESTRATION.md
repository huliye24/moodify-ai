# DSK-MFY-DAY2-CLOSURE-003｜第二天验证基线封口审查

**日期：2026-07-31**  
**任务所有者与最终 Judge：Codex / 授权用户**  
**执行 Worker：DeepSeek（用户手动发送执行命令）**  
**状态：READY FOR EXECUTION**  
**性质：只读审查、隔离重放、机械验证；不是产品开发任务**

## 1. 目标

独立验证 Moodify 第二天交付是否满足以下标准：

> 即使换一名执行者从头重做，也能使用同一输入、同一权利边界、同一协议和明确命令，得到可解释、可审计且不掩盖失败的结果。

DeepSeek 负责繁琐但必要的证据核对、重放测试、协议一致性检查和问题分级。DeepSeek 不负责声音审美、产品边界、权利授权、门限修改、Preset 调参、第三天工作或最终验收。

## 2. 当前已知事实

1. VSR-001 已由用户确认，VS-001 至 VS-005 仅可用于内部验证。
2. 验证集 v0.1 已冻结，5 个源文件具有路径、元数据和 SHA-256。
3. 盲听协议 v0.1 已冻结。
4. VS-001 使用 `warm_vocal` 完成一次正式试跑。
5. 当前试跑技术门禁为 `FAIL`：
   - 动态范围变化：`-7.61 dB`；
   - 风险标志：`dynamic_damage`；
   - MRS proxy 变化：`+24.82`，不得覆盖硬失败。
6. 当前人工盲听仍为 `PENDING`。
7. 本任务不进入第三天，不运行其余 4 首音频。

## 3. 权威输入

必须完整读取：

```text
E:\moodify\docs\product\MOODIFY_WEEKLY_EXECUTION_2026-08-03.md
E:\moodify\docs\product\daily\2026-07-30\CURRENT_EXECUTION_BASELINE.md
E:\moodify\docs\product\daily\2026-07-30\ASSET_INVENTORY.md
E:\moodify\docs\product\daily\2026-07-30\VALIDATION_SET_RIGHTS_GATE.md
E:\moodify\docs\product\daily\2026-07-30\validation_set_rights.json
E:\moodify\docs\product\daily\2026-07-31\VALIDATION_SET_V0.1.md
E:\moodify\docs\product\daily\2026-07-31\LISTENING_PROTOCOL_V0.1.md
E:\moodify\docs\product\daily\2026-07-31\TRIAL_PREFLIGHT_REPORT.md
E:\moodify\docs\product\daily\2026-07-31\DAILY_GATE_REPORT.md
E:\moodify\outputs\daily_runs\20260731_vs001_trial
```

同时检查以下实现入口，不得仅依赖文档：

```text
E:\moodify\moodify-core-package\src\moodify\cli.py
E:\moodify\moodify-core-package\src\moodify\v01_pipeline.py
E:\moodify\scripts\v01_inspector.py
E:\moodify\scripts\v01_create_treatment_record.py
```

## 4. 执行批次

必须按 A → B → C → D 串行执行。任一批出现证据污染、源文件变化或越权风险，立即停止并记为 `HOLD`。

### Batch A｜静态证据完整性审计

逐项核验：

1. VSR-001 Markdown 与 JSON 的确认人、时间、范围、单项状态一致；
2. 5 个源文件存在、可读，实际 SHA-256 与验证集清单一致；
3. 格式、采样率、声道、时长和大小与登记值一致；
4. VS-001 运行目录中关键 JSON 均能以 UTF-8 解析；
5. Process manifest 内每个产物的路径、大小和 SHA-256 与实际文件一致；
6. Metadata 中输入哈希、Git hash、分支、Python 和依赖版本可定位；
7. Treatment Record 的输入、输出、Inspector 与响度匹配路径均存在；
8. 报告中的 `dynamic_damage`、`-7.61 dB`、`+24.82` 与机器文件一致；
9. A.wav 与源文件同哈希，B.wav 与 `after_matched.wav` 同哈希；
10. 映射种子、种子哈希、首字节和 A/B 规则可独立重算。

输出：`AUDIT_A_EVIDENCE_INTEGRITY.md`。

### Batch B｜协议与门禁一致性审查

审查但不擅自改规则：

1. 盲听评分语义在不知道 A/B 身份时是否无歧义；
2. “1—5 分”究竟表示 B 相对 A，还是处理版相对原版；
3. 映射文件是否与评分材料充分隔离；
4. 响度匹配 `0.2 dB` 门限、测量精度和边界等号是否一致；
5. FFmpeg 一位小数输出是否足以证明“不超过 0.2 dB”；
6. 技术硬失败是否在所有文档中保持失败，没有被 MRS 上升冲销；
7. `DAY 2 PASS` 是否明确只表示“验证集与协议可执行”，而非声音结果通过；
8. 人工评分 `PENDING` 是否在所有相关文件中一致；
9. 是否存在路径泄露身份、提前揭盲或评分后可静默修改的问题；
10. 当前协议是否说明评分记录的不可覆盖和揭盲追加方式。

不得自行改变 `0.2 dB`、`-4 dB`、评分尺度或任何产品门禁。发现歧义时给出最小修订建议和影响分析，交由 Codex 决策。

输出：`AUDIT_B_PROTOCOL_REVIEW.md`。

### Batch C｜隔离重放与可复现性测试

只允许使用 VS-001，禁止运行 VS-002 至 VS-005。

隔离输出根：

```text
E:\moodify\outputs\deepseek_validation\DSK-MFY-DAY2-CLOSURE-003
```

规则：

1. 运行前记录源文件哈希、Git HEAD、分支和 `git status --short`；
2. 禁止覆盖 20260731 原运行目录；
3. 使用当前权威 CLI，以 `warm_vocal` 重放 VS-001；
4. 运行 Inspector 并写出响度匹配副本；
5. 创建隔离 Treatment Record；
6. 记录每条命令、工作目录、开始/结束时间、退出码和运行时长；
7. 重放后再次校验源文件哈希；
8. 比较原运行与重放：
   - 输出音频 SHA-256；
   - 样本率、声道、时长；
   - 关键 Before/After/Delta 指标；
   - `passed`、risk flags、MRS、damage loss；
   - manifest 的稳定字段和预期非稳定字段；
9. 若音频哈希不同，不得直接判失败或通过；必须定位随机性、浮点、依赖、代码状态或元数据差异；
10. 不试听、不填写人类听感、不修改 Preset。

输出：

```text
AUDIT_C_REPLAY_LOG.md
AUDIT_C_REPRODUCIBILITY_COMPARISON.md
```

### Batch D｜独立审查与分级

按以下等级汇总所有发现：

- `P0`：证据错误、源文件变化、权利越界、结果被错误宣布通过；
- `P1`：无法可靠重放、哈希或指标不一致且无解释、盲听身份泄露；
- `P2`：协议歧义、记录不充分、工具精度不足；
- `P3`：措辞、导航或低风险可维护性问题。

每条发现必须包含：

1. 证据文件与字段/行；
2. 可复现命令；
3. 实际结果；
4. 风险；
5. 最小修订建议；
6. 是否需要 Codex/用户判断。

最终只能给出：

- `PASS`：没有 P0/P1，且重放结果可解释；
- `REWORK`：存在可修复的 P1/P2；
- `HOLD`：权利、源文件、证据污染或关键输入不可信。

输出：`HANDOFF.md`。

## 5. 允许写入

仅允许写入：

```text
E:\moodify\docs\tasks\deepseek\DSK-MFY-DAY2-CLOSURE-003\
E:\moodify\outputs\deepseek_validation\DSK-MFY-DAY2-CLOSURE-003\
```

允许在任务目录创建审查文档、日志和机器可读汇总；允许在隔离输出目录产生 VS-001 重放产物。

## 6. 禁止事项

- 不修改产品代码、测试、Preset、算法、MRS、门限或协议正文；
- 不修改 2026-07-30、2026-07-31 的现有文档与原运行产物；
- 不处理 VS-002 至 VS-005；
- 不听音频、不代替人工填写评分；
- 不作权利确认、艺术判断或产品判断；
- 不进入第三天工作；
- 不删除、移动、重命名或覆盖用户资产；
- 不使用 Git reset、clean、stash、rebase、checkout-discard；
- 不提交、不推送、不切分支、不联系远程；
- 不安装或升级依赖；
- 不把自动测试写成 `PRODUCTION-PROVEN`、专业听感通过或商业可用。

## 7. 证据要求

所有结论必须来自当前实际运行，不得引用旧测试数字代替。命令需记录：

```text
工作目录
完整命令
开始时间
结束时间
退出码
通过/失败/跳过数
关键输出
产物路径
```

长日志不整段复制进 Markdown；保存原始日志并在报告中写摘要与失败摘录。

## 8. 最终交接

`HANDOFF.md` 必须包含：

1. A—D 四批状态；
2. 实际写入文件；
3. 原始与重放音频哈希；
4. 指标差异表；
5. 所有发现及等级；
6. 哪些事实已验证，哪些仍未验证；
7. 明确说明自动测试不能证明听感；
8. 需要 Codex 决策的问题；
9. 唯一下一动作。

完成 `HANDOFF.md` 后停止，不继续修复。最终终端回复不超过 20 行，只报告总判定、P0/P1/P2/P3 数量和交接文件路径。

