# DSK-MFY-ANDROID-009｜作品库本地持久化与云同步地基

**计划日期：** 2026-08-02  
**目标完成日期：** 2026-08-02  
**依赖：** ANDROID-008 ACCEPT  
**执行 Worker：** DeepSeek  
**最终 Judge：** Codex / 授权用户  
**执行时限：** 150 分钟  
**任务状态：** PLANNED

## 1. 目标

作品是 Moodify 的核心资产（001 起贯穿的概念）。本包建立**作品库**：本地持久化 + 与电脑端/服务端同步的地基，让用户换设备、清缓存后作品不丢失，且离线可浏览。

## 2. 当前基线

- 008 已交付上传鲁棒性：断点续传、SHA-256、失败重试；
- 作品/任务数据目前内存态或简单文件，无结构化持久化；
- 电脑端 Workspace v2 有 Project/Asset 概念（domain 模型），App 尚未对齐。

## 3. 允许范围

```text
apps/android/app/src/main/
apps/android/app/src/test/
apps/android/app/src/androidTest/
apps/android/docs/
docs/tasks/deepseek/DSK-MFY-ANDROID-009/
outputs/deepseek_validation/DSK-MFY-ANDROID-009/
```

禁止：修改电脑端代码、引入云端账号体系（本包只做同步协议地基，不做账号）、
支付/合作、Git 危险操作。

## 4. 执行阶段

### Stage A｜作品数据模型与存储

- 定义 `WorkItem`：work_id、title、source_uri、sha256、status、created_at、versions；
- Room 数据库：WorkItem / Version / TaskRecord 三表，外键关联；
- 存储抽象 `WorkRepository`：读写、查询、分页；UI 不直接碰数据库。

### Stage B｜与电脑端 Project 对齐

- 将 App work_id 映射到电脑端 project_id（读取电脑端 API 的 Project 契约）；
- 作品详情从 Project 派生：原始音频、处理版本、导出记录；
- 不引入不一致的重复模型：App 本地是缓存，电脑端是权威（读多写少）。

### Stage C｜同步协议地基

- 定义 `SyncManifest`：本地上次同步点、增量变更列表、冲突标记；
- 实现单向同步（App→电脑端或电脑端→App 其一，以 API 能力为准）：
  - 拉取：电脑端作品列表合并进本地；
  - 推送：本地新增/修改回传；
- 冲突不自动解决：标记 CONFLICT 等待用户决定（023 失忆防护在移动端的对应）；
- 离线时本地可浏览，联网后自动同步。

### Stage D｜真机验证

- 离线浏览、同步合并、冲突标记三个场景在真机跑通；
- 清缓存后从电脑端恢复作品列表；
- 001-008 门禁全绿。

## 5. P0 门槛

- 作品库持久化：应用重启后作品/版本/任务不丢；
- 电脑端为权威，App 本地为缓存，无双向覆盖；
- 冲突标记而非自动覆盖；
- 离线可浏览，联网自动同步；
- 前序门禁全绿；交付四件套。

## 6. 停止条件

若电脑端 Project API 契约不可读、同步需账号体系、需新依赖或超时，HOLD + SCOPE_CHANGE_REQUEST.md。最终状态只能是 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。
