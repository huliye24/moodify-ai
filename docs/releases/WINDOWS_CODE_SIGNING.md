# Windows Code Signing — WINDOWS_CODE_SIGNING

**Task:** `MOODIFY_DESKTOP_TRUST_CHAIN_001`
**Status:** 策略已定（Decision A，2026-10-05）。**证书尚未获得**——本文说明怎么拿到与如何验证。

---

## 1. 当前策略

```text
Windows Authenticode publisher = SignPath Foundation
```

即 Windows 属性面板中显示的是 **`SignPath Foundation`**，不是 `Moodify` /
`Rongjing Culture` / `荣景文川`。这是**当前阶段主动接受的产品取舍**，不是待议事项。

依据：

```text
Moodify = GPL-3.0 open source + public GitHub repository + early stage
阶段目标 = 零成本、可验证的发布基础设施
```

现阶段**不购买** OV / EV / 商业代码签名证书。未来具备稳定现金流后再迁移到自有证书
（见 §5）。

---

## 2. 为什么是这个取舍

### 2.1 签名解决的是「谁发布了这个字节」

Authenticode 回答的是发布者身份与字节完整性。用户双击时，Windows 会检查：

```text
有没有签名 → 证书链是否可信 → 字节是否被篡改 → 证书是否在有效期内（含时间戳）
```

对开源早期项目，把发布者身份交给一个**专门为开源项目提供签名服务的基金会**，
比「完全未签名」是实质提升：用户至少能验证这个二进制出自某个受信任的签名机构，
而不是匿名下载。

### 2.2 代价要说清楚

| 代价 | 说明 |
|---|---|
| **发布者不是我们的名字** | 属性面板显示 `SignPath Foundation`。这是免费档的固有条件 |
| **不立即消除 SmartScreen** | 签名让「未知发布者」变成已知发布者，但信誉需要靠下载量累积；新签名的二进制仍可能弹警告一段时间 |
| **签名经过第三方服务** | 每次签名都要把构建产物提交给 SignPath。对我们而言这不构成问题（产物本来就要公开发布），但它是一条真实的外部依赖 |
| **签名策略由对方定义** | 哪些文件被签、如何重打包，由 SignPath 侧的 artifact configuration 决定 |

### 2.3 为什么不用另外两条 $0 路线

| 方案 | 为什么不是现在 |
|---|---|
| **Microsoft Store（MSIX）** | Store 由 Microsoft 代签，确实免费，但它是**另一个分发渠道 + 另一套打包格式**。MSIX 与我们依赖外部 Python 运行时的架构是否相容**尚未验证**（见 `MSIX_COMPATIBILITY.md`）。而且它只覆盖 Store 安装的用户，不覆盖 GitHub 直接下载的用户——后者才是第一官方渠道 |
| **Azure Trusted Signing** | 约 $10/月，不是 $0；且个人开发者资格与是否需要额外 Entra ID 许可**需在实施时核实** |

---

## 3. 验证一个下载的二进制（用户手册）

### 3.1 Windows 属性面板（最直观）

```text
右键安装包 → 属性 → 数字签名
→ 应看到 Signer: SignPath Foundation
→ 选中条目 → 详细信息 → 应显示「此数字签名正常」
→ 时间戳应存在
```

时间戳不是装饰：**没有时间戳的签名会在证书到期后失效**，用户手里的安装包会在某一天
突然变成「签名无效」。我们的验签脚本把「无时间戳」当作**失败**，不是警告。

### 3.2 PowerShell（可脚本化）

```powershell
Get-AuthenticodeSignature .\Moodify_Studio_1.0.0-rc.1_Setup_x64.exe |
  Format-List Status, SignerCertificate, TimeStamperCertificate
```

期望：

```text
Status                 : Valid
SignerCertificate      : CN=SignPath Foundation, ...
TimeStamperCertificate : <非空>
```

`Status` 必须是 `Valid`。`UnknownError` / `NotSigned` / `HashMismatch` 都表示不可信。

### 3.3 仓库自带的验签脚本（CI 与本地同源）

```powershell
pwsh -File moodify-desktop/scripts/verify-signature.ps1 `
  -Path .\Moodify_Studio_*_Setup_x64.exe `
  -ExpectedPublisher "SignPath Foundation"
```

这个脚本是 CI 用来生成 `SIGNATURE_FACTS.json` 的**同一个实现**，它检查四件事：
有签名 / 状态 `Valid` / **有时间戳** / 签名者与期望发布者一致。
第 4 条最容易被忽略——**用别人的证书签出来的包同样是 `Valid` 的**。

