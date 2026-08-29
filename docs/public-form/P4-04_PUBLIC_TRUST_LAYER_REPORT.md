# P4-04 Public Trust Layer Report

**Date:** 2026-08-22

**Status:** COMPLETE
**Canon change:** NO

## 1. 新增页面

| 页面 | 公开职责 | 事实边界 |
|---|---|---|
| `/release.html` | 记录真实产品成长与版本状态 | 区分官网当前稳定版、已验证包与归档包，不写未来功能 |
| `/research-log.html` | 以实验日志形式公开有限研究记录 | 每条均包含问题、方法、实验、观察、下一步，并省略算法、私有音频与商业机密 |
| `/letter.html` | 解释 Why We Build Moodify | 讨论播放演进、机器听觉与长期建设，不使用个人英雄、融资或创业鸡汤叙事 |
| `/press.html` | 提供准确引用、品牌素材、产品画面和联系入口 | 不提供虚构合作方、用户数、融资或市场数据 |
| `/developers.html` | 给工程师提供有限技术方向说明 | 不是 API 文档，不开放核心代码，不承诺未验证部署 |

## 2. 修改文件

### 新增

- `ops/web_origin/site/rongjingmusic/release.html`
- `ops/web_origin/site/rongjingmusic/research-log.html`
- `ops/web_origin/site/rongjingmusic/letter.html`
- `ops/web_origin/site/rongjingmusic/press.html`
- `ops/web_origin/site/rongjingmusic/developers.html`
- `ops/web_origin/site/check_public_trust.mjs`
- `docs/public-form/P4-04_PUBLIC_TRUST_LAYER_REPORT.md`

### 更新

- `ops/web_origin/site/rongjingmusic/index.html`
  - 在首页页脚加入 Releases、Research Log、Letter、Press 与 Technical 发现入口。
- `ops/web_origin/site/rongjingmusic/sitemap.xml`
  - 加入全部五个 Public Trust 页面。
- `ops/web_origin/site/rongjingmusic/assets/site-public-form-20260820.css`
  - 增加时间线、研究日志、Founder Letter、Press assets 与 Technical overview 的克制版式。

未修改 Player UI、Android 下载、后端 API、云端处理逻辑或数据库。

## 3. 内容结构

### Release Notes

```text
Public Web Player (2026-08-22)
Android 3.1.0 validated package (2026-08-16)
Android 3.0.0 archived package (2026-08-16)
Android 2.0.0 current public stable (2026-08-15)
```

信息来自仓库 release manifest、README、已验证公开入口和发布记录。3.x 包没有被描述为官网当前稳定下载。

### Research Log

每条记录固定为：

```text
Research Question
Method
Experiment
Observation
Next Step
```

首批公开日志覆盖：

- 跨机器测量重复性；
- 音频 Range 部分交付；
- 有限范围的算法审查与人工升级。

### Founder Letter

叙事顺序：唱片 → 数字音乐 → 流媒体 → 播放体验仍需进化 → 先听再播放 → 长期机器听觉探索。

### Press Kit

包含：

- Moodify 官方简介；
- 荣景文川官方简介；
- 品牌与公司标准事实；
- Moodify Logo PNG 下载；
- 当前 OG 素材下载；
- 当前 Player 产品画面入口；
- 最新发布截图的邮件申请入口；
- `hello@rongjingmusic.com` 联系方式。

### Technical Overview

仅解释三个方向：Audio Intelligence、Cloud Processing、Research Direction。公开模型保持在 Input → Understand → Prepare → Play，不公开内部编排、凭据、核心算法或未验证能力。

## 4. SEO 检查

五个新增页面全部包含：

- 唯一 `title`；
- 唯一 meta description；
- canonical URL；
- `og:title`、`og:description`、`og:type`、`og:url`、`og:image`；
- Twitter large-image card；
- 可解析的 Schema.org JSON-LD；
- favicon；
- sitemap 收录。

Schema 类型分别使用 `CollectionPage`、`Article`、`AboutPage` 与 `TechArticle`，并连接 Moodify Product / WebSite 与荣景文川 Organization。

## 5. 品牌一致性检查

- 对外产品保持 Moodify / Moodify Player；类别为 AI Audio Player。
- 核心用户动作保持 Play。
- 品牌信念保持 `Every voice deserves to be heard.`。
- 产品原则保持 `Listen. Then Play.`。
- `Can machines learn to hear?` 只出现在 Research 深层语境。
- Developer 页面没有进入主导航，也没有成为公开第一身份。
- Ear、内部状态机、核心算法和处理复杂度没有被提升为公开产品。
- 公司主体统一使用 `荣景文川（深圳）科技有限公司`。
- 没有用户数量、融资、合作伙伴、收入或领先性虚构声明。

`CANON_CHANGE = NO`：本任务新增长期可信资产，没有改变产品身份、内外能力边界或任何运行权威。

## 6. 验证与发布

- P4-04 专项自动检查：7/7 passed。
- Git whitespace 检查：passed。
- 五个线上页面：HTTP 200，canonical 与 JSON-LD 已核验。
- 线上 sitemap：五个页面全部存在。
- Android 2.0.0 公开下载：HTTP 200，未因发布丢失。
- Nginx 与 Cloudflare Tunnel：active。
- 生产发布：`/var/www/rongjingmusic.com/releases/20260822T152042Z-p4-04-public-trust`。

### 已知测试基线差异

`check_site.mjs` 与 `check_company_site.mjs` 的部分断言仍冻结在 P4-02/P4-03 之前的标题和首页段落顺序，因此会对已经批准的 P4-02/P4-03 内容报旧基线错误。P4-04 没有回退现有内容来迎合旧断言；新增 `check_public_trust.mjs` 对本包边界独立验证。后续应单独执行一次测试基线迁移，把旧断言更新到当前已批准的 P4-03 页面结构。

## 7. 后续建议

1. 将 P4-02/P4-03 后已经过时的站点测试断言迁移到当前 Canon 与首页结构。
2. 建立 Press screenshot 的版本化发布流程，避免媒体长期引用过期 UI。
3. Research Log 只在形成新证据后追加，不按营销日历强制更新。
4. Release Notes 后续由 release manifest 自动生成候选内容，再由人审核公开状态。
5. 在真实社交平台分别验证 OG 卡片缓存与裁切，不因页面上线就假定传播预览已经正确刷新。
