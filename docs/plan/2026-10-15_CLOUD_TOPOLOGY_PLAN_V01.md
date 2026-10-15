# Moodify 云拓扑与连接方案 V01

日期：2026-10-15
状态：DRAFT — 待授权
CANON_CHANGE: NO（纯基础设施，不改产品定义）

---

## 一、实测资源清单

### 1.1 三节点

| 节点 | 位置 / 规格 | 当前角色 | 状态 |
|---|---|---|---|
| **香港** `103.144.246.242` | 亿速云 4核 / 7.7G，hostname `yisu-6a7bcb73aac20` | **全部线上服务中枢** | 运行中 |
| **宁夏 GPU** `i-0e829060d861d4c5f` | `g5.xlarge`，A10G 24GB，`cn-northwest-1a`，公网 `52.83.185.175` | 无任务 | **关机** |
| **宁夏 CPU** `i-02d2c7bcf190ae84c` | `m6i.2xlarge`，300GB EBS，`cn-northwest-1c`，公网 `52.82.24.90` | 无任务 | **关机** |

- AWS 账户 `382309211832`（business），区域 `cn-northwest-1`
- 两台宁夏机器**同在 VPC `vpc-04405868081ca464c`**（不同 AZ：1a / 1c）
- 两台均已挂载实例角色 `MoodifyExperimentWorkerRole`：可读 `moodify-dataset`、读写 `moodify-experiments`、**无 DeleteObject**
- 已部署 `/home/ubuntu/moodify-s3-integration`，venv 内已有 boto3

> 修正一条历史记忆：旧 GPU 实例 `161.189.223.96` 已作废（`S3_DIRECT_UPLOAD.md` 明确标注「不用再启动」）。

### 1.2 三条硬约束（2026-10-15 实测）

1. **香港出口 ~18 Mbps**（实测 2.28 MB/s）。一首 40MB WAV 理论 18 秒，叠加跨境链路更差。
2. **香港 ↔ 宁夏 TCP 完全不通**。从香港与本机双向测 `52.83.185.175:22` 均 timeout，AWS 中国区安全组未放行。
3. **香港磁盘 83% 满**（98G，剩 17G；docker 可回收约 12G，治标不治本）。

### 1.3 已具备、不要重复建设的能力

| 能力 | 现状 | 出处 |
|---|---|---|
| 本机 → S3 直传 | **已打通**，实测 13GB / 3 分钟 | `S3_DIRECT_UPLOAD.md` |
| 权限边界 | 仅 `moodify-dataset/raw/non-ai/*`，**子前缀一路通** | 同上 |
| 本地转码 | **ffmpeg 9.0.2** 在 `moodify-desktop/build/runtime/ffmpeg/`，支持 aac / flac / alac | 本次实测 |

> 两条必须记住的既有坑：`aws s3 ls`（不带前缀）**必然 403**，这是设计如此，不要用它判断权限；`DeleteObject` 未授权，禁止 `sync --delete`。

---

## 二、三个改变结论的发现

### 发现 1：「香港当中转」判断正确，但瓶颈不是性能，是带宽

4核/7.7G 跑控制面绰绰有余。真正卡死体验的是 18 Mbps 出口。**结论：香港只配处理 KB 级流量，音频一个字节都不要经过它。**

### 发现 2：三个域名全在 Cloudflare 后面，香港靠 Tunnel 主动出站

```
play.rongjingmusic.com  -> 172.67.131.155 / 104.21.4.34
rongjingmusic.com       -> 172.67.131.155 / 104.21.4.34
crestwavecoin.com       -> 172.67.151.236 / 104.21.12.82
```

均为 Cloudflare IP 段；`cloudflared tunnel list` 接入点为 `2xlax01 / 1xlax10 / 1xlax12`（LAX = 洛杉矶边缘节点）。

- ✅ 利好：香港**无需开放任何入站端口**，cloudflared 主动出站即可。
- ⚠️ 隐患：**Cloudflare 免费版在中国大陆没有稳定节点**。听众以国内为主时，音频**绝不能**走 CF —— 否则等于把 40MB 音频塞进一条不稳定且穿香港的管道。

（顺带解释记忆偏差：你记得「洛杉矶」没错，那是 CF 边缘节点；服务器物理位置是**香港旺角，亿速云**。）

### 发现 3：宁夏两台目前没有真实任务，开机即烧钱

- Studio 的分析跑在本地 Core（`E:/moodify/.venv-core`）
- 逐轨分离在 Core 侧**尚未实现**（`MIP-0002-stem-tuning-loop.md` 仍为 DRAFT）
- 转码 ffmpeg 本机就能做，不需要云

**现在开机没有任务可跑。** 成本量级（请以 AWS 中国区控制台当前定价为准）：`g5.xlarge` 24×7 全月运行约数千元/月，`m6i.2xlarge` 约千元/月量级。两台常开合计约万元/月量级。

---

