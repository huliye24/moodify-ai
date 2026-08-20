# Previous Phase Gate — MFY-DATA-FOUNDATION-001-REV2 Phase A1

依据：`MFY-INFRA-FOUNDATION-001` Final Report（verdict: PASS_WITH_HUMAN_BLOCKERS，2026-08-13）。

| Gate | 要求 | 状态 |
|---|---|---|
| canonical_git_baseline = known | LA 生产 music 源码已回收 | PASS：apps/music-web-baseline @ 3180703f，Draft PR #1 |
| hangzhou_internal_api = authenticated | 杭州 8000 应用层鉴权 | PASS：X-Moodify-Service-Key/Bearer 401/200 实测（本机/公网/LA 三处） |
| polardb_runtime_identity = least_privilege | moodify_app 最小权限 | PASS：moodify_app@172.21.10.9 仅 moodify_dev DML，负向 CREATE USER 测试通过 |
| la_direct_polardb = false | LA 不直连 PolarDB | PASS：零连接代码/配置，架构不变 |

遗留人工项（不影响本阶段数据层工作）：
1. 阿里云安全组收紧 8000 → 103.144.246.242/32（BLOCKED_BY_HUMAN_AUTHORITY）
2. PolarDB 白名单收紧至 172.21.10.9（BLOCKED_BY_HUMAN_AUTHORITY）

本阶段继续前提满足。
