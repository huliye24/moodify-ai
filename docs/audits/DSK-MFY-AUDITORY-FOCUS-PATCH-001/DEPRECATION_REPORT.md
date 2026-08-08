# DEPRECATION_REPORT — 遗留分支移除清单

任务：DSK-MFY-AUDITORY-FOCUS-PATCH-001
日期：2026-08-08

## REMOVE（活跃运行时代码移除）

| 项 | 处置 |
|---|---|
| CWC 四屏（Intro/Auth/Center/Gift） | 删除（git 历史可恢复） |
| CwcRepository / CreatorPass | 删除 |
| `moodify://cwc/` 深链 + intent-filter | 删除 |
| CWC 首启登录门 | 删除（`MoodifyApp` 启动门移除） |
| Profile 通行证快捷卡 / CreatorCenter CWC 状态卡 | 删除 |
| 重置对话框 CWC 激活清除 | 删除（保留作品/配对/服务器地址重置） |
| CWC 字符串（87 key × 6 语言 + 6 快照） | 删除 |
| CwcRepositoryTest / LanguageSwitchTest CWC seeding | 删除 |

## DEFER（从主导航移除，代码保留不可达）

| 项 | 现状 |
|---|---|
| 创作者中心（CreatorCenterScreen） | 抽屉项移除；代码保留 |
| 版权与发布（CopyrightCenterScreen） | 抽屉项移除；代码保留 |
| 合作计划（CollaborationHubScreen） | 抽屉项移除；代码保留 |
| 云空间（CloudQueue） | 抽屉项保留但未接线（维持原状） |

## 保留（非 CWC，勿误删）

| 项 | 理由 |
|---|---|
| `data/TokenStore.kt` | 配对/API 令牌（AES-GCM + Keystore），被 ConnectionViewModel/Home/Processing 活跃引用 |
| v1 API pair-token 认证 | core 移动端契约，非经济概念 |
| `nav_works` / `home_hot_works` 等 | 内容分类标签（搜索/数据中心表头），非遗留词 |

## 数据迁移

无生产数据（CWC 为本地演示状态，SharedPreferences "moodify_cwc" 不再被读取；用户侧残留键无害）。未执行物理数据删除。
