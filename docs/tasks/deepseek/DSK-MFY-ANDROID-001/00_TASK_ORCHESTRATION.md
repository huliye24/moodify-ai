# DSK-MFY-ANDROID-001｜Android 工程地基与小米真机首装

**计划日期：** 2026-08-02  
**目标完成日期：** 2026-08-02  
**执行 Worker：** DeepSeek  
**最终 Judge：** Codex / 授权用户  
**执行时限：** 90 分钟  
**任务状态：** PLANNED

## 1. 当前基线

- Android 工程位于 `apps/android/`，使用 Kotlin、Jetpack Compose、AGP 8.11.1、Gradle 8.14；
- SDK 36 与小米真机已连接，设备 `M2102J2SC / Android 12 / SDK 31`；
- 首轮构建已通过 Manifest、资源和 Kotlin 编译，长时间停留在 DEX 合并且未生成 APK；
- 第二轮离线构建被外部中断，不能视为成功或失败；
- 当前代码和 Gradle 缓存是用户资产，不得删除后重建以绕过诊断。

## 2. 目标

1. 诊断并解决构建阻塞，生成可重复的 Debug APK；
2. 补齐安全的 Gradle Wrapper，统一 JDK、SDK 和构建入口；
3. 安装 APK 到已授权的小米手机；
4. 验证启动 Activity、应用进程、包名和基础导航；
5. 建立构建与真机日志基线，为后续任务提供稳定地基。

## 3. 允许范围

```text
apps/android/
docs/tasks/deepseek/DSK-MFY-ANDROID-001/
outputs/deepseek_validation/DSK-MFY-ANDROID-001/
```

禁止修改 Python 业务代码、下载来历不明的二进制、删除 Gradle 全局缓存、删除用户 Android Studio 配置、修改手机个人数据、创建发布密钥，以及 Git reset/clean/stash/checkout/commit/push。

## 4. 执行阶段

### Stage A｜确定阻塞点

- 检查遗留 Gradle/Java 进程、守护进程状态、磁盘、内存和构建日志；
- 使用 `--no-daemon --console=plain --stacktrace` 保存可审计日志；
- 区分依赖下载、Kotlin 编译、D8/R8、DEX 合并、APK 打包和会话通信问题；
- 只终止由本任务启动且已确认失去进展的进程。

### Stage B｜固定工具链

- 补齐 wrapper 脚本与 wrapper JAR，构建入口为 `gradlew.bat`；
- 明确 `JAVA_HOME`、`ANDROID_HOME`、compileSdk、minSdk、targetSdk；
- 清理 Kotlin DSL 弃用警告；
- 不随意升级依赖，任何版本变化必须记录原因。

### Stage C｜构建与安装

- 先执行 Debug clean-room 等价构建，再执行一次增量构建；
- 记录 APK 大小和 SHA-256；
- 使用 ADB 安装或升级 `com.moodify.app`；
- 启动 `MainActivity`，验证进程和前台 Activity。

### Stage D｜真机冒烟

- 验证首页、作品、任务、我的四个入口；
- 首页进入处理演示页并返回；
- 无崩溃、ANR、黑屏和系统栏遮挡；
- 保存 Logcat、设备信息和手机截图。

## 5. P0 门槛

- `gradlew.bat :app:assembleDebug` 连续两次退出码 0；
- Debug APK 存在、非空、有 SHA-256；
- `adb install -r` 成功，包可查询；
- 冷启动成功，前台 Activity 正确；
- 主导航与处理页无崩溃；
- 无密钥、绝对开发机路径或内部数据打入 APK；
- 交付 `PROGRESS.md`、`VALIDATION.md`、`FAILURE_LEDGER.md`、`HANDOFF.md`。

## 6. 今日规则与停止条件

本包以今日完成为目标，但不得以跳过构建、伪造截图或只在 Preview 中运行代替真机证据。若需要删除全局缓存、修改系统环境、安装新 SDK、解除手机安全设置或覆盖范围外文件，立即 HOLD 并提交 `SCOPE_CHANGE_REQUEST.md`。最终状态只能是 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。

