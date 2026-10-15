# 发布列车与产品重整执行报告

**日期：** 2026-10-04
**执行者：** Cloud AI（本机 Windows + LA 云构建节点 `103.144.246.242`）
**范围：** 发布列车执行、Windows 验收、Linux Studio 重建、产品重整 C0 审计
**状态：** 两条线均已推到绿灯，**均未合并、未发布**，等人工裁决

---

## 一、执行摘要

本轮把 Windows RC 发布列车从"三个 PR 都开着"推进到 **main 上已含全部四个 PR**，并在打标签前拦下一个会污染发布版的缺陷。同时完成 Linux Studio 的重建（脱离 stacked base）与 Product Loop 的 Phase C0 审计。

**共四条 PR 由我操作：** #39（重建）、#45（新建）、#46（新建）；#36/#37/#38/#40 由我合并。

**两条阻塞性发现：**

1. **HOTFIX 000（含立体声响度 ~3.01 dB 修正）不在发布路径上** —— 在打标签前发现，经你裁决改为先落 #40，避免了发布一个已知少报 3 dB 测量值的 RC。
2. **Linux 分支硬同步会连根拔掉 PR #37** —— 差异核对发现我的分支会把 #37 刚删除的约 40 个生成音频加回来，并删掉 #37 为此新增的守卫。已改为"从 main 起新分支、只取自有文件"重建。

---

## 二、已合并进 main

| PR | 内容 | merge commit |
|---|---|---|
| **#36** | Cloud node 集成/验证节点文档 | `5f8005d3` |
| **#37** | Repository cleanup —— 移除生成物（含 `FORBIDDEN_GENERATED_PREFIXES` 守卫） | `5fc74d24` |
| **#40** | **HOTFIX 000 —— Core 测量正确性**（立体声 LUFS、通道域指标、静默回退） | `f9a00de2` |
| **#38** | Desktop release 001 —— Windows RC 打包 | `1dd5b2e1` |

`main` 现为 `1dd5b2e1`。

**合并方式说明：** 分支保护要求 `strict`（head 必须与 base 同步）且 `enforce_admins: true`，所以**没有用 `--admin` 绕过**，而是对 #37 与 #40 分别走 GitHub 官方 "Update branch"，再等必需检查 `test` 通过后合并。#38 与 main 有真实冲突（两边都改了 `package.json` 的 `scripts` 块），我以并集方式解决并保留了双方的产物。

---

## 三、Windows 验收（本机）

### 3.1 被验收的工件

| | 第一次验收 | 发布源验收 |
|---|---|---|
| PR #38 head | `54d77b0a` | `0e0aee71` |
| run | `37167247477` | `37178855849` |
| CI merge sha | `a2b33913` | `30a4e40b` |
| Setup 字节 | 190,267,612 | 190,269,903 |
| Setup SHA-256 | `f01b5e68…cf8edd` | `9b1753ad…21cbab` |

`main` 与 `0e0aee71` 的**代码树完全相同**，所以第二次验收覆盖的就是发布源。

### 3.2 结果

| 环节 | 结果 |
|---|---|
| 哈希核对 | 三文件对 `SHA256SUMS.txt` **3/3 MATCH** |
| 安装（静默） | exit **0**，29.9–42.8 s，712.5 MB / 497–498 文件 |
| 注册表卸载项 | `Moodify Studio 1.0.0-rc.1`，`UninstallString … /allusers` ✓ |
| 开始菜单 / 公共桌面快捷方式 | 均存在且指向已装 EXE ✓ |
| 启动 + 主窗口渲染 | 标题栏、Moodify logo、左侧图标栏、水印均正常 ✓ |
| 真实音频 | 打开一首真实音乐 → **Detect（ANALYZED）→ Diagnose（DIAGNOSED）**，产出 `measurements.json`、`evidence.json`、`report.{json,md,html}`、`charts/` 全套 ✓ |
| **HOTFIX 000 打包风险核查** | `src/runtime.js` **已进包**；被删除的静默回退行 `existsSync(exe) ? exe : PYTHON` **不在包内** ✓ |
| 卸载 | exit **0**；安装目录 / 注册表 / 两处快捷方式 **4/4 全部移除**；用户数据（9.46 MB）与 21 个 case、源音频**完好未动**；无关旧应用 `Moodify 0.1.0-beta5` 未受波及 ✓ |

### 3.3 一次未解释的事件

