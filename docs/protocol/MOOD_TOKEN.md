# MOOD Token — Protocol Documentation

**Authority:** MOOD-GENESIS-001（协议包）→ 本文档 → `apps/web/lib/mood-token.ts`（应用配置权威）
**Status:** Active
**CANON_CHANGE:** NO（普通功能任务,不改变产品身份）
**Last updated:** 2026-08-26

---

## 1. 官方代币事实

| 字段 | 值 |
|---|---|
| 网络 | BNB Smart Chain |
| Chain ID | 56 |
| 代币名称 | Moodify |
| 符号 | Mood |
| 官方合约 | `0x1BB3115D43E397f7bb586F090831B02cA639e73E` |
| 小数位 | 18 |
| 总量 | 33,000,000 MOOD |
| 区块浏览器 | <https://bscscan.com/token/0x1BB3115D43E397f7bb586F090831B02cA639e73E> |
| 主要 DEX | PancakeSwap V3 |
| 交易对 | MOOD / WBNB |
| 费率档 | 1% |
| 交易入口 | <https://pancakeswap.finance/swap?outputCurrency=0x1BB3115D43E397f7bb586F090831B02cA639e73E> |

**池地址(Pool address):未核验,刻意不记录。** 在从链上/浏览器核验之前,不得虚构或硬编码池地址(MOOD-GENESIS-001 token canon)。

## 2. 权威结构

```text
MOOD-GENESIS-001 协议包(人类批准的事实)
        ↓
docs/protocol/MOOD_TOKEN.md(本文档,协议层记录)
        ↓
apps/web/lib/mood-token.ts(应用配置单一来源,唯一代码权威)
        ↓
apps/web/app/token/page.tsx(/token 页面,只从 config 读取,不硬编码第二份地址)
```

- **Metadata authority:** 链上部署的 BEP-20 合约本身是最终事实来源;BscScan 为只读验证入口。
- **Configuration authority:** `apps/web/lib/mood-token.ts` 是应用级唯一配置来源。任何 UI 需要代币事实时必须 import 该模块,不得在其它文件硬编码合约地址。
- **Public surface:** `/token` 页面(`apps/web/app/token/page.tsx`)。

## 3. 语言与合规约束

- 不引入 staking、yield、APY、ROI、锁仓、空投领取或价格承诺语言。
- 不虚构分配百分比、池地址、价格、市值、持有人数或交易量。
- 未核验的链上事实按"未知"呈现或直接省略。
- 页面必须保留风险提示(新上线、流动性浅、价格波动、合约与市场风险、自行核实地址、无回报保证)。
- 分配政策当前为占位措辞:"代币分配政策正在规范化过程中,并将在任何大规模分配之前通过 Moodify 协议文档公布。"

## 4. 更新程序

1. 提出变更的一方提供**链上可验证的证据**(BscScan 交易/合约记录或人类签发的决定)。
2. 依次更新:`apps/web/lib/mood-token.ts` → `docs/protocol/MOOD_TOKEN.md`(Last updated 字段)。
3. 运行 `npm test`(apps/web),确认 `tests/mood-token.test.mjs` 通过。
4. 确认 `/token` 页面渲染正确(本地 dev 或构建产物)。
5. 一次聚焦提交,例如 `feat(web): update MOOD token facts`。

## 5. 需要人类确认的事项

以下任何一项**必须**先获得明确的人类确认,不得由代理自行决定:

- 修改或替换官方合约地址;
- 变更 chain ID / 网络(包括任何跨链或迁移声明);
- 修改总供给的对外表述;
- 发布代币分配比例或分配政策;
- 添加交易、钱包连接、签名或任何资金相关交互;
- 声称新的 DEX、池地址或上线信息;
- 任何涉及真实资金、流动性或合约所有权的操作(完全超出本仓库任务范围)。

## 6. 范围与不变量

- 本文档与 `/token` 页面**不改变** Moodify 对外产品身份(Moodify Music / Player,核心动作 PLAY)。
- MOOD 是生态协议层资产;持有 MOOD 不是使用 Moodify 的前提。
- 不部署新合约、不修改现有合约、不动流动性、不签名、不托管私钥(MOOD-GENESIS-001 guardrails)。
