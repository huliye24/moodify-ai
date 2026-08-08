# DSK-MFY-ORDER-BEAUTY-025 Progress

**Status:** READY_FOR_CODEX_REVIEW  
**依赖：** DSK-MFY-ORDER-BEAUTY-022/023/024 ACCEPTED（本机执行完成后由 Codex 验收）

| Stage | Status | Gate | Evidence |
|---|---|---|---|
| Stage A｜指标契约与输入模板 | PASS | PASS (2026-08-02) | metric_contracts.json v0.2（15 指标 + 2 schema + 历史回放） |
| Stage B｜只读采集器 | PASS | PASS (2026-08-02) | observability.py（复用 022/023/024，PARTIAL，确定性） |
| Stage C｜三种报告节奏 | PASS | PASS (2026-08-02) | reports.py weekly/stage/special（JSON+MD+manifest） |
| Stage D｜趋势与决策规则 | PASS | PASS (2026-08-02) | trend_rules.py（三红线 + 决策） |
| Stage E｜回放与收口 | PASS | PASS (2026-08-02) | 首次观测 + 28/28 测试 + HANDOFF |

## 阶段记录（2026-08-02 UTC）

- **Stage A**：metric_contracts v0.2——15 指标含公式/单位/来源/刷新频率/
  owner/限制/红线标记；task_investment（planned vs active/wait/rework/
  machine 分离）+ user_value（聚合级、无个人行为）schema；0.1 定义保留；
  historical_snapshot_2026_08_02 保留 421/19、57.1%、83.6%、55/140。
- **Stage B**：只读采集器复用 022 门禁/023 账本/024 边界；采集失败标记
  PARTIAL；metrics 双运行一致（测试）；run_id/时间戳与数据主体分离。
- **Stage C**：weekly（可信度/冲突/工作区/违例/WIP）、stage（投入/返工/
  传播/首次验收/水平化）、special（迁移/事故/异常）——JSON+MD+manifest。
- **Stage D**：三红线（收集错误/状态冲突/边界违例）+ 观察项（集中度/边/
  循环）+ 决策（RESUME/CONTINUE/TRIGGER）——不自动干预。
- **Stage E**：首次观测 complete（0 红线）→ RESUME_DEVELOPMENT；未测量项
  全部 NOT_MEASURED 诚实标注（含 horizontalization EVIDENCE_INSUFFICIENT）。
- 深度维持验收：观测层零写入；历史不可覆盖；红线不自动干预；
  3 条失败（解析正则/fixture 目录/ROOT 污染）入台账，测试隔离用 monkeypatch。