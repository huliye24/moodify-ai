# EXTRACTION MATRIX — INITIAL GUIDANCE

这是 012 的初始候选矩阵，Codex 必须用真实仓库审计结果修正。

| Domain | Likely source | Desired result | Default action |
|---|---|---|---|
| Wallet connect | `WalletConnect.tsx`, `wallet.ts` | token-independent wallet session | ADAPT |
| EVM address | `evm-address.ts` | shared validator/normalizer | EXTRACT |
| Chain RPC | `mood-chain.ts` | generic read-only chain adapter | ADAPT |
| Token-specific reads | `mood-token.ts`, token page | dark adapter | FREEZE |
| Contribution tasks | contribution service/API | reusable domain | EXTRACT |
| Submission review | contribution admin/API | reusable workflow | EXTRACT |
| Reputation | contribution/genesis data | off-chain append-only model | ADAPT |
| Pending reward | reward events | accounting only | KEEP BUT DARK |
| Genesis registration | genesis APIs | identity primitives only | ADAPT |
| Airdrop | airdrop page/API | not foundation | FREEZE |
| Distributor contracts | Solidity | future launch asset | FREEZE |
| Transparency | transparency API/page | network/public provenance | ADAPT |
| Treasury token reads | treasury helpers | future economic layer | KEEP BUT DARK |
| Security docs | docs/security | trust foundation | EXTRACT/REFERENCE |

## Rule

不要按文件名机械 cherry-pick。

任何提取必须先画依赖关系：

```text
module
├── pure dependencies
├── token-specific dependencies
├── database dependencies
├── auth dependencies
└── UI dependencies
```

只有依赖关系清楚后才行动。
