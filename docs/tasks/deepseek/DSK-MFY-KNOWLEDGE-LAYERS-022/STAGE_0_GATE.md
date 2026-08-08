# STAGE 0 GATE｜三层盘点与合同冻结（2026-08-02）

## 判定：PASS ✅

### 1. 素材盘点（真实，可核对）

| 层 | 素材 | 数量 | 来源位置 |
|---|---|---|---|
| 原理 | ADR-001~004 | 4 | `docs/decisions/` |
| 原理 | 工程厚度标准 MFY-ETS-001 | 1 | `docs/strategy/MOODIFY_ENGINEERING_THICKNESS_STANDARD.md` |
| 原理 | POSC-003 地质记录原则 | 1 | `E:\软件建造的哲学\markdown\POSC_003_*.md` |
| 原理 | 能力引力井论文（工具拥有执行、Moodify 拥有解释权） | 1 | 用户提供文档 DSK-MFY-CAPABILITY-ACCRETION-001 |
| 原理 | 009 合同（推断不冒充事实） | 2 | `DSK-MFY-SCORE-ENGINE-009/MOODIFYSCORE_CONTRACT.md`、`SCORE_BACKEND_CONTRACT.md` |
| 经验 | Failure and Boundary Ledger | 4 | `docs/standards/FAILURE_LEDGER.md` (FL-001~004) |
| 经验 | 009 失败台账 | 10 | `DSK-MFY-SCORE-ENGINE-009/FAILURE_LEDGER.md` (1-10) |
| 经验 | 008 限制声明 | 5 | `DSK-MFY-STEM-MIDI-008/HANDOFF.md` Remaining Limitations |
| 经验 | 017 系列环境事实 | 7 | `DSK-MFY-CAPABILITY-ACCRETION-017/00_SERIES_ORCHESTRATION.md` §2 |
| 代码 | 顶层模块清单 | 见右 | `moodify-core-package/src/moodify/`（score_engine、transcription_pipeline、capability_registry 未实现、cli_v2、moodify_runtime 等） |

### 2. 注册表 schema 冻结

**PRINCIPLE_REGISTRY.md 条目结构（PR-0xx）**：

```text
PR-0xx | 原理陈述 | 来源（文档路径/章节/ADR 编号） | 适用范围（模块/阶段） | 关联经验 EX-xxx（可空）
```

**EXPERIENCE_REGISTRY.md 条目结构（EX-0xx）**：

```text
EX-0xx | 失败事实 | 根因 | 边界 | 防复发机制（真实文件/测试/流程） | 关联模块 | 关联原理 PR-xxx（可空）
```

### 3. 引用约定（Stage D 展开）

- 任务包/交接单中引用 `PR-xxx` / `EX-xxx`；
- 新条目必须来自真实失败/真实决策，禁止凑数编造；
- 经验防复发机制必须指向真实文件/测试/流程。

## 结论

素材真实且充足（原理 ≥8 条可提取，经验 ≥10 条可提取），schema 已冻结。
**批准进入 Stage B（原理注册表）。**
