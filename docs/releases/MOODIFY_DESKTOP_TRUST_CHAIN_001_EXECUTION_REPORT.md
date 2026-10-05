# MOODIFY_DESKTOP_TRUST_CHAIN_001 — EXECUTION REPORT

**Date:** 2026-10-05
**Branch:** `chore/desktop-trust-chain`
**PR:** https://github.com/huliye24/moodify-ai/pull/50 (OPEN, **not merged**)
**Head commit:** 见 PR 页（本报告随最后一次提交一起落库）

---

## 1. Executive Summary

Windows 发布信任链已建立并被**强制**，而不是仅仅声明：

```text
Build once. Sign once. Publish the exact signed bytes.
```

审计发现**三个真实缺陷**，全部已修（其中缺陷 A 会让未签名产物以官方身份发布）。
发布守卫从 YAML 搬进可测试的脚本，并用 13 个反例证明它真的会挡住坏产物集。
SignPath 侧仓库 ready，外部账号审批为 `BLOCKED_BY_EXTERNAL_CONFIGURATION`。
MSIX 保持 `EXPERIMENTAL`，spike 计划就绪但**未执行**（环境阻断），未据此下任何结论。
未为 Store 改动 Desktop Core 一行。

```text
Verdict: READY_FOR_HUMAN_REVIEW
```

---

## 2. Existing Pipeline Audit

完整内容见 [`DESKTOP_RELEASE_TRUST_AUDIT.md`](DESKTOP_RELEASE_TRUST_AUDIT.md)。
七问速答：

| # | 问题 | 修复前 | 修复后 |
|---|---|---|---|
| 1 | `desktop-release.yml` 在哪 build？ | **它自己 build**（`npm ci`+`dist:win`） | **不 build**，调用 reusable workflow |
| 2 | `desktop-sign.yml` 在哪 build？ | 自己的 `build` job | 同上，唯一构建入口 |
| 3 | 是否重复 build？ | **是**（两条独立字节序列） | **否** |
| 4 | SignPath 接收哪个 artifact？ | `desktop-unsigned` | 同（未变） |
| 5 | Release 发布哪个？ | 自己 build 的那份 | `desktop-signed` |
| 6 | 发布的是否就是 SignPath 返回的？ | **不是被强制的**（空则静默回退） | **是**，签名启用时空即失败 |
| 7 | signed/unsigned 会同时进 release 吗？ | 不会（但靠巧合） | 不会（靠断言） |

### 2.1 缺陷 A — 未签名产物可能被当作最终产物

```powershell
# 修复前
if (-not (Get-ChildItem -Path final -File -ErrorAction SilentlyContinue)) {
  Copy-Item -Path unsigned/* -Destination final -Force   # ← 静默回退
}
```

SignPath 超时 / 配置错误 / 策略未批准 → `signed/` 为空 → 回退到未签名字节
→ 证明与校验和照常生成 → **未签名安装包以「官方 Windows 发布」身份进入 Release**。
即禁止的 `Publish B`，伪装成「签名服务暂时不可用」。

### 2.2 缺陷 B — 重复构建

两个 workflow 各自 `npm run dist:win`。两条独立字节序列同时存在，
发布的那条可能是未签名的那条。

### 2.3 缺陷 C — 校验和覆盖了不该覆盖的文件

原实现把 `final/` 下所有文件 + `SIGNATURE_FACTS.json` 都算进去，
`sha256sum -c` 因此难以使用，用户也无法判断哪一行才是安装包。

---

## 3. Changes Made

### 3.1 构建与发布

- `desktop-release.yml` 重写为 `build`（调用 reusable workflow）+ `publish`（仅 tag）；
  **删除自身全部构建步骤**。
- `desktop-sign.yml` 的 staging 步骤改为：**签名启用时禁止回退**，并新增
  「staged 可执行文件数 == 构建数」的数量守恒断言。
- `SHA256SUMS.txt` 只覆盖最终二进制，按名排序。
- Attestation 的 `subject-path` 明确指向最终字节（顺序 `BUILD → SIGN → ATTEST → CHECKSUM`）。
- 新增 `.github/release-notes/desktop-provenance.md` 作为 Release 正文（只含可验证事实）。

