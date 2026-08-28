# Test Matrix
## Transparency & Treasury

| ID | Scenario | Expected |
|---|---|---|
| T-001 | Official token page config | exact contract |
| T-002 | totalSupply RPC succeeds | exact chain value |
| T-003 | totalSupply RPC fails | unavailable/stale, not zero |
| T-004 | Valid treasury address | balance read |
| T-005 | Invalid treasury address | config validation fail |
| T-006 | Duplicate treasury address | config validation fail |
| T-007 | Empty treasury config | public page works |
| T-008 | Unknown wallet with large balance | not auto-labeled |
| T-009 | Genesis registration query | correct aggregate |
| T-010 | Genesis allocation | correct aggregate |
| T-011 | Package 004 approved snapshot | metadata visible |
| T-012 | Unapproved snapshot | not presented as official |
| T-013 | Distributor deployed | on-chain balance/read |
| T-014 | Distributor absent | safe not-deployed state |
| T-015 | Claimed event/state | claimed aggregate |
| T-016 | DB says claimed, chain disagrees | reconciliation warning |
| T-017 | Pending contribution rewards | pending only |
| T-018 | Included rewards | separate bucket |
| T-019 | Distributed rewards | separate bucket |
| T-020 | pending counted as distributed | must fail |
| T-021 | Circulating methodology draft | no numeric circulating claim |
| T-022 | Allocation policy absent | no invented pie chart |
| T-023 | RPC stale cache | stale label |
| T-024 | DB failure | unavailable, not zero |
| T-025 | Public API | no signatures |
| T-026 | Public API | no nonces |
| T-027 | Public API | no internal notes |
| T-028 | Treasury admin route | read-only |
| T-029 | Transfer button/action | absent |
| T-030 | Write client/signer in module | absent |
| T-031 | Percentage 1/3 supply | safe formatted result |
| T-032 | 18-decimal balance | exact |
| T-033 | Pancake pool unverified | no fabricated liquidity |
| T-034 | Verified pair | links/facts render |
| T-035 | Mobile transparency page | usable |
| T-036 | Production build | pass |

### Manual audit

1. Open `/transparency`.
2. Verify official contract manually.
3. Compare total supply to BscScan/RPC.
4. Compare one configured account balance.
5. Inspect Genesis numbers.
6. Inspect contribution pending reward total.
7. Confirm no market cap claim.
8. Confirm no unsupported circulating supply claim.
9. Disable RPC and verify graceful failure.
10. Inspect public API for private-data leakage.
