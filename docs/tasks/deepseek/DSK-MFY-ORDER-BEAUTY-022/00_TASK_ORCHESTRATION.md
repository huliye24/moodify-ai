# DSK-MFY-ORDER-BEAUTY-022｜城基：恢复全量测试可信基线

**计划日期：** 2026-08-02  
**执行 Worker：** DeepSeek  
**任务所有者与最终 Judge：** Codex / 授权用户  
**前置依据：** `project_analytics/runs/2026-08-02T094746+0800/overall-project-analysis/`  
**建议投入：** 6–12 小时  
**任务状态：** PLANNED

## 1. 任务意图

高级的秩序不是减少系统拥有的能力，而是让底层承重可靠、故障边界清晰。南京明城墙可以因地制宜，但每一块砖都要能被追溯、检验和替换。本任务只修复 Moodify 的“可信城基”：让全量测试先能够稳定完成收集，再建立可重复的分层测试门禁。

当前证据：

- 2026-08-02 09:43:58 快照：421 个测试、19 个收集错误；
- 任务编写时复核：450 个测试、19 个收集错误；
- 主要错误族：`moodify.domain` 公共导出契约漂移，以及 `pretty_midi` 测试依赖契约不清；
- 在收集错误归零前，不得宣称全量测试基线为绿色。

## 2. 核心目标

1. `pytest --collect-only -q` 退出码为 0，收集错误为 0；
2. 修复领域模型的定义、导出与调用方之间的契约漂移，不用虚假占位对象掩盖问题；
3. 明确 `pretty_midi` 属于必需依赖、测试依赖还是可选能力，并让测试行为与包元数据一致；
4. 建立 fast / core / integration 三层测试命令和证据文件；
5. 生成一份失败族谱，使未来错误按根因聚合，而不是按 19 个表面报错逐个修补。

## 3. 允许范围

```text
moodify-core-package/src/moodify/domain/
moodify-core-package/src/moodify/api/                 # 仅为恢复导入契约
moodify-core-package/tests/
moodify-core-package/pyproject.toml                   # 仅依赖/测试分组与 pytest 配置
moodify-core-package/tools/                           # 测试门禁脚本
docs/testing/
docs/tasks/deepseek/DSK-MFY-ORDER-BEAUTY-022/
outputs/deepseek_validation/DSK-MFY-ORDER-BEAUTY-022/
```

禁止：新增产品功能；大规模领域模型重写；修改音频算法；网络下载；用 `try/except ImportError`、空类、无条件 skip 或删除测试伪造绿灯；Git reset/clean/stash/checkout/commit/push。

## 4. 执行阶段

### Stage A｜建立错误族谱

- 保存全量收集输出、Python 版本、安装模式与依赖可用性；
- 将错误按“缺失定义、缺失 re-export、历史接口漂移、可选依赖、测试环境”聚类；
- 为每一族确定唯一根因、受影响测试和最小修复面；
- 记录初始测试数，不把测试数短暂波动误判为成功。

### Stage B｜恢复领域契约

- 逐项核对 `AudioProject`、`ApprovalActorType`、`ProjectThread`、`TreatmentAction` 等符号的真实定义与公共导出；
- 若实现仍存在，恢复明确 re-export；若实现已被替代，迁移测试和调用方到唯一当前模型；
- 禁止同时保留两个含义不同但同名的领域对象；
- 增加公共 API 合约测试，保证导出表稳定且循环导入不复发。

### Stage C｜明确依赖契约

- 决定 `pretty_midi` 的依赖层级并写入包元数据和测试说明；
- 可选能力必须在能力边界处显式降级，不能在测试收集阶段随机失败；
- 不允许现场联网安装作为交付证据。

### Stage D｜建立分层门禁

- `collect`：全量收集必须通过；
- `fast`：无外部二进制、无真实音频、适合每次改动；
- `core`：领域、服务、CLI/API 合约；
- `integration`：允许显式环境条件，但跳过原因必须可审计；
- 输出每层命令、耗时、通过/失败/跳过数和失败族摘要。

## 5. P0 验收门槛

- `py -3.11 -m pytest --collect-only -q` 退出码 0、收集错误 0；
- 不得通过减少测试文件、静默吞掉导入错误或扩大 skip 达成；
- 领域公共 API 合约有自动化测试；
- fast 层连续运行两次结果一致；
- 所有仍失败的执行期测试都有根因分类和后续处置，不与收集失败混写；
- 交付 `PROGRESS.md`、`VALIDATION.md`、`FAILURE_LEDGER.md`、`HANDOFF.md`。

## 6. 停止条件

需要删除历史测试、改写范围外核心算法、安装新系统组件、联网下载、修改真实歌曲资产或覆盖用户现有改动时，立即停止并提交 `SCOPE_CHANGE_REQUEST.md`。最终状态只能是 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。