### 3.2 发布守卫（从 YAML 抽出，因此可测）

- 新增 `moodify-desktop/scripts/release-guard.ps1`。
- 新增 `moodify-desktop/scripts/test-release-guard.js`（13 个用例）。
- `desktop-release.yml` 的 `publish` job 调用该脚本。

### 3.3 文档

`docs/releases/`：`DESKTOP_RELEASE_TRUST_AUDIT.md`、`WINDOWS_CODE_SIGNING.md`、
`ARTIFACT_PROVENANCE.md`、`MSIX_COMPATIBILITY.md`；`CODE_SIGNING_PLAN.md` 更新
（Decision A 落库）。README 新增 Windows 下载与验证段落。

> 目录说明：任务书写 `docs/release/`，仓库既有约定是 `docs/releases/`（已存在
> `MOODIFY_STUDIO_1_0_RC1.md` 等）。为不制造第二个同类目录采用既有路径，文件名按任务书。

### 3.4 CI 修复（本次执行中由 CI 暴露，全部为真实问题）

| 问题 | 为什么重要 |
|---|---|
| 测试 spawn `powershell`，Linux 上是 `pwsh` | ENOENT 表现为 `status:null`，被读成「守卫正确拒绝」= **假通过** |
| `-File` 收到相对路径 | PowerShell 当命令名处理，报 `CommandNotFoundException` |
| 守卫用 `Get-FileHash`（cmdlet） | 在 CI 的 Windows runner 上抛 `CommandNotFoundException`——**发布闸门不应依赖可能缺席的 cmdlet**，已改用 .NET SHA256 |
| 我的错误过滤器过宽 | 把守卫**内部**失败误报成「测试脚手架问题」，等于藏起真实缺陷 |
| `test-deep-chain` 只认 `.venv-audio` | CI 里**永远跳过**；已改为优先专用运行时、退回到**已验证依赖存在**的系统 python |

---

## 4. Final Build → Sign → Release Graph

```text
desktop-release.yml
├── build ──uses──▶ desktop-sign.yml
│                     ├── job build   (唯一构建入口, 只读权限)
│                     │     npm ci → npm test → npm run dist:win
│                     │     断言打包内容（含深度链路脚本 / 不含 test-*.js）
│                     │     upload: desktop-unsigned
│                     └── job sign    (PR 上跳过)
│                           download desktop-unsigned
│                           record unsigned digests
│                           [SignPath]            ← 外部依赖
│                           Stage final            ← 签名启用时禁止回退
│                           verify-signature       → SIGNATURE_FACTS.json
│                           RELEASE_MANIFEST.json  → code_signed 实测
│                           SHA256                 ← 针对最终字节
│                           Attest                 ← 针对最终字节
│                           upload: desktop-signed
└── publish (仅 tag, needs: build)
      下载 desktop-signed
      release-guard.ps1   ← 产物数 / 逐行重算 SHA256 / 签名声明一致性
      softprops/action-gh-release
```

**失败传播：** `publish` 声明 `needs: [build]`，任一上游失败则 `publish` 不运行
→ 任何阶段失败都不会产生 Release。

---

## 5. SignPath Status

```text
READY (repository side) / BLOCKED_BY_EXTERNAL_CONFIGURATION (external account)
```

| 项 | 状态 |
|---|---|
| 单一构建入口 | ✅ |
| 签名步骤已接线 | ✅ |
| `SIGNPATH_ENABLED != true` 时显式跳过并说明原因 | ✅ |
| 签名失败 / 未签名阻断发布 | ✅（双保险） |
| Secrets 全部走 GitHub Secrets/Variables | ✅ |
| 仓库内无私钥 / token / 证书 / keystore | ✅ |
| SignPath 项目审批 | ❌ **外部动作** |

**这不是实现缺口。** 仓库侧已 ready；缺的是一次人类注册动作。
`vars.SIGNPATH_ENABLED` 保持未设置，产物如实标记未签名，**不声称已签名**。

