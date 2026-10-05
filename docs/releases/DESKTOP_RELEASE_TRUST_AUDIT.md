# Desktop Release Trust Audit — DESKTOP_RELEASE_TRUST_AUDIT

**Task:** `MOODIFY_DESKTOP_TRUST_CHAIN_001`
**Date:** 2026-10-05
**Scope:** `.github/workflows/desktop-release.yml`, `.github/workflows/desktop-sign.yml`,
`moodify-desktop/package.json`(electron-builder), `moodify-desktop/scripts/*`
**Nature:** 只读审计 + 结论。事实以本文件为准；计划见同目录另外三份文档。

> 目录说明：任务书写的是 `docs/release/`，本仓库既有约定是 `docs/releases/`
> （已存在 `MOODIFY_STUDIO_1_0_RC1.md` 等）。为不制造第二个同类目录，采用既有
> `docs/releases/`。文件名为任务书指定的四个。

---

## 1. 审计问题与答案

任务书要求回答 7 个问题。以下是审计时（本任务开始前）的状态。

### Q1. `desktop-release.yml` 当前在哪里 build？

**修复前：是的，它自己 build。** 它内联了完整的构建步骤（`setup-node` → `npm ci` →
`npm test` → `npm run dist:win`），并使用自己的 `dist-electron/` 产物。

**修复后：不 build。** 它只有 `build`（调用 reusable workflow）与 `publish` 两个 job，
自身不执行任何 `npm` / `electron-builder` 命令。

### Q2. `desktop-sign.yml` 当前在哪里 build？

它在自己的 `build` job 里 build（`moodify-desktop` 工作目录，`npm ci` → `npm test` →
`npm run dist:win`），并把**未签名**产物上传为 `desktop-unsigned`。
这是本任务引入的文件，因此它从建立起就是唯一的构建入口。

### Q3. 是否发生重复 build？

**修复前：是，而且这是最严重的缺陷。** 两个 workflow 都会 `npm run dist:win`：

```text
desktop-release.yml  ──npm run dist:win──▶  dist-electron/  ──▶ 直接发布
desktop-sign.yml     ──npm run dist:win──▶  dist-electron/  ──▶ 签名（尚未启用）
```

两条路径各自产出一份字节序列。当时**恰好**只有前者在发布，所以没有立刻造成
「发布未签名产物」，但结构上「签名的那一份」与「发布的那一份」是两次独立构建的结果——
这正是任务书 §1 明令禁止的 `Build A → Sign A → Build B → Publish B`。

**修复后：不存在重复 build。** `desktop-release.yml` 通过
`uses: ./.github/workflows/desktop-sign.yml` 调用，构建只发生一次。

### Q4. SignPath 接收哪个 artifact？

`desktop-sign.yml` 的 `build` job 上传的 `desktop-unsigned` artifact
（仅 `Moodify_Studio_*_Setup_x64.exe` 与 `Moodify_Studio_*_Portable_x64.exe`）。
`sign` job 下载它，提交签名，输出到 `signed/`。

> ⚠️ 该步骤的具体输入名（尤其 `github-artifact-id` 的取值形态）**必须以 SignPath
> 为 Moodify 生成的项目文档为准**。我们尚未获得账户，无法离线验证。这一条被明确标记为
> 外部依赖，不是实现缺口。

### Q5. GitHub Release 最终发布哪个 artifact？

`desktop-signed` artifact。`publish` job 下载它到 `release/`，发布
`release/*.exe` + `RELEASE_MANIFEST.json` + `SIGNATURE_FACTS.json` + `SHA256SUMS.txt`。

### Q6. 最终发布的文件是否就是 SignPath 返回的 signed artifact？

**修复后：是，且这是被强制的。** `sign` job 的 "Stage the artifacts" 步骤规则：

```text
签名已启用（SIGNPATH_ENABLED=true）⇒ final 只能来自 signed/；
                                     signed/ 为空即整个 job 失败。
签名未启用                        ⇒ final = unsigned，且清单如实报告 code_signed=false。
```

**修复前：不是被强制的。** 原逻辑是「signed 目录为空就回退复制 unsigned」——
SignPath 失败或产物为空时，流水线会静默把未签名字节当作最终产物继续走完证明与发布。
这是本审计发现的两个真实缺陷之一（见 §3）。

### Q7. signed / unsigned artifact 是否可能同时进入 release？

**不会。** `final/` 目录在任一时刻只包含一套产物，且发布只 glob `release/*.exe`。
unsigned 产物留在 `desktop-unsigned` artifact 中，从不进入发布路径。
`desktop-release.yml` 额外断言：`final` 中可执行文件数量必须**等于**本次构建的数量，
多一个少一个都失败。

---

## 2. 修复后的依赖图

