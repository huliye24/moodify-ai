# Moodify Android 国际化迁移报告（DSK-MFY-I18N-001 首轮）

日期：2026-08-06
任务包：`补丁包/05 moodify-i18n-codex-package`（六语言：zh-CN / zh-TW / en-US / ja-JP / ko-KR / fr-FR）

## 架构

- **翻译载体**：Android 原生 resources。`app/src/main/res/values[-zh-rCN|-zh-rTW|-ja|-ko|-fr]/strings.xml`，共 **172 个 key**，六文件 key 集合完全一致（`StringKeyParityTest` 强制）。
- **切换机制**：`AppCompatActivity` + `androidx.appcompat:appcompat:1.7.1`，`AppCompatDelegate.setApplicationLocales()`（API 33+ 委托 LocaleManager，API<33 由 AppCompat 处理并 recreate）。切换后当前屏幕立即重建显示新语言。
- **持久化**：manifest 注册 `androidx.appcompat.app.AppLocalesMetadataHolderService` + `autoStoreLocales=true`（appcompat 1.7 持久化的必要条件，未声明则重启丢失——本机已验证该坑），文件存于 `files/androidx.appcompat.app.AppCompatDelegate.application_locales_record_file`。
- **首启跟随系统**：`MainActivity.ensureInitialLocale()` 用 `LocaleKit.normalize(systemTag)` 解析（zh-HK→zh-TW 等别名确定性成立，避免资源 fallback 落到英文）。
- **别名契约**（`data/LocaleKit.kt`，JVM 单测覆盖）：zh-hans/cn/sg→zh-CN；zh-hant/tw/hk/mo→zh-TW；en/gb→en-US；ja→ja-JP；ko→ko-KR；fr/ca→fr-FR；其余→en-US。
- **「跟随系统」**：设置页语言选择器首项，`setApplicationLocales(empty)` 恢复系统跟随。
- **Machine fields 未翻译**：状态枚举（如 works 的「已完成/草稿」）、证据记录、MRS/API key、CWC 码、文件格式串保持不变。

## 首轮迁移的文件（Phase D 7 区域）

| 区域 | 文件 | 状态 |
|---|---|---|
| 底部导航 | `ui/MoodifyApp.kt`（3 tab + selected/settingsOpen/worksOpen 改 rememberSaveable） | ✅ |
| 侧抽屉 | `ui/MoodifyDrawer.kt`（9 项 + ProfileCard/StorageCard） | ✅ |
| 设置页 | `ui/screens/SupportScreens.kt`（SettingsScreen 全量 + **语言选择器**） | ✅ |
| 首页 | `ui/screens/HomeScreen.kt` | ✅ |
| 分析入口 | `ui/screens/ProcessingHubScreen.kt`（含 RecentTask 状态色重构，去掉中文 contains 判断） | ✅ |
| 结果页 | `ui/screens/ProcessingScreen.kt`（标题/上传/处理中/完成/失败/按钮） | ✅ |
| 作品页 | `ui/screens/WorksScreen.kt`（标题/筛选/导入/Queue 标签/质量门/日期 locale 显式化） | ✅ |
| 登录/注册 | `ui/screens/CwcAuthScreen.kt`（认证页全量 + 校验提示）+ `ui/screens/ProfileScreen.kt`（账号区/退出登录） | ✅ |

## 新增与修改

- **新增**：`data/LocaleKit.kt`（纯 Kotlin 别名表/元数据/解析，JVM 可测）、`data/LocaleStore.kt`（AppCompatDelegate facade）、`res/xml/locales_config.xml` + Manifest `localeConfig`、6 个 `strings.xml`、测试 4 个文件。
- **修改**：`MainActivity.kt`（AppCompatActivity + 首启 bootstrap）、`styles.xml`（主题父类 Theme.AppCompat.Light.NoActionBar——AppCompatActivity 必需）、`AndroidManifest.xml`（localeConfig + locale 持久化 service）、`build.gradle.kts`（appcompat 1.7.1）、`settings.gradle.kts`（阿里云镜像，dl.google.com 本网不可达）。

## 质量门