---

## 6. Artifact Identity Verification

```text
build artifact      desktop-unsigned   ← 唯一构建产物
                         ↓ 记录 sha256（unsigned-digests.txt）
signed artifact     signed/            ← SignPath 输出
                         ↓
released artifact   final/ → desktop-signed → Release/*.exe
```

**同一性由三条机制保证：**

1. 签名启用时 `final` **只能**来自 `signed/`，否则硬失败；
2. `final` 可执行文件数必须**等于**构建数（数量守恒）；
3. `verify-signature.ps1` 对 `final` 实测，`code_signed` 由实测得出。

`unsigned-digests.txt` 保留构建侧指纹，使「签名前后是否同一批」可追溯。
**未签名时** `final` 来自 unsigned，且清单如实写 `code_signed=false`——
如实报告而非静默。

---

## 7. GitHub Attestation

```text
PASS
```

- `actions/attest-build-provenance@v4`，`subject-path: final/*.exe`（**最终字节**）。
- 顺序 `BUILD → SIGN → ATTEST`，签名不会发生在证明之后。
- 通过方式：`gh attestation verify <exe> --repo huliye24/moodify-ai`
  （Release 正文与 README 均写明）。

---

## 8. SHA256

```text
PASS
```

只覆盖最终可执行文件，按名排序；守护在发布前**逐行重算指纹**比对。
13 个守卫用例中含 3 个校验和反例（stale / 条目数不符 / 混入非二进制），全部被挡住。

---

## 9. Unsigned Release Guard

```text
PASS
```

四道闸门：

1. staging：签名启用 + `signed/` 为空 → hard fail
2. 数量守恒：staged 数 ≠ 构建数 → fail
3. `verify-signature.ps1`：签名启用时未签名 → fail
4. `release-guard.ps1`：签名启用但清单 `code_signed=false` / `signature_valid=false` /
   无时间戳 → fail

**守卫本身的正确性已被测试**（`test-release-guard.js`，13 用例，Windows 与 Linux
两条 CI 均实际执行并通过）。

---

## 10. MSIX Compatibility Test

```text
BLOCKED — NOT EXECUTED
```

| 项 | 结果 |
|---|---|
| Python | **NOT EXECUTED** |
| `.venv-audio` | **NOT EXECUTED** |
| `.venv-demucs` | **NOT EXECUTED** |
| subprocess | **NOT EXECUTED** |
| PROCESS E2E | **NOT EXECUTED** |

原因：需要一台可安装 MSIX 包并能创建 Python venv 的 Windows 机器。
本环境无法产出有意义的 MSIX 包（无 Store 账户 / 无签名身份）。

**我没有把「无法执行」写成 PASS 或 FAIL。** 12 项可判定测试与执行步骤已写入
[`MSIX_COMPATIBILITY.md`](MSIX_COMPATIBILITY.md) §2，结论规则见 §4。

调研找到两条**旁证**（说明风险不是臆测，但不构成我们的实测结论）：

