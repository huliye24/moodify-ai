# DSK-MFY-ORDER-BEAUTY-025｜验证报告

**日期：** 2026-08-02 UTC

## 1. P0 验收门槛对照

| 门槛 | 结果 |
|---|---|
| 每指标有可机器读取契约和限制 | ✅ metric_contracts.json v0.2（公式/单位/来源/刷新频率/owner/限制/红线） |
| 观测层对产品代码/任务状态/工作区零写入 | ✅ 全部只读；观察按 run_id 追加 |
| 历史分析不可覆盖，registry 只能追加 | ✅ observations/ 按时间戳不可覆盖；metric_contracts 保留 0.1 定义 |
| 实测/计划/估算/缺失在 schema 与报告中可区分 | ✅ NOT_MEASURED 显式；planned vs active/wait/rework 分字段 |
| 同一输入连续运行两次数据主体一致 | ✅ collect_all 双运行 metrics 相等（测试） |
| 采集失败标记 PARTIAL | ✅ Collector.partial + status=PARTIAL（测试） |
| 三种报告节奏可复现入口 | ✅ weekly/stage/special 均有 JSON+MD+manifest |
| 2026-08-02 基线可回放 | ✅ metric_contracts.historical_snapshot 保留 421/19、57.1%、83.6%、55/140 |
| 无网络上传/后台监听/个人行为跟踪/新服务 | ✅ 无新依赖，纯标准库脚本 |

## 2. 首次观测（2026-08-02）

| 指标 | 值 | 历史口径（回放） |
|---|---|---|
| 测试收集错误 | 0（662 collected） | 421/19 → 469/19 → 0 |
| 任务状态冲突 | 0 | — |
| 工作区 UNKNOWN | 0（54 tracked/153 untracked） | 55/140 |
| 边界违例 | 0（债务 2 有期限） | — |
| 核心集中度 | 77.5% | 83.6% |
| 验收率 | 39.1%（023 口径） | 57.1%（快照口径，分母不同） |
| 决策 | **RESUME_DEVELOPMENT** | — |

## 3. 红线状态

- test_collection_errors > 0：**false**
- task_state_conflicts > 0：**false**
- enclosure_violations > 0：**false**
- 决策：RESUME_DEVELOPMENT（所有红线清除，观测完整）

## 4. 测试

- `tools/project_governance/test_observability.py`：**8/8 PASS**
  （collector partial/确定性/红线/报告）
- `tools/project_governance/test_governance.py`：**20/20 PASS**（023 回归）
- Ruff：clean

## 5. 未测量项（诚实 NOT_MEASURED）

- first_acceptance_rate：需 ledger 记录首次验收（023 事件已支持，待积累）
- rework_drag / owner_leverage：需任务投入记录（schema 已定义）
- change_propagation_scope：需 task→commit 映射
- horizontalization_judgment：EVIDENCE_INSUFFICIENT（需连续 3+ 阶段窗口）
- 用户价值（D 组）：无数据 → NOT_MEASURED，不推断 ROI
