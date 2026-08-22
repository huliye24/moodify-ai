# 00 — Executive Reality Summary

**Package:** W01-P00 — Moodify Project Reality Snapshot
**Scan window:** 2026-08-17 19:45–20:15 CST（本地仓库 + GitHub 远端 + LA/杭州只读 SSH）
**Operator:** Claude A（huliye24 本地会话）
**Repository:** huliye24/moodify-ai（origin）；huliye24/moodify（moodify remote）
**GitHub main HEAD:** `fa88b0b9`（2026-08-08）
**Local HEAD:** `98f7b96e`（branch `codex/moodify-classic-reconstruction-001`，2026-08-17，领先 origin/main 154 commits）
**Read-only guarantee:** 未修改任何仓库/服务器文件，未 commit/push/merge，未安装/重启/改库/改 OSS/改安全组。全部为只读命令（git 只读、ls/stat/df/ps/ss、systemctl cat/list、docker ps/inspect、curl GET 自身服务、SQLite/MySQL 元数据只读尝试）。
**Inaccessible areas:** PolarDB 直接只读核验（凭据不符）；GitHub Actions 历史日志细节；云端数据库内容（除黑箱调查）。

---

## 1. 当前真正可运行的主链

```text
真实（有运行证据）：
  静态音乐托管链：  LA nginx(:80) + cloudflared 隧道 → music-platform(:3100 vinext)
                     + music-bff(:8100) + music-media 音频（248MB/5 文件）→ 浏览器/App 播放
  数据工厂批处理链： 杭州 moodify-data-worker（moodify-node worker + 4 timers）
                     → /var/lib/moodify（历史 10 曲 pilot，6.5GB）
  内部 API：        LA moodify-api(:8000, Ear FastAPI) + 杭州 moodify-api(:8000, 公网, service-key)
  分轨代理：        LA docker moodify-audiolla（lalal.ai 代理，:18080→8000，健康）——无自动调用

未运行（仅代码/文档存在）：
  Listen→Judge→Intervene→Verify 完整 Ear 链路：仓库代码完整，云端无生产流量（队列近空）
  AI 模型推理：云端无任何模型/checkpoint 在运行（无 GPU）
  反馈学习闭环：不存在
```

## 2. Canonical code 与 deployed runtime 是否一致

- **Status: 不一致（UNVERIFIED_DIVERGENT）**
- GitHub `main`（fa88b0b9）≠ 本地 HEAD（98f7b96e，领先 154 commits，含 Classic Reconstruction 全系列）。
- 云端部署**非 git 副本**（/opt/moodify 为时间戳 tar 发布，无 .git），无法与任何 commit 精确对齐；
  releases 目录最新为 `20260816T080724Z` / `20260816T080310Z`（LA）与 20260813 系（杭州 moodify-music）。
- 部署代码身份只能近似推断（时间戳 + 文件清单），标记 UNKNOWN 级别为部署对齐。

## 3. 最大的 5 个 reality / authority conflicts

1. **产品权威冲突（authority_conflict=true）**：GitHub main 的 README/AGENTS 仍以「The Ear of AI — Auditory Intelligence System」为产品身份；本地未合并分支上 Classic Reconstruction Constitution v1.0 明确宣称「对外产品 = 重建优先聆听环境，Ear 为内部智力层」并 Supersedes 旧表述。两套权威并存，未合并。
2. **工作现实 vs 仓库现实**：补丁包/记忆声称大量「已完成」（73 个补丁包、MAMSE 16 篇、重建 P01-P07、Phase1 43–65 等），但 GitHub `main` 只含 2026-08-08 之前内容；绝大多数交付证据只存在于本地分支与 artifacts/，未进入 canonical main。
3. **PR #21 双重身份**：冻结协议（docs/PR_DISPOSITION.md）裁定 #21 为「canonical release carrier，KEEP」，但至今仍 OPEN/DRAFT 未合并；其内容与 Classic Reconstruction 方向（reconstruction-first）的关系未裁决。
4. **REPOSITORY_STATUS.md 过时**：其 Verification Baseline 为 0b355e7（2026-08-08）且 canonical identity 仍写 Ear of AI；当前代码 98f7b96e 与宪法已变，文档落后于代码。
5. **「Moodify Cloud」名实差距**：名义上的云 = 2 台 VPS + 3 个托管 DB + 1 容器；没有对象存储、没有 AI 推理、没有生产 Ear 流量（同日 11:00 黑箱调查独立确认）。

## 4. 最大的 5 个 UNKNOWN

1. PolarDB 三实例的直接核验（凭据不符 → BLOCKED；仅同日黑箱调查声称内容）。
2. 云端部署代码与仓库 commit 的精确对应（tar 发布无 git 身份）。
3. LA `moodify-music`（vinext node 平台）与 `moodify-music-bff` 的代码来源与版本（仓库中未找到对应构建产物）。
4. 外部能力（LALAL.AI/Audiolla/Demucs/Basic Pitch/Matchering）中除 audiolla 容器与 FFmpeg 外，均无生产调用证据。
5. 真实音频资产总 identity：无全库统一 track-hash 注册表（仅 golden case 有 source_manifest 哈希）；各处音乐目录（pre-music/07Music/music/local_audio_assets）是否重叠 UNKNOWN。

---

## 5. 一句话总结

> Moodify 此刻的真实存在 = **一个 GitHub main 上「Ear of AI」时代（2026-08-08 冻结）的仓库 + 一个本地分支上「重建优先」新时代的 154 个未合并提交 + 两台运行静态音乐网站/API 壳/数据工厂批处理的 VPS + 一个健康的 lalal 分离代理容器 + 一个 19 表近乎无数据的 PolarDB + 一批已部署但队列近空的 Ear worker**。完整「听→判→预→验」链路只存在于仓库代码，云端没有任何真实音频走完该链路。

详细证据见 `01`–`08` 各报告与 `08_EVIDENCE_INDEX.md`。
