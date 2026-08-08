# DSK-MFY-ANDROID-004｜作品上传与真实处理任务闭环

**计划日期：** 2026-08-02  
**目标完成日期：** 2026-08-02  
**依赖：** ANDROID-003 ACCEPT  
**执行 Worker：** DeepSeek  
**最终 Judge：** Codex / 授权用户  
**执行时限：** 180 分钟  
**任务状态：** PLANNED

## 1. 目标

跑通第一条真实纵向链路：从小米手机选择音频、创建作品、可靠上传到本地电脑、提交 Moodify 处理任务、离开页面后继续、恢复并获得可下载产物。处理进度必须来自后台真实事件，禁止计时器伪造。

## 2. 状态机

```text
DRAFT -> UPLOADING -> UPLOADED -> QUEUED -> ANALYZING
      -> PLANNING -> PROCESSING -> VERIFYING -> READY
      -> FAILED / CANCELED
```

每次状态变化包含 task_id、sequence、timestamp、engine_version、progress、message_code 和可选 evidence。客户端按 sequence 去重并拒绝非法倒退。

## 3. 允许范围

```text
apps/android/
moodify-core-package/src/moodify/api/
moodify-core-package/src/moodify/services/          # 仅任务适配
moodify-core-package/tests/api/
docs/api/
docs/tasks/deepseek/DSK-MFY-ANDROID-004/
outputs/deepseek_validation/DSK-MFY-ANDROID-004/
```

禁止改写 DSP 算法、增加云存储、支付、账户、合作计划、手机本地渲染或后台常驻监控；禁止用固定延时生成处理进度。

## 4. 执行阶段

### Stage A｜手机文件导入

- 使用 Storage Access Framework，不申请全盘存储权限；
- 读取显示名、大小、MIME、时长和可用 URI 权限；
- 拒绝空文件、不可读文件和超出配置上限的输入；
- 不复制整份音频到内存。

### Stage B｜可靠上传

- 分块、可恢复、输入 SHA-256、upload_id 和幂等键；
- 服务端在完成前写临时区，校验成功后原子登记；
- 重传同一块不重复写入，输入 hash 相同可显式复用；
- 断网、进程被杀和服务重启后可以续传或安全重开。

### Stage C｜作品与任务

- 创建 project_id、source_asset_id、job_id；
- App 本地保存同步索引，电脑为正式数据源；
- 提交任务必须引用输入 hash、处理意图和 API 版本；
- 任务取消为幂等操作，不能留下伪 READY 产物。

### Stage D｜真实进度与恢复

- 使用轮询或 SSE/WebSocket 中最简单可靠的一种；
- App 切后台、Activity 重建和进程重启后重新同步；
- MIUI 终止客户端不应终止电脑任务；
- 状态未知时显示“正在重新同步”，不猜测完成度。

### Stage E｜端到端真机

- 使用授权测试音频跑通上传、处理、验证和产物登记；
- 测试断网、重复点击、重复上传、取消、服务停止与恢复；
- 保存客户端日志、服务端日志、状态事件和 hash 链。

## 5. P0 门槛

- 真机选择文件不需要全盘权限；
- 大文件不整体读入内存；
- 上传可断点续传且 hash 一致；
- 创建任务幂等，重复点击不产生重复处理；
- 所有进度来自真实后台状态；
- App/Activity 重启后任务可恢复；
- 失败与取消不产生伪成功产物；
- 003 契约、022 测试和 Android 构建门禁持续通过。

## 6. 今日规则

今日目标是完成一首测试音频的真实闭环，不扩大到批处理、多用户或云端。若现有 Engine 无法提供可验证处理入口，立即 HOLD 并提交最小接口缺口，不得伪造 READY。最终状态仅 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。