> 脚本内含中文注释，因此**必须**以 UTF-8 **带 BOM** 保存。
> Windows PowerShell 5.1 在无 BOM 时按 ANSI(GBK) 读取 `.ps1`，中文会破坏解析，
> 且报错位置（很靠后的 `}`）与真因相距极远。CI 有一步专门断言 BOM 仍在。

---

## 4. 接线状态（仓库侧已 ready）

| 项 | 状态 |
|---|---|
| 单一构建入口 | ✅ `desktop-sign.yml` 是唯一 build 处 |
| 未签名不得发布（签名启用时） | ✅ 双保险：验签步骤失败 + 发布 job 的 release guard |
| 验签脚本 | ✅ 已实测（见 §6） |
| SignPath 步骤 | ✅ 已接好，但 `SIGNPATH_ENABLED != 'true'` 时**显式跳过并说明原因** |
| Secrets | ✅ 全部走 GitHub Secrets/Variables；repo 内无任何密钥/证书/keystore |
| 来源证明 | ✅ 与签名独立，已启用 |

### 4.1 需要的配置（获得审批后）

| 类型 | 名称 | 用途 |
|---|---|---|
| Secret | `SIGNPATH_API_TOKEN` | 提交签名请求 |
| Secret | `SIGNPATH_ORGANIZATION_ID` | SignPath 组织 |
| Secret | `SIGNPATH_PROJECT_SLUG` | 项目 |
| Variable | `SIGNPATH_SIGNING_POLICY_SLUG` | 签名策略 |
| Variable | `SIGNPATH_ARTIFACT_CONFIGURATION_SLUG` | 哪些文件被签、如何重打包 |
| Variable | `SIGNPATH_ENABLED` = `true` | **打开严格性** |
| Variable | `SIGNATURE_EXPECTED_PUBLISHER` | 期望发布者（届时填 `SignPath Foundation`） |

打开 `SIGNPATH_ENABLED` 的**唯一**效果是把「未签名」从「如实记录」变成「硬失败」。
在此之前不应把它设为 `true`，否则每次发布都会失败。

> 具体名称与 `github-artifact-id` 的取值形态**以 SignPath 为 Moodify 生成的项目文档为准**。
> 我们尚未获得账户，无法离线验证这一步——这是 `BLOCKED_BY_EXTERNAL_CONFIGURATION`，
> 不是实现缺口。

---

## 5. 何时切换到自有证书

触发条件（任一）：

```text
1. 有稳定现金流，可以承担年度证书成本
2. 需要对外以公司主体（Rongjing Culture / 荣景文川）名义出现
3. 企业客户 / 采购流程要求我们自己的发布者身份
4. SignPath Foundation 的免费档条件发生变化
```

切换时**不需要改动构建架构**：证书路径同样只影响 `SIGNPATH_ENABLED` /
`SIGNATURE_EXPECTED_PUBLISHER` 两个变量的取值与签名步骤的实现，
`verify-signature.ps1` 的 `-ExpectedPublisher` 改为新主体即可，
release guard 与 attestation 完全不用动。

---

## 6. 本仓库已实测的行为（2026-10-05）

用真实的 Windows 二进制与合成文件验证 `verify-signature.ps1`，五个用例：

| # | 输入 | 期望 | 实际 |
|---|---|---|---|
| 1 | `notepad.exe`（有效签名） | 通过 | ✅ `Status=Valid`，有签名者/颁发者/指纹/时间戳 |
| 2 | 非 PE 文本文件（未签名） | **失败** | ✅ `NOT SIGNED` |
| 3 | `notepad.exe` + `-ExpectedPublisher Moodify` | **失败** | ✅ 报签名者不含 `Moodify` |
| 4 | `notepad.exe` + `-ExpectedPublisher "Microsoft Windows"` | 通过 | ✅ |
| 5 | 未签名 + `-AllowUnsigned` | 通过并标注 | ✅ `unsigned accepted (-AllowUnsigned)` |

用例 2 暴露了实现里一个真实 bug 并已修复：「有没有签名」的判据必须是
**签名者证书是否存在**，而不是 `Status -ne 'NotSigned'`——
非 PE 文件的 `Status` 是 `UnknownError`，用字符串比较会把它算成「已签名」，
从而**跳过错过了未签名分支**。
