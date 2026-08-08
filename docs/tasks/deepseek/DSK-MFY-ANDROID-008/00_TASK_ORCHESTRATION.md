# DSK-MFY-ANDROID-008｜上传鲁棒性与断点续传

**计划日期：** 2026-08-02  
**目标完成日期：** 2026-08-02  
**依赖：** ANDROID-007 ACCEPT  
**执行 Worker：** DeepSeek  
**最终 Judge：** Codex / 授权用户  
**执行时限：** 120 分钟  
**任务状态：** PLANNED

## 1. 目标

007 打通真实处理，但上传仍是单次请求。本包把上传做成**可恢复**的：大文件、弱网、应用被杀都不丢失用户作品。Moodify 的价值在作品资产，上传是资产进入系统的唯一城门（023 城门语义在移动端的对应）。

## 2. 当前基线

- 007 已交付真实任务事件流：上传→处理→下载全链路可用；
- 上传为单次 HTTP 请求，无分片、无重试、无断点；
- 作品源文件在手机本地（相册/文件选择器授权）。

## 3. 允许范围

```text
apps/android/app/src/main/
apps/android/app/src/test/
apps/android/app/src/androidTest/
apps/android/docs/
docs/tasks/deepseek/DSK-MFY-ANDROID-008/
outputs/deepseek_validation/DSK-MFY-ANDROID-008/
```

禁止：修改电脑端代码、引入付费第三方上传库、删除用户媒体、Git 危险操作。

## 4. 执行阶段

### Stage A｜上传状态机

- 定义 `UploadState`：Idle / Preparing / Transferring(progress) / Verifying / Paused / Failed / Completed；
- 上传任务持久化（Room 或文件），进程被杀后可恢复；
- 每次状态变化写审计记录（时间、字节数、sha256 校验）。

### Stage B｜分片与断点续传

- 若电脑端支持分片（Range/分片协议），实现分片上传；
- 否则实现"重试 + 已完成部分缓存"，断网恢复后从断点继续；
- 上传前计算文件 SHA-256，完成后服务端校验；
- 进度来自真实字节数，不伪造百分比。

### Stage C｜失败与重试策略

- 网络切换、超时、服务端 5xx 自动重试（指数退避，上限 3 次）；
- 4xx 不重试，明确展示错误原因；
- 上传中应用被杀：重启后恢复任务，已传部分不重传（能力允许时）。

### Stage D｜真机验证

- 3MB 文件在正常网络、弱网（飞行模式打断）、应用被杀三种场景下均能完成；
- 验证 SHA-256 一致性；
- 001-007 门禁全部回归。

## 5. P0 门槛

- 上传中断后可恢复（应用重启或网络恢复），不丢文件；
- 进度为真实字节数；
- SHA-256 前后一致；
- 4xx/5xx 行为正确（4xx 停、5xx 退避重试）；
- 上传任务持久化，无内存态丢失；
- 前序门禁全绿；交付四件套。

## 6. 停止条件

若电脑端不支持任何断点能力且无法在客户端缓存已完成部分、需要改电脑端代码、需新依赖或超时，HOLD + SCOPE_CHANGE_REQUEST.md。最终状态只能是 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。
