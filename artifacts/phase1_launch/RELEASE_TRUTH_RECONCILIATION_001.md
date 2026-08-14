# Release Truth Reconciliation — 差异报告

**Document ID:** MFY-RELEASE-TRUTH-001
**Version:** 1.0
**Date:** 2026-08-14
**Package:** MFY_RELEASE_TRUTH_RECONCILIATION_001 (55)
**Executor:** DeepSeek（只读审计 + 文档账本修正；未改产品代码、未部署、未签署 GO）

## 1. 候选标识

```text
Candidate ID:      MFY-PHASE1-RC-20260814-1
Branch:            codex/mfy-data-foundation-001-rev2
HEAD:              9d128588b329dcf7827200fd66c6249d584b4252
Package count:     12（43–54）
Commit count:      13（含 47 先决 088b25e，本包 55 前共 13 个发布 commit）
Tracked dirty:     1（apps/music-web/package-lock.json — 第三方变更，未提交）
Untracked release-relevant: ops/web_origin 部署脚本族、ops/ear_batch、docs/contracts/music/music_public_api.md（见 §4）
Local gates:       Gate A PASS_LOCAL；Gate B–D 组件级 PASS_LOCAL（见 §6）
Live gates:        ALL NOT_RUN（真机部署/验证归 59–61/65）
Blocking risks:    R06（PolarDB 凭据/VPC 对等，58 包解除）
Next package readiness: 56（云资源盘点）与 57（候选完整性）可并行开工
```

## 2. 每项旧记录差异说明

| 旧记录 | 差异 | 修正 |
|---|---|---|
| Evidence Index 54 行「待提交」 | 54 实际已提交 9d12858 | 更新为 9d12858 |
| 「43–54 是 12 个包」 | 实际 13 个 commit | 55 起口径 = 13 commits / 12 packages |
| Capability Matrix 仍留 MISSING/PARTIAL | 45–53 已实施 | 按提交证据更新为 READY/明示待真机 |
| GO/NO-GO Gate B–D 状态滞后 | 组件级本地证据已具备 | 标 PASS_LOCAL（不覆盖 PASS_LIVE） |
| 测试口径混写（music 94/104、前端 4/5 套） | 各包提交时快照不同 | 统一为 55 包全量口径（§5） |
| 工作区未提交部署/契约/测试/证据 | 部署脚本族未跟踪（57 处理）；package-lock 未提交 | 记录不删除不移动 |

## 3. Commit 序列（43–54，父子顺序）

| # | commit | 包 |
|---|---|---|
| 1 | 8404de1 | 43 总控 |
| 2 | 7319c93 | 44 治理冻结 |
| 3 | 06b2e6b | 45 设计系统 |
| 4 | a7378ae | 51 身份隐私 |
| 5 | 90f9aa4 | 46 官网 |
| 6 | 088b25e | 47 先决（async job API） |
| 7 | a4927a8 | 47 Ear 表面 |
| 8 | 9b5e7eb | 49 Music 聆听 |
| 9 | 7eec681 | 48 Ear 升级 |
| 10 | 45e7f91 | 50 Creator 发布 |
| 11 | 68811f5 | 52 证据桥 |
| 12 | 8031c0f | 53 生产运维 |
| 13 | 9d12858 | 54 上线验收 |

## 4. 工作区分类（只读列出）

- **tracked modified（1）**：apps/music-web/package-lock.json
- **untracked release-relevant（19）**：ops/web_origin/（deploy_moodify_service.sh、deploy_static_origins.sh、rollback_static_origin.sh、verify_origins.sh、nginx/moodify-api-limits.conf、node.env.example、cloudflared/、systemd/、README.md）、ops/ear_batch/、docs/contracts/music/music_public_api.md、artifacts/（ear_batch、ear_pilot_001、mfy_data_foundation_001_rev2、mfy_infra_foundation_001、mfy_music_creator_lifecycle_001、web_origin）
- **untracked 非 release-relevant**：.claude/、.codex_tmp/、tsconfig.tsbuildinfo、temp/、tests/、moodify-core-package/outputs/ear_wb_demo/（本地演示）

→ 57 包必须把部署脚本族纳入候选（自包含候选），55 只记录。

## 5. 统一测试口径（55 包基线，本地，2026-08-14）

| 套件 | 数量 | 类型 | 运行环境 |
|---|---|---|---|
| moodify-core-package 全量 | 639 passed / 5 skipped | pytest | 本地 Windows + Python 3.11 |
| moodify-music-package 全量 | 104 passed | pytest | 本地 Windows + Python 3.11 |
| 前端静态 checks（5 套） | design 7/7、site 6/6、workbench 7/7、listening 7/7、creator-studio 6/6 | node --test | 本地 Node 22 |
| ruff | clean（本包引入代码） | — | 本地 |

口径规则：最终全量（639/104）与包内增量（15/14/10…）分列；静态检查按套计数；环境与日期随行记录；禁止混写。

## 6. Gate 标记（55 包基线）

| Gate | 标记 | 证据 |
|---|---|---|
| A 产品框架冻结 | **PASS_LOCAL**（人类批准 2026-08-14） | 四框架 APPROVED v1.0（7319c93） |
| B 可交互产品壳 | **PASS_LOCAL**（组件级） | 45/46/47/49 截图 + 静态检查；真机视觉归 64/65 |
| C 关键闭环 | **PASS_LOCAL**（组件级） | 47 真实案例、49 Range 5/5、50/52 测试 |
| D 生产准备 | **PARTIAL**（本地演练通过，真机未执行） | 53 secrets clean + 恢复演练；R06 未解除 |
| E 公共上线 | **NOT_RUN**（GO 未签署，禁止自动化） | GO_NO_GO_RECORD NOT SIGNED |

## 7. 风险账更新（对照 43 包 Risk Register）

| 风险 | 43 状态 | 55 状态 | 依据 |
|---|---|---|---|
| R01 身份（三处 PARTIAL） | OPEN | **CLOSED_LOCAL**（51 已实施，生产默认匿名+会话） | a7378ae；真机验证归 59 |
| R11 判断权威漂移 | MONITOR | **MONITOR**（48 已实施范围合同+升级） | 7eec681 |
| R12 人工评审资源 | OPEN | **OPEN**（reviewer 角色待指定；48 记录格式已具） | 7eec681；真机归 59/65 |
| R06 跨域（PolarDB 凭据/VPC 对等） | BLOCKED | **BLOCKED**（58 包解除） | 凭据未到位 |
| R05–R10 运维 | OPEN | **PARTIAL_LOCAL**（53 告警/备份/回滚演练） | 8031c0f；真机归 61 |

## 8. 事实边界

- 本报告基于 55 包开工时（2026-08-14）工作树；55 不处理未跟踪文件（57 处理）。
- 任何 Gate 不得以本报告 PASS_LOCAL 冒充 PASS_LIVE；GO 签署仅限人类。
- 56–58 为后续包；59–65 依赖真机/Codex/人类 GO，本包不预支其结论。
