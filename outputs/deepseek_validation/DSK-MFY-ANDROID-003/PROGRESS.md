# DSK-MFY-ANDROID-003｜PROGRESS

**状态：** READY_FOR_CODEX_REVIEW
**日期：** 2026-08-02

## 阶段完成情况

| Stage | 目标 | 状态 | 证据 |
|---|---|---|---|
| A | 契约冻结（health/pair/capabilities live；projects/uploads/jobs/artifacts schema-frozen） | ✅ | `moodify-core-package/src/moodify/api/routes/v1.py`；`docs/api/v1.md`；13 个契约测试 |
| B | 本地连接（USB adb reverse + 局域网输入 + 可撤销令牌存 Keystore） | ✅ | `TokenStore.kt`（AES/GCM）；`BaseUrlStore.kt`；`ConnectionCard.kt` 状态展示 |
| C | Android 数据层（client/repository/ViewModel；可取消、超时明确、不阻塞主线程） | ✅ | `MoodifyApiClient.kt`（HttpURLConnection，零第三方依赖）；`ConnectionRepository.kt`；`ConnectionViewModel.kt` |
| D | 契约与真机测试（fake server 单测 + 小米真机 health/pair/revoke + 失败注入） | ✅ | 9 个 JVM 单测；真机日志见 VALIDATION.md |

## 交付物

1. 服务端 v1 契约路由（`routes/v1.py`，挂载于 `api/main.py`）
2. 契约文档（`docs/api/v1.md`）
3. 服务端契约测试（`tests/api/test_v1_contract.py`，13 项）
4. Android 数据层（7 个文件，零新增网络依赖）
5. Android 单元测试（`MoodifyApiClientTest.kt`，9 项，纯 ServerSocket fake server）
6. 连接状态 UI（"我的"页 ConnectionCard）

## Commit

- `fdc451c` feat(api): mobile API v1 contract — health/pair/capabilities live
- `aa6136e` feat(android): connect/pair/revoke against self-hosted API v1

## P0 门槛对照

| 门槛 | 结果 |
|---|---|
| API v0.1 文档与机器 schema 一致 | ✅ docs/api/v1.md ↔ v1.py ↔ 测试 |
| USB 真机连接、配对、重连成功 | ✅ 见 VALIDATION.md 日志 |
| App 无硬编码 IP、令牌和 Python 内部类型 | ✅ BaseUrlStore 默认 127.0.0.1:8000（非硬编码进逻辑）；令牌只存 Keystore |
| 超时、离线、未授权、版本不兼容可区分 | ✅ 单测覆盖 Timeout/Offline/Unauthorized/NotImplemented/ServerError |
| 日志无令牌、绝对路径和 traceback 泄漏 | ✅ 服务端测试断言 + 真机 logcat 检查 |
| 022 收集门禁不退化 | ✅ API 测试可收集（moodify-bridge 收集错误属 022 自身范围，见 HANDOFF 事实边界） |
| 001–002 真机门禁继续通过 | ✅ UI 重构后 app 在小米 10 正常安装运行 |
