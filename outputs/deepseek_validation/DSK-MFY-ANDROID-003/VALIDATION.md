# DSK-MFY-ANDROID-003｜VALIDATION

**日期：** 2026-08-02
**设备：** Xiaomi 10（adb serial 5fe6dfde，1080x2120）
**服务端：** `python -m uvicorn moodify.api.main:app --host 0.0.0.0 --port 8000`
**连接：** `adb reverse tcp:8000 tcp:8000`

## 1. 服务端契约测试（13/13 绿）

```text
$ python -m pytest tests/api/test_v1_contract.py -q
.............  [100%]
13 passed in 3.19s
```

覆盖：health schema、pair 令牌生成/幂等/缺参/非 JSON、revoke 成功与未知令牌、capabilities、冻结端点 501 结构、无 traceback/绝对路径、request_id 回传。

## 2. Android 单元测试（9/9 绿）

```text
$ ./gradlew :app:testDebugUnitTest
BUILD SUCCESSFUL
testsuite tests="9" skipped="0" failures="0" errors="0"
```

覆盖：health/pair/capabilities 解析、401→UNAUTHORIZED、501→NOT_IMPLEMENTED、连接拒绝→OFFLINE、慢服务→TIMEOUT、500 无 traceback、错误体解析。

## 3. 真机端到端（uiautomator 驱动 UI + 服务端日志）

| 步骤 | 操作 | 服务端日志 | 结果 |
|---|---|---|---|
| 1 | 启动 app → 我的 → 连接电脑端 | `GET /api/v1/health 200`（127.0.0.1:7031） | ✅ 真机→adb reverse→FastAPI 链路通 |
| 2 | 点"配对" | `POST /api/v1/pair 200`（127.0.0.1:7225）→ 自动 `GET /health 200` | ✅ 令牌生成并落 Keystore |
| 3 | UI 状态检查（uiautomator dump） | — | ✅ "已连接 · API v0.1.0 · 模式 mobile-v1"；按钮变为"撤销配对" |
| 4 | 点"撤销配对" | `POST /api/v1/pair/revoke 200`（127.0.0.1:7349） | ✅ 服务端撤销 + 本地清除 |
| 5 | 停服务 → 点"连接电脑端" | —（服务已停） | ✅ UI 显示"连接失败"+ "无法连接服务器，请检查 USB 转发或网络" + "重新连接"按钮（OFFLINE 分类 + 可行动提示） |

## 4. 泄漏检查

```text
$ adb logcat -d | grep -iE "Bearer|token_id"
（无输出——App 日志无令牌泄漏）
```

服务端测试同时断言响应不含绝对路径（`E:\` / `C:`）与 `Traceback`。

## 5. 版本与构建

- APK：`app-debug.apk`，versionName 0.1.0，SHA-256 见下
- 构建命令：`JAVA_HOME=<Android Studio jbr> ANDROID_HOME=<SDK> ./gradlew :app:assembleDebug`
