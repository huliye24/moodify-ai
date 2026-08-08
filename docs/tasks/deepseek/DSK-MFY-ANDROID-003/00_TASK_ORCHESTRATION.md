# DSK-MFY-ANDROID-003｜本地电脑连接与 Moodify API v0.1 契约

**计划日期：** 2026-08-02  
**目标完成日期：** 2026-08-02  
**依赖：** ANDROID-002 ACCEPT；ORDER-BEAUTY-022 至少恢复 API 导入与测试收集  
**执行 Worker：** DeepSeek  
**最终 Judge：** Codex / 授权用户  
**执行时限：** 150 分钟  
**任务状态：** PLANNED

## 1. 目标

建立 Android 永久依赖的稳定协议，使同一 App 可以连接 USB 转发、本地局域网、未来 Go Gateway 或云端，而不认识 Python 内部模块。

## 2. API v0.1 最小契约

```text
GET  /api/v1/health
POST /api/v1/pair
GET  /api/v1/capabilities
POST /api/v1/projects
GET  /api/v1/projects/{id}
POST /api/v1/uploads
GET  /api/v1/jobs/{id}
POST /api/v1/jobs/{id}/cancel
GET  /api/v1/artifacts/{id}
```

003 只要求 health、pair、capabilities 与连接状态真实可用；项目、上传、任务和产物先冻结 schema，由 004/005 实现。

## 3. 允许范围

```text
apps/android/
moodify-core-package/src/moodify/api/             # 新增薄适配层，不重写引擎
moodify-core-package/tests/api/
docs/api/
docs/tasks/deepseek/DSK-MFY-ANDROID-003/
outputs/deepseek_validation/DSK-MFY-ANDROID-003/
```

禁止修改 DSP、领域语义和声音结果；禁止云部署、Go 重写、开放无鉴权局域网服务、在 App 硬编码电脑 IP 或令牌。

## 4. 执行阶段

### Stage A｜契约冻结

- 定义版本化 JSON schema/OpenAPI、稳定 ID、时间、错误、进度和幂等语义；
- 错误至少区分 OFFLINE / TIMEOUT / UNAUTHORIZED / INCOMPATIBLE / SERVER_ERROR；
- App 不解析 Python traceback；服务不返回绝对路径。

### Stage B｜本地连接

- 支持 USB `adb reverse tcp:8000 tcp:8000`；
- 支持用户输入局域网地址，禁止隐式扫描整个网络；
- 配对产生可撤销的本地令牌，安全保存于 Android Keystore；
- 展示连接、未连接、版本不兼容和服务忙。

### Stage C｜Android 数据层

- 建立 API client、repository、domain use case 和 ViewModel；
- 所有网络操作可取消、超时明确且不阻塞主线程；
- base URL 可配置但不允许任意非本地明文地址进入发布构建。

### Stage D｜契约与真机测试

- 服务端 schema 测试、Android fake server 测试；
- USB 转发真机 health/pair；
- 断开 USB、错误端口、服务停止、令牌失效均有可行动提示；
- 不记录令牌和原始敏感响应。

## 5. P0 门槛

- API v0.1 文档与机器 schema 一致；
- USB 真机连接、配对、重连成功；
- App 无硬编码 IP、令牌和 Python 内部类型；
- 超时、离线、未授权、版本不兼容可区分；
- 日志无令牌、绝对路径和 traceback 泄漏；
- 022 收集门禁不退化；001–002 真机门禁继续通过。

## 6. 今日规则

今日只冻结并实现连接契约，不得借机重写后端或引入 Go。若 022 前置未满足则 HOLD，并报告阻断，不得复制一套临时后端。最终状态仅 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。

