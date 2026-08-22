# 12 — P06 Playback Test Report

**W01-P06 · 2026-08-17 → 2026-08-18**

## 执行环境（事实）

- 服务端 Python：`pytest 9.1.1` / Python 3.13.14（隔离 venv），`moodify-core-package`（`pythonpath=src`）。
- Android JVM：`gradlew :app:testDebugUnitTest`（AGP 8.11.1 / Kotlin 2.2.20 / JBR 17，`--offline`）。
- Lint：`ruff 0.16.3`（项目默认规则集）。

## 结果总览

| 侧 | 套件 | 结果 |
|---|---|---|
| 服务端 | `test_delivery.py` | **10/10 PASS** |
| 服务端 | P06 依赖面（data_plane 9 + control 12 + pipeline 16） | **37/37 PASS**（合并 47/47） |
| Android | `PlaybackDeliveryClientTest` | **6/6 PASS**（修复后） |
| Lint | `delivery.py` + `test_delivery.py` | **ruff 全过** |

## TST-01..15 逐项

| TST | 项 | 覆盖 | 结果 |
|---|---|---|---|
| 01 | READY-only | 服务端 `test_tst01` | ✅ PASS |
| 02 | valid playback metadata | 服务端 `test_tst02` | ✅ PASS |
| 03 | missing object | 服务端 `test_tst03` | ✅ PASS |
| 04 | URL expiry refresh | 服务端 `test_tst04` + Android `tst04` | ✅ PASS（Android 侧本包修复） |
| 05 | range/seek | 服务端 `test_tst05`（契约） | ✅ PASS（契约）；真实 HTTP range 部署后验（BLOCKED） |
| 06 | buffering recovery | 服务端 `test_tst06` | ✅ PASS |
| 07 | unauthorized access | 服务端 `test_tst07` + Android `tst07` | ✅ PASS（Android 侧本包修复） |
| 08 | no client secrets | 服务端 `test_tst08` + APK 扫描 | ✅ PASS |
| 09 | playback failure isolation | 服务端 `test_tst09` + Android `tst09` | ✅ PASS（Android 侧本包修复 client） |
| 10 | stable Track identity | 服务端 `test_tst10` + Android `tst10` | ✅ PASS |
| 11 | PLAY/PAUSE | Android `tst11`（状态映射） | ✅ PASS（映射）；真机 PLAY BLOCKED |
| 12 | next/previous/swipe | 契约 | ⚠️ next/previous 有；**swipe 无**（产品面无手势系统）；真机 BLOCKED |
| 13 | app lifecycle | 代码审查 | ⚠️ 播放器随 Activity 生死；真机验证 BLOCKED |
| 14 | audio focus | — | ❌ **未实现**（契约占位）→ HUMAN_DECISION_REQUIRED |
| 15 | playback evidence | Android `tst15`（失败码映射） | ✅ PASS（映射）；事件持久化未建（第一阶段不建分析平台） |

## 本包修复的 Android 缺陷（3 处）

1. **Client bug（`PlaybackDeliveryClient.resolve`）**：fetcher 已抛 `DeliveryException` 时被 `catch(Exception)` 重新经 `fromJson` 按消息文本二次推导，丢失结构化 `failure` code（tst09 失败根因）。修复：优先 `catch(DeliveryException) { throw e }` 透传结构化错误。→ tst09 PASS。
2. **Test bug（tst04）**：fetcher 刷新时只改 `uri` 字符串，`expiresAt` 恒为 `50L`，导致 refreshed 仍过期。修复：第二次调用返回未过期 `expiresAt`。→ tst04 PASS。
3. **Test bug（tst07）**：`JSONObject(...) as Exception` 抛 `ClassCastException`，实际未测 ACCESS_DENIED 映射。修复：改为抛含 `ACCESS_DENIED` 消息的异常并断言映射到 `ACCESS_DENIED`。→ tst07 真实有效。

> 修复后 Android `compileDebugKotlin` / `compileDebugUnitTestKotlin` / `testDebugUnitTest` 全部 BUILD SUCCESSFUL。

## Lint 说明（不虚构）

- 本包自有文件（`delivery.py`/`test_delivery.py`）：初跑 ruff 有 4 处可修复样式项（UP037/UP012/RUF100/RUF059），已 `ruff --fix` + 手改，现 **全过**。
- 旁观测得 P05 `pipeline.py` 在当前 ruff 0.16.3 默认规则下有若干 `RUF100`（历史 `# noqa: BLE001` 在默认规则集下被判 unused）——属 ruff 版本/配置漂移，**P05 文件超出 P06 边界，本包未改动**，仅记录。

## E2E（任务书 §20）

```text
READY → metadata → URI → Android → PLAY → seek → pause → resume → finish（+expiry refresh）
```

**状态：BLOCKED。** 需要：真实 BFF 交付端点（未部署）+ 真实 READY 曲目（无）+ Android 真机/模拟器（本会话无）+ OSS/签名落地（未开通）。本包只在**契约层 + 本地/单元层**验证全链逻辑，不伪造真机 E2E 证据。→ 转 P07 + 人类。
