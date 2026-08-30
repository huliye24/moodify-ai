# ARCHITECTURE TARGET

## Foundation First

```text
MOOD PORTAL
   │
   ├── Identity
   │    ├── wallet address
   │    ├── signature
   │    └── resident identity
   │
   ├── Contribution
   │    ├── tasks
   │    ├── submissions
   │    ├── review
   │    └── evidence
   │
   ├── Reputation
   │    └── append-only events
   │
   ├── Transparency
   │    ├── provenance
   │    ├── policies
   │    └── public state
   │
   └── Chain Adapter
        └── read-only generic EVM capability

FUTURE ECONOMIC LAYER
   │
   ├── MOOD Token
   ├── Holder rewards
   ├── Treasury assets
   ├── DEX
   ├── Claim
   └── Distribution

               ↑
          LAUNCH GATE
```

## Important boundary

Foundation must remain useful even if:

- no Token is ever launched tomorrow
- contract address is unknown
- DEX does not exist
- treasury balance is zero
- reward distribution is disabled

如果基础网络离开 Token 就无法运行，012 失败。
