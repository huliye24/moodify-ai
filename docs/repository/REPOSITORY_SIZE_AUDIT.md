# 仓库体积审计 — REPOSITORY_SIZE_AUDIT

**任务:** `MOODIFY_REPOSITORY_SLIM_001`
**Date:** 2026-10-05
**仓库:** `huliye24/moodify-ai`（public / GPL-3.0）
**本轮决策:** **不改写 Git 历史**（Decision A）。因此本文件的目标不是「把 306 MB 变成 30 MB」，
而是把**新贡献者的入门成本**从 50 分钟降到几分钟，并阻止体积继续增长。

> **一句话结论：过去的历史保留，但不应该要求每个新贡献者先下载全部历史才能参与。**

---

## 0. 四类体积必须分开看

混为一谈会得出错误结论（例如「删掉 `.gitignore` 里的大文件就能让克隆变小」——不能）。

| 类别 | 本轮实测 | 是否影响新克隆 |
|---|---|---|
| **A. 当前 HEAD 已跟踪数据** | **86.7 MiB** → 本轮降到 **40.8 MiB** | 是（浅克隆几乎只下这个） |
| **B. 远端可达 Git 历史** | blob 合计 **749.6 MiB**（未压缩） | **是**（全量克隆 ≈ 306 MB 压缩后） |
| **C. 本地悬空 / 垃圾对象** | **563.8 MiB** 垃圾 + ~359 MB 悬空 blob | **否** —— 克隆下不到 |
| **D. 工作树生成物** | ~2.1 GB venv（本机） | 否（已被 `.gitignore` 覆盖） |

**关键点：** `.gitignore` 只阻止*未跟踪*文件被加入。已经进过历史的文件**永久留在克隆成本里**。
所以本轮能真正改善新贡献者体验的手段只有两个：

```text
1. 让浅克隆成为官方默认（把 306 MB 变成 27 MB）
2. 阻止新的大家伙进入 Git（保护未来）
```

---

## 1. Baseline Metrics（本轮开始前）

```text
GitHub 报告仓库体积        : 313,146 KB ≈ 306 MB
.git 对象库（本地主库）     : 4,091.7 MB
  ├─ pack 合计              : 776.19 MiB
  ├─ 垃圾（中断操作残渣）    : 563.83 MiB
  └─ 松散对象               : 818.11 KiB（164 个）
可达对象（含路径）          : 19,463
HEAD 已跟踪文件             : 1,599 个 / 86.7 MiB
pack 内对象总数             : 26,074
远端分支                    : 60（默认分支 main）
本地分支                    : 84
linked worktree             : 31
```

### 1.1 克隆实测（同一网络，2026-10-05）

| 模式 | 耗时 | 下载体积 |
|---|---:|---:|
| 全量 `git clone` | 85 秒 | **306.8 MB** |
| 单分支 `--single-branch --branch main` | 76 秒 | 259 MB |
| **`--depth 1`** | **12 秒** | **27.1 MB** |

慢网络外推（同伴实测约 100 KB/s）：全量 ≈ 50 分钟 → 浅克隆 ≈ **4 分钟**。

> 注意 `--single-branch` 几乎没有帮助（259 MB）：体积不在「分支多」，而在 `main` **自身的历史**。

---

## 2. Historical Bloat Findings

远端可达 blob 共 **749.6 MiB**（未压缩）。分布：

| 区间 | 文件数 | 合计 |
|---|---:|---:|
| ≥10 MiB | 12 | 405.2 MiB |
| 5–10 MiB | 18 | 113.5 MiB |
| 1–5 MiB | 47 | 126.4 MiB |
| 100 KB–1 MiB | 146 | 59.1 MiB |

### 2.1 最大的历史 blob 及其类别

| 体积 | 路径 | 类别 | 今天的 `.gitignore` 会挡吗 |
|---:|---|---|---|
| 98.9 MB | `runs.tar.gz` | 归档 | ✅ `*.tar.gz` |
| 84.4 MB | `moodify-mainline-codex.bundle` | Git bundle | ❌ **未覆盖** |
| 42.1 MB | `apps/android/app/build/.../classes.dex` | 构建产物 | ✅ `apps/android/app/build/` |
| 35.7 MB | `apps/android/app/build/.../zip-cache/*` | 构建产物 | ✅ 同上 |
| 32.0 MB | `artifacts/mix_graph_v01/golden/example_mixgraph_8eec7960.wav` | 生成产物 | ✅ `/artifacts/` |
| 28.8 MB | `backend/moodify-server.exe` | 二进制 | ✅ `*.exe` |
| 21.8 MB | `deliverables/releases/.../Moodify_Music_3.1.0_Android_20260816.apk` | 发布产物 | ✅ `*.apk` |
| 15.7 MB | `backend/server.exe` | 二进制 | ✅ `*.exe` |
| 11.2 / 11.0 / 10.8 MB | `artifacts/mamse_005/.../mamse005_cepstrum.npz` | 生成产物 | ✅ `/artifacts/` |

