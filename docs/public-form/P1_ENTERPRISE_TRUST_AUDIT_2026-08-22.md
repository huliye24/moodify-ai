# P1 公开身份与企业可信度盘点

**日期：** 2026-08-22  
**范围：** Moodify Product Home、荣景文川 Company Home、Web Player、Android 公开下载、GitHub、企业邮箱、法律/备案信息  
**方法：** 仓库只读检查 + 公网 HTTPS/DNS 只读核验 + 本线程已完成变更证据  
**Canon 判定：** `CANON_CHANGE = NO`

## 1. 结论

Moodify 已经跨过了“纯个人项目”的第一道门槛：产品官网有明确产品名、公司主体、企业域名邮箱、隐私页、Play 与 Android 下载入口。但公开体系仍未形成一致的企业身份，主要断点是：

1. **公司官网线上仍是旧身份。** `rongjingwenchuan.com` 线上首页仍将 Moodify 定义为 `Auditory Intelligence Infrastructure`，未展示完整法定公司名称，且线上内容与仓库中的新 Company Home 源文件不一致。
2. **三个公开面尚未收敛。** 产品官网是 `rongjingmusic.com`，播放器仍是易混淆的 `rongjinwenchuan.xyz`，目标 `play.rongjingmusic.com` 尚无可用 TLS/路由证据。
3. **邮箱基础链路已通，但安全和运营未闭环。** MX/SPF 已生效；DKIM/DMARC 缺失；公开地址 `hello@rongjingmusic.com` 的账号存在性与实际收信尚需独立验证。
4. **法律与服务页不完整。** 已有阶段性 Privacy，但未发现 Terms/服务条款、版权/知识产权声明或可核验的 ICP/公安备案展示。
5. **产品交付版本不一致。** 官网稳定下载为 2.0.0，仓库有 3.1.0 发布物，当前 Android 源码显示 2.0.1；3.1.0 公网下载返回 404。

**P1 总体判定：** `PARTIAL — 产品官网的企业信号已建立，公司官网、播放器域名、邮箱安全、法律页和发布权威仍未形成闭环。`

## 2. 公开面盘点

| 公开面 | 应有角色 | 线上实况（2026-08-22） | 状态 | 主要问题 |
|---|---|---|---|---|
| `rongjingmusic.com` | Moodify Product Home | HTTPS 200；首页品牌信念正确；Play、Android 下载、Company、Privacy、Contact 可达；页脚有完整公司名 | **正确 / 局部待改** | 仍公开 `/ear.html`；次级页导航/页脚不完全一致；无 Terms/备案展示 |
| `rongjingmusic.com/contact.html` | 单一企业联系入口 | HTTPS 200；仅展示 `hello@rongjingmusic.com`；完整公司名在页脚 | **正确** | `hello@` 账号是否真实存在并可收信待验证 |
| `rongjingmusic.com/privacy.html` | Moodify 隐私说明 | HTTPS 200；有联系邮箱与公司主体 | **部分正确** | 仍标记 `Phase I statement`；需法务完整性复核 |
| `rongjingmusic.com/ear.html` | Ear 应属内部 | HTTPS 200；可公开访问；Title 直接表述 Moodify Ear | **冲突** | 内部系统被置于产品官网公开路径，削弱单一产品身份 |
| `rongjingwenchuan.com` | 荣景文川 Company Home | HTTPS 200；线上 Title = `Moodify — Auditory Intelligence Infrastructure`；无 canonical；无完整公司名 | **高优先级冲突** | 旧公开身份仍在生产；线上内容与仓库新 Company Home 不一致 |
| `rongjingwenchuan.com/privacy.html` | 公司隐私说明 | 线上返回与旧公司首页相同的标题，无完整公司名 | **冲突 / 部署错位** | 线上 Privacy 路径疑未部署仓库中对应文件 |
| `rongjinwenchuan.xyz` | 过渡 Web Player | HTTPS 200；Title = `Moodify Music`；仓库中已有返回 Product/Company 链接 | **过渡可用** | 域名拼写与公司/产品域名不一致；仍有 Creator/Studio 等非当前主线路由 |
| `play.rongjingmusic.com` | 目标 Web Player | TLS 连接失败；无已验证公网路由 | **缺失** | 目标域名尚未可用，不得宣称迁移完成 |
| Android 公开下载 | 稳定可安装的 Moodify Music | 2.0.0 APK/ZIP HTTP 200；3.1.0 APK HTTP 404 | **可用但权威不一致** | 官网 2.0.0、当前源码 2.0.1、发布物 3.1.0 并存 |
| GitHub | 开源/工程信任入口 | 网站链接个人账号 `huliye24/moodify-ai`；仓库 README 已对齐 Canon | **部分正确** | 个人账号/旧仓库名仍强化“个人项目”信号；组织化迁移需单独决策 |

## 3. 企业信任要素矩阵

