# Cloud Product E2E — 执行结果

**Package:** MFY_CLOUD_PRODUCT_E2E_001 (60)
**Date:** 2026-08-14
**工具:** ops/e2e_runner.py（用户入口开始；从不以 localhost 冒充生产）

## Stage 1 — 真实公网链（只读）13/13 PASS

| 场景 | 结果 |
|---|---|
| 官网 /、/ear、/music、/evidence、/about、/contact、/privacy | 7/7 200（注：当前 origin 为占位站；新站部署为 Gate 项） |
| Music catalogue（匿名发现） | 200，2 首真实曲目 |
| Track 页 | 200 |
| Creator 页 | 200 |
| 音频 Range（seek 前提） | 206 / 1024B |
| 音频全量（播放） | 200 / 47,451,230B（完整曲目） |
| Ear API health | 200 |

## Stage 2 — Ear 全链路闭环（本地 API+worker，真实音频）4/4 PASS

上传→Job QUEUED→SUCCEEDED→result（case_manifest+production_case）→authority_state ALGORITHM
Job: job_64d4983be77f4800a571f55fa3c2c043

## 发现（CAVEAT）

- **UA 过滤**：线上 origin 对非浏览器 User-Agent 返回 403（裸 urllib → 403；浏览器 UA → 200）。程序化客户端需浏览器 UA 或 nginx 按路径豁免 /api/（改 nginx 需授权，记录不擅改）。
- 官网新站（46 包 7 页）尚未部署到线上 origin（现为旧占位站）——部署归 65 授权后。

## 事实边界

- 认证路径（登录/favorite/发布）E2E 需部署授权与测试身份（56 数据集）；读路径已验。
- 重复运行：`python ops/e2e_runner.py --live` / `--local-ear <url>`。
