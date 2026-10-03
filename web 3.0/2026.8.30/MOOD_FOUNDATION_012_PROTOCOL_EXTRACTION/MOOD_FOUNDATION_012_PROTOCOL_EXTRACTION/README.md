# MOOD FOUNDATION 012 — Protocol Foundation Extraction

**Package ID:** `MOOD-FOUNDATION-012`  
**Target repository:** `huliye24/moodify-ai`  
**Depends on:** `MOOD-FOUNDATION-011`  
**Primary branch target:** new isolated branch based on the accepted 011 result

## Mission

从现有 `codex/mood-mainnet-integration-009` 和仓库现有资产中，**选择性提取** MOOD Portal 后续真正需要的协议底座。

不是把 009 整条合并回来，而是把“可复用基础能力”与“旧 Token Launch 语义”拆开。

核心目标：

```text
OLD WEB3 BUNDLE
wallet + token + genesis + airdrop + contribution + transparency
                         │
                         ↓
                  selective extraction
                         │
                         ↓
MOOD PROTOCOL FOUNDATION
identity + wallet + contribution + reputation + transparency + read-only chain adapters
```

## 012 完成后应得到

- 可独立使用的钱包连接层
- Wallet Signature / Identity 基础
- Contribution domain 基础
- Reputation 基础
- Transparency / provenance 基础
- Read-only EVM / chain abstraction
- 清晰的 Token Launch boundary
- 不依赖“新 MOOD Token 已发行”的 Portal foundation

## 明确不做

- 不发新 Token
- 不部署合约
- 不执行 Genesis / Airdrop / Claim
- 不启用 DEX CTA
- 不建立新的官方 CA
- 不把 reward points 自动映射成链上资产
- 不把 009 整条 merge 进来
