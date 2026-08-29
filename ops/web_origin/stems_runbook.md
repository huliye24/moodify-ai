# Moodify 云端音频分离 Runbook(LALAL-STEMS-001)

云端功能:lalal.ai 人声/乐器分离,通过 Ear API 暴露。部署于 LA 103.144.246.242。

## 端点(公网:`https://rongjingmusic.com/api/v1/stems/*`)

| 端点 | 说明 |
|---|---|
| `POST /api/v1/stems/jobs` | 上传音频(multipart `audio` + `stems` 逗号分隔,可选 `extraction_level`/`splitter`/`dereverb_enabled`/`multivocal`)→ 202 + job |
| `GET /api/v1/stems/jobs/{id}` | 轮询状态;非终态时实时向 lalal 查询(节流 5s);终态含 `results`(签名 URL) |
| `GET /api/v1/stems/jobs/{id}/download/{stem}` | 307 重定向到 lalal 产物;`{stem}_back` 为伴奏轨 |
| `GET /api/v1/stems/jobs` | 任务列表(status/limit 过滤) |
| `GET /api/v1/stems/usage` | 计费估算汇总(实际扣费以 lalal 账号后台为准) |

Stem 类型(10 轨):vocals, drum, piano, bass, electric_guitar, acoustic_guitar,
synthesizer, strings, wind, instrumental。每轨一个独立 lalal 任务。

## 完整分离流程(实测通过)

```bash
# 1. 提交(25s 音频预估扣 1 分钟)
curl -s -X POST https://rongjingmusic.com/api/v1/stems/jobs \
  -F 'audio=@song.wav' -F 'stems=vocals,drum'
# → {"job": {"job_id": "stem_xxx", "status": "PROCESSING", ...}}

# 2. 轮询(约 30-60s 完成)
curl -s https://rongjingmusic.com/api/v1/stems/jobs/stem_xxx
# → status SUCCEEDED, results.vocals = 签名 URL(24h 有效)

# 3. 下载(跟随 307)
curl -s -L -o vocals.wav https://rongjingmusic.com/api/v1/stems/jobs/stem_xxx/download/vocals
curl -s -L -o instrumental.wav https://rongjingmusic.com/api/v1/stems/jobs/stem_xxx/download/vocals_back
```

## 计费对账

- 扣费 = `ceil(文件时长秒/60) × stem 数`(Pro 分钟);`/usage` 为本地估算,对账以
  lalal.ai 账号后台扣减为准。
- 多 stem 提交 = 多付费任务,提交前确认调用方知悉。
- 下载 URL 24h 过期,过期后 `/download/` 返回 410,需重新提交任务。

## 密钥管理(重要)

- 环境变量 `LALAL_LICENSE_KEY` 仅存在于服务器 `/etc/moodify/node.env`,**不进仓库**。
- 真实密钥备份在 `/etc/moodify/lalal.key`(0600)。
- **`deploy_moodify_service.sh` 每次部署会用 node.env.example 覆盖 node.env**,密钥丢失。
  部署后必须重新执行:

```bash
sudo sed -i 's|^LALAL_LICENSE_KEY=.*|LALAL_LICENSE_KEY='"$(cat /etc/moodify/lalal.key)"'|' /etc/moodify/node.env
sudo systemctl restart moodify-api
```

(占位行已存在于 node.env.example,直接 sed 替换即可。)

## 已知约束

- 上传 ≤ 50MB(nginx 52m location `=/api/v1/stems/jobs`);后缀 wav/mp3/flac/m4a/ogg/aac。
- 无自动重试:`/split/` 提交即计费,任务状态以 lalal 后台 task_id 为准
  (任务记录在 `/var/lib/moodify/state/stems.sqlite3`)。
- 本地源文件提交成功后即删除,仅保留计费记录。
