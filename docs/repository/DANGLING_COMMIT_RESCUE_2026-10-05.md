# Dangling Commit Rescue — 2026-10-05

**任务:** `MOODIFY_REPOSITORY_SLIM_001` 的后续动作
**触发:** 仓库瘦身过程中发现本地对象库有 32 个 unreachable commit，其中包含
2026-10-03 / 10-04 的真实开发成果（Linux 打包、Android 退役、Windows RC 打包等）。
**人类裁决:** `YES — recover all valuable dangling work before any GC.
Restore by workstream tip, not one branch per dangling commit.
Push the rescue branches to origin, but do not merge them into main yet.`

> **恢复和合并是两件事。第一步保住历史，第二步才是判断是否还有产品价值。**
> 本文档只记录第一步。这些分支**不参与 main**，需要时逐条 `diff` / `cherry-pick` / PR。

---

## 1. 为什么必须先救再 GC

这些 commit 当时的状态：

```text
不在任何分支上（git branch -a --contains 为空）
reflog 提及数为 0（没有 reflog 锚点）
只依赖"对象还躺在 .git 里"而存在
```

因此任何一次 `git gc`（默认 `gc.pruneExpire=2.weeks.ago`）都会**永久删除**它们。
在本轮瘦身中，`git gc` 被**主动跳过**——原因是发现了这批数据，而
`git prune`（只回收松散对象）已验证不会触及 pack 内的这些 commit。

**19 个候选全部经确认是 ORPHANED（无任何 ref 引用）。**

---

## 2. 方法：按工作链 tip 建 ref

恢复一个 **tip** 即可保护它的全部祖先 —— 不需要为每个 commit 建分支。

执行前的两项安全检查：

1. **祖先链是否已被现有 ref 保护**：每个 tip 的祖先里只有 1–6 个是不可达的，
   其余全已可达。所以建 ref **只保护那些孤儿提交本身**，不会牵进额外的不可达历史。
2. **是否夹带 stash 提交**：`rescue/temporal-texture-repair-2026-10-04` 的父链含
   `index on` / `untracked files on`（stash 对象）。这里**显式记录**该事实，
   而不是悄悄把它变成分支内容。

---

## 3. 恢复清单（17 个分支，全部已推送 origin）

| rescue 分支 | tip | 保护提交数 | 内容 |
|---|---|---:|---|
| `android-retirement-2026-10-04` | `a144897301` | 1 | 退役重复 Android 客户端（变体 A） |
| `android-retirement-2026-10-04-v2` | `97343231a5` | 1 | 同主题**内容不同**的变体 B |
| `linux-packaging-2026-10-04` | `a30afe6d04` | 1 | Studio Linux x64 打包（AppImage + deb）变体 A |
| `linux-packaging-2026-10-04-v2` | `030ffe6b1e` | 1 | 同主题变体 B（`package.json`/`main.js`/`test-studio.js` 有差异） |
| `desktop-windows-rc-packaging-2026-10-03` | `d93e57a10e` | 1 | Windows RC 打包 |
| `workspace-recovery-2026-10-03` | `5b3d9bda6e` | 4 | 本地工作区恢复 + Evidence Loop v0.1 草案 + Listen Demo 渲染工具 |
| `workspace-recovery-2026-10-03-v2` | `819c06e9c0` | 4 | 同链的另一个合并变体 |
| `product-realignment-2026-10-04` | `ffe2473611` | 1 | 产品重整**任务书三件**（+1755 行）+ Android 退役文档 |
| `product-realignment-audit-2026-10-04` | `aef9f35451` | 1 | 对照仓库核实产品重整现实审计 |
| `temporal-texture-triage-2026-10-04` | `719ac8ee30` | 1 | temporal-texture 错误分诊报告 |
| `temporal-texture-repair-2026-10-04` | `6a99e91e3a` | 3 | 修复探针（**内含 2 个 stash 提交**，见 §2） |
| `audio-intelligence-2026-08-08` | `7838945a9b` | 6 | Ocean Listen 吸收桥 / 歌词时间对齐 / Pairwise Auditory Judge / Android 听觉减法重构 / 部署脚本 |
| `public-trust-layer-2026-08-22` | `732f52fdf1` | 1 | 公共信任层与项目可信度资产（P4-04） |
| `music-data-plane-2026-08-15` | `c6936c7b4d` | 1 | Music 数据面加固 |
| `genesis-decision-log-2026-08-30` | `aece1e8cf9` | 1 | genesis 决策日志哈希刷新 |
| `web3-inflight-preserve-2026-08-29` | `e22809129d` | 1 | 保留 MOOD 数字主页 + LA Web3 根改动 |
| `web3-rpc-timeout-2026-08-28` | `20ff2c832f` | 1 | BSC 链读取 RPC 超时 |

**为什么 `-v2` 变体也保留：** 它们不是重复内容 —— 经 `git diff --stat` 确认
`linux-packaging` 的两个 tip 在 3 个文件上有差异，`android-retirement` 的三个
候选各有独立内容（其中一个还是带任务书的超集）。丢掉任何一个都是真的丢内容。

**为什么 Web3 的两条也保留：** MOOD Web3 线已于 2026-10-03 移出主线
（见 `docs/ARCHIVE_INDEX.md`），但"移出主线"不等于"该被 GC 删除"。
它们作为历史记录先保住，是否再引用由人决定。

---

## 4. 执行结果

| 指标 | before | after |
|---|---:|---:|
| unreachable commit | **32** | **5** |
| dangling commit | **19** | **2** |
| 剩余 unreachable 的性质 | 混有真实工作 | **全部是 stash 提交** |
| origin 上的 rescue 分支 | 0 | **17** |
| 缺失（未推上去的） | — | **0** |

**验证方式：** 用 `git ls-remote --heads origin 'refs/heads/rescue/*'` 逐个核对
tip 是否已在远端。缺失数 0 —— 即这些提交**已彻底脱离 dangling**，
任何后续 `git gc` 都不会再触及它们。

**剩余 5 个 commit 全部是 `git stash` 产物**（`WIP on` / `index on` /
`untracked files on`），且 `git stash list` 仍持有它们（3 条 stash 记录）。
它们不是"失去引用的开发成果"，故未建分支。

---

## 5. 后续（不由本任务决定）

```text
GitHub 上确认 rescue/* 已在          ✅ 已完成
确认重要提交均 reachable             ✅ 已完成
现在可以安全执行常规 git gc          ✅ 已解锁（见下）
```

**GC 现在可以执行了** —— 那批真实工作已有 17 个 origin ref 保护。
但本任务**没有执行**它：`git gc` 仍会重写 pack，属于独立动作，
且需要先确认没有其他 worktree 正在使用。

逐条评估这些分支的产品价值是**后续独立工作**：

```text
git log --oneline main..rescue/<name>
git diff main...rescue/<name>
git cherry-pick <sha>   # 或开 PR
```

**不要把这 17 个分支合并进 main。** 它们是存档，不是待合并的变更集。