## 三、目标架构：控制面 / 数据面 / 计算面分离

```
        Moodify Studio（本机 Windows）
             │
             ① ffmpeg 本地转码  WAV 40MB ──▶ AAC ~4MB   （省 90%）
             │
             ② HTTPS 直传 S3（国内直连，已验证 ~70MB/s）
             ▼
    ┌─────────────────────────────┐
    │  宁夏 S3  moodify-dataset   │  ← 数据面：音频 / 封面 / 歌词
    │  raw/non-ai/works/<id>/     │     国内直连，绕开香港 18 Mbps
    └─────────────────────────────┘
             ▲                    ▲
             │ ③ 注册元数据        │ ⑤ 直连下载（不经香港、不经 CF）
             │   （几 KB JSON）    │
    ┌────────┴────────┐      ┌────┴─────┐
    │ 香港 103.144... │      │ 手机 App │
    │ 控制面：        │      └──────────┘
    │  manifest.json  │
    │  预签名 URL     │
    │  CF Tunnel 暴露 │
    └────────────────┘

    宁夏 GPU（异步，仅 Phase 3 需要）
      S3 取 job ──▶ demucs / Core 分析 ──▶ S3 写回结果
      ▲ 两端不直接通信，一个端口都不用开（绕开硬约束 2）
```

**分工表**

| 层 | 位置 | 流量 | 理由 |
|---|---|---|---|
| 控制面（manifest / 鉴权 / 签名） | 香港 | KB 级 | 无需备案，200ms 延迟可接受 |
| 数据面（音频 / 封面 / 歌词） | 宁夏 S3 | MB 级 | 国内直连，绕开 18 Mbps 与 CF 不稳定 |
| 计算面（分析 / 分离） | 宁夏 GPU | 内部 | 走 S3 异步队列，不需要两端互通 |

**关键设计：音频读写完全绕开香港。** 香港只签发一个字符串，不搬运一个字节。

---

## 四、分阶段实施

### Phase 0 — 本机准备（不需要任何云资源开机）

| # | 动作 | 验证 |
|---|---|---|
| 0.1 | `E:\亚马逊云\s3-direct-upload.ps1 -Check` | 输出 `RESULT: READY` |
| 0.2 | 验证 ffmpeg 转码链路：`ffmpeg -i 源.wav -c:a aac -b:a 192k 出.m4a` | 产物可播放，体积 ≤ 源 15% |
| 0.3 | 备份香港 nginx 配置与 `manifest.json` | 备份文件存在且可 diff |

### Phase 1 — 数据面（S3 布局 + Studio 直传改造）· 仍不需要宁夏开机

**1.1 前缀选择（这里有一个能省掉一次 IAM 审批的捷径）**

现有 SSO 权限允许 `raw/non-ai/*` 下**任意子前缀**（已实测「子前缀一路通」）。因此：

```
s3://moodify-dataset/raw/non-ai/works/<work_id>/audio.m4a
s3://moodify-dataset/raw/non-ai/works/<work_id>/cover.jpg
s3://moodify-dataset/raw/non-ai/works/<work_id>/lyrics.lrc
```

→ **沿用现有权限即可写入，无需新增 IAM 策略、无需管理员审批。**

代价：`works/` 与数据集 `raw/non-ai/*.flac` 混在同一前缀下。若后续要严格隔离，再申请独立前缀（需审批）。

**1.2 Studio 发布链路改造（当前最脆弱的一环）**

现状（`src/main.js`）实测缺陷：

```
scp 音频 → ssh ffprobe 取时长 → ssh cat 整个 manifest → 本地改 → scp 回去 → ssh mv
→ ssh cp 到 public/ → ssh systemctl restart moodify-music.service
```

四个问题：
1. **每发一首歌重启整个生产服务**（`rongjingmusic.com` 有真实访问）
2. manifest 是「读—改—写整个文件」，**无并发保护**，两台 Studio 同时发布会互相覆盖
3. 同步阻塞，15 分钟超时
4. 依赖本机装 scp / ssh，且数据经香港 18 Mbps

改造后：

```
本地转码 → S3 直传（并发、可重试）→ HTTP POST 元数据到香港 → 完成
```

- **去掉重启**：manifest 移出 vinext 的 `dist/client/`，改由 nginx 以 `no-store` 直接服务静态文件。写完即生效，永久消灭重启。
- **并发保护**：原子写（临时文件 + `mv`）+ 版本号乐观锁，冲突时读—改—写重试，而非静默覆盖。
- **异步化**：上传与处理分离，发布不阻塞 UI。

### Phase 2 — 控制面（香港元数据 + 读取授权）· 需动服务端

manifest 结构（草案）：

```json
{
  "version": 3,
  "updated_at": "2026-10-15T...",
  "works": [
    { "id": "w_xxx", "title": "...", "creator": "...",
      "audio": "works/w_xxx/audio.m4a",
      "cover": "works/w_xxx/cover.jpg",
      "lyrics": "works/w_xxx/lyrics.lrc",
      "duration": 173.5, "published": true }
  ]
}
```

