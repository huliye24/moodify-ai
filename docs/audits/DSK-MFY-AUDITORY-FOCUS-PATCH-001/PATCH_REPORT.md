# PATCH_REPORT — 减法 + 4-tab 重构改动清单

任务：DSK-MFY-AUDITORY-FOCUS-PATCH-001
日期：2026-08-08

## 1. 删除文件（7 个，git 历史可恢复）

| 文件 | 说明 |
|---|---|
| `apps/android/.../ui/screens/CwcIntroScreen.kt` | CWC 介绍页 |
| `apps/android/.../ui/screens/CwcAuthScreen.kt` | CWC 激活/登录门 |
| `apps/android/.../ui/screens/CwcCenterScreen.kt` | CWC 中心 |
| `apps/android/.../ui/screens/CwcGiftScreen.kt` | CWC 礼物页 |
| `apps/android/.../data/CwcRepository.kt` | CWC 状态存储 |
| `apps/android/.../model/CreatorPass.kt` | CWC 数据模型 |
| `apps/android/.../test/.../CwcRepositoryTest.kt` | CWC 单测（5 例） |

保留：`data/TokenStore.kt`（配对 API 令牌，非 CWC）

## 2. 接线修改

| 文件 | 改动 |
|---|---|
| `MainActivity.kt` | 删深链解析 + `MoodifyApp()` 无参 |
| `AndroidManifest.xml` | 删 `moodify://cwc/` intent-filter |
| `ui/MoodifyApp.kt` | 删全部 CWC 状态/分支；4-tab 重构（首页/听觉检测/案例/我的）；worksOpen overlay → 案例 tab；抽屉 7 项重排 |
| `ui/MoodifyDrawer.kt` | 移除创作者中心/版权与发布/合作计划；案例/听觉检测标签 |
| `ui/screens/ProfileScreen.kt` | 删 CWC 通行证快捷卡 + onOpenCwcCenter 参数 |
| `ui/screens/CreatorCenterScreen.kt` | 删 CwcStatusCard + onOpenCwcCenter 参数 |
| `ui/screens/WorksScreen.kt` | 标题 → 听觉案例（cases_title）；tab 模式品牌头 |
| `ui/screens/SupportScreens.kt` | 重置对话框删 CwcRepository 调用 |
| `androidTest/.../LanguageSwitchTest.kt` | 删 CWC seeding |

## 3. i18n（6 xml + 6 snapshot 同步，parity 契约保持）

- **改值**：nav_process → 听觉检测/Listen；home_start_analysis → 开始听觉检测/Start Auditory Analysis；analysis_processing_title → 听觉干预实验/Auditory Intervention
- **新增**：nav_cases（案例/Cases）、cases_title（听觉案例/Auditory Cases）
- **删除**：87 个死 key（62 cwc_* + 21 CWC auth + works_title + auth_password + auth_creator_pass + creator_cwc_line）

## 4. 金路径结果

导入（UploadFlow）→ 分析（ProcessingScreen 真实服务器链路）→ 结果/证据展示 → 保存案例（WorksLibrary→案例 tab）：非干预路径完成，不经过市场/社交/版权模块。

## 5. 测试

- JVM 单测 41 全绿（46 − CwcRepositoryTest 5）
- StringKeyParityTest：6 文件 key 集一致 + snapshot 值一致
- `:app:assembleDebug` 通过
- 详见 TEST_REPORT.md