**结论：** 这些类别今天基本都已被正确忽略。忽略规则是**对**的——
它们只是在规则写出来**之前**进了历史。**本轮不动历史。**

### 2.2 一个仍未覆盖的类别

`*.bundle`（Git bundle，84.4 MB）**不在 `.gitignore` 里**。虽然不改历史，
但必须补上规则，否则它可能再次进入。

---

## 3. Current HEAD Large Files

移除生成产物后，HEAD 最大的已跟踪文件：

| 体积 | 路径 | 分类 | 处理 |
|---:|---|---|---|
| 8.24 MiB | `moodify-core-package/tests/baseline/test_audio/vocal_folk.wav` | **REQUIRED_FIXTURE** | **保留**（见 §4） |
| 7.32 MiB | `.../test_audio/electronic.wav` | **REQUIRED_FIXTURE** | **保留** |
| 5.49 MiB | `.../test_audio/piano.wav` | **REQUIRED_FIXTURE** | **保留** |
| 1.13 MiB | `moodify-desktop/renderer/vendor/opensheetmusicdisplay.min.js` | VENDORED | 保留（已随壳 vendor） |
| 0.84 MiB | `moodify-desktop/renderer/vendor/xterm.js` | VENDORED | 保留 |
| 0.81 MiB | `brand/assets/moodify-horizontal.svg` | SOURCE（品牌资产） | 保留 |
| 0.56 MiB | `.moodify/tt_baseline/report.json` | EVIDENCE（守卫基线） | 保留 |
| 0.47 MiB | `moodify-desktop/renderer/vendor/xterm.js` 相关 | VENDORED | 保留 |

### 3.1 本轮移除：`moodify-core-package/outputs/phase2_agent_b/`（32 个文件，46.0 MiB）

**证据链：**

```text
run_agent_b.py:179   out_path = str(OUT / f'e2e_gate_{emo}.wav')
run_agent_b.py:180   sf.write(out_path, processed, sr)      ← 生成，不是读取
```

- 全仓库检索：**没有任何代码读取这些 wav**（只有 `docs/restructure/*` 的目录清单提到路径）
- `.gitignore:215-216` 自己写着 `# ── Generated outputs (never track) ──` / `outputs/`
  → **跟踪它们违反仓库自己的政策**
- 已用 `git rm -r --cached` 移出索引，**磁盘文件保留**（可随时重跑 `run_agent_b.py` 再生成）

**效果：** HEAD 已跟踪 86.7 MiB → **40.8 MiB**。健康度从 `>50 MiB review required`
回到 `30–50 MiB` 警告带。

**诚实边界：** 这**不会**让新克隆变小——那些字节仍在历史里。
它的价值是停止继续在源码树里维护生成产物，并让体积指标反映真实源码规模。

---

## 4. Baseline Audio Decision — **KEEP**（Decision A）

三个 baseline WAV 合计 **21.0 MiB**，是浅克隆 27.1 MB 里的主要部分。
但**不允许为了数字好看删掉**：

| 文件 | 用途 | 引用证据 |
|---|---|---|
| `electronic.wav` | **CI 测试实际加载** | `moodify-desktop/scripts/test-studio.js:91` |
| `vocal_folk.wav` | 验证套件 / 校准 baseline / 治疗记录 | `moodify-core-package/src/moodify/physics/validation_suite.py:32`；`treatment_records/vocal_folk_*.json` |
| `piano.wav` | 校准 baseline；被云节点文档引用 | `docs/MHP/MHP009.md:34`；`docs/cloud/MOODIFY_CLOUD_NODE.md:205` |

**为什么不能替换成合成信号（拒绝 Decision B）：**

- 它们是**真实音频**，带 provenance：`README.md` 记录 `CAD-MFY-002 / CAD-MFY-006, Suno v4`
- 语义依赖内容类型：`piano.wav`（纯器乐）、`vocal_folk.wav`（人声+民谣）、
  `electronic.wav`（电子）—— 三种**不同音乐内容**，用于校准。
  合成正弦波无法替代「人声+民谣」这种语义
