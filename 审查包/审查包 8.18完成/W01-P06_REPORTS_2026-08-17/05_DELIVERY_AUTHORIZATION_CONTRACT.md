# 05 — Delivery Authorization Contract

**W01-P06 · 2026-08-17 · 实现：`delivery.py::DeliveryService`**

## Request

- authenticated actor / access scope：`user_scope`（现状 V1 匿名 = `"public"`；`SecureStore` 预留 session token 未启用）
- `track_id`
- app version（可选，`app_version`）
- `correlation_id`（可选，证据关联）

## Checks（顺序，全过才签发）

1. **Track exists** — `repo.get_track(track_id)`，否则 `TRACK_NOT_FOUND`。
2. **Track is READY** — authoritative `jobs.current_state='READY' AND ready_object_id IS NOT NULL`（P04 语义），否则 `TRACK_NOT_READY`。
3. **Final render object exists** — `objects` 行存在且对象存储 `head()` 命中，否则 `OBJECT_NOT_FOUND`（reconciliation 路径）。
4. **Actor/access scope may play it** — `_check_access()` 按 `owner_scope`，否则 `ACCESS_DENIED`。
5. **Object access class permits delivery** — render = 私有/受控（P03 数据类），仅经签发入口，不公读。
6. **Issue with bounded TTL** — `URI_TTL_SECONDS=3600`，过期可刷新。

> 对应 TST-01/02/03/07。全部本地通过。

## Result

- `playback_session_id`
- playback metadata（04 报告）
- URI / session token（`moodify://deliver/` 签名定位符）
- expiry

## Forbidden（红线）

- ❌ public-read default bucket（P03 OSS policy：默认禁止 public-read）
- ❌ permanent mobile OSS credential（DLV-INV-02 / P02 S-09：OSS 凭据服务端 only，永不落 Android）
- ❌ permanent URL written into Track record（身份与 URL 分离）
- ❌ 客户端自己拼 OSS key / 根据 DB 字段猜 URL（任务书 §6.1）

## 现状事实（不虚构）

- 访问域模型当前为**单维 `owner_scope`**（track 级）。V1 匿名收听下 `user_scope="public"`，`owner_scope=NULL` 即公开可播。更细粒度（用户/订阅/地区）授权 = 后续 + HUMAN_DECISION_REQUIRED。
- 真实鉴权（账号/session token）未启用：`SecureStore` 预留未接；BFF 现状无鉴权（NW-02 current）。**鉴权上线依赖 BFF 部署（BLOCKED）。**