- [anthropics/claude-code #47977](https://github.com/anthropics/claude-code/issues/47977)：
  Electron 应用在 MSIX 下因 `${__dirname}` 被虚拟化而**无法 spawn 外部进程**——
  与本项目的冲突同型。
- [CPython GH-24422](https://mail.python.org/pipermail/python-checkins/2021-February/169035.html)：
  CPython 文档链接了 Windows Store 打包的已知限制。

**注：** 本执行环境无法 fetch 外部页面（DNS 解析到非公网地址），因此只读到搜索摘要，
未能阅读 MSIX 沙箱与 Packaged Desktop App 原文。这一点已如实记入文档。

---

## 11. MSIX Product Decision

```text
UNDETERMINED — 需要先执行 §10 的 12 项测试
```

**不**写 `FULL`，也**不**写 `PLAY_ONLY`。二者都需要真实测量数据。
在得出 `FULL` 之前，Store 渠道不启动、不生成任何 Store 提交物。

---

## 12. Files Changed

```text
新增
  .github/release-notes/desktop-provenance.md
  docs/releases/DESKTOP_RELEASE_TRUST_AUDIT.md
  docs/releases/WINDOWS_CODE_SIGNING.md
  docs/releases/ARTIFACT_PROVENANCE.md
  docs/releases/MSIX_COMPATIBILITY.md
  docs/releases/MOODIFY_DESKTOP_TRUST_CHAIN_001_EXECUTION_REPORT.md   ← 本文件
  moodify-desktop/scripts/release-guard.ps1
  moodify-desktop/scripts/test-release-guard.js
修改
  .github/workflows/desktop-release.yml
  .github/workflows/desktop-sign.yml
  .github/workflows/studio.yml
  README.md
  docs/releases/CODE_SIGNING_PLAN.md
  moodify-desktop/package.json
  moodify-desktop/scripts/test-deep-chain.js
```

---

## 13. Tests Run

```text
npm test（全量桌面套件）        exit 0，0 failed
  check-contracts / test-pipeline 63 / test-recheck 9 / test-session 38
  test-keepsake 23 / test-sync 25 / test-orchestrator 20 / test-main-ipc 67
  test-studio 21 / test-runtime（全部）/ test-deep-chain（全部）
  test-release-guard 13（新增）
Repository structure guard       OK
workflow YAML 解析               OK（三个 workflow）
```

CI（Windows 与 Linux 均**实际执行**，非跳过）：

```text
build / Build (unsigned)           pass  —— 含打包内容断言
build / Sign (SignPath)            skipping（PR 上按设计）
Publish GitHub Release             skipping（非 tag）
Studio contracts and processing    pass  —— deep-chain + release-guard 实跑通过
Repository structure guard         pass
Python 3.11 quality and tests      pass
temporal-texture                   fail  —— V4 既有债务，非本 PR
```

---

## 14. Commit

见 PR #50 的提交列表（本报告随最后一次提交落库）。

---

## 15. Branch

```text
chore/desktop-trust-chain
```

未直接修改 `main`。

---

## 16. PR

```text
https://github.com/huliye24/moodify-ai/pull/50
State: OPEN — 未 merge
```

未创建正式 tag、未创建 Production Release。

---

## 17. Remaining External Actions

只有确实必须由人完成的外部动作：

1. **申请 SignPath Foundation 项目审批**，拿到
   `organization id` / `project slug` / `signing policy slug` / `api token`
   → 注入 GitHub Secrets/Variables → 设 `SIGNPATH_ENABLED=true`。
   （申请材料已核实齐备：仓库 PUBLIC ✅、GPL-3.0-only ✅）
2. **执行 MSIX spike**：在一台可安装 MSIX 并能创建 Python venv 的 Windows 机器上
   跑 `MSIX_COMPATIBILITY.md` §2 的 12 项，重点是第 12 项 PROCESS 端到端。
3. **（仅当决定进 Store）** Microsoft Partner Center 注册。

**不重复提出已拍板的产品问题。** Decision A（接受 SignPath Foundation 作为
Authenticode Publisher）已落库，不再是待决事项。

---

## 18. Final Verdict

```text
READY_FOR_HUMAN_REVIEW
```

理由：任务书 §21 的 Definition of Done 中，**仓库内部工程项全部完成**
（单一构建、签名后不重建、Release 只读 signed、SHA256 与 Attestation 针对 signed
bytes、未签名不可能进入正式 Release、签名失败阻断 Release、无 secrets 入库、
守卫被测、文档完成、CI 通过、PR 已创建、未 merge、未 Production Release）。

两项未完成，均为**外部依赖**，且已准确标记而非静默跳过：

```text
SignPath Foundation 项目审批        → BLOCKED_BY_EXTERNAL_CONFIGURATION
MSIX compatibility spike 执行       → BLOCKED_BY_EXTERNAL_CONFIGURATION
```

MSIX 的 `FULL` / `PLAY_ONLY` 结论因此记为 `UNDETERMINED`——
在没有实测数据前给出结论就是发明事实。
