# DSK-MFY-ORDER-BEAUTY-023｜失败台账

**日期：** 2026-08-02 UTC  
**规则：** 历史失败不得删除或改写为成功（PR-007）。

| # | 阶段 | 失败 | 根因 | 处置 |
|---|---|---|---|---|
| 1 | Stage A | 导入事件同一时间戳导致 gate 报 4 个"非法跳转" | 所有导入事件用同一 `now`，时间戳排序任意 | 每任务按逻辑序分配递增合成时间戳（orch<handoff<acceptance）；gate 放宽导入历史的信息缺口（PLANNED→ACCEPTED 合法、多 acceptance 文件合法） |
| 2 | Stage B | git status 中文路径转义（`\\NNN` 八进制）导致 UNKNOWN | git 默认 quotepath=true，text 层解码后反斜杠混乱 | `-c core.quotepath=false` 直接输出原始 UTF-8，彻底绕开转义 |
| 3 | Stage B | `.idea/`、中文目录（实验图库/投资ppt/研究论文）未归桶 | 桶规则未覆盖 | 补充 generated/.idea + research_assets/中文目录规则；UNKNOWN 42→14→7→1→0 |
| 4 | 测试 | 5 个测试失败 | 测试辅助函数用固定 event_id/时间戳，silent_downgrade 场景构造错误；duplicate 测试与 append 拒绝重复 | 辅助函数支持 seq/ts 参数；duplicate 测试改为验证 append 拒绝 |

## 负面知识沉淀

- **git quotepath 教训**（EX-009 模式）：Windows 中文路径在 git status 中
  以 `\NNN` 八进制转义，text 层解码不可靠——用 `-c core.quotepath=false`
  让 git 直接输出原始 UTF-8，这是最可靠方案。
- **时间戳排序陷阱**：事件流的逻辑顺序（事实顺序）不能依赖导入时刻的
  单一时间戳——必须为每个事件分配反映事实顺序的时间戳。

## 边界

- 导入事件的证据来自文件存在性与 handoff status 行，非真实时间线；
  真实时间线需人工/工具后续补充 reconciliation 事件。
- 在制品上限（5）是告警阈值，不自动关闭任务（023 §Stage D 明确）。
