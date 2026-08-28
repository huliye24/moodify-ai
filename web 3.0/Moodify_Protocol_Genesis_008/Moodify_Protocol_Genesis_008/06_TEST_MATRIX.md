# Full Genesis Test Matrix
## Security & Public Launch

### Package 001 — Token Foundation

| ID | Test | Expected |
|---|---|---|
| R-001 | Official contract consistency | exact |
| R-002 | Chain ID consistency | 56 |
| R-003 | Decimals | 18 |
| R-004 | Total supply display | 33,000,000 |
| R-005 | Placeholder scan | none |

### Package 002 — Registration

| ID | Test | Expected |
|---|---|---|
| R-101 | Valid registration | success |
| R-102 | Replay nonce | reject |
| R-103 | Expired nonce | reject |
| R-104 | Wrong signer | reject |
| R-105 | Wrong chain | reject |
| R-106 | Concurrent duplicate | one record |
| R-107 | Address casing | same wallet |
| R-108 | Signature log exposure | absent |

### Package 003 — Admin

| ID | Test | Expected |
|---|---|---|
| R-201 | Unauthorized read | deny |
| R-202 | Unauthorized mutation | deny |
| R-203 | IDOR participant mutation | deny |
| R-204 | Status audit | append event |
| R-205 | Allocation audit | append event |
| R-206 | Pool ceiling | enforced |
| R-207 | Internal notes public leak | absent |

### Package 004 — Distribution

| ID | Test | Expected |
|---|---|---|
| R-301 | Same input same root | yes |
| R-302 | Different row order | same root |
| R-303 | Duplicate wallet | fail |
| R-304 | Wrong status | excluded/fail |
| R-305 | Amount >18 decimals | fail |
| R-306 | Pool ceiling overflow | fail |
| R-307 | Proofs all verify | yes |
| R-308 | Artifact privacy | pass |
| R-309 | Snapshot overwrite | guarded |

### Package 005 — Airdrop

| ID | Test | Expected |
|---|---|---|
| R-401 | Package 004 fixture | verifies |
| R-402 | Valid claim | success |
| R-403 | Wrong wallet | revert |
| R-404 | Wrong amount | revert |
| R-405 | Wrong participant | revert |
| R-406 | Corrupt proof | revert |
| R-407 | Double claim | revert |
| R-408 | Insufficient balance | revert/no consumed state |
| R-409 | Fuzz | pass |
| R-410 | Invariants | pass |
| R-411 | Static analysis | no unresolved critical/high |
| R-412 | No active arbitrary drain | pass |

### Package 006 — Contribution

| ID | Test | Expected |
|---|---|---|
| R-501 | Unregistered submit | deny |
| R-502 | Unauthorized reviewer | deny |
| R-503 | Self-review | deny |
| R-504 | Invalid transition | deny |
| R-505 | Reward exactness | pass |
| R-506 | Duplicate approval | no duplicate reward |
| R-507 | Genesis allocation untouched | yes |
| R-508 | Trade-to-earn | absent |
| R-509 | Export privacy | pass |

### Package 007 — Transparency

| ID | Test | Expected |
|---|---|---|
| R-601 | RPC fail | unavailable/stale, not zero |
| R-602 | DB fail | unavailable, not zero |
| R-603 | Circulating draft | no numeric claim |
| R-604 | Unknown wallet | not auto-labeled |
| R-605 | Public API privacy | pass |
| R-606 | Signer/write client | absent |
| R-607 | Fake market cap | absent |
| R-608 | Liquidity unknown | no fabricated USD |

### Cross-system

| ID | Test | Expected |
|---|---|---|
| X-001 | Same MOOD contract everywhere | yes |
| X-002 | Same chain everywhere | yes |
| X-003 | Package 004 root = Package 005 config | yes/blocked until approved |
| X-004 | Claimed status reconciles chain/frontend | yes |
| X-005 | Contribution rewards not Genesis allocation | separated |
| X-006 | Public routes contain no dev data | pass |
| X-007 | Production build | pass |
| X-008 | Secret scan | clean/no unresolved real secret |
| X-009 | Mobile core flows | usable |
| X-010 | Dead link scan | pass |
