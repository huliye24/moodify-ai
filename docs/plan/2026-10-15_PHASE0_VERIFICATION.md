# Phase 0 验证报告 — 本机能力核验（不依赖任何云服务器）

> 执行日期：**2026-10-15**
> 性质：**只读 + 本地**，不含任何生产改动。云服务器（宁夏 CPU）仅在配置阶段被写入 worker 代码，未处理任何业务数据。
> 结论：**三步全部通过**，Phase 1 可以开工。唯一的外部阻塞是 IAM 策略需管理员在控制台 attach。

---

## 一、核验目标

Phase 0 的目的是在动任何云资源之前，先用本机能力证明方案的两个核心假设成立：

1. 本机到 S3 的直传可用（音频不需要经过香港那台 18 Mbps 的机器）
2. WAV 能在本地压到足够小（手机下载体感可改善）

---

## 二、Step 1 — S3 直传自检 ✅ READY

```powershell
Set-Location E:\亚马逊云
.\s3-direct-upload.ps1 -Check
```

```
== environment check (read-only) ==
  shell      : Windows PowerShell 5.1.19041.6456
  python.exe : C:\Program Files\Python311\python.exe (boto3 OK)
  session    : arn:aws-cn:sts::382309211832:assumed-role/AWSReservedSSO_MoodifyDatasetIngestion_383702643b65cf10/Raphael33
  bucket     : moodify-dataset is in cn-northwest-1
  prefix     : raw/non-ai/ is listed and writable (probe ok)

RESULT: READY
```

**SSO 会话仍有效**，身份是 `moodify-ingestion` 权限集。
授权边界沿用既有实测结论：`s3:PutObject` 仅限 `moodify-dataset/raw/non-ai/*`，
`ListAllMyBuckets` / `DeleteObject` / `sts:AssumeRole` / `ec2:*` 全部 DENY。

> 这意味着作品可以直接写 `s3://moodify-dataset/raw/non-ai/works/<work_id>/…`，
> **不需要新增 IAM 策略、不需要管理员审批**。代价是与那 510 个 FLAC 数据集共用同一前缀。

---

## 三、Step 2 — 本地转码验证 ✅ 省 82–88%

### 3.1 ffmpeg 位置（一个易踩的坑）

`ffmpeg` **不在 PATH**，但存在于桌面壳的打包 runtime 里：

```
E:/moodify/moodify-desktop/build/runtime/ffmpeg/ffmpeg.exe   (9.0.2)
```

编码器实测齐备：`aac` · `flac` · `alac`。

### 3.2 实测结果（作品库真实文件）

| 作品 | 源 WAV | AAC 192k | AAC 256k | FLAC |
|---|---|---|---|---|
| 她的日程表里没有我（173.5s） | 31.8 MB | **4.1 MB（13.0%）** | **5.5 MB（17.3%）** | 18.6 MB（58.4%） |
| 紫色自语 | 78.5 MB | — | **9.7 MB（12.4%）** | — |

**时长偏差全部 0.000 s**，采样率 48000 Hz、立体声均保持不变（不做偷偷降采样）。

```
源:   pcm_s16le  48000Hz  2ch  1536 kbps  31.8 MB  173.479979s
AAC:  aac        48000Hz  2ch   266 kbps   5.5 MB  173.479979s
```

### 3.3 选型建议

- **发布默认用 `aac256`**（≈ 源 17%，5.5 MB/首）。流媒体标准档，iOS/Android/浏览器全支持，
  `-movflags +faststart` 已加，支持边下边播。
- `aac192` 省得更多但余量小，适合弱网场景。
- `flac` 只省 41.6%，且移动端体积仍大；**仅建议用于归档或审片**。

验证脚本：`E:/亚马逊云/tools/transcode.py`
（含回验逻辑：时长偏差 > 0.5s 判失败，转码后比源大也判失败——不制造假优化）

---

## 四、Step 3 — 香港生产机只读备份 ✅ 已归档

备份脚本：`E:/亚马逊云/香港节点/tools/backup.py`（**只读**：远端打包、下载，不改任何生产状态）

产物：`E:/亚马逊云/香港节点/backup/20261015-162127/`

| 文件 | 内容 |
|---|---|
| `nginx.tar.gz` | `/etc/nginx` 全量（55 项，含 origin-certs） |
| `services.txt` | 25 个 active service 列表 |
| `cloudflared.txt` | tunnel 列表 + config.yml |
| `disk.txt` | 磁盘、`/var/www`、`docker ps` |
| `catalogue.json` | 作品 manifest |
| `manifest.json` | 备份清单 |