```text
push tag desktop-v*  ──┐
pull_request (paths) ──┤
workflow_dispatch ─────┘
                       │
                       ▼
        desktop-release.yml
        ├── job: build   ──uses──▶ desktop-sign.yml
        │                            ├── job: build    (唯一构建入口)
        │                            │     npm ci → npm test → npm run dist:win
        │                            │     断言打包内容（含深度链路脚本）
        │                            │     upload artifact: desktop-unsigned
        │                            └── job: sign     (PR 上跳过)
        │                                  下载 desktop-unsigned
        │                                  记录 unsigned 指纹
        │                                  [SignPath 签名]  ← 外部
        │                                  Stage final（签名启用时禁止回退）
        │                                  验签 → SIGNATURE_FACTS.json
        │                                  RELEASE_MANIFEST.json
        │                                  SHA256（针对最终字节）
        │                                  Attestation（针对最终字节）
        │                                  upload artifact: desktop-signed
        └── job: publish (仅 tag)
              下载 desktop-signed
              Release guard（产物数 / SHA256 逐个重算 / 签名声明一致性）
              仅此一处产生 GitHub Release
```

失败传播：`publish` 声明 `needs: [build]`。任一上游 job 失败，`publish` 不会运行，
因此**任何阶段失败都不会产生 Release**。

---

## 3. 审计发现的两个真实缺陷（均已修复）

### 缺陷 A — 未签名产物可能被当作最终产物（静默回退）

```powershell
# 修复前
if (-not (Get-ChildItem -Path final -File -ErrorAction SilentlyContinue)) {
  Copy-Item -Path unsigned/* -Destination final -Force
  Write-Host "final = unsigned artifacts (no signing was performed)"
}
```

后果链：SignPath 超时 / artifact-configuration 配错 / 策略未批准
→ `signed/` 为空 → 回退到未签名 → 证明与校验和照常生成
→ **一个未签名的安装包以「官方 Windows 发布」的身份出现在 Release 里**，
而 `code_signed` 会被验签步骤如实写成 `false`——但**没有任何东西阻止它被发布**。

这正是任务书 §1 禁止的 `Publish B`，只不过伪装成了「签名服务暂时不可用」。

修复：签名启用时 `signed/` 为空即 `throw`；并新增
「final 可执行文件数必须等于 unsigned 数」的数量守恒断言。

### 缺陷 B — 校验和覆盖了不该覆盖的文件

```powershell
# 修复前：final 下所有文件 + SIGNATURE_FACTS.json
$paths = (Get-ChildItem final -File | Where-Object { $_.Name -ne 'SHA256SUMS.txt' }).FullName
$paths += (Join-Path $PWD 'final/SIGNATURE_FACTS.json')
```

`SHA256SUMS.txt` 的语义是「这些二进制的指纹」。混入描述性 JSON 后，
用户无法判断哪一行才是安装包，`sha256sum -c` 也会因多余条目而难以使用。

修复：只覆盖最终可执行文件（`.exe` / `.msix` / `.msi`），并按名称排序保证确定性。

---

## 4. 其他审计结论（无缺陷，如实记录）

| 项 | 结论 |
|---|---|
| Release Manifest 的 `code_signed` | 由 `verify-signature.ps1` **实测**得出，不是手写常量 |
| SignPath secrets | 全部走 GitHub Secrets/Variables，仓库内**不存在**任何密钥、证书、keystore |
| `desktop-sign.yml` 的权限 | `build` job 只读；`sign` job 才持有 `id-token` / `attestations` |
| 但经 reusable workflow 调用时 | 两个权限会覆盖整条链（含跑 `npm ci` 的 build）——GitHub 不允许被调用 workflow 超出调用方授权。这是复用换来的**真实让步**，已记录在 `desktop-release.yml` 注释里 |
| Attestation 顺序 | `BUILD → SIGN → ATTEST → CHECKSUM`。证明与校验和都针对**最终字节**，签名不会在它们之后发生 |
| Release 正文 | 由 `.github/release-notes/desktop-provenance.md` 提供，只含可验证事实，无营销文案 |
| MSIX | **不在本发布链中**，保持独立 spike，见 `MSIX_COMPATIBILITY.md` |

---

## 5. 尚未消除的外部依赖（不是实现缺口）

```text
BLOCKED_BY_EXTERNAL_CONFIGURATION
  SignPath Foundation 项目审批（organization id / project slug / policy slug / api token）
  → 未获得之前，vars.SIGNPATH_ENABLED 保持未设置
  → 此时产物如实为未签名，清单 code_signed=false，不声称已签名
```

**关键区分：** 这不是「实现不完整」。仓库侧已经 ready：
workflow 已接好、守卫已就位、失败会阻断发布、验签与证明已实测通过。
缺的是一次**人类在第三方服务上的注册动作**。
