# 代码签名方案 — CODE-SIGNING-PLAN-001

**Date:** 2026-10-05
**Status:** 方案（DEFINED）。**当前没有任何签名证书**——本文描述的是怎么拿到，不是已经拿到。
**Authority:** 本文件是实施方案，不是 Canon；产品对外身份相关部分标 `HUMAN_DECISION_REQUIRED`。

---

## 0. 现状（事实，不是计划）

```text
签名证书              无
code_signed           由实测得出（见下），不是手写常量
产物                  未签名 NSIS 安装包 + 未签名 portable exe + SHA256SUMS
来源证明（attestation）未接线 → 本方案接入（不需要证书，立即可用）
```

用户装这些产物时看到的是 **SmartScreen「Windows 已保护你的电脑」**。
这不是 bug，是「未知发布者」的正常表现。

---

## 1. 先把两件不同的事分开

这是本方案最重要的一节。混淆这两件事，会导致「我们签名了，所以用户不再看到警告」这类
错误预期，或者「我们加了证明，所以二进制被信任了」这类错误结论。

| | **代码签名（Authenticode）** | **来源证明（attestation）** |
|---|---|---|
| 回答什么 | 「这个二进制的发布者是谁，有没有被篡改」 | 「这个字节序列由哪次 commit、哪个 workflow 产出」 |
| 谁验证 | Windows / SmartScreen / 用户双击时 | 会去看证明的人或自动化（`gh attestation verify`） |
| 需要证书吗 | **需要** | **不需要** |
| 消除 SmartScreen 警告吗 | 最终会（需累积信誉），EV 证书曾可立即生效 | **完全不会**。它是给审计者看的，不是给 Windows 看的 |
| 成本 | 证书成本（见 §2） | $0 |

**结论：attestation 不能替代代码签名。** 它能做的是让「这个包确实来自 huliye24/moodify-ai
的某次构建」变成可独立验证的事实——这对开源项目的发布可信度是真实的提升，
但它解决不了「用户双击时看到一个吓人的警告」。

---

## 2. 四条路的真实代价

| 方案 | 钱 | 能解决 SmartScreen 吗 | 发布者身份是谁 | 对我们的主要代价 |
|---|---|---|---|---|
| **A. SignPath Foundation**（免费 OSS 签名） | **$0** | 会，但需时间累积信誉；头几个月仍可能有警告 | **SignPath Foundation**（不是 Moodify） | 必须申请并通过审核；签名要经过 SignPath 的服务；发布者名不是我们 |
| **B. Microsoft Store（MSIX）** | 一次性注册费（历史上 $19；**需核实当前政策**） | **是，彻底解决**——从 Store 安装不经 SmartScreen | **Microsoft 代签**，显示为 Store 应用 | 必须过 Store 政策审核；MSIX 沙箱对「在用户机器上装 Python 运行时」这件事是否可行**尚未验证**（见 §5） |
| **C. Azure Trusted Signing** | 约 $10/月 | 会（OV 级）；信誉仍需累积 | **我们自己的名字** | 不是 $0；个人开发者资格曾有额外要求（有报告称需 Entra ID P2/Governance，**需核实**） |
| **D. 购买 EV/OV 证书** | 约 $200–600/年 | EV 传统上立即生效 | 我们自己的名字 | 最贵；EV 的即时信誉政策近年也变过 |

用户提议的 A + GitHub Actions + attestation + Store MSIX **在现金成本上确实是 $0 路线**
（Store 的注册费除外，且可能已免）。它的问题不是钱，是下面三点。

### 2.1 缺口一：SignPath 免费档的发布者不是 Moodify

免费 OSS 签名用 SignPath Foundation 的证书，最终签名主体是 SignPath Foundation，
不是 Moodify。用户看到的发布者会是基金会而不是我们。
**这是一个产品身份决策，不是工程细节** → `HUMAN_DECISION_REQUIRED`（见 §6）。

### 2.2 缺口二：两套分发渠道 = 两个不同的产物

MSIX（Store）与 NSIS/portable（官网/GitHub Release）是**两个不同的包**、两条不同的
构建路径。如果两条路径各有各的构建，就会出现「Store 那版是新的、GitHub 那版是旧的」
这类问题。本方案的处理方式是**只有一份构建实现**（见 §4），MSIX 作为同一份产物的
另一种打包目标接进来，而不是另起一条链。

### 2.3 缺口三：Store 与「装 Python 运行时」的冲突尚未验证

Moodify Studio 的深度处理依赖**外部 Python 运行时**（`.venv-audio` / `.venv-demucs` /
`.venv-basic-pitch`，见 `docs/reports/2026-10-05_DEEP_PROCESSING_GAP_SCAN.md`）。
MSIX 默认运行在轻量沙箱中。虽然 MSIX 有 `runFullTrust` 能力、Microsoft 也发布了
[Electron 打包成 MSIX 的官方指引][ms-electron]，但「应用运行期间在用户目录里创建包含
本机可执行文件的 Python 虚拟环境」这件事是否被 Store 政策接受，**我没有验证**。
**在验证之前不得把 Store 方案写成已可用。**

[ms-electron]: https://learn.microsoft.com/en-us/windows/apps/dev-tools/winapp-cli/guides/electron-packaging

---

## 3. 本仓库已经做了什么（不需要任何证书）

已接入 `actions/attest-build-provenance@v2`（`.github/workflows/desktop-sign.yml`）：

```bash
# 任何人拿到发布产物后可以独立验证来源，不需要信任我们：
gh attestation verify Moodify_Studio_1.0.0-rc.1_Setup_x64.exe --repo huliye24/moodify-ai
```

这一条**现在就能用**，且与签名完全独立。它使我们能在「还没签名」的阶段就提供
可验证的构建来源——比一个 `code_signed: false` 的清单强得多。

