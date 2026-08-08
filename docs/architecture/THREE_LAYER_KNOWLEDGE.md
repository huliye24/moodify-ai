# Moodify 三层知识结构（THREE_LAYER_KNOWLEDGE）

**Created:** 2026-08-02  
**任务来源：** DSK-MFY-KNOWLEDGE-LAYERS-022  
**Status:** 现行约定

## 1. 三层定义

Moodify 的知识组织为三层，每层回答一个问题：

```text
原理层（为什么必须这样）      docs/standards/PRINCIPLE_REGISTRY.md
   ↑ 约束/授权
工程经验层（哪次失败教会我）  docs/standards/EXPERIENCE_REGISTRY.md
   ↑ 防复发/边界
代码功能层（现在是什么）      moodify-core-package/src/ + tests/
```

| 层 | 回答 | 注册表/载体 | 条目格式 |
|---|---|---|---|
| 原理层 | 为什么必须这样 | `PRINCIPLE_REGISTRY.md` | `PR-0xx` + 陈述 + 来源 + 适用范围 + 关联经验 |
| 经验层 | 哪次失败教会我 | `EXPERIENCE_REGISTRY.md` | `EX-0xx` + 失败事实 + 根因 + 边界 + 防复发机制 + 关联模块 + 关联原理 |
| 代码层 | 现在是什么 | src/ + tests/ | —（文档层只读引用，不写入代码） |

## 2. 层间关系

- **原理 → 经验**：原理约束经验的取舍（如 PR-007 要求失败不可删除，所以经验条目只追加）。
- **经验 → 代码**：经验的防复发机制落地为代码规则/测试/流程（如 EX-003 落地为 009 backend 分两次 argv 调用）。
- **代码 → 经验 → 原理**：代码中的一条规则应能向上回答"哪次失败教会我"（EX）与"为什么必须这样"（PR）。

## 3. 维护规则

1. **新条目必须真实**：来自真实失败（FAILURE_LEDGER/交接单/审计）或真实决策
   （ADR/战略/架构文档/哲学文献）；禁止为凑数量编造。
2. **编号连续**：PR-0xx / EX-0xx 递增，无重复。
3. **来源可核对**：条目必须携带可定位来源（文档路径/章节或 ADR 编号），
   Codex 或任何执行者能逐条核对。
4. **不可删除，只可 superseded**：已生效条目不得删除或改写（PR-007 失忆
   防护）；修正以新版本条目 + `superseded` 标注。
5. **经验防复发机制必须指向真实对象**：真实文件/测试/流程，禁止笼统写
   "已修复"。

## 4. 引用约定（任务包/交接单）

- 任务包 00_TASK_ORCHESTRATION 的 P0 门禁应声明本包受哪些原理约束
  （`PR-xxx`）与涉及哪些经验边界（`EX-xxx`）。
- 交接单（HANDOFF）应引用本包新建/触碰的 PR/EX 条目。
- 新发现失败必须：写 FAILURE_LEDGER → 在 EXPERIENCE_REGISTRY 登记 →
  关联原理。

## 5. 反向索引方法

- 从代码找知识：以模块名（如 `score_engine/musescore_backend`）查
  EXPERIENCE_REGISTRY 的"关联模块"字段 → 由 EX 的"关联原理"上溯 PR。
- 从原理找代码：以 PR 的"适用范围"查注册表 → 经验 → 防复发机制的
  文件/测试路径。
- 更新注册表时如涉及既有条目，检查其"关联"字段是否已过期（如 EX-011
  环境事实需随重新探测更新）。

## 6. 与既有账本的关系

- FAILURE_LEDGER（FL-xxx）：原始失败台账，逐失败详细记录——EX 注册表是
  它的**可引用摘要层**（每个 EX 有 FL 来源或任务台账来源）。
- STANDARD_EVOLUTION_LEDGER / CRAFT_EVIDENCE_LEDGER：分别记录标准演化与
  工艺证据——与 PR/EX 注册表互补，不重复。
- 三层结构不取代任何既有账本，只提供跨账本的引用入口。
