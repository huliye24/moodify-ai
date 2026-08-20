# CURRENT ARCHITECTURE — Moodify（现状，非理想图）

**Canon v1.0（W01-P01, 2026-08-17）**
**规则 R6/R10：** 本文件只记录已由运行时证据支持的现状；理想架构不得写入。完整事实见 W01-P00 报告（审查包）。

## 1. 云端现状（P00 扫描 2026-08-17，与同日黑箱调查一致）

```text
LA 103.144.246.242（亿速云，核心节点，4C/8G/98G）
  ├── nginx :80（三域名）
  ├── cloudflared 隧道（rongjingmusic.com 等）
  ├── moodify-api :8000（Ear FastAPI，127.0.0.1）
  ├── moodify-music :3100（node vinext 平台）
  ├── moodify-music-bff :8100
  ├── moodify-worker（SQLite 队列，近空）
  └── docker: moodify-audiolla（:18080→8000，lalal.ai 代理）

杭州 120.55.191.146（阿里云，2C/1.6G/40G）
  ├── moodify-api :8000（公网，service-key 鉴权）
  ├── moodify-data-worker（moodify-node + 4 timers）
  └── /var/lib/moodify（SQLite + 历史批处理 6.5GB）

PolarDB（3 实例，直接核验 BLOCKED，内容引用同日黑箱调查）
  ├── MySQL 8.0.13 172.27.118.106（空壳）
  ├── MySQL 8.0.18 172.27.118.104（moodify_dev 19 表 ≈0 数据）
  └── PG 16.14 101.133.107.206（在线未用）

OSS/S3/R2：NOT_PROVISIONED
云端 AI 推理：无（无 GPU、无模型 serving）
```

## 2. 真实主链

- **静态音乐托管链（运行中）**：网站 → nginx → music-bff / music-platform → music-media 音频 → 浏览器/App 播放。
- **数据工厂批处理链（历史运行）**：杭州 worker → /var/lib/moodify（10 曲 pilot 全 SUCCEEDED）。
- **完整 Ear 链路（仅仓库代码）**：Listen→Judge→Intervene→Verify 云端无生产流量。

## 3. 仓库侧主链（canonical mainline）

- `moodify-core-package`：`v01_pipeline` 为 supported mainline（REPOSITORY_STATUS），`data_factory` 管线 + 算法评审器为数据侧主链。
- 未合并分支承载重建系列（objective/guard/diagnostic/factory）与 Music 产品面（music-web / music-android / music-package）。

## 4. 角色分配（现状 vs 目标）

| 层 | 现状（P00 事实） | 目标角色 |
|---|---|---|
| 对外产品面 | Moodify Music Android 3.1（APK）+ music-web + vinext 平台 | Music/Player（P01 Canon） |
| 内部听觉 | 仓库代码完整；云端 API 壳 | Ear 内部系统 |
| 云端生产 | 静态托管 + 批处理 | Intake→…→Delivery（P02 拓扑） |
| 数据权威 | SQLite 实跑；PolarDB schema 空转 | 待 P03/P04 |
| 存储 | 本地磁盘（无对象存储） | 待 P03 |

> 本文件是「现状」；目标拓扑由 W01-P02 承接，不在此虚构。
