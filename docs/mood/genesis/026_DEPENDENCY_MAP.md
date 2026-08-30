# Genesis Integration 026 Dependency Map

## Main integration spine

```text
origin/main e24b29f5
  -> 011 Foundation 429fbbb3
  -> 013 Portal bridge 97c91068
  -> 014 Library 72e582eb
  -> 015 Passport cf9df8a8
  -> 016 Contribution 5e8a44a2
  -> 017 Network 0a7a669f
  -> 018 Agents 1a3b7933
  -> 019 Nodes 70727ec8
  -> 020 Governance 3dde397c
```

## Divergent commits requiring explicit absorption

| Package | Commit | Relationship | 026 treatment |
|---|---|---|---|
| 012 Protocol Extraction | `3fbd2cd6` | Descends from 011 but is absent from the 013-020 spine | Review and absorb after 011 |
| 013 Full Portal | `660d613d` | Descends from the 013 bridge but is absent from 014-020 | Review and absorb before 014 |

## Historical packages 021-025

| Package | Initial 026 classification | Rule |
|---|---|---|
| 021 Treasury | `UNVERIFIED / NOT_IN_BASELINE` | Gap-analysis input only |
| 022 Security | `UNVERIFIED / NOT_IN_BASELINE` | Security requirements may become release gates; code is not auto-admitted |
| 023 Staging | `UNVERIFIED / NOT_IN_BASELINE` | Deployment plan is evidence input, not deployment truth |
| 024 Genesis readiness | `UNVERIFIED / NOT_IN_BASELINE` | Review checklist input only |
| 025 Token activation | `BLOCKED_BY_GENESIS_AND_HUMAN_AUTHORITY` | No activation in 026 |

## Planned absorption order

1. `429fbbb3` - 011
2. `3fbd2cd6` - 012
3. `97c91068` - 013 bridge
4. `660d613d` - 013 full portal
5. `72e582eb` - 014
6. `cf9df8a8` - 015
7. `5e8a44a2` - 016
8. `0a7a669f` - 017
9. `1a3b7933` - 018
10. `70727ec8` - 019
11. `3dde397c` - 020, only after governance authority review

Each absorption must produce a build/test checkpoint. A later package cannot be used to hide an earlier regression.

