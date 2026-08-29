# CANON_CHANGELOG — Moodify

> 所有产品身份、authority order、内部/外部边界变化必须记录于此（R7）。

## 2026-08-29 — MOOD Digital Home Public Identity

- **CANON_CHANGE = YES。** 人类明确将 MOOD 定义为比 Moodify 更广阔的数字家园：以独立意志、自由选择、闲暇、艺术、美与真实连接为公共精神；Moodify Music 是进入 MOOD 世界的一个入口，而非 MOOD 的上位产品。
- **Why：** 原公开页面过度聚焦代币事实与技术状态，不能表达用户要求的生活哲学、文化与审美世界。
- **Evidence：** 当前人类指令明确引用存在主义咖啡馆、罗素《赞美闲暇》与《在路上》的精神取向，并要求以乌托邦插画构建 MOOD 官网。
- **Migration：** `crestwavecoin.com` 首屏转为 MOOD 数字家园叙事；技术状态退出公共界面；钱包与官方合约保留为后段实用入口；Moodify 明确为音乐入口之一。
- **Rollback：** 恢复上一 LA 时间戳发布目录，并回退本条与对应公共页面文案/插画资产。
- **受影响 authority / runtime 文件：** 本 changelog、`apps/web/app/token/page.tsx`、`apps/web/app/globals.css`、MOOD 公共插画资产。
- **边界：** 本变更不改 Moodify Music / Player 在 `rongjingmusic.com` 的既有产品身份，也不改变链上合约、供应量、资产控制或内部生产系统。

## 2026-08-29 — Crestwave Web3 Public Root on LA

- **CANON_CHANGE = YES。** 人类明确批准将 `crestwavecoin.com` 作为 Web3 对外站点，并删除旧 Cloudflare Pages 公共界面；该站点不改变 Moodify Music / Player 在既有 Moodify 域名上的身份。
- **Evidence：** `crestwavecoin.com` 与 `www.crestwavecoin.com` DNS 均指向 Tunnel `92f54925-3754-4093-9ac9-1702a14e2a70`；LA 上 `crestwave-web3.service`、Nginx、`cloudflared-moodify.service` 均运行；公网 `/healthz` 返回 `origin=la`，根路径进入 `/token`，并显示 BSC chain ID 56 与 MOOD 合约 `0x1BB3115D43E397f7bb586F090831B02cA639e73E`。
- **Migration：** 移除 Pages 项目 `crestwavecoin` 的自定义域名绑定，以 Tunnel CNAME 取代 `crestwavecoin.pages.dev` CNAME；LA 发布目录为 `/opt/crestwave/releases/20260829T083422Z`，服务仅监听 `127.0.0.1:3200`。
- **Rollback：** DNS 恢复到旧 Pages CNAME 并重新绑定 Pages 自定义域名，或在 LA 恢复 `/root/crestwave-backups/` 中的 Nginx/Tunnel 配置；应用发布可切回保留的时间戳目录。
- **受影响 authority / runtime 文件：** 本 changelog、`ops/web_origin/cloudflared/config.yml`、`ops/web_origin/nginx/crestwavecoin.conf`、`ops/web_origin/systemd/crestwave-web3.service`。
- **安全边界：** 本次只发布公开 Web 与只读链上信息；未部署 Distributor、未移动资产、未启用 claim、未请求或使用项目私钥。

## 2026-08-19 — Public Form Brand Authority Freeze（v1.1）

- **CANON_CHANGE = YES。** 人类通过 Package 01 明确冻结 Public Brand：创始价值原点「弱者的声音也值得被世界听见」；公共表达「每一种声音，都值得被世界听见。 / Every voice deserves to be heard.」；产品原则 `Listen. Then Play.`；动作 `Play.`。
- **站点职责：** `rongjingmusic.com` = Moodify Product Home；`rongjingwenchuan.com` = 荣景文川 Company Home；`rongjinwenchuan.xyz` = 过渡 Web Player / 历史入口；`play.rongjingmusic.com` 为优先迁移目标但当前 `UNVERIFIED`。
- **语言边界：** `The Ear of AI`、Auditory Intelligence Infrastructure、API/ACU/Developers、Creator Platform 与内部处理链退出公共第一叙事；研究与工程上下文可保留。
- **Authority：** 新增 `docs/brand/public/`，其中 `PUBLIC_BRAND_CONSTITUTION.md` 为最高 Public Brand 主题权威；旧 product-framework、站点和域名文档保留但不得覆盖它。
- **Evidence：** Package 清单 SHA-256 全部匹配；三站仓库/线上只读审计见同目录 Inventory、Conflict Matrix、Backlog、Authority Report。
- **Migration：** Package 02 Product Home；Package 03 Company Home；Package 04 Player/域名收敛。本包不提前修改生产表面。
- **Rollback：** 将本条、Canon/索引链接及 `docs/brand/public/` 作为一个文档变更单元回退；因本包未改运行时，无生产回滚步骤。
- **受影响 authority 文件：** `AGENTS.md`、`docs/canon/CURRENT_CANON.md`、`PRODUCT_BOUNDARY.md`、`AUTHORITY_ORDER.md`、本 changelog、`docs/product-framework/PRODUCT_AUTHORITY_INDEX.md`。
- **明确未改：** production website/App/DNS/Cloudflare/API/database/audio chain。

## 2026-08-17 — W01-P01 Canonical Convergence（v1.0）

- **对外产品身份：** Moodify Music / Moodify Player；第一阶段核心用户动作 PLAY。
  - 旧身份（公开产品层面）：「The Ear of AI — an Auditory Intelligence System」、「Reconstruction-first listening environment」均不再作为对外身份。
  - 受影响文件：README.md、AGENTS.md、docs/REPOSITORY_STATUS.md、docs/canon/*（新建）。
- **内部边界：** Moodify Ear / Auditory Intelligence 明确为内部听觉、判断、验证与研究系统；Classic Reconstruction（宪法 v1.0）保留为内部生产哲学。
  - 受影响文件：AGENTS.md、README.md、docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md（INTERNAL 标记）、docs/ASSET_MODEL.md（INTERNAL 标记）。
- **权威顺序：** 固定 8 级 authority order（人类指令 > AGENTS > docs/canon/* > runtime evidence > canonical main behavior+tests > subsystem docs > experimental docs > historical docs）。
- **Canon 不变量：** 一个对外产品身份；PLAY 优先；Canon 不虚构现实；历史文档不反向覆盖 Canon；Canon 变更必须可见。
- **Canon drift guard：** scripts/canon_guard.py + moodify-core-package/tests/test_canon_guard.py（2026-08-17）。
- **决策注册：** W01-P01 Decision Register（CD-001..CD-016）。

### HUMAN_DECISION_REQUIRED（未决，不猜测）

1. CD-011：对外命名细节（Moodify Music vs Player、域名品牌 rongjingmusic.com 等）。
2. CD-014：Classic Reconstruction Constitution v1.0 正文是否更新（其 Article I 对外表述已被本 Canon 覆盖，文本未动）。
3. CD-015：单一 authoritative state machine 统一方案。
4. GitHub main 合并策略（未合并分支 154 commits 的去向）。