- `MHP005.md:102` 明确建议用这三个不同类型做校准

**为什么不做 FLAC 转换（本轮）：** 无损压缩大约省 40–50%，
但要改若干调用点与 `.gitignore` 白名单，属于独立一轮的改动，
且本轮不能减小克隆（历史里仍是 WAV）。记为**未来可选项**，不是现在的欠债。

---

## 5. Local Object Store Cleanup

### 5.1 linked worktree 结构（§17 要求先确认）

```text
E:\moodify-local\.git    → 文件: "gitdir: E:/moodify/.git/worktrees/moodify-local"
E:\moodify\.git          → 目录（真正的共享对象库）
git rev-parse --git-common-dir → .git
worktree 总数: 31
```

所以对单独 worktree 的 `.git` **文件**做 GC 是错的——必须对 `E:\moodify` 操作。

### 5.2 发现：563.8 MiB 垃圾 + 一个孤立 idx

```text
garbage: 92
size-garbage: 563.83 MiB      ← 91 个 .git/objects/*/tmp_obj_*
孤立文件: .git/objects/pack/pack-ac6677...idx （没有对应的 .pack）
```

这些是**中断的 git 操作**留下的残渣，`git count-objects` 自己把它们列为 `garbage`。

### 5.3 为什么没用任务书默认的 `git gc`

任务书 §18 默认建议 `git gc`、禁止 `--prune=now`。执行前我做了 §18 要求的安全检查，
发现**两个必须停下的信号**：

```text
worktree: 31 个，其中 18 个有未提交改动（一个 837 项）
dangling commit: 19 个，含 2026-10-04 的真实工作：
   a30afe6d04  feat(desktop): package Moodify Studio for Linux x64 (AppImage + deb)
   97343231a5  refactor(app): retire duplicate Android client
   719ac8ee30  docs(reports): triage the temporal-texture error findings
```

**它们的 reflog 提及数 = 0，且不被任何分支包含** —— 说明它们只靠
「对象仍存在」而存活，没有 reflog 锚点。

`git gc` 默认的 `gc.pruneExpire=2.weeks.ago` 会把这些 **2026-10-04（昨天）**
的 commit 一起永久删除。**这正是任务书警告的那类不可逆损失。**

### 5.4 实际执行：更精确、同时更安全的做法

改用 `git prune --dry-run` 先验证，结果显示：

```text
prune 会删除的对象总数: 109
其中 commit 类型: 0          ← 不碰任何 commit
tmp_obj 文件: 91 个 / 563.8 MB
```

于是执行范围被收窄到**只回收松散垃圾**，完全不触碰 pack（所有历史与
dangling commit 都在 pack 里）：

```bash
git prune          # 只清理不可达的松散对象；不 repack、不碰历史
```

并单独删除那个没有 `.pack` 的孤立 `.idx`。

**结果：**

| 指标 | before | after | 变化 |
|---|---:|---:|---|
| garbage | 92 / **563.83 MiB** | **0 / 0 bytes** | **−563.8 MiB 垃圾** |
| 松散对象 | 164 / 818.11 KiB | 146 / 697.86 KiB | 少量 |
| `.git` 目录实际占用 | 4,091.7 MB | **3,880.2 MB** | **−211.5 MB** |
| dangling commit | 19 | **19** | **全部保留** ✅ |
| pack 对象 / pack 体积 | 26,074 / 776.19 MiB | 26,074 / 776.19 MiB | **未改动** |
| `git fsck` error/missing/broken/corrupt | 0 | **0** | 对象库健康 |

**未使用 `--prune=now`。** `git gc` **未执行**——理由是它有真实的
数据损失风险（§5.3），而 `git prune` 已达成同一目的且零风险。

---

## 6. Contributor Clone Path（最终推荐）

```bash
git clone --depth 1 https://github.com/huliye24/moodify-ai.git
cd moodify-ai
python -m pip install -e moodify-core-package
```

**为什么用 `--depth 1` 而不是更长的参数串：** onboarding 应当是**一条最短可靠命令**。
`--single-branch` 实测只省 47 MB（306→259），不值得让命令更复杂。

### 6.1 浅克隆会失去什么（实测，不猜）

