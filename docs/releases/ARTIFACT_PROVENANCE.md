# Artifact Provenance — ARTIFACT_PROVENANCE

**Task:** `MOODIFY_DESKTOP_TRUST_CHAIN_001`
**Scope:** 一次 Windows 发布里，用户能独立验证的四件事与它们各自的边界。

---

## 1. 四层证据，四个不同的问题

这四样东西经常被混为一谈。逐条分开：

| 层 | 产物 | 回答什么问题 | 谁验证 |
|---|---|---|---|
| **来源** | GitHub Artifact Attestation | 这个字节序列由**哪次 commit、哪个 workflow** 产出？ | `gh attestation verify` |
| **完整性** | `SHA256SUMS.txt` | 我下载到的字节与发布者上传的**是否是同一批**？ | `sha256sum -c` |
| **发布者** | Authenticode 签名 | **谁**声明发布这个二进制，是否被篡改？ | Windows / `Get-AuthenticodeSignature` |
| **出处** | `RELEASE_MANIFEST.json` + Source commit | 这一版对应源码的哪个状态？ | 人工对照 |

**关键边界：**

```text
Attestation ≠ Code signing
```

- Attestation 由 GitHub 签发，**不需要证书**，但它**不会让 Windows 信任这个二进制**。
  它面向的是「会去看证明的人或自动化」。
- Code signing 由证书签发，它才是 Windows 用来判断发布者的依据。
- 两者互补：签名说「谁发布」，证明说「从哪来」。缺任何一个都留有空白。

**并且两者都不表示「安全」。** 它们不承诺没有缺陷，也不是「Microsoft 认证」。
任何这类说法都无法严格证明，因此不写。

---

## 2. 顺序：为什么必须是 BUILD → SIGN → ATTEST → CHECKSUM → RELEASE

```text
BUILD
  ↓
SIGN          ← 这一步**改变字节**
  ↓
ATTEST        ← 必须针对签完的字节
  ↓
CHECKSUM      ← 必须针对签完的字节
  ↓
RELEASE
```

签名会修改 PE 文件（写入签名与时间戳），因此签名前后的 SHA-256 **必然不同**。
如果先对未签名文件算校验和或做证明，再签名，那么：

- 证明指向的字节**不是用户下载到的字节** → 证明失效（且是静默失效，最坏的一种）
- 校验和与用户实际文件**对不上** → 用户会以为下载被篡改

本仓库的实际顺序由 `desktop-sign.yml` 的步骤顺序保证，且 `publish` 只消费
`desktop-signed` 这个 artifact：

```text
Build          npm ci → npm test → npm run dist:win
Sign           SignPath（未配置时显式跳过并说明）
Stage final    签名启用时禁止回退到未签名字节
Verify         verify-signature.ps1 → SIGNATURE_FACTS.json（实测 code_signed）
Manifest       RELEASE_MANIFEST.json
Checksum       SHA256SUMS.txt ← 针对 final/ 里的**最终**可执行文件
Attest         actions/attest-build-provenance ← subject-path: final/*.exe
Upload         desktop-signed
        ↓
Publish        Release guard → GitHub Release
```

---

## 3. 用户侧验证手册

### 3.1 完整性

```bash
sha256sum -c SHA256SUMS.txt
# Windows PowerShell:
Get-FileHash .\Moodify_Studio_*_Setup_x64.exe -Algorithm SHA256
# 与 SHA256SUMS.txt 中对应行比对
```

`SHA256SUMS.txt` **只包含被发布的二进制**。描述性的
`RELEASE_MANIFEST.json` / `SIGNATURE_FACTS.json` 不在其中——
它们是佐证，不是被校验的对象。这样 `sha256sum -c` 可以直接使用，
用户也不必自己判断哪一行才是安装包。

### 3.2 来源（本文的重点）

```bash
gh attestation verify Moodify_Studio_1.0.0-rc.1_Setup_x64.exe \
  --repo huliye24/moodify-ai
```

成功意味着：GitHub 的透明日志里存在一份记录，把**你手上这个文件的 SHA-256**
与**某次具体的 workflow 运行及其 commit** 绑定在一起，且该记录由 GitHub 的
签名密钥签发。无需信任 Moodify 的服务器。

### 3.3 发布者

见 `WINDOWS_CODE_SIGNING.md` §3。

### 3.4 出处

```bash
# RELEASE_MANIFEST.json 里的 commit 字段
git -C <your-clone> log -1 <commit>
git -C <your-clone> rev-parse HEAD
```

---

## 4. Release 资产清单（内容与作用）

| 文件 | 是什么 | 是否被 SHA256SUMS 覆盖 |
|---|---|---|
| `Moodify_Studio_<version>_Setup_x64.exe` | NSIS 安装包 | ✅ |
| `Moodify_Studio_<version>_Portable_x64.exe` | 便携版 | ✅ |
| `SHA256SUMS.txt` | 上述二进制的 SHA-256 | — （自身） |
| `RELEASE_MANIFEST.json` | version / commit / 实测签名事实 / 产物指纹 | ❌ |
| `SIGNATURE_FACTS.json` | 验签步骤的原始输出 | ❌ |

### 4.1 用户应该只有**一个**官方 Windows 安装包

不发布 `Moodify.exe` 与 `Moodify-signed.exe` 两个并列文件。
**是否签名是供应链属性，不是文件名属性。**
用户看到一个名字，看不到「签名版 / 未签名版」的区别——这正是我们要的效果：
签名状态通过验证工具查询，而不是通过文件名猜测。

### 4.2 `RELEASE_MANIFEST.json` 的诚实字段

```json
{
  "code_signed": false,
  "signature_valid": false,
  "signature_timestamped": false,
  "publisher_checked": false,
  "signer_subject": null
}
```

这些值由 `verify-signature.ps1` **实测**得出，不是硬编码。
在 SignPath 接通前它们如实为 `false`——**这就是「未签名」的正确表达方式**，
而不是靠一句「即将支持签名」的说明文字。

`publisher_checked: false` 表示本次**没有**校验签名者身份（因为还没有签名者）。
它不是「发布者校验通过」。

---

## 5. 当前状态

```text
Attestation:   ENABLED   ✅（不需要证书，已接入）
SHA256:        ENABLED   ✅（针对最终字节）
Signature:     NOT CONFIGURED
               BLOCKED_BY_EXTERNAL_CONFIGURATION
               = SignPath Foundation 项目审批未完成
```

**关键区分：** 签名未生效**不是**实现缺口。仓库侧的接线、守卫、验签、证明
均已就位并实测；缺的是一次人类在第三方服务上的注册动作。
在此之前，产物如实标记为未签名，不声称已签名。
