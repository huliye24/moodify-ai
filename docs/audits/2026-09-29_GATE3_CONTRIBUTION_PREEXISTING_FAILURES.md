# GATE-3 失败转交单：Contribution 域 17 个预存失败

**日期：** 2026-09-29
**发现于：** Mix Graph v0.1 工程包落地四道门（Gate 3 全量 pytest）
**性质：** 预存失败（PRE-EXISTING），非本包引入。本包按纪律不越权修复，转交域负责人裁决。

## 1. Gate 3 快照

```text
17 failed, 1072 passed, 5 skipped, pytest exit 1（真实退出码）
耗时 375 s（LSM parallel=1，i7-7500U / 12GB）
```

17 个失败 100% 集中在 contribution 域两个测试文件：

- `tests/contribution_test.py` — 13 failed（ContributionCore 9、Validator 2、Scorer 1、StateMachine 1）
- `tests/integration/test_complete_workflow.py` — 4 failed

## 2. 归因证据（三条独立线索）

1. **同 commit 自相矛盾**：`moodify/contribution/` 与上述两个测试文件均由 commit `4f2b2386`（MPF-002 Contribution Core Python mirror）引入。示例矛盾：状态机代码允许 `rejected → under_review`，而 `test_workflow_state_machine_constraints` 断言 rejected 状态允许转移数为 0。
2. **环境无关**：contribution 模块源码不 import pydantic/httpx；本次同步的两个依赖（pydantic 2.5.0→2.13.2、httpx 0.28.1→0.27.2）对该域零接触。失败均为断言级域逻辑不一致，非导入/版本错误。
3. **历史基线声明**：`docs/REPOSITORY_STATUS.md` 早已注明历史验证基线与当前专题分支不一致；本分支全量从未在本机跑绿过。

## 3. 需要的裁决（HUMAN_DECISION_REQUIRED）

矛盾的正向语义必须由域负责人拍板，二选一：

| 选项 | 含义 | 修复动作 |
|---|---|---|
| A：rejected 为终态（吸收态） | 拒绝后不可复活，重新提交须走新 contribution | 改 `moodify/contribution/` 状态机 |
| B：rejected 可回 under_review | 允许复审翻案 | 改两个测试文件的断言 |

外加：`contribution_test.py` 另有 12 个失败需逐个核对是同一根因（状态机变更涟漪）还是独立问题，修 A/B 后重跑确认。

## 4. 复现

```bash
cd moodify-core-package
PYTHONPATH=src python -m pytest tests/contribution_test.py tests/integration/test_complete_workflow.py -q --tb=short
```

## 5. 本包（Mix Graph v0.1）自身门状态

- Gate 1 ruff：绿（src + tests + release_cli）
- Gate 2 `pytest -m v01`：169 passed, 5 skipped
- canon_guard + 守卫测试：PASSED + 6/6
- Gate 3 全量：除上述 17 个预存失败外，**本包新增 0 失败**（1072 passed 覆盖全部 43 个 mix_graph 测试）
- Gate 4 GitHub Actions：待 push 后确认
