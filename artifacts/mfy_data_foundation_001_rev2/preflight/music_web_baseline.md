# Music Web Baseline — MFY-DATA-FOUNDATION-001-REV2 Phase A3

| 项 | 值 |
|---|---|
| Repo | github.com/huliye24/moodify |
| Branch | codex/moodify-music-commercial-v1-001 |
| Commit | 5cbbc16（feat(music-web): establish commercial domain authority） |
| Base | 71428a1 listening-first + d747043 audit + 5cbbc16 drizzle/DOMAIN_CONTRACT |
| Build | `bash scripts/build-verified.sh`（vinext build，带 timeout） |
| Start | `vinext start --hostname 127.0.0.1 --port 3100`（LA systemd moodify-music） |
| 部署路径 | tar → /opt/moodify/music/releases/<ts> → symlink current（LA，机制保留） |
| 当前 routes | `/`（单页 app/page.tsx，listening-first） |
| 当前 player | browser audio（原生 audio 元素：seek/queue/ended-next） |
| Catalogue | Cadeau10 专辑1 5 曲（public/audio + NEXT_PUBLIC_AUDIO_BASE_URL=https://rongjinwenchuan.xyz/audio） |
| 已有数据层 | drizzle schema（D1/SQLite 语义：users/creator_profiles/tracks/track_versions/creation_passports/creator_follows/track_favorites/license_intents/support_intents/listen_events/publication_events）+ drizzle migration 0000 |
| 已有文档 | docs/DOMAIN_CONTRACT.md（Phase C foundation）、AUDIT.md（325 行产品审计） |

**Rev.2 权威调整**：PolarDB MySQL B（moodify_dev）= Operational Source of Truth；drizzle schema 保留为 Web 前端类型/契约参考（非生产数据权威）。本阶段在其上实现 12 步商业闭环，不重写首页视觉（保留 listening-first + 已删营销文案状态）。
