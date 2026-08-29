# P2 官网基础信任层进度

**日期：** 2026-08-22  
**状态：** `IN_PROGRESS`  
**Canon 判定：** `CANON_CHANGE = NO`

## P2-00 企业联系邮箱

**状态：`COMPLETE`**

- 公开联系地址：`hello@rongjingmusic.com`。
- 人类权威于 2026-08-22 确认该邮箱已实际使用且无问题。
- Product Home Contact 已收敛为单一邮箱入口。
- Company Home 与 Company Privacy 已同步到该已验证地址。
- MX/SPF 已生效；DKIM/DMARC 仍待补齐。

## P2-01 Company Home 线上身份收敛

**状态：`COMPLETE`**

### 变更前证据

- 生产 `current` 指向：`/var/www/rongjingwenchuan.com/releases/20260812T021349Z`。
- 线上 Title：`Moodify — Auditory Intelligence Infrastructure`。
- 线上无完整法定公司名称，且与仓库新 Company Home 不一致。

### 已实施

- 上线仓库 `ops/web_origin/site/rongjingwenchuan/` 中的 Company Home。
- 增加法定主体：“荣景文川（深圳）科技有限公司”。
- 公司联系地址改为 `hello@rongjingmusic.com`。
- 同步更新 Company Privacy 的主体、邮箱、日期和页脚。
- 保留荣景文川为 Company、Moodify 为主要公开产品的层级。

### 验证证据

- 仓库公司站测试：`7/7 PASS`。
- 新发布：`/var/www/rongjingwenchuan.com/releases/20260822T022937Z-company-home`。
- Nginx 配置测试成功，服务状态 `active`。
- `https://rongjingwenchuan.com/`：HTTP 200，Title = `荣景文川 - Rongjing Wenchuan`。
- `https://rongjingwenchuan.com/privacy.html`：HTTP 200，Title = `Privacy - 荣景文川`。
- 首页和 Privacy 均存在完整法定公司名称。
- 线上 Cloudflare 邮箱保护值解码后均为 `hello@rongjingmusic.com`。
- 退出文案 `Auditory Intelligence Infrastructure` 已从新线上首页消失。
- 旧 release 保留，可通过原子软链接切换回滚。

## P2-02 邮箱发信身份

**状态：`DEFERRED`**

- MX/SPF 已生效，`hello@rongjingmusic.com` 已由人类验证可用。
- DKIM 需要阿里邮箱后台生成的域名专属 TXT 值；本轮按人类指令跳过。
- DMARC 将在 DKIM 生效后配置，避免在签名链未完成时过早收紧策略。

## P2-03 Terms / 知识产权边界

**状态：`COMPLETE`**

- Product Home 新增 `/terms.html` 与 `/intellectual-property.html`。
- Company Home 新增 `/terms.html`，并指向统一的 Moodify 知识产权声明。
- 两站页脚及 sitemap 已接入法律页面。
- 条款仅描述当前真实开放范围，不虚构付费、账号或未来能力承诺。
- 明确音乐内容权利归原权利人；Evidence / Creation Passport 不构成版权登记、权属裁决或法律意见。
- 权利通知统一发送至 `hello@rongjingmusic.com`。

### 验证证据

- 静态站回归：`21/21 PASS`。
- Product release：`/var/www/rongjingmusic.com/releases/20260822T025601Z-legal-trust`。
- Company release：`/var/www/rongjingwenchuan.com/releases/20260822T025601Z-legal-trust`。
- Nginx 配置测试成功，服务状态 `active`。
- 线上 `/terms.html`、`/intellectual-property.html` 与 Company `/terms.html` 均为 HTTP 200。
- 旧 release 均保留，可原子回滚。

## P2 剩余项

| 项目 | 状态 | 阻塞/下一步 |
|---|---|---|
| 邮箱 DKIM/DMARC | `DEFERRED` | 按人类指令跳过；后续取得阿里邮箱专属 DKIM 值再恢复 |
| Terms / 服务条款 | `COMPLETE` | 已上线两站最小真实版本 |
| 版权/知识产权边界 | `COMPLETE` | 已上线权利归属、创作者内容、Evidence 与通知渠道边界 |
| ICP/公安备案 | `HUMAN_DECISION_REQUIRED` | 需人类提供真实备案状态/号码；不得猜测或虚构 |

## 下一个最小任务

> **P3-01：统一 Product Home 到真实可用的 Play / Download 入口，并消除版本与域名认知冲突。**

P2 中仍需人类输入的两项（DKIM 专属值、真实备案状态/号码）保留在案，不阻塞下一阶段。
