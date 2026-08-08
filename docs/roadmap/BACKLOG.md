# Moodify v0.4 Backlog

## 前 10 个立即执行任务

1. FND-001 核验并提交 v0.4 审计/定位/ADR（P0/S）。
2. CASE-001 为 bridge 外部可读 ID 加唯一约束与生成器（P0/M）。
3. CASE-002 编写 core `ProcessResult`→ProductionCase adapter（P0/M）。
4. CASE-003 编写 Runtime job→CaseEvent adapter（P0/M）。
5. WSE-001 建 metric registry（定义/单位/backend/confidence）（P0/M）。
6. WSE-002 纠正 proxy loudness 命名并加兼容字段（P0/S）。
7. WSE-003 用合成信号交叉验证所有 bridge adapters（P0/M）。
8. GOLD-001 建授权/合成 Golden Set manifest（P0/M）。
9. REP-001 统一 before/after/case report（P0/M）。
10. INT-001 跑通一例真实入口→ledger→report 回归（P0/M）。

## 90 天具体任务

| ID | Epic | 类型 | 任务/交付 | 测试与验收 | 依赖 | Pri | Effort | 状态 |
|---|---|---|---|---|---|---|---|---|
| FND-001 | 01 | Doc | v0.4审计、定位、架构、ADR | 链接/状态/Mermaid检查 | - | P0 | S | Done |
| FND-002 | 01 | Task | 统一版本与状态词典 | README/package/report无冲突 | FND-001 | P0 | M | Planned |
| CASE-001 | 02 | Feature | 外部ID生成/唯一约束 | unit：格式、重复、并发 | FND-001 | P0 | M | Planned |
| CASE-002 | 02 | Feature | core结果adapter | integration：不改源、hash一致 | CASE-001 | P0 | M | Planned |
| CASE-003 | 02 | Feature | Runtime事件adapter | failure/rollback append | CASE-001 | P0 | M | Planned |
| CASE-004 | 02 | Test | revision与schema migration回归 | 旧case可读 | CASE-001 | P0 | M | Planned |
| WSE-001 | 03 | Feature | metric registry | 全字段定义/单位/version | CASE-001 | P0 | M | Planned |
| WSE-002 | 03 | Task | proxy/standard指标分离 | 近似值不名为LUFS/TP | WSE-001 | P0 | S | Planned |
| WSE-003 | 03 | Test | 合成信号夹具 | peak/gain/corr/residual精确 | WSE-001 | P0 | M | Planned |
| WSE-004 | 03 | Feature | 标准响度backend | 参考工具容差 | WSE-001 | P1 | L | Planned |
| WSE-005 | 03 | Feature | section evolution | section轨迹可重放 | MSE-003 | P1 | L | Planned |
| MSE-001 | 04 | Feature | BPM/beat adapter | 标注集误差分布 | CASE-001 | P1 | L | Planned |
| MSE-002 | 04 | Feature | key estimate adapter | accuracy/confusion/null | CASE-001 | P1 | M | Planned |
| MSE-003 | 04 | Feature | section candidate+correction | boundary F1、人审保留 | MSE-001 | P1 | L | Planned |
| MSE-004 | 04 | Feature | lyrics timeline interface | 无歌词明确null | CASE-001 | P1 | M | Planned |
| MSE-005 | 04 | Research | melody/MIDI实验接口 | 不进入production gate | MSE-001 | P3 | XL | Planned |
| TRT-001 | 05 | Task | stage/version adapter | 现有DSP输出不变 | CASE-002 | P1 | M | Planned |
| TRT-002 | 05 | Test | pipeline deterministic config | 参数/versions相同 | TRT-001 | P0 | M | Planned |
| CAND-001 | 06 | Feature | Experiment/Candidate registry | 多候选不覆盖 | TRT-001 | P1 | L | Planned |
| CAND-002 | 06 | Task | 受限参数网格 | bounds与停止条件 | CAND-001 | P1 | M | Planned |
| CAND-003 | 06 | Test | 候选失败保留 | invalid candidate仍可查 | CAND-001 | P1 | S | Planned |
| EVAL-001 | 07 | Feature | 四类Evaluation schema/API | 评分null与protocol版本 | WSE-001,CAND-001 | P0 | L | Planned |
| EVAL-002 | 07 | Feature | Decision registry | 只能选已登记候选 | EVAL-001 | P0 | M | Partial |
| GATE-001 | 07 | Feature | 六项PPE门禁 | PASS/WARN/FAIL evidence | EVAL-001 | P0 | L | Planned |
| GATE-002 | 07 | Test | 失败阻断deliverable | regression | GATE-001 | P0 | M | Planned |
| LOOP-001 | 08 | Feature | Theory Note关联 | decision/evidence必填 | EVAL-002 | P0 | M | Planned |
| LOOP-002 | 08 | Feature | Rule registry兼容Craft | 状态映射不自动晋级 | LOOP-001 | P0 | L | Planned |
| LOOP-003 | 08 | Test | 人批与Golden回归门 | 无approval/失败则拒绝 | LOOP-002 | P0 | M | Partial |
| ASSET-001 | 09 | Feature | Deliverable manifest | hash/rights/reports完整 | GATE-001 | P1 | M | Planned |
| ASSET-002 | 09 | Doc | Music Asset Package规范 | 缺失结构显式标记 | ASSET-001 | P1 | S | Planned |
| BATCH-001 | 10 | Feature | batch case runner | job隔离/可恢复 | CASE-003 | P1 | L | Planned |
| BATCH-002 | 10 | Test | 中断恢复/幂等 | 不重复覆盖 | BATCH-001 | P1 | M | Planned |
| COST-001 | 10 | Feature | runtime/human/cost tracking | 单位和范围明确 | BATCH-001 | P1 | M | Planned |
| HUMAN-001 | 11 | Doc/Test | A/B/C预注册协议 | 盲听/随机/分组 | EVAL-001 | P1 | M | Planned |
| HUMAN-002 | 11 | Experiment | 小规模pilot | 报告分布和失败 | HUMAN-001 | P1 | L | Planned |
| HUMAN-003 | 11 | Experiment | 扩展benchmark | 不从单例外推 | HUMAN-002 | P1 | XL | Planned |
| REL-001 | 12 | Task | v0.4 release checklist | 全路径、tests、privacy | 全部P0 | P1 | M | Planned |
| REL-002 | 12 | Doc | runbook/changelog | 新旧入口明确 | REL-001 | P1 | S | Planned |

## 当前关键路径

FND-001→CASE-001→CASE-002→WSE-001→GOLD-001→CAND-001→EVAL-001→GATE-001→LOOP-002→LOOP-003→REL-001。

## 可并行工作

MSE-001/002 可与 WSE registry 并行；Human protocol 可与 candidate registry 设计并行；Asset Package 规范可在 gate 实现期间编写；文档链接检查可持续运行。

## 当前不应该做

重写DSP、消费者GUI、完整自动扒谱、训练自学习模型、自动production规则晋级、扩张大量preset、无预注册“优于人工”宣传、提交客户/私有/大音频。

