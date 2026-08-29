# W01-P06 Acceptance Checklist

图例：✅ 完成 · 🟡 契约/单元层验证(真机/部署未验) · 🔴 BLOCKED · ❌ 未做

## Gates
- [x] READY contract loaded ✅
- [x] object access contract loaded ✅
- [x] secret ownership loaded ✅
- [x] Android reality scan complete ✅

## Delivery
- [x] READY-only guard ✅
- [x] authorization ✅
- [x] metadata contract ✅
- [x] signed URL/proxy ADR ✅
- [x] bounded expiry ✅
- [x] refresh path ✅
- [ ] range/seek（🟡 契约+TST-05；真实 HTTP range 部署后验）
- [x] stable Track identity ✅
- [x] no source/stem accidental exposure ✅

## Android
- [x] existing player reused where viable ✅（ExoPlayer 复用）
- [ ] PLAY（🟡 状态映射单测过；真机 BLOCKED）
- [ ] PAUSE（🟡 同上）
- [ ] seek（🟡 seekTo 契约；真机 BLOCKED）
- [ ] buffering（🟡 isLoading 映射；真机 BLOCKED）
- [ ] reconnect（🟡 契约；真机 BLOCKED）
- [ ] URL refresh（🟡 客户端+服务端单元过；真机 BLOCKED）
- [ ] next/previous/swipe if in scope（🟡 next/previous 有；swipe 无=不在当前范围）
- [ ] lifecycle behavior（🟡 代码审查；真机 BLOCKED）
- [ ] audio focus behavior（❌ 未实现 → HUMAN_DECISION_REQUIRED）

## Failure
- [x] playback taxonomy ✅
- [x] compute failure isolation ✅（TST-09）
- [x] missing object behavior ✅（TST-03）
- [x] expired URI behavior ✅（TST-04）

## Security
- [x] no OSS secret in APK ✅
- [x] no DB secret in APK ✅
- [x] no external processing API secret in APK ✅
- [x] HTTPS production path ✅
- [x] no full signed URL in durable logs ✅（契约 + redact 工具）

## Evidence
- [x] playback events ✅（契约；持久化未建=第一阶段不建分析平台）
- [x] render traceability ✅
- [x] correlation ID ✅（预留）

## E2E
- [ ] READY test track plays end-to-end（🔴 BLOCKED）
- [ ] seek works（🔴 BLOCKED）
- [ ] pause/resume works（🔴 BLOCKED）
- [ ] expiry refresh works if applicable（🟡 单元过；E2E BLOCKED）

## Scope
- [x] no compute changes ✅
- [x] no state-machine changes ✅
- [x] no unrelated UI expansion ✅
- [x] no iOS/offline/community work ✅

## Handoff
- [x] P07 handoff complete ✅
- [x] stop after P06 ✅
