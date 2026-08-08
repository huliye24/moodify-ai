# AUDIT_BEFORE — 听觉智能减法策略审计基线

任务：DSK-MFY-AUDITORY-FOCUS-PATCH-001
日期：2026-08-08
状态：Phase 0 完成（本文件在变更前撰写）

## 1. 运行时/栈检测

- **Android app**：Kotlin + Jetpack Compose（Material3），3-tab 底部导航（首页/处理/我的）+ 抽屉（9 项）+ 全屏 overlay 导航
- **core 包**：Python 3.11，moodify CLI v2（project/asset/case/run 生命周期）+ FastAPI（/api/v1 移动端契约 14 端点）
- **i18n**：6 语言（zh-CN/zh-TW/en-US/ja-JP/ko-KR/fr-FR），StringKeyParityTest 强制 key 集一致 + snapshot 值一致

## 2. 遗留范围（真实遗留面 = Android）

### 2.1 CWC 源文件（8 个，将删除）

| 文件 | 职责 |
|---|---|
| `ui/screens/CwcIntroScreen.kt` | CWC 介绍页（什么是 CWC/权益/步骤） |
| `ui/screens/CwcAuthScreen.kt` | CWC 激活/登录门（首启强制） |
| `ui/screens/CwcCenterScreen.kt` | CWC 中心（分享码/可赠送通行证/邀请记录） |
| `ui/screens/CwcGiftScreen.kt` | CWC 礼物接收页（深链落地） |
| `data/CwcRepository.kt` | CWC 状态/激活/重置（SharedPreferences "moodify_cwc"） |
| `model/CreatorPass.kt` | CreatorPass/CwcBenefits/AuthMode/CwcValidationState |
| `test/.../CwcRepositoryTest.kt` | 5 个 CWC 单测 |

### 2.2 CWC 入口点（可达性地图）

- **首启登录门**：`MoodifyApp.kt:102` `!cwcRepo.isActivated() -> CwcAuthRequest(...)`（全屏覆盖）
- **深链**：`MainActivity.kt:38-42` `moodify://cwc/{code}` + `AndroidManifest.xml:21-26` intent-filter → CwcGiftScreen
- **抽屉**：创作者中心项 → CreatorCenterScreen → CwcStatusCard → CwcCenterScreen（MoodifyApp:233）
- **Profile tab**：QuickActions 第一项「CWC 通行证」→ CwcCenterScreen（MoodifyApp:248）
- **屏幕间流转**：CwcGiftScreen.onAccept → CwcAuthScreen；CwcIntroScreen.onStart → CwcAuthScreen；CwcAuthScreen onShowIntro → CwcIntroScreen（MoodifyApp:212-222）

### 2.3 其他遗留概念

交易中心/版权市场/藏品/NFC/钱包/代币：**Android 与 core 均无真实代码**。core 的 token 命中全部为配对认证（v1.py PairTokenStore/bearer）与文本对齐 token，已人工核验为假阳性。

## 3. 扫描基线（scan_legacy_concepts.py）

| 范围 | 命中数 | 真实遗留 | 假阳性 |
|---|---|---|---|
| apps/android | 85 | CWC 文件/深链/入口 ~30 | MoodifyApiClient/ConnectionRepository/TokenStore/PlaybackManager 的 bearer token ~55 |
| moodify-core-package | 58 | 0 | 全部（v1.py 配对 token 24、测试 25、lyric_align 文本 token 4 等） |

verify_strategy_alignment.py：`aligned: false`（6 项 core 概念全部 true；legacy_active_files 全为 token 假阳性）

## 4. 路由清单（变更前）

Android 底部导航 3 tab：[首页 HomeScreen / 处理 ProcessingHubScreen / 我的 ProfileScreen]
抽屉 9 项：作品 / 处理任务 / 云端空间 / 创作者中心 / 数据中心 / 版权与发布 / 合作计划 / 设置 / 帮助与反馈 / 关于
深链 1 个：`moodify://cwc/`

## 5. 变更前基线测试

- JVM 单测 46 个（含 CwcRepositoryTest 5 个）+ instrumented LanguageSwitchTest 2 个（含 CWC seeding）
- StringKeyParityTest：6 文件 506 key 一致
