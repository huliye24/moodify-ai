# DSK-MFY-ANDROID-007｜真实处理体验与任务事件流

**计划日期：** 2026-08-02  
**目标完成日期：** 2026-08-02  
**依赖：** ANDROID-006 ACCEPT  
**执行 Worker：** DeepSeek  
**最终 Judge：** Codex / 授权用户  
**执行时限：** 120 分钟  
**任务状态：** PLANNED

## 1. 目标

006 封版后，App 只有演示处理。本包把"标准处理"从演示状态升级为**真实任务事件流**：上传成功后，App 通过任务事件驱动页面状态，不再用假进度冒充后端事件（002 已声明"禁止用假进度"）。

## 2. 当前基线

- 006 已交付本地 Alpha：四入口、设计系统、API v0.1 契约、作品上传与 A/B 结构占位；
- 处理任务目前走演示数据源（fake data source），真实处理未接；
- 电脑端 `moodify` API v0.1 已可用（`POST /process` 返回 WAV）。

## 3. 允许范围

```text
apps/android/app/src/main/
apps/android/app/src/test/
apps/android/app/src/androidTest/
apps/android/docs/
docs/tasks/deepseek/DSK-MFY-ANDROID-007/
outputs/deepseek_validation/DSK-MFY-ANDROID-007/
```

禁止：修改电脑端 Python 业务代码、支付/云账号/合作计划、下载新依赖库、
删除用户缓存、Git 危险操作。

## 4. 执行阶段

### Stage A｜任务事件模型

- 定义 `ProcessingEvent` 密封类：Submitted / Queued / Started / Progress / Completed / Failed / Canceled；
- UiState 与事件一一映射，页面只消费事件流，不轮询猜测；
- 事件带 server timestamp、job_id 和 evidence 引用，不伪造进度百分比。

### Stage B｜真实处理接入

- 上传作品后调用真实 `POST /process`，轮询或 SSE 任务状态（以电脑端 API 实际能力为准，无 SSE 则用带指数退避的轮询）；
- 处理完成后下载 WAV 到 App 沙箱，保存本地 URI 与 SHA-256；
- 网络错误、超时、服务端 4xx/5xx 映射为 Error 状态，带重试入口；
- 后台任务在前台切换后状态不丢失（进程存活时）。

### Stage C｜任务列表真实化

- 任务列表从真实任务记录渲染，不再用 fake data；
- 每项显示状态徽章、耗时、大小与失败原因；
- 提供取消入口（仅当服务端支持取消；否则禁用并说明）。

### Stage D｜真机冒烟与回归

- 真实上传→处理→完成全链路在小米真机跑通；
- 断网、服务端 500、超时三个失败注入均有可审计表现；
- 001 构建门禁、002 四入口导航、006 视觉验收全部回归通过。

## 5. P0 门槛

- 真实处理全链路（上传→处理→下载）在真机成功，产物有 SHA-256；
- 无假进度：所有进度来自真实事件或明确"未知"；
- 三个失败注入都有对应 UiState 与重试路径；
- fake data source 从任务/处理流程中移除（可保留在未接功能的占位页）；
- 前序全部门禁回归通过；
- 交付 PROGRESS/VALIDATION/FAILURE_LEDGER/HANDOFF。

## 6. 停止条件

若电脑端 API 无法支持真实处理、需要修改电脑端代码、需要新依赖或突破时限，立即 HOLD 并提交 SCOPE_CHANGE_REQUEST.md。最终状态只能是 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。
