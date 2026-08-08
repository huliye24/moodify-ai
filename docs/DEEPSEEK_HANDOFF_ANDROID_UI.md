# Moodify Android UI 接续任务包（给无视觉模型）

## 目标

继续完成 `E:\moodify\apps\android` 的 Jetpack Compose App。不要重新设计页面，不要删除现有功能。按本文进行页面接线、导航整理、编译修复并安装到小米 10。

## 已完成（不要重做）

- 首页、处理、作品、我的、搜索、通知、左侧栏、创作者中心、版权与发布、数据中心、合作计划等页面已经存在。
- 上传流程已创建：`ui/screens/UploadFlowScreen.kt`。
- 这次新增的三个页面已经写入：`ui/screens/SupportScreens.kt`：
  - `SettingsScreen`
  - `HelpFeedbackScreen`
  - `AboutScreen`
- 参考图已归档在 `E:\moodify\docs\ui-sketches\references`。
- 用户姓名必须统一为“泫榛”，账号为 `@moodify_xzhen`。

## 必须完成的导航结构

底部仅保留三个入口：

1. 首页（index 0）
2. 处理（index 1）
3. 我的（index 2）

“作品”不能出现在底部导航，但 `WorksScreen` 不可删除；它由左侧栏“我的作品”进入。

首页已经移除了“上传作品”大卡片。上传统一放到处理中心。

## 左侧栏目标映射

- 发现音乐 → 首页
- 我的作品 → `WorksScreen`
- 处理任务 → 处理中心
- 创作者中心 → `CreatorCenterScreen`
- 数据中心 → `DataCenterScreen`
- 版权与发布 → `CopyrightCenterScreen`
- 合作计划 → `CollaborationHubScreen`
- 设置 → `SettingsScreen`
- 帮助与反馈 → `HelpFeedbackScreen`
- 关于 Moodify → `AboutScreen`

修改 `MoodifyDrawer.kt`，推荐给设置/帮助/关于使用 destination 8/9/10，并在 `MoodifyApp.kt` 用独立 Boolean 页面状态接线。作品也使用 `worksOpen` 独立状态，避免与三项底部索引冲突。

## 处理中心目标流程

主链路必须是：

`处理中心 → 导入音频 → 处理设置 → 处理中 → 处理完成`

处理中心应包含：

- 本地导入、微信导入、云端导入
- 标准处理：¥30/首起
- 免费入驻：先保存作品库，之后可再次处理或发布
- 最近处理任务或能力说明

可基于用户参考图和现有 `ProcessingScreen.kt` 实现 `ProcessingHubScreen(onUpload)`。原 `ProcessingScreen` 保留为“处理中”状态页。底部点击“处理”应打开处理中心，不应直接打开进度页。

## 上传流程待修复

`UploadFlowScreen.kt` 当前已知两个编译错误：

1. `Icons.Outlined.Wechat` 不存在，替换为 `Icons.Outlined.Forum` 或 `Icons.Outlined.ChatBubbleOutline`。
2. `Checkbox(checked, toggle, ...)` 的第二参数需要 `(Boolean) -> Unit`，改为 `Checkbox(checked, { toggle() }, ...)`。

上传页使用 Android 系统文件选择器，保留 WAV/MP3/FLAC/AAC/M4A、多文件、微信导入模拟列表、批量上传、上传完成页。

## MoodifyApp.kt 接线要求

- 导入 `SettingsScreen`、`HelpFeedbackScreen`、`AboutScreen`，以及新增的 `ProcessingHubScreen`。
- 增加：`worksOpen/settingsOpen/helpOpen/aboutOpen`。
- 任意底部按钮点击时关闭所有二级页面状态。
- `UploadFlowScreen.onProcess` → 打开原 `ProcessingScreen` 进度页。
- `UploadFlowScreen.onLibrary` → 打开 `WorksScreen`。
- 处理完成后不要跳到已经移除的底部 index 2“作品”；index 2 现在是“我的”。
- 左侧抽屉只在主页面开放，二级页打开时禁用手势。

## 视觉约束（不要自行发挥）

- 背景接近白色，卡片白底，16–22dp 圆角，轻阴影。
- 主色渐变：紫色 `#7B61FF` 到蓝色 `#4A9BFF`。
- 主文字深海军蓝，辅助文字灰蓝。
- 图标使用 2px 线性 Material Outlined 风格。
- 小米 10 屏幕要能纵向滚动，不允许内容被底部导航遮挡。
- 三个新页面以 `SupportScreens.kt` 为准，不需要重写视觉。

## 编译与安装

PowerShell：

```powershell
$env:JAVA_HOME='C:\Program Files\Android\Android Studio\jbr'
$env:ANDROID_HOME='C:\Users\Administrator\AppData\Local\Android\Sdk'
cd E:\moodify\apps\android
.\gradlew.bat :app:assembleDebug
```

修复全部 Kotlin 编译错误后安装：

```powershell
$adb='C:\Users\Administrator\AppData\Local\Android\Sdk\platform-tools\adb.exe'
& $adb devices
& $adb install -r 'E:\moodify\apps\android\app\build\outputs\apk\debug\app-debug.apk'
& $adb shell am force-stop com.moodify.app
& $adb shell monkey -p com.moodify.app -c android.intent.category.LAUNCHER 1
```

目标设备序列号通常为 `5fe6dfde`，型号 `M2102J2SC`。

## 验收清单

- [ ] App 编译成功
- [ ] 小米 10 安装成功
- [ ] 底部只有：首页 / 处理 / 我的
- [ ] 首页没有上传作品卡片
- [ ] 处理页能进入系统文件选择器
- [ ] 左侧“我的作品”可打开作品列表
- [ ] 设置、帮助与反馈、关于 Moodify 都能从左侧栏进入和返回
- [ ] 姓名全部为“泫榛”
- [ ] 无崩溃，无底部遮挡

