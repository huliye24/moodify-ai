# DeepSeek Independent Release Verification — 复验报告

**Document ID:** MFY-INDEPENDENT-VERIFICATION-001
**Version:** 1.0
**Date:** 2026-08-14
**Package:** MFY_DEEPSEEK_INDEPENDENT_RELEASE_VERIFICATION_001 (63)
**基线:** 62 冻结 HEAD（e2be112 → 修复后 47c4db2）
**方法:** 干净环境（worktree，无工作区残留）；不读原执行者"通过结论"，只读契约/命令/原始证据

## 1. 发现清单

| 级别 | 发现 | 复现 | 处置 |
|---|---|---|---|
| **P0** | 官网 7 个 HTML 页面不在冻结 HEAD（`*.html` gitignore 规则吞掉）——干净 checkout 的 rongjingmusic/ 仅 5 个文件，check_site 6 项失败 | 干净环境 `node --test check_site.mjs` → 1 pass/5 fail | 补丁 47c4db2（归 46 包责任）；修复后重跑 **6/6 PASS** |
| CAVEAT | 同类陷阱已全局排查：已跟踪 html 17 个（工作台 8 + 官网 7 + 遗留 2）；未跟踪的均为构建报告/venv 库文件（合理不提交） | 全仓 html 审计 | 无动作 |
| NOT_VERIFIED | 云端（59–61）真机项：安全头、E2E 用户入口、soak/DR —— 未部署授权，无法独立复验 | — | 归 65 上线窗口 |

## 2. 干净环境全量（独立重跑）

| 套件 | 结果 | 与 55 声称一致 |
|---|---|---|
| core 全量（干净 checkout） | **639 passed / 5 skipped** | ✓ |
| music 全量 | **108 passed** | ✓（55 后 +4 = 58 包数据面测试） |
| design-system | 7/7 | ✓ |
| listening-product | 7/7 | ✓ |
| creator-studio | 6/6 | ✓ |
| workbench | 7/7 | ✓ |
| site（修复后） | **6/6** | ✓（修复前 1/6） |
| 数字交叉核对 | authority 15 / bridge 10 / creator 4 / 截图 14 | ✓ |

## 3. P0 失败/边界抽样（既有测试存在性验证）

| P0 | 负向用例存在 | 测试 |
|---|---|---|
| 身份越权 | ✓ | 51 spoof/IDOR/CSRF |
| 判断权威越界 | ✓ | 48 八类升级 |
| 发布幂等 | ✓ | 50 重放/冲突 |
| 桥 publish-safe 门 | ✓ | 52 未审/未 safe 拒绝 |
| 数据面 fail closed | ✓ | 58 无 actor 写拒绝 |
| 上传边界 | ✓ | 49/50 签名/size |

## 4. 结论

- 非视觉 P0 全部通过（1 个 P0 缺口已修复并重跑受影响 gate）；
- 输出推荐：**READY_FOR_VISUAL_REVIEW**（64 包 Codex 视觉终审）；
- 修复纪律执行：补丁 commit 47c4db2（独立于本报告，候选版本已更新）；
- 本报告不签署 GO（63 铁律）；云端真机项未验证不冒充通过。

## 5. 事实边界

- 复验环境 = 冻结 HEAD 的干净 checkout；云端隔离环境（60/65）未授权未执行；
- 截图证据抽查 14 张存在且像素验证过（45/46/47 包记录）；
- 任何后续修复须从受影响最早 gate 重跑并更新本报告。