同时新增 `moodify-desktop/scripts/verify-signature.ps1`：签名是否**真的**有效由它实测，
产物里的 `code_signed` 来自它的输出，不是手写常量。它检查四件事，缺一不可：

1. 有签名（判据是签名者证书存在，**不是** `Status -ne 'NotSigned'`——
   实测一个非 PE 文件的 Status 是 `UnknownError`，用字符串比较会把它算成已签名）
2. 状态是 `Valid`（证书链可信且未被篡改）
3. **有时间戳**（否则证书到期后，用户手里的包会突然变成「签名无效」）
4. 签名者与期望发布者一致（可选但**强烈建议**：用别人的证书签出来的包同样是 `Valid`）

---

## 4. 落地顺序

### 第 0 步（已完成，$0，无依赖）

- ✅ 来源证明接入
- ✅ 验签脚本 + 实测签名事实写入发布清单
- ✅ 单一构建入口（`desktop-sign.yml`），发布流程复用而不是各建一次
- ✅ 打包内容断言（缺脚本 / 测试脚本泄漏进产品包都会失败）

### 第 1 步：申请 SignPath Foundation（$0）

需要准备的材料（这些是申请表的实质内容）：

- 项目主页与**公开**仓库：`https://github.com/huliye24/moodify-ai`（已确认 PUBLIC）
- OSI 认可的开源许可：**GPL-3.0-only**（已确认，`licenseInfo.key = gpl-3.0`）
- 项目用途说明、下载量/用户规模、为什么需要签名
- 同意在构建与发布流程中遵守其要求（包括在项目里标注签名由 SignPath Foundation 提供）

**申请前必须由人决定**：是否接受「发布者显示为 SignPath Foundation」（§2.1）。

通过后需要的配置（届时按 SignPath 生成的文档核对具体名）：

| 类型 | 名称 | 来源 |
|---|---|---|
| Secret | `SIGNPATH_API_TOKEN` | SignPath 控制台 |
| Secret | `SIGNPATH_ORGANIZATION_ID` | SignPath 控制台 |
| Secret | `SIGNPATH_PROJECT_SLUG` | SignPath 控制台 |
| Variable | `SIGNPATH_SIGNING_POLICY_SLUG` | SignPath 控制台 |
| Variable | `SIGNPATH_ARTIFACT_CONFIGURATION_SLUG` | SignPath 控制台 |
| Variable | `SIGNPATH_ENABLED` = `true` | 打开签名步骤 |
| Variable | `SIGNATURE_EXPECTED_PUBLISHER` | 期望的签名主体子串 |

打开 `SIGNPATH_ENABLED` 之后，**未签名会变成硬失败**——这正是想要的严格性。

### 第 2 步：验证 MSIX 可行性（$0，纯验证）

在做任何 Store 投入之前先回答两个问题：

1. electron-builder 当前是否仍支持 `appx` 目标，或是否应改用 Microsoft 的
   [winappcli / 官方 MSIX 指引][ms-electron]？（**需核实**）
2. 在 MSIX 沙箱下，应用能否创建并运行外部 Python 运行时？如果不行，
   是否接受「Store 版只做 PLAY（播放/审听），不做 PROCESS（深度处理）」？

第 2 问是一个**产品边界决策**：一个只能播放、不能完成歌曲的 Store 版，
是否符合「一个 Core、两个接口」的定位 → `HUMAN_DECISION_REQUIRED`。

### 第 3 步（可选，若希望发布者是我们自己的名字）

Azure Trusted Signing。先核实个人开发者资格与是否需要额外 Entra ID 许可，再决定。

---

## 5. 验证清单（每条都必须能跑出来，不接受「应该可以」）

```text
[ ] `gh attestation verify <exe> --repo huliye24/moodify-ai` 对发布产物返回成功
[ ] RELEASE_MANIFEST.json 的 code_signed 与实际签名状态一致（由脚本实测）
[ ] 未签名时：verify-signature.ps1 默认**失败**（不是警告）
[ ] 未签名时：SIGNPATH_ENABLED=true 让构建失败（严格性生效）
[ ] 有签名时：Status=Valid 且 timestamped=true
[ ] 有签名时：signer_subject 与 SIGNATURE_EXPECTED_PUBLISHER 匹配
[ ] 打包产物内含 model_separate.py / roundtrip.py / structure.py，且不含 test-*.js
[ ] 只有一份构建实现：desktop-release.yml 不再自行 npm run dist:win
```

---

## 6. HUMAN_DECISION_REQUIRED

1. **是否接受代码签名的发布者显示为 `SignPath Foundation` 而不是 `Moodify`？**
   （免费档的固有条件；要显示自己的名字就需要 Azure Trusted Signing 或购买证书）
2. **是否进入 Microsoft Store？** 若是，需先回答 §4 第 2 步的第 2 问——
   Store 版是否允许「只播放、不完成」，或接受为 Store 版单独维护一份受限能力。
3. **是否需要 Windows 之外的分发渠道？** macOS 的公证（notarization）是另一套
   （Apple Developer Program 年费），本方案未覆盖。

---

## 7. 参考

- [Windows 应用的代码签名选项（Microsoft）](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options)
- [将 Electron 应用打包为 MSIX（Microsoft）](https://learn.microsoft.com/en-us/windows/apps/dev-tools/winapp-cli/guides/electron-packaging)
- [GitHub artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations)
- [SignPath Foundation 条款](https://signpath.org/terms.html)

> 本文件写作时无法从该环境访问上述站点（DNS 解析到非公网地址），因此**版本号、
> 价格与政策均需在实施时核实**。凡是标「需核实」的地方都不得当成已确认事实使用。
