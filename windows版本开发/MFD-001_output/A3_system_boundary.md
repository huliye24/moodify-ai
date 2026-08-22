# MFD-001 客户端与服务边界盘点

**生成时间:** 2026-08-20
**任务:** MFD-001 阶段 A3 — 系统边界图

---

## 真实系统图 (基于运行时证据)

```text
┌─────────────────────────────────────────────────────────────┐
│                    User-Facing Clients                       │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────┐   │
│  │  music-android  │  │    music-web    │  │  Desktop   │   │
│  │  (Jetpack+Exo)  │  │   (PWA/SPA)     │  │  (待建立)  │   │
│  └────────┬────────┘  └────────┬────────┘  └─────┬─────┘   │
│           │                    │                 │           │
└───────────┼────────────────────┼─────────────────┼───────────┘
            │                    │                 │
            ▼                    ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  Playback API / BFF                          │
│                                                             │
│  ┌──────────────────────────────────────────────────┐       │
│  │         moodify-music-bff (:8100)                │       │
│  │   /api/v1/music/bootstrap                        │       │
│  │   /api/v1/music/catalogue                       │       │
│  │   /api/v1/music/tracks/{id}                      │       │
│  │   /api/v1/auth/*                                 │       │
│  └──────────────────────┬───────────────────────────┘       │
│                         │                                  │
│  ┌──────────────────────▼───────────────────────────┐       │
│  │      moodify-music-package (Python FastAPI)      │       │
│  │   routes_auth / routes_library / tracks         │       │
│  │   routes_playlists / search / social / users    │       │
│  └──────────────────────┬───────────────────────────┘       │
└─────────────────────────┼───────────────────────────────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
┌─────────────────┐ ┌──────────┐ ┌──────────────────┐
│  Cloud Runtime  │ │ Storage  │ │ Internal Ear     │
│                 │ │          │ │                  │
│  LA VPS         │ │ PolarDB  │ │ Listen            │
│  - nginx:80     │ │ (空转)   │ │ Represent        │
│  - api:8000     │ │          │ │ Judge             │
│  - bff:8100     │ │ SQLite   │ │ Intervene         │
│  - audiolla     │ │ (本地)   │ │ Verify            │
│                 │ │          │ │ Learn             │
│  杭州 VPS       │ │          │ │                   │
│  - api:8000     │ │          │ │ 状态: 仅仓库代码  │
│  - data-worker  │ │          │ │ (无生产流量)      │
└─────────────────┘ └──────────┘ └──────────────────┘
```

## 层级状态表

| 层 | 状态 | 证据路径 |
|---|---|---|
| **User-facing Client - Android** | PRESENT | `apps/music-android/`, deliverables/releases/ |
| **User-facing Client - Web** | PRESENT | `apps/music-web/`, rongjinwenchuan.xyz |
| **User-facing Client - Desktop** | ABSENT | 本任务将建立 |
| **Playback API / BFF** | PRESENT | `moodify-music-package/src/moodify_music/bff/main.py` |
| **Cloud Runtime** | PARTIAL | LA VPS 运行中，杭州 worker 历史 |
| **Storage / DB** | PARTIAL SQLite / PolarDB 空转 | W01-P00 报告 |
| **Internal Ear / Processing** | CODE ONLY | `moodify-core-package/`，无生产流量 |
| **Research / Experimental** | PRESENT | `experiments/`, `science/`, `phys-lab/` |
| **Legacy** | PRESENT | `apps/android` (旧版), 历史文档 |

## Desktop 需要对接的接口

### 已验证可用 (Android 正在使用)

| Endpoint | 方法 | 用途 | 来源 |
|---|---|---|---|
| `/api/v1/music/bootstrap` | GET | 应用启动配置 | BffClient.kt |
| `/api/v1/music/catalogue` | GET | 可见曲目列表 | BffClient.kt |
| `/api/v1/music/tracks/{id}` | GET | 单曲详情(含播放资源) | BffClient.kt |

### 存在但需确认

| Endpoint | 方法 | 用途 | 状态 |
|---|---|---|---|
| `/api/v1/auth/*` | POST/GET | 认证 | routes_auth.py |
| `/api/v1/library/*` | GET | 用户曲库 | routes_library.py |
| `/api/v1/playlists/*` | CRUD | 播放列表 | routes_playlists.py |

### Media Delivery

| 组件 | 状态 | 说明 |
|---|---|---|
| BFF media endpoint | PRESENT | `bff/media.py` |
| Signed URL | UNKNOWN | 需在 MFD-003 确认 |
| Range request | UNKNOWN | 需验证 |

---

*本图基于真实文件和运行时证据，不含理想化推测。*
