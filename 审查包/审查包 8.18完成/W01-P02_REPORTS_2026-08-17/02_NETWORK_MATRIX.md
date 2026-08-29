# 02 — Network Matrix

**规则（任务书 §2.7）:** 同地域私网 > 受控公网 HTTPS > 外部 API 官方 HTTPS；数据库不得直接暴露为不受控公网服务。P00 现实记录不改，目标边界单独标注。

| # | Source | Destination | Protocol | Port | Direction | Purpose | Public/Private | Authentication | Data class | Status | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NW-01 | Internet 用户 | Cloudflare → LA nginx | HTTPS | 443→80 | → | 官网/音乐平台访问 | 公网 | TLS 终止（隧道） | 公开静态内容 | current | E13/E15 |
| NW-02 | Android App | LA music-bff | HTTPS | 443→80→8100 | → | 播放 URL / metadata | 公网 | 无（现状）；目标：API 签发 | 公开元数据 | current | E18 §23 |
| NW-03 | Android App | LA music-media 静态音频 | HTTPS | 443→80 | → | 播放音频（resolveUrl） | 公网 | 无（现状）；目标：限时签名 URL | 音频对象 | current | E18 §24 |
| NW-04 | LA BFF | 杭州 moodify-api | HTTPS | 公网 8000 | → | 数据/元数据查询 | 公网 | service-key（现状） | 业务数据 | current | E16/E18 |
| NW-05 | LA Ear API :8000 | 内部调用方 | HTTP | 127.0.0.1:8000 | → | Ear API（仅本机） | 私网（loopback） | 无（本机限制） | 内部 | current | E13 |
| NW-06 | LA worker | audiolla 容器 | HTTP | 127.0.0.1:18080→8000 | → | 分离请求（无自动调用证据） | 私网（loopback） | 无（本机限制） | 音频 | current | E13 |
| NW-07 | audiolla 容器 | LALAL.AI 云端 API | HTTPS | 443 | ↔ | stem 分离推理 | 公网 | 官方 API 凭据（容器配置） | 音频 | current | E13/E18 §27 |
| NW-08 | LA worker | LA node.sqlite3 | file | — | ↔ | 队列读写 | 本地 | 文件权限 | 任务状态 | current | E13 |
| NW-09 | 杭州 worker | /var/lib/moodify | file | — | ↔ | 状态+批处理数据 | 本地 | 文件权限 | 任务/产物 | current | E14 |
| NW-10 | 杭州 moodify-api | PolarDB 172.27.118.104 | MySQL | 私网 3306 | ↔ | 元数据（目标） | 私网（杭州 VPC 对等） | DB 凭据 | 业务元数据 | **target**（现状 BLOCKED 核验） | E17/E18 |
| NW-11 | LA BFF/API | PolarDB | — | — | — | 跨地域直连 | — | — | — | **forbidden target**（经杭州 API 间接访问） | 本包决策 |
| NW-12 | 公网 | PolarDB 3306/5432 | — | — | — | 数据库公网暴露 | — | — | — | **forbidden**（现状已关闭） | E16（3306/5432 closed） |
| NW-13 | LA nginx | moodify-music:3100 / bff:8100 | HTTP | 127.0.0.1 | → | 内部代理 | 私网（loopback） | 无 | 公开内容 | current | E13 |
| NW-14 | Cloudflare | LA cloudflared | HTTPS | 20241 | ↔ | 隧道长连接 | 公网（出站） | 隧道凭据 | 流量 | current | E13 |
| NW-15 | 运维 SSH | LA :22 / 杭州 :22 | SSH | 22 | ↔ | 运维 | 公网 | 密钥（LA）/ 密码（杭州，现状风险） | 运维 | current | E13/E14 |
| NW-16 | 杭州 moodify-api | 公网 | HTTP | 0.0.0.0:8000 | → | 内部数据 API（现状公网可达） | 公网 | service-key | 业务数据 | current；**target: 仅 LA 可访问（安全组/白名单）** | E16 |
| NW-17 | LA worker | 杭州 API | HTTPS | 公网 8000 | → | 数据回传（目标） | 公网 | service-key | 业务数据 | target（现状无证据） | E18 |
| NW-18 | 杭州 timers | moodify-data-worker | systemd | — | → | 定时触发（inbox/resource/daily/backup） | 本地 | systemd | 任务 | current | E14 |

## Public / Private Boundary（总结）

- **现状公网面：** Cloudflare 隧道（HTTPS）、LA:22、杭州:22/8000（service-key）。
- **现状私网面：** LA 全部业务端口 loopback（8000/3100/8100/18080）；杭州 PolarDB 私网（VPC 对等）；LA/杭州本地 SQLite。
- **目标边界（本包不实施，P03+ 执行）：**
  1. 杭州 :8000 从「公网可达」收紧为「仅 LA 白名单」（NW-16 target）。
  2. LA→PolarDB 不建跨地域直连（NW-11 forbidden）；经杭州 API 间接访问。
  3. 数据库端口保持关闭（NW-12）。
  4. 播放音频从「无鉴权静态 URL」演进为「BFF 签发限时 URL」（NW-03 target；P06 范围）。

## 网络设计原则落实

1. 同地域私网：杭州 ↔ PolarDB（NW-10，目标）。
2. 受控公网 HTTPS：隧道 + service-key（NW-01/02/04）。
3. 外部 API 官方 HTTPS：audiolla → LALAL.AI（NW-07）。
4. DB 不公网：现状已关闭（NW-12），目标保持。
