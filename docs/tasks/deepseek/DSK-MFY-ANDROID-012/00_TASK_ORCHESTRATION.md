# DSK-MFY-ANDROID-012｜小米真机稳定化与 0.2.0 Beta 封版

**计划日期：** 2026-08-02  
**目标完成日期：** 2026-08-02  
**依赖：** ANDROID-011 ACCEPT；ORDER-BEAUTY-023/024/025 治理接口可用  
**执行 Worker：** DeepSeek  
**最终 Judge：** Codex / 授权用户  
**执行时限：** 150 分钟  
**任务状态：** PLANNED

## 1. 目标

006 封了 0.1.0 本地 Alpha（演示为主）。本包封 **0.2.0 本地 Beta**：真实处理、断点上传、作品库、A/B 试听、安全合规全部就位，且在小米真机上稳定运行 30 分钟无崩溃、无 ANR、无内存泄漏迹象。

## 2. 当前基线

- 007-011 已交付：真实任务事件流、断点续传、作品库同步、A/B 试听决策、安全合规；
- 电脑端治理接口（023 账本/024 边界/025 观测）可用；
- App 版本号当前为 0.1.0（debug）。

## 3. 允许范围

```text
apps/android/app/src/main/
apps/android/app/src/test/
apps/android/app/src/androidTest/
apps/android/docs/
docs/tasks/deepseek/DSK-MFY-ANDROID-012/
outputs/deepseek_validation/DSK-MFY-ANDROID-012/
```

禁止：新增功能、修改电脑端代码、支付/合作、创建发布密钥（签名仅 debug）、
Git 危险操作。

## 4. 执行阶段

### Stage A｜稳定性收口

- 30 分钟真机稳定性：连续上传/处理/试听/浏览循环；
- 监控内存（无持续增长）、ANR、崩溃日志（Logcat + tombstone）；
- 修复发现的稳定性问题，禁止用"重启就好"掩盖；
- 冷启动/热启动/进程恢复三种路径验证。

### Stage B｜版本与构建固化

- versionName 升到 0.2.0，versionCode 递增；
- 建立可复现的 Beta 构建脚本（gradlew 命令 + 环境变量清单）；
- 记录 APK 大小与 SHA-256；proguard 保持 debug 不混淆（说明原因）。

### Stage C｜与电脑端治理对齐

- App 构建/冒烟结果写入电脑端观测（复用 025 observability 或补充 run manifest）；
- App 版本与电脑端 API 版本的兼容矩阵文档化；
- 确认 App 未引入新的架构边界违例（复用 024 enforcer 思路，移动端区域独立声明）。

### Stage D｜封版证据

- Beta 验收清单：功能清单、真机截图、稳定性日志、权限清单、APK 哈希；
- 已知限制清单（不含掩盖项）；
- 下一周期（0.3.0）只提一个主方向。

## 5. P0 门槛

- 30 分钟真机稳定运行：0 崩溃、0 ANR、内存无持续增长；
- 0.2.0 APK 可复现构建，有 SHA-256；
- 007-011 功能回归全绿；
- 与电脑端 API 兼容矩阵文档化；
- 已知限制如实列出，无隐藏；
- 交付四件套 + Beta 验收清单。

## 6. 停止条件

若需发布签名密钥、需上架商店、需修改电脑端或超时，HOLD + SCOPE_CHANGE_REQUEST.md。最终状态只能是 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。