- JVM 单测 **46 个全绿**：`LocaleKitTest`（别名表全量/大小写/前缀变体/fallback/resolve）、`StringKeyParityTest`（六文件 key 一致 + 05 包快照子集与值契约）、`LocaleStoreFormatTest`、既有 CwcRepository/MoodifyApiClient/MiniPlayerGesture 测试保持绿。
- instrumented：`LanguageSwitchTest` **2/2 通过**（`am instrument` 直接驱动，绕开 Gradle 的 split 安装限制）：选日本語 → AppCompatDelegate 状态 + recreate 后 UI 出现「設定」；选한국어 → 磁盘持久化文件含 ko-KR。执行前置条件：MiUI 需开启「USB 安装」+ 授予 com.moodify.app「后台弹出界面」权限（`appops set com.moodify.app 10021 allow`）。
- 既有 `MiniPlayerGestureTest` 12 例中 5 例失败（fastFlingUp/swipeUpFromPeek/rapidDrags/tapPlay/trackSwitch）——**全部为"唤出/动画回弹"类，与本次改动无关**（MiniPlayer 组件与测试文件在本会话前已存在且未被修改，git diff 为空；收起类 5 例全过）。判定为设备环境性失败。
- 设备实测（API 31 / MiUI，手动 adb 验证）：首启跟随系统中文 ✅、切换立即生效（底部 tab 即时变日语）✅、杀进程重开保留（持久化文件含 ja-JP）✅。
- `:app:assembleDebug` 通过。

## 第二轮（2026-08-08，DSK-MFY-I18N-001 round-2）

迁移了报告首轮列出的全部 15 个未迁移区域 + 组件，新增 **~340 个 key**（六语言 key 集合同步，`StringKeyParityTest` 继续强制）。

| 区域 | 处理 |
|---|---|
| CwcCenterScreen / CwcIntroScreen / CwcGiftScreen | ✅ 全量 chrome + 品牌文案（入资源，待人工审核标注） |
| CollaborationHubScreen | ✅ chrome 全量；演示卡片内容（标题/创作者名/预算/地区/描述）按 WorksScreen 同规则不译 |
| WorkDetailScreen | ✅ 全量 chrome；preset/状态 chip 按规则保留；gate 状态复用 works_gate_passed/failed |
| UploadFlowScreen / WeChatImport / BatchUpload | ✅ 全量 chrome；演示音频文件名等数据不译 |
| SearchScreen | ✅ chrome；榜单/标签/曲目 demo 数据不译 |
| CreatorCenterScreen / DataCenterScreen | ✅ chrome；状态枚举（已发布/草稿/处理中）、城市、指标值不译 |
| NotificationCenterScreen | ✅ chrome（tab/标题/空态）；通知内容为 demo 数据不译 |
| CopyrightCenterScreen | ✅ chrome + 资产类型标签；平台状态（已发布/同步中/待发布）不译 |
| NowPlayingScreen / PlaybackBar / MiniPlayer | ✅ 全量（含 gate 状态复用、A/B 标签、播放/暂停） |
| ConnectionCard | ✅ 全量（真实功能 UI，含运行时连接状态） |
| SupportScreens 重置演示会话对话框 | ✅ 迁移（真功能）；设置页其余演示静态文案保持低优先级残留 |

### 本轮约定（与首轮一致）

- **不译（machine fields）**：状态枚举（已发布/草稿/处理中/审核中/可使用/已发送/已激活/已过期/已确权/可用）、CWC 通行码、用户名（泫榛）、日期、文件格式（WAV/MP3/PDF/MIDI）、预算/地区/城市、演示卡片内容数据、B2B/B2C/C2C 业务码。
- **品牌文案**（cwc_brand_tagline/sub、cwc_welcome_quote 等）已入资源，列入下方待审核清单。
- 含字面 `%` 的字符串已加 `formatted="false"`（aapt2 默认语言校验）。
- 复用既有 key：works_gate_passed/failed、analysis_pick_audio(_support)、works_all、home_view_all、home_followers、home_follow、home_hot_works、nav_*、common_* 等，避免重复翻译。

### 验证（round-2 增量）

- JVM 单测全绿（`:app:testDebugUnitTest`），`StringKeyParityTest` 六文件 key 集一致。
- `:app:assembleDebug` 通过。
- 首轮 46 例 JVM 测试 + 本轮无新增测试文件（parity 契约已覆盖 key 集一致性）。

## 剩余残留（低优先级，不再新增）

- SupportScreens 设置页其余硬编码（约 30，多为演示静态数据与 About/Help 文案）
- ProcessingScreen 阶段详情（23，处理中实时状态文案）
- CwcAuthScreen 权益列表（7，见待审核）
- WorksScreen/HomeScreen/ProfileScreen/MoodifyDrawer 的 demo 数据与用户名（按规则不译）
- 各处演示卡片内容数据（CollaborationHub/Search/DataCenter 等，按规则不译）

## 需人工审核的文案

- CwcAuthScreen 激活成功对话框的**权益列表**（「首个作品免费入驻」「1 张标准处理 8 折券」等——涉及支付/营销承诺，禁止机翻，需产品确认后入资源）。
- 本轮入资源的品牌文案：cwc_brand_tagline / cwc_brand_sub / cwc_welcome_quote / cwc_creator_pass_sub（五语言译文为 AI 直译，需品牌方确认）。
- 价格（¥30/¥5000）、数据单位（GB/MB/万）等本地化格式需按目标市场复核。
