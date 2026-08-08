# DSK-MFY-ORDER-BEAUTY-024｜失败台账

**日期：** 2026-08-02 UTC  
**规则：** 历史失败不得删除或改写为成功（PR-007）。

| # | 阶段 | 失败 | 根因 | 处置 |
|---|---|---|---|---|
| 1 | Stage C | enforcer 报 2 个违例（api_cli → runtime） | api/main.py 确实直接导入 moodify_runtime——**真实穿墙点**（既有债务，非本次新增） | 登记为 documented exception EXC-002（期限 2026-10-01 + 移除条件），债务只降不升 |
| 2 | Stage A | EXC-001 定义为 services→processing 例外，但 archive.py 实际只导入 domain/storage | manifest 凭印象声明，未核对真实导入 | 用 enforcer + AST 核对，删除虚假例外 EXC-001——**检查器暴露了 manifest 过度声明** |
| 3 | 测试 | counterexample 测试断言 `forbidden_deps[0]` 失败 | domain 的 forbidden_deps[0] 是 services 而非 processing | 改为 `any(...)` 检查整个列表 |

## 负面知识沉淀

- **manifest 必须由检查器验证**：围护图声明不能凭印象——EXC-001 是虚假
  例外（archive.py 从不导入 processing），检查器自动核对后才暴露。
- **真实穿墙点登记为有期限债务**：api→runtime 是既有事实，强行重构会动
  承重区——先登记（expiry + remove_condition），择机处理。

## 边界

- EXC-002（api_cli→runtime）是唯一既有穿墙点，2026-10-01 到期。
- 未触碰 moodify_runtime（编排明确默认只读）。
- **moodify-bridge 收集隔离**：从仓库根跑 `pytest --collect-only` 会把
  moodify-bridge/tests（9 个文件，依赖 typer/moodify_bridge 未装）纳入并报错。
  022 门禁的正规入口是 **package 目录内**（pyproject testpaths=["tests"]）——
  那里 662 collected 0 errors 保持绿色。仓库根收集的 10 个错误是
  bridge 项目隔离问题（其 pyproject 未配置 testpaths），非 024 回归；
  由 025 观测系统或 bridge 项目自身处理。
