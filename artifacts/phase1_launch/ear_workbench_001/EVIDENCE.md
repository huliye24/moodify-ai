# Ear Workbench V1 — Evidence Record

**Package:** MFY_EAR_PRODUCT_SURFACE_V1_001 (47)
**Date:** 2026-08-14

## 真实链路案例（成功案例）

- Job: `job_4b85f0621ab04a1fbd4649b27bfd33ea`
- Case: `case_df1c22f8280844a1b0250b43a4c0ab04`
- 源: `benchmarks/reference_audio/fixtures/clipped.wav`（192KB，测试基准 wav）
- 目标: "Measure loudness balance and detect clipping"
- 状态序列: QUEUED → RUNNING → SUCCEEDED（约 40s，本地 worker）
- authority_state: `ALGORITHM` · lifecycle_state: `COMPLETED`
- case_manifest sha256: `328c3a9877b1d842b25e45b2…`（文件哈希）

## API trace 摘要

1. `POST /api/v1/auditory/jobs` (multipart audio + prompt) → 202 `{job, request}`
2. `GET /api/v1/auditory/jobs/{id}` → `{job}`（轮询）
3. `GET /api/v1/auditory/jobs/{id}/result` → `{job, case_manifest, production_case, algorithmic_review, algorithmic_scores}`（全量存在 ✓）

## 截图（本目录）

- `home-1440.png` — Home（仪器状态 + 空态 recent cases）
- `case-1440.png` / `case-390.png` — Active Case（真实 job SUCCEEDED + View result 动作）
- `result-1440.png` — Result 三层（Findings → Measurements → Method & versions，真实数据）
- DOM 验证：`pill verified` + job id 渲染于 case 页（headless dump-dom）

## 验收对照（47 包 P0）

| P0 | 结果 |
|---|---|
| 从 Home 创建并追踪真实案例 | ✓ 真实上传→轮询→结果全链路 |
| 结果首层不依赖原始 JSON | ✓ findings/measurements/method 分层，无 <pre>/<code> |
| 判断可追到证据与版本 | ✓ formula_version/schema_version/source_id/evidence_ids 展示 |
| UI 与 authoritative case state 一致 | ✓ 只渲染服务端状态；本地不推导 |
| 比较不混淆测量与偏好 | ✓ compare 页无候选时不显示伪播放；notice 明示 |
| 不确定/人工/失败不显示为成功 | ✓ 四个一级状态（processing/human/inconclusive/failed）均为一级 pill |
| 中断后可恢复或明确关闭 | ✓ Recovery 区块 + 服务端权威重读 |
| 私人音频/内部路径/日志不进公开缓存 | ✓ check_workbench.mjs 静态断言（7/7）；API 响应 no-store |

## 事实边界

- 比较页候选播放依赖证据桥暴露 publish-safe 媒体（包 52），V1 诚实显示不可用。
- human_required / inconclusive 的真实案例截图待 48 包升级路径落地后补拍。
- 工作台 dev 代理（dev_proxy.py）为同源代理形态，生产由 nginx 承担同源。