### 4.1 备份暴露的关键事实（影响后续方案）

**这台机器承载的业务远超 Moodify**：

```
Moodify:  moodify-music · moodify-music-bff · moodify-api · moodify-worker
其它:     crestwave-web3 · duoweilai · duoweilai-webhook · cloudflared-moodify · nginx
Docker:   duoweilai-frontend · mood-relay (mood-node:alpha-001) · moodify-audiolla
站点:     rongjingmusic.com · crestwavecoin.com · rongjingwenchuan.com · rongjingwenchaun.cc
```

磁盘 **83%**（77G/98G，剩 17G）。**它是单点，动它必须有备份 + 显式授权。**

### 4.2 ⚠️ 发现：音频分发已有过一轮优化

```nginx
location ^~ /audio/ {
    alias /opt/moodify/music-media/audio-opt/;
    types {
        audio/flac  wav;      # ← *.wav 的实际内容是原生 FLAC 流
        audio/mp4   m4a;
        ...
    }
    add_header Cache-Control "public, max-age=3600" always;
    add_header Accept-Ranges bytes always;
}
```

**已经有人把 WAV 转成了 FLAC**，文件名保留 `.wav`，靠 nginx `types` 强行声明正确 Content-Type
（回滚方式写在该 location 上方的注释里）。

这对方案是**利好而非冲突**：

- 方向一致（都在压缩音频），我的方案是同一思路的升级版
- 现有 FLAC 只省 41.6%，AAC 256k 能省 82.7%，**再压一半**
- `audio/mp4 m4a` 已在 types 里，切 AAC **不需要改 nginx 的 MIME 表**
- 但**文件仍在香港这台 18 Mbps 的机器上** —— 分发瓶颈一个字节都没解决

### 4.3 发布链缺陷已确认

```
/opt/moodify/music/releases/20261015T-mobile-responsive-02/
/opt/moodify/music/releases/20261015T-desktop-switching-03/
```

存在多版本 release 目录，`internal-catalogue.json` 在 `public/` 与 `dist/client/` 各一份。
Studio 发布仍是 `scp → ffprobe → 改 manifest → scp 回 → systemctl restart moodify-music.service`。

---

## 五、宁夏 CPU 节点：不依赖 S3 的部分已配完 ✅

| 项 | 状态 |
|---|---|
| worker 代码（s3queue / worker / node_info） | ✅ 已部署 |
| systemd unit | ✅ 已 install，**未 enable**（刻意：IAM 未就绪时 enable 会 crash loop） |
| logrotate | ✅ 已装，语法校验通过 |
| shell alias（`mstatus` / `mcheck` / `monce` / `mstart`…） | ✅ 已装，幂等追加 |
| awscli | ✅ 1.46.1（venv 内） |
| 一键同步脚本 `tools/sync.py` | ✅ 可用（含 `--check` 只读模式） |

`node_info.py` 当前如实报：

```
NOT READY：S3 被拒（{'list_jobs': 'DENY (AccessDenied)'}）。
  原因：instance role 未挂 IAM 策略，需管理员在 AWS 控制台 attach。
  节点配置本身：已全部就位；systemd unit 已装、enable=disabled、active=inactive（未 enable 是刻意设计）。
```

---

## 六、唯一阻塞：IAM 策略（需人手点一次）

`MoodifyExperimentWorkerRole` 没有挂任何 S3 策略。
`MOODIFY_CLOUD_S3_INTEGRATION_001/iam-policy.proposed.json` 文件名带 `.proposed` —— **拟定稿，从未应用**。
本机 SSO 被拒 `iam:*`，无法代办。

步骤见 `E:/亚马逊云/宁夏CPU节点/iam-worker-policy.json`（最小权限，不含 dataset 写入、不含 DeleteObject）。

生效后验证：

```bash
ssh moodify-cpu 'source ~/.moodify_aliases && mcheck'   # 期望 READY
```

---

## 七、Phase 0 结论

| 假设 | 结论 |
|---|---|
| 音频可以绕开香港直传 S3 | ✅ 成立，SSO 权限现成可用 |
| 本地转码能显著减小体积 | ✅ 成立，AAC 256k 省 82.7%，时长零偏差 |
| 宁夏节点可作为计算面 | ⏸ 配置就绪，等 IAM |
| 香港可安全改动 | ⚠️ 已有备份 + 已知单点风险，**仍需用户显式放行** |

**下一步（Phase 1）**：S3 布局 + Studio 发布链路改造（去重启、加并发保护、异步化）。
这部分只动 Studio 本地代码，**不需要服务器权限**。
