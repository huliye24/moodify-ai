# Moodify Cloud Production

**日期：** 2026-08-24
**阶段：** Moodify Entropy Reduction 002 — Mainline Context Freeze
**下一步：** Cloud Production 001 — Build the upload → process → READY → play loop
**CANON_CHANGE：** `NO`
**执行状态：** 仅入口文件；未修改、删除、移动任何业务代码或目录。

---

## Responsibilities

Cloud Production is responsible for:

1. **Store audio assets** — upload from creator → OSS
2. **Run processing jobs** — analyze → stem → judge → intervene → render
3. **Generate READY versions** — verified tracks ready for playback
4. **Deliver playable assets** — stable URLs → Music BFF → Player

The complete loop:

```
Upload (Creator/Admin)
      ↓
OSS (audio asset storage)
      ↓
Worker (intake → analyze → stem → judge → intervene → render)
      ↓
Verify (human listening gate or automated quality check)
      ↓
READY Version (playable asset)
      ↓
PolarDB (track metadata: URL, version, status, timestamp)
      ↓
Music BFF (catalogue / track / playback URL endpoint)
      ↓
Moodify Player (Web / Android)
      ↓
User presses Play
```

---

## Not Responsible For

Cloud Production is **NOT** responsible for:

| Not our job | Reason |
|---|---|
| Creator platform | No creator product evidence yet |
| Enterprise API | No enterprise users yet |
| Billing / Credit ledger | No revenue model yet |
| Social graph (follows, shares) | No social evidence yet |
| Public evidence dashboard | Evidence is internal |
| Auto-mastering presets exposed to users | Complexity belongs inside |
| Real-time streaming (HLS/DASH) | v1.0 serves static files |

---

## Current Infrastructure

| Component | Provider | Status | Reference |
|---|---|---|---|
| LA VPS (ECS) | 亿速云 | Running: nginx, cloudflared, moodify-api, moodify-music, music-bff, worker, audiolla | `CURRENT_ARCHITECTURE.md §1` |
| Hangzhou VPS (ECS) | 阿里云 | Running: moodify-api (public), data-worker, 4 timers, /var/lib/moodify (6.5GB, 10-song pilot SUCCEEDED) | `CURRENT_ARCHITECTURE.md §1` |
| OSS | 阿里云 | NOT_PROVISIONED | Target for Cloud Production 001 |
| PolarDB | 阿里云 | BLOCKED (schema empty, replication not verified) | Needs activation in Cloud Production 001 |
| Worker / Queue | Local SQLite | Near-empty | Target for production queue in Cloud Production 001 |
| Cloud AI Inference | — | No GPU, no model serving | Controlled introduction when evidence exists |

---

## Next Step: Cloud Production 001

Build the upload → process → READY → play loop:

```
Aliyun ECS (Hangzhou)
      |
      v
OSS (audio asset storage)          ← NOT_PROVISIONED
      |
      v
Worker (processing pipeline)       ← Upgrade SQLite queue → production queue
      |
      v
PolarDB (track metadata)           ← BLOCKED → activate schema
      |
      v
Music BFF (catalogue/track endpoint) ← existing, use as-is
      |
      v
Moodify Player (Web)               ← existing, use as-is
      |
      v
User presses Play
```

**Cloud Production 001 的目标：**

让 Moodify 从"软件项目"进入"产品系统"。

验收条件：

- [ ] 一首歌上传 → 云端处理 → 生成 READY → Web 可播放
- [ ] 3-10 首 READY 曲目在 catalogue
- [ ] Playback URL 稳定，弱网可恢复
- [ ] PolarDB 写入 track metadata
- [ ] OSS 存储音频资产

---

## Entry Points

| File | Role |
|---|---|
| `docs/STATUS.md` | v1.0 working state |
| `docs/development/README.md` | What to develop |
| `docs/canon/CURRENT_ARCHITECTURE.md` | Current cloud reality |
| `docs/canon/INTERNAL_SYSTEMS.md` | Ear + Cloud Production topology |
| `docs/reduction/MAINLINE_DECLARATION.md` | Full boundary map |

---

## Definition of Done (Cloud Production 001)

A Cloud Production change is complete when:

1. What case does this serve? — A creator/admin uploads a track and it becomes playable
2. What is measured? — Track status transitions: UPLOADING → PROCESSING → READY
3. What evidence is produced? — PolarDB record with track URL, version, timestamp
4. How is the result verified? — Human listens to READY version; plays from Web Player
5. What happens on failure? — PROCESSING fails → error status → retry or abort
6. Is the result reusable? — Same pipeline runs for next track