发布源构建在 **13:30:22** 退出（进程消失），当时你正要做"打开真实音频"这一步。

**已排除：** Windows 应用日志**无**崩溃/WER 记录；**无** crashpad 转储目录（从未产生过）；**无**新 case（说明打开音频未走完）；安装目录完好。

**更像"窗口关闭 → 应用正常退出"**（Electron `window-all-closed` 在非 macOS 会 quit），但这是推断。**当时你未描述看到什么，此事件至今未定性。**

### 3.4 一个必须记下的边界事实

该构建是 `runtime_mode: external`：**它的测量来自本机 Core，不来自 EXE**。所以 HOTFIX 000 的**桌面部分**（`runtime.js` / F4）随 EXE 发布，但它的**测量修正**（立体声 LUFS 那 3.01 dB）走 Core 发行渠道。**Release Notes 必须写明这一点**，否则拿到 EXE 的人会以为测量修正跟着来了。

另：`E:\moodify` 检出停在旧 commit，**未必含 HOTFIX 000 的 Core 改动**，故本机跑出的数字未必是修正后的。此事我未动。

---

## 四、我操作的 PR

### 4.1 PR **#46** —— 共同父级权威（当前最高优先）

`1010232c`（产品重整三份文档）的父提交是 `0e0aee71`，**发生在 #38 合并点之后**，因此从未进入 main。用 **cherry-pick** 送入 main：

```
e386796e  docs(product): define local and cloud realignment tracks
          author 保留为原作者，日期保留 2026-10-04 14:56:31 +0800
docs/tasks/MOODIFY_PRODUCT_REALIGNMENT_001.md        +790
docs/tasks/MOODIFY_PRODUCT_REALIGNMENT_CLOUD_001.md  +446
docs/tasks/MOODIFY_PRODUCT_REALIGNMENT_LOCAL_001.md  +486
```

CI：`test` pass、结构守卫 pass、Studio pass —— 全绿（除既有 `temporal-texture`）。**未合并。**

### 4.2 PR **#39** —— Linux Studio 重建

| | 原状态 | 现状态 |
|---|---|---|
| base | `codex/desktop-release-001`（已合并） | **`main`** |
| head | `267c5afe` | **`06e8c90f`** |
| 相对 base | 50 文件（含 #37 的倒退） | **9 文件 / +1255 −12** |
| 状态 | `BLOCKED` | `MERGEABLE` |

**为什么是重建而不是同步：** 我的分支基于 `06dce343`，比 main 落后两个清理提交。差异核对显示它会重新跟踪约 40 个 `moodify-core-package/outputs/phase2_agent_b/*.wav`（#37 刚删掉的生成物），并删除 `scripts/check_repo_structure.py` 里 #37 新增的 `FORBIDDEN_GENERATED_PREFIXES` 守卫——**即把 PR #37 整体回滚**。

改为从 `origin/main` 起新分支、**只 checkout 我拥有的 9 个文件**，并逐文件验证它们与已验收版本**逐位一致**。最终差异恰好 9 文件，无生成物、无守卫改动。

同时 HOTFIX 000 的重复携带也消失（#40 已独立合并进 main）。

**按你的指示：未合并、未发布，`HUMAN_CHECK_REQUIRED` 保留。**

### 4.3 PR **#45** —— Product Loop Phase C0 审计

```
a77f065f  docs(product-loop): add the Phase C0 reality and authority audit
分支  cloud/product-loop-core-001      base = main @ 1dd5b2e1
文件  docs/reports/PRODUCT_LOOP_CLOUD_REALITY_AUDIT_001.md  (+479)
```

CI 全绿（除既有 `temporal-texture`）。**未合并。**

核心结论摘要：

- **六个 Phase 里三个已有在途实现**：#44 ≈ C2（`moodify/project/`）、#42/#43 ≈ C5（`moodify/capabilities/`）、#41 ≈ C1 部分。两个包在 main 上都不存在。
- **9 套互不相同的生产状态词汇**，其中两套**顺序相反**：`pipeline.js` 是 `ANALYZED → DIAGNOSED → SEPARATED`，`data_plane` 是 `STEM → ANALYZE`。
- **`ProductionCase` 一个定义、三条写入路径、两个文件名**。
- **Studio 有 9 个无校验器的 JS 契约**，且 `renderer/app.js` **另抄一份**门控（§3 未点名它）。
- **§8 的九条不变量在 `pipeline.js` 里已全部实现** → C3 是"移植 + parity 证明"，不是新设计。
- §7 真实缺口只在 **attempt/version 层**；另有 `extra="forbid"` 与 `SchemaVersion = Literal["1.0"]` 两个硬约束。

---

## 五、Linux 构建（LA 节点）

对新分支 `06e8c90f` 重做全套，**全绿**：

```
check-contracts  ✓      pipeline 33/33      studio 21/21
NEG_PASS basic-pitch / score               POS_PASS
PTY_SMOKE_PASS （ABI 130，exit 0）
RUNTIME_FAIL_SMOKE_PASS （打包布局 DEPENDENCY_MISSING，无 exe，不泄漏解释器）
Xvfb 存活 18 s，无 MODULE_NOT_FOUND
DIST_EXIT=0
```

| 产物 | 字节 | SHA-256 |
|---|---:|---|
| `Moodify_Studio_1.0.0-rc.1_Linux_x64.AppImage` | 273,617,598 | `835455bf2a0d48c810dc3d9c33821eb93edf80414b3c083baf4b636b45eff71b` |
| `Moodify_Studio_1.0.0-rc.1_Linux_amd64.deb` | 207,657,396 | `2bb9faec2f443f0e693c922100bd2d5709b6fb881d5173b3502285f21b64acf3` |

---

## 六、值得记住的三个仓库事实

**1. `ci.yml` 只在 base = main 的 PR 上运行。**

```yaml
on:
  pull_request:
    branches: [main]
```

它产出的 `test` 正是分支保护要求的检查。**所以任何 stacked PR 在改 base 之前 `test` 永不上报，PR 永远 `BLOCKED`**——这正是 #39 之前卡死的原因。而且**改 base 本身不触发 workflow**，需要 close/reopen 或推一个提交来启动。

**2. `temporal-texture` 守卫是全仓既有红灯**，前 12 次连续 PR 运行全部失败（跨 `desktop-release-001`、`repository-cleanup-001`、`cloud-node-001`、`studio-pipeline-realignment`），最早 2026-10-03T12:22，**从未在 main 上跑过**。它不是必需检查，不阻塞合并，但会长期出现在每个 PR 上。

**3. 本地 `core.autocrlf=true` 且无 `.gitattributes`**，工作区全是 CRLF 而提交对象是 LF。本次已逐位验证（`git show HEAD:… | sha256sum` 与 Linux 侧一致），提交到 Linux 是干净的。但新增 `.sh` / shebang 文件时仍应留意。

---

## 七、尚未完成

| 事项 | 状态 |
|---|---|
| `desktop-v1.0.0-rc.1` 标签 | **未打**（原序列要求先完成验收；验收卡在 3.3 那次未解释的退出） |
| Docker Container PR | **未开始**（现实审计已完成，见 `LINUX_DOCKER_RELEASE_001` 报告） |
| Product Loop C1–C5 | **未开始**，等 #46 合并 |
| Studio 退出事件定性 | **未解释** |
| 本机 `E:\moodify` 检出是否含 HOTFIX 000 的 Core 改动 | **未核实、未改动** |

---

## 八、等人工裁决

1. **#46 是否合并？** 它是 Cloud C1–C5 与 Local 线的共同父级，仓库规则是 no auto-merge，我不会自行合并。
2. **发布列车如何收尾？** 标签仍未打。选项：(a) 就本机再做一次完整验收（含你点一次"打开音频"）后打标签；(b) 先查清 3.3 那次退出再打；(c) 其他。
3. **Docker Container PR 是否现在开？** 你给的约束已记下：先 CLI/Core headless image、worker 修好前不作默认 Compose 服务、不放 Electron/Xvfb 进生产镜像、Phase A 不推 GHCR 不发 `latest`、标签命名空间用 `container-v*` 以避免与 Android `v*`、Desktop `desktop-v*` 冲突。

---

## 附：本报告相关的既有报告

```
docs/reports/LINUX_DOCKER_RELEASE_001_2026-10-04.md           （Linux/Docker 发布执行）
docs/reports/LINUX_STUDIO_HOTFIX_RECONCILE_001_2026-10-04.md  （HOTFIX 000 对账）
docs/reports/PRODUCT_LOOP_CLOUD_REALITY_AUDIT_001.md          （C0 审计）
```

本文件为本地交付，未提交入仓库。
