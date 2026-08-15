# Moodify Music 2.0 云端运行手册

日期：2026-08-15
范围：云端基础设施；不包含新增或修改歌曲内容。

## 权威边界

- PolarDB 是用户、创作者、曲目、版本、发布状态和歌单的唯一数据权威。
- 杭州 Music Data API 是唯一可以访问 PolarDB 的应用服务。
- 公网 Music BFF 不连接数据库，只通过服务凭据访问杭州 API。
- 音频对象以 `audio_asset_key` 引用，数据库不存放音频正文。
- 客户端只能访问公网 BFF 和 `/audio/{asset_key}`，不得持有数据库或内部服务凭据。

## 每日只读检查

```bash
bash ops/web_origin/probe_resources.sh
```

通过条件：官网、BFF、catalogue、音频 Range、杭州 API liveness 和 PolarDB readiness 全部返回预期状态。

## 备份

在批准的秘密注入环境中设置 `MOODIFY_DB_HOST`、`MOODIFY_DB_USER`、`MOODIFY_DB_PASSWORD`、`MOODIFY_DB_NAME`，然后执行：

```bash
bash ops/web_origin/backup_snapshot.sh
```

成功条件：

- `music-db.sql` 存在且非空；
- `media-manifest.sha256` 覆盖媒体根目录下全部音频；
- `backup.sha256` 可通过 `sha256sum -c`；
- 任一数据库导出错误必须使脚本失败，不得生成伪成功备份。

## 媒体审计

默认只读，不会删除文件：

```bash
python3 moodify-music-package/scripts/media_audit.py
```

脚本递归扫描内容寻址目录，忽略 `.incoming` 临时上传目录。只有显式提供 `--apply` 才允许逐文件删除，并且每一项都必须留下审计记录。

## 新歌发布门（以后启用）

每一首新作品依次经过：音频签名检查 → SHA-256 内容寻址上传 → 创建草稿 → 创建不可变版本 → 权利/来源声明 → 人工确认 → 发布 → catalogue 与 Range 验证。

任何一步失败都保留为草稿或明确失败，不得进入公共 catalogue。当前阶段不运行此流程，不上传新歌曲。

## 故障行为

- `/health` 只判断进程存活。
- `/ready` 必须实际执行 PolarDB `SELECT 1`；数据库不可达时返回 5xx。
- BFF `/ready` 必须验证杭州 `/ready`，不得在上游失效时报告可用。
- catalogue 使用稳定游标分页，每页最多 100 首，并直接返回当前音频版本，避免客户端逐首请求。
- 恢复必须进入隔离数据库并核对实体数量与媒体 SHA-256；存在漂移即失败并升级人工处理。