App 侧只存**相对路径**，基础 URL 与签名方式由控制面下发 —— 这样将来换存储（S3 → R2 → CDN）只改控制面一处，App 不用发版。

**读取授权：三个选项，需你拍板**

| 选项 | 做法 | 优点 | 缺点 | 需要的授权 |
|---|---|---|---|---|
| **A（推荐）** 公开读 + 不可猜路径 | 关 Block Public Access + bucket policy `Allow GetObject`，路径含随机 `work_id` | 零运维、无凭据分发、国内直连最快 | 链接泄露即可下载；有盗刷流量风险（可加 `aws:Referer` 条件缓解） | 管理员改桶策略 |
| **B** 预签名 URL | 香港持 IAM 用户长期 key，只做 HMAC 签名（纯本地计算，不需访问 AWS 网络），签发短期 URL | 可控、可审计、可吊销 | 需创建 IAM 用户并保管 key；URL 有有效期 | 创建 IAM 用户 |
| **C** 宁夏 CPU 跑签名服务 | m6i 常开提供签名 | 数据与控制同区 | 需常开机 + 开端口，**中国区 80/443 有 ICP 备案要求**，风险最高 | 开机 + 备案评估 |

### Phase 3 — 计算面（GPU 异步队列）· **这时才需要开机**

前提：Core 侧已具备可远程执行的任务（当前分离能力仍未实现，见发现 3）。

机制（绕开硬约束 2，两端**不直接通信**）：

```
Studio 写 s3://moodify-experiments/jobs/pending/<job_id>.json
   ↓
GPU 节点轮询 pending/ → 取任务 → demucs / Core 分析
   ↓
写 s3://moodify-experiments/jobs/done/<job_id>.json
   ↓
Studio 轮询结果
```

- 一个端口都不用开，彻底绕开「香港↔宁夏 TCP 不通」
- 两台同 VPC，建议加 **S3 Gateway VPC Endpoint**（省 NAT 流量费）；⚠️ 创建/改动 endpoint 会替换路由表、可能中断现有 S3 会话，须先检查路由表 / DNS / 安全组 / NACL，且**不要**在未验证管理员恢复通道前加 `aws:SourceVpce` 硬拒绝桶策略

**开机纪律**：任务跑完立即停机。GPU 不是常驻服务，是批处理资源。

---

## 五、开机决策矩阵

| 阶段 | 需要香港 | 需要宁夏开机 | 说明 |
|---|---|---|---|
| Phase 0 | 只读探测 | ❌ 否 | 本机即可完成 |
| Phase 1 | 否（仅改本机代码） | ❌ 否 | S3 直传已打通，不需要 EC2 |
| Phase 2 | ✅ 需改 nginx | ❌ 否 | 控制面在香港 |
| Phase 3 | 否 | ✅ **是** | 有真实批处理任务时才开 |

> ⚠️ **与既有文档的冲突**：`S3_DIRECT_UPLOAD.md` 明确写「不要为了上传去启动 GPU / CPU 实例 —— 与上传无关，纯浪费钱」。本方案的 Phase 0–2 遵循该原则；只有 Phase 3 才开机。

---

## 六、需要你批准的授权项

1. **【安全·立即】改 root 密码 + 禁密码登录**：你把香港机器的 root 密码明文发在了对话里。且该机器是当前所有线上服务的单点。建议改用 SSH key。
2. **【Phase 2】允许修改香港服务端**（nginx + 元数据 API）。线上跑着 `rongjingmusic.com`、`crestwavecoin.com` 等真实站点。我会先备份配置再改，每步留回滚。
   - 注意：这与项目既有铁律「禁止部署到云端生产」冲突，**必须你显式放行**。
3. **【Phase 2】读取授权选 A / B / C**（见上表）。
4. **【Phase 3】GPU 开机预算与停机纪律**。

---

## 七、回滚

| 阶段 | 回滚方式 |
|---|---|
| Phase 1 | Studio 发布改为可开关：保留旧 scp 路径作为 fallback，新增 `PUBLISH_BACKEND=s3\|scp` 环境变量切换 |
| Phase 2 | nginx 配置先 `cp` 备份，改完 `nginx -t` 校验再 reload；失败即还原备份 |
| Phase 3 | 停机即回滚；S3 任务文件有 `pending/done` 状态，可人工重投 |

---

## 八、未决问题

1. **ICP 备案状态**：若 `rongjingmusic.com` 已备案，宁夏 CPU 可直接开 80/443 提供国内加速，选项 C 的风险大幅下降。需确认。
2. **作品是否对外公开**：当前定位是「内部生产 + 私有客户审片」。若如此，选项 A 的盗刷风险实际很低。
3. **`raw/non-ai/` 混放数据集与作品**是否可接受，还是申请独立前缀。
