# MFY_MUSIC_CREATOR_LIFECYCLE_001 — Evidence

日期：2026-08-13

## 测试（本地 SQLite + TestClient）
```
48 passed（含 10 项新生命周期测试）
```
新增测试（tests/test_lifecycle.py）：
- test_drafts_list_and_stages / test_draft_isolation_cross_creator（403）
- test_resume_stage_transitions（draft→version_ready→passport_ready→published + media 指纹）
- test_resume_rejected_for_other_creator / test_abandon_cross_creator_forbidden（403）
- test_abandon_draft（→archived + 幂等 + audit）/ test_abandon_published_forbidden（409）
- test_media_references_only_referenced / test_publish_replay_is_safe
- test_version_retry_no_duplicate / test_audit_event_endpoint
conftest.py：统一 DB override（修复跨文件 override 污染）。

## 线上部署验证（2026-08-13）
```
内部（经 LA 隧道/LA 视角）:
  GET  /internal/v1/music/media/references -> 200 {"references":["cadeau10-album1/...wav"]}
  GET  /internal/v1/music/creators/{id}/drafts -> 200 {"drafts":[]}
  写路径（tracks/abandon）-> 503 BETA_AUTH_REQUIRED（Beta 门控，产品预期）
BFF 公共:
  GET  https://rongjinwenchuan.xyz/api/v1/music/media/references -> 200
  POST /api/v1/music/audit-events -> 201
媒体审计 dry-run（LA /opt/moodify/music-bff/scripts）:
  referenced media keys: 1；no orphan candidates（保留期 0 也干净）
```

## 部署清单
| 组件 | 版本/位置 | 状态 |
|---|---|---|
| 杭州 moodify-api | :8000（含 drafts/resume/abandon/references/audit-events） | active |
| LA moodify-music-bff | :8100（转发端点） | active |
| 媒体审计脚本 | /opt/moodify/music-bff/scripts/media_audit.py | dry-run 验证 |
| Git | 062c760 on codex/mfy-data-foundation-001-rev2（PR #2） | pushed |

## 关键修复
- publish 幂等 payload 稳定化（去掉 from 字段）+ 已发布安全重放
- 测试共享 conftest（StaticPool ENGINE + app override 统一）
