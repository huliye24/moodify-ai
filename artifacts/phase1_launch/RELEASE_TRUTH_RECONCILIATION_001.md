# Release Truth Reconciliation — 差异报告（v1.1 最新真相）

**Document ID:** MFY-RELEASE-TRUTH-001
**Version:** 1.1（2026-08-14 更新：纳入 56–65 完成事实与两项 P0 修复）
**Date:** 2026-08-14
**Package:** MFY_RELEASE_TRUTH_RECONCILIATION_001 (55)
**Executor:** DeepSeek（只读审计 + 文档账本修正；未改产品代码、未部署、未签署 GO）

## 1. 候选标识（最新）

```text
Candidate ID:      MFY-PHASE1-RC-20260814-3（43–65 全序列 + 两项 P0 修复后）
Branch:            codex/mfy-data-foundation-001-rev2
HEAD:              e106b1f18aa50706755e927b7f20a63376646c8b
Package count:     23（43–65）
Commit count:      25（含 47 先决 088b25e、57 三连 80b3c5c/7d4982b/a28ab02、63 修复 47c4db2）
P0 修复 commit:    2（7d4982b 工作台 HTML、47c4db2 官网 HTML — 均因 *.html gitignore 吞源码）
Tracked dirty:     1（apps/music-web/package-lock.json — 第三方变更，未提交）
Untracked release-relevant: 0（57 已全部纳入候选）
Ignored release-relevant:    0（ignored 分类见 §4，无候选必需文件被忽略）
Local gates:       Gate A PASS_LOCAL；Gate B–D 非视觉 P0 全过（63 独立验证）
Live gates:        ALL NOT_RUN（真机部署/验证待授权，归 59–61/65）
Blocking risks:    R06（PolarDB 凭据/VPC 对等，58 包已冻结计划，云端解除待授权）
Next package readiness: 64（Codex 视觉终审，证据包已备）→ 65（Canary GO，待授权 A–E）
```

## 2. 每项旧记录差异说明（v1.0 → v1.1）

| 旧记录（v1.0） | 差异 | 修正（v1.1） |
|---|---|---|
| 候选 RC-20260814-1（HEAD 9d12858） | 55 后完成 56–65（12 commits）+ 2 修复 | RC-20260814-3 / HEAD e106b1f |
| commit 13 / 包 12 | 全序列 25 commits / 23 包 | §3 更新 |
| untracked release-relevant 19 个 | 57 包已纳入候选（80b3c5c） | 0 个 |
| 工作台 HTML 被忽略（55 未发现） | 57 发现并修复（7d4982b） | 已跟踪 |
| 官网 HTML 被忽略（55 未发现） | 63 独立验证发现并修复（47c4db2） | 已跟踪 |
| 测试口径 music 104 | 58 包 +4（数据面约束） | music 108 |
| Gate B–D「组件级 PASS_LOCAL」 | 63 干净环境独立复验全绿 | 非视觉 P0 全过 → READY_FOR_VISUAL_REVIEW |
| ignored 分类缺失 | 55 执行步骤 3 要求三分列 | §4 补齐 |

## 3. Commit 序列（43–65，父子顺序，25 commits）

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
| 14 | 7506bdc8 | 55 真相核对（v1.0） |
| 15 | dcc7a36 | 56 验证织网 |
| 16 | 80b3c5c | 57 候选完整性（纳入 29 文件） |
| 17 | 7d4982b | **57/63 P0 修复：工作台 HTML 纳入** |
| 18 | a28ab02 | 57 release manifest |
| 19 | 5424c66 | 58 数据面冻结 |
| 20 | ab5968d | 59 安全验收 |
| 21 | 90ac3a7 | 60/61 E2E+可靠性 |
| 22 | e2be112 | 62 季度冻结 |
| 23 | 47c4db2 | **63 P0 修复：官网 HTML 纳入** |
| 24 | a0bbd17 | 63 独立验证报告 |
| 25 | e106b1f | 64/65 视觉包+Canary |

## 4. 工作区三分列（v1.1 补齐 ignored）

- **tracked modified（1）**：apps/music-web/package-lock.json（第三方，55 不处理、57 不处理，发布前需人类决定）。
- **untracked（0 release-relevant）**：57 已纳入部署脚本族/契约/ear_batch；其余 untracked（.claude/、.codex_tmp/、outputs/ear_wb_demo/、tsbuildinfo）非候选必需。
- **ignored（候选相关为 0）**：`*.html` 规则曾吞工作台/官网页面（双 P0 已修，例外规则已加）；其余 ignored 均为缓存/构建产物/历史素材（node_modules、__pycache__、build/、dist/、.venv、07Music/、RJWC_VideoPack_System/、android-studio-quail2-windows.exe、apps/tools/、artifacts/audits/ 等）——无候选必需文件。

## 5. 统一测试口径（v1.1，干净环境独立重跑，2026-08-14）

| 套件 | 数量 | 类型 | 运行环境 |
|---|---|---|---|
| moodify-core-package 全量 | 639 passed / 5 skipped | pytest | 干净 checkout（63 独立重跑）+ 本地 |
| moodify-music-package 全量 | 108 passed（55 后 +4 数据面） | pytest | 干净 checkout + 本地 |
| 前端静态 checks（5 套） | design 7/7、site 6/6、workbench 7/7、listening 7/7、creator-studio 6/6 | node --test | 干净 checkout（63 重跑，site 修复后 6/6） |
| ruff | clean | — | 本地 |

口径规则：最终全量与包内增量分列；静态检查按套计数；环境与日期随行记录；禁止混写。

## 6. Gate 标记（v1.1，63 独立验证后）

| Gate | 标记 | 证据 |
|---|---|---|
| A 产品框架冻结 | **PASS_LOCAL**（人类批准 2026-08-14） | 四框架 APPROVED v1.0（7319c93） |
| B 可交互产品壳 | **PASS_LOCAL**（非视觉 P0 全过） | 45–49 检查 + 63 干净环境重跑；视觉终审归 64（Codex） |
| C 关键闭环 | **PASS_LOCAL**（非视觉 P0 全过） | 47 真实案例、49 Range 5/5、50/52 测试、63 复验 |
| D 生产准备 | **PARTIAL**（本地演练通过；真机未执行） | 53 演练 + 58 计划；R06 未解除 |
| E 公共上线 | **NOT_RUN**（GO 未签署，禁止自动化） | GO_NO_GO_RECORD NOT SIGNED |

63 输出：**READY_FOR_VISUAL_REVIEW**（全部非视觉 P0 通过）。

## 7. 风险账更新（对照 43 包 Risk Register，v1.1）

| 风险 | 状态 | 依据 |
|---|---|---|
| R01 身份 | **CLOSED_LOCAL** | a7378ae；真机归 59 |
| R03 证据权威 | **MONITOR** | 68811f5（桥 publish-safe 门） |
| R05–R10 运维 | **PARTIAL_LOCAL** | 8031c0f + 90ac3a7（soak/SLO） |
| R06 跨域 | **BLOCKED（计划已冻结）** | 5424c66；凭据/VPC 授权待人类 |
| R11 判断权威漂移 | **MONITOR** | 7eec681 |
| R12 人工评审资源 | **OPEN** | reviewer 待指定；真机归 59/65 |

## 8. 事实边界（v1.1）

- 本报告基于 2026-08-14 全序列完成后的工作树；只读审计，未部署、未签署 GO。
- 55 为「可签署的发布事实」：任何 Gate 不得以 PASS_LOCAL 冒充 PASS_LIVE；GO 仅限人类。
- 后续变更（64 Codex 结论、65 真机）将再次更新本报告（v1.2+）。