| 能力 | `--depth 1` 下的实际情况 |
|---|---|
| `git status` / `add` / `commit` | ✅ 正常 |
| `git diff main` | ✅ 正常 |
| 建分支 / push / 开 PR | ✅ 正常 |
| `python scripts/check_repo_structure.py` | ✅ OK（浅克隆里实测通过） |
| `python scripts/check_repository_size.py` | ✅ OK（只读 `ls-tree HEAD`） |
| `git log --oneline` | ⚠️ **只有 1 条**（不是"少一些"，是只有当前提交） |
| `git blame` 深层历史 / 老 tag / 长距离 bisect | ❌ 需要更多历史 |

### 6.2 需要更多历史时：`--deepen` 不是渐进成本（实测）

| 状态 | `git log` 条数 | `.git` |
|---|---:|---:|
| `--depth 1` | 1 | 27.1 MB |
| `--deepen=5` | 22 | **70.5 MB** |
| `--deepen=25` | 131 | 239.9 MB |
| `--deepen=100` | 328 | 258.9 MB |
| `--deepen=500` | 379 | 259.2 MB（= 全量） |

**原因：** `main` 上有 **31 个 merge commit**。深度每加一层，会把被合并分支
的整条历史一起拉下来，所以 `--deepen` 会**跳变**而不是线性增长——
小数值就可能一次拉掉 200+ MB。

**因此文档必须如实说明：** 如果你确实需要历史，不要指望「先小步 deepen」——
直接做一次完整克隆更可预期：

```bash
git fetch --unshallow          # 补齐全部历史（≈ 再下 230 MB）
```

---

## 7. Repository Size Guard

`scripts/check_repository_size.py` —— 见该文件顶部的详细理由。要点：

```text
检查对象 : git ls-tree -r HEAD（只查 Git 跟踪的文件，不扫文件系统）
单文件上限: 10 MiB（默认）
allowlist : .repository-size-allowlist（每项必须写理由）
HEAD 健康度: <30 MiB preferred / 30–50 warning / >50 review required（只警告，不失败）
CI        : .github/workflows/repo-structure.yml
```

本地提交**之前**想确认改动效果，用 `--index`（否则你会盯着一个还没反映
你刚 `git rm` 的旧数字）：

```bash
python scripts/check_repository_size.py            # HEAD —— CI 用的就是这个
python scripts/check_repository_size.py --index    # 暂存区 —— 提交前自检
python scripts/check_repository_size.py --report   # 附带最大文件清单
```

**为什么阈值是 10 MiB 而不是 GitHub 的 100 MB：** 100 MB 太晚了。
我们的目标不是「不触发 GitHub 报错」，而是保持源码仓库轻量。
当前最大正常文件 8.24 MiB，10 MiB 留有余量。

**它是被验证过的，不是写完就交：** 在一个浅克隆里提交一个 12 MiB 文件，
守卫输出 `ERROR: large tracked file detected` 并 `exit 1`。

---

## 8. 本轮不做什么

| 不做 | 原因 |
|---|---|
| 改写历史 / force push / filter-repo / BFG | Decision A 明确不授权 |
| 删除旧 tag / 旧分支 / 旧 commit | 历史证据不得删除 |
| Git LFS 迁移 | 不会让已存在的历史 blob 消失，只增加账号/工具/clone 复杂度 |
| 删除 baseline WAV | §4 证据表明必须保留 |
| `git gc --prune=now` | 会删掉 2026-10-04 的真实 dangling commit |
| 提高阈值到 100 MB | 见 §7 |

---

## 9. 验收指标

| 指标 | before | after |
|---|---:|---:|
| GitHub 报告仓库体积 | 306 MB | 306 MB（**不变，符合预期**） |
| 全量克隆下载 | 306.8 MB / 85 秒 | 306.8 MB（**不变，未改历史**） |
| **浅克隆下载** | — | **27.1 MB / 12 秒** |
| **新贡献者入门成本** | ~50 分钟（慢网） | **~4 分钟** ← 本轮真正 KPI |
| 当前 HEAD 已跟踪 | 86.7 MiB | **40.8 MiB** |
| 本地 `.git` 占用 | 4,091.7 MB | **3,880.2 MB**（−211.5 MB） |
| 本地垃圾对象 | 563.83 MiB | **0** |
| 最大已跟踪文件 | 8.24 MiB | 8.24 MiB（保留的 baseline 音频，< 10 MiB 上限） |

**注意：** 由于本轮禁止历史改写，「全量克隆体积」不会数量级下降。
这是**预期的正常结果**，不是失败。
