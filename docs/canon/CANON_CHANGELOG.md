# CANON_CHANGELOG — Moodify

> 所有产品身份、authority order、内部/外部边界变化必须记录于此（R7）。

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