| 要素 | 当前证据 | 判定 | 下一步 |
|---|---|---|---|
| 法定公司名 | 产品官网已显示“荣景文川（深圳）科技有限公司” | **已建立** | 同步到 Company Home、Privacy、Terms、App About |
| 企业域名邮箱 | `rongjingmusic.com` MX 指向阿里企业邮箱；SPF 已生效 | **基础可用** | 验证 `hello@` 实际收发；补 DKIM/DMARC |
| 联系入口 | Product Contact 仅保留 `hello@rongjingmusic.com` | **已收敛** | 建立收件人、回复时限与归档责任 |
| Privacy | Product/Company 仓库均有 Privacy 文件 | **部分完成** | 部署 Company Privacy；校验主体、数据、保留和删除表述 |
| Terms / 服务条款 | 公开站点未发现 | **缺失** | 先建立最小适用版，不虚构尚未存在的付费/账户能力 |
| 版权/知识产权声明 | 仅有页脚版权年份；无独立声明 | **不完整** | 明确网站内容、音乐与用户来源的边界 |
| ICP/公安备案 | 公开 HTML 未发现可核验展示 | **待确认** | 由人类提供真实备案状态与号码；未取得前不虚构 |
| 客服运营 | 邮箱账号已创建部分角色，无公开响应承诺 | **尚未建立** | 定义 `hello/support/business/admin/postmaster` 职责与检查频率 |
| 发布权威 | 网站、源码、发布物版本不一致 | **冲突** | 选定唯一公开稳定版，建立校验值与回滚记录 |

## 4. 正确 / 缺失 / 冲突 / 待确认

### 4.1 正确

- 公开主产品已收敛为 Moodify Music / Player。
- Product Home 首屏使用 `Every voice deserves to be heard.`，未用技术管线定义产品。
- Product Home 已展示完整公司名称。
- Product Contact 已收敛为单一 `hello@rongjingmusic.com`。
- 域名邮箱 MX 和 SPF 已在公网生效。
- Android 2.0.0 APK 与 ZIP 目前公网 HTTP 200，用户仍有可用下载路径。
- Web Player 仓库实现已增加 Product Home 和 Company Home 返回链接。

### 4.2 缺失

- `play.rongjingmusic.com` 可用路由/TLS。
- 邮箱 DKIM、DMARC。
- Terms/服务条款。
- 独立版权/知识产权边界说明。
- 可核验的 ICP/公安备案信息展示。
- 客服邮箱职责、回复标准与归档机制。
- 唯一公开发布版本权威。

### 4.3 冲突

- Company Home 线上旧身份 vs Canon 中的荣景文川 Company Home。
- Company Home 线上内容 vs 仓库 `ops/web_origin/site/rongjingwenchuan/` 新源文件。
- Product Home 公开 `/ear.html` vs Ear 仅为内部系统的边界。
- 官网 Android 2.0.0 vs 当前源码 2.0.1 vs 已归档发布物 3.1.0。
- Company 仓库页仍使用未验证的 `hello@rongjingwenchuan.com`，而已建立的邮箱域为 `rongjingmusic.com`。
- 网站 GitHub 指向个人账号和旧 `moodify-ai` 仓库命名，与企业化对外感知存在张力。

### 4.4 待确认（`HUMAN_DECISION_REQUIRED` 或运行证据不足）

- `hello@rongjingmusic.com` 已由人类权威确认实际使用无问题（2026-08-22）；该项从待确认转为已验证。
- 公司是否已取得 ICP 备案/公安备案；若有，真实备案号是什么。
- 公司是否需要单独的 `@rongjingwenchuan.com` 邮箱，还是三站统一使用 `@rongjingmusic.com`。
- Android 下一个唯一公开稳定版是 2.0.0、2.0.1 还是 3.1.0。
- GitHub 是否迁移到企业组织账号以及仓库是否改名；这不应由普通网站任务静默决定。
- `.xyz` 迁移后采用 301、302 还是保留兼容入口。

## 5. 风险优先级

### P0 — 立即验证，不应等待网站大改

1. **停止把线上 Company Home 当作已完成的企业官网。** 它当前仍传达已退出的旧身份。

### P1 — 下一个实施包

1. 确认 `rongjingwenchuan.com` 真实部署源与回滚点。
2. 将仓库中新 Company Home 按原子发布模型上线。
3. 在上线前改为完整公司名，并将联系邮箱指向真实存在的企业邮箱。
4. 验证 Company → Product、Product → Company、Privacy、Contact、SEO/OG 和移动端。

### P2 — 企业信任收尾

1. 补 DKIM/DMARC，并形成邮箱职责表。
2. 编写最小、事实准确的 Terms 与版权说明。
3. 核实备案现状，只展示真实号码。
4. 将 `/ear.html` 从产品官网公开面移除、限制或迁移到明确的内部/研究边界；具体策略需人类确认。

### P3 — 产品交付与组织化

1. 决定 Android 唯一稳定版，统一网站、APK、源码和发布记录。
2. 完成 `play.rongjingmusic.com` 的 DNS/TLS/CORS/媒体路径验证，再决定 `.xyz` 迁移策略。
3. 评估 GitHub 组织账号与仓库命名的企业化迁移。

## 6. P1 验收结果

| 验收项 | 结果 |
|---|---|
| 三站/App/下载/GitHub/邮箱/法律面均已纳入盘点 | **PASS** |
| 线上事实与仓库意图已分开记录 | **PASS** |
| 正确/缺失/冲突/待确认已分类 | **PASS** |
| 每个高优先级问题有下一步验证 | **PASS** |
| 本包是否修改公开页面或 Canon | **NO** |

**P1 状态：`COMPLETE`**

## 7. 建议的下一个最小任务

> **P2-00 已完成：`hello@rongjingmusic.com` 已由人类权威确认实际使用无问题。下一项为 Company Home 部署收敛。**

原因：该邮箱已公开给访客，它是当前唯一可能直接造成外部消息丢失的风险；验证成本最低，且不涉及 Canon 或大规模部署。
