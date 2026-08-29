# Test Matrix
## Merkle Airdrop

| ID | Scenario | Expected |
|---|---|---|
| M-001 | Deploy with valid token/root | success |
| M-002 | Deploy with zero token | revert |
| M-003 | Deploy with zero root | revert if contract requires nonzero root |
| M-004 | Valid Package 004 proof | claim succeeds |
| M-005 | Wrong wallet | revert |
| M-006 | Wrong amount | revert |
| M-007 | Wrong participant # | revert |
| M-008 | Corrupted proof | revert |
| M-009 | Claim twice | second reverts |
| M-010 | Two different valid participants | both succeed |
| M-011 | Insufficient distributor token balance | revert, claim remains unconsumed |
| M-012 | Fund then retry failed claim | succeeds |
| M-013 | Claimed event | exact fields emitted |
| M-014 | Random amount fuzz | only approved amount succeeds |
| M-015 | Random wallet fuzz | only approved wallet succeeds |
| M-016 | Mutated Package 004 fixture | fails |
| M-017 | Frontend not eligible | no claim button |
| M-018 | Frontend eligible | exact amount shown |
| M-019 | Wrong network | switch prompt |
| M-020 | User rejects tx | recoverable UI |
| M-021 | Insufficient BNB gas | clear error |
| M-022 | Pending tx | hash shown |
| M-023 | Receipt success | claimed state |
| M-024 | Receipt revert | error state, not claimed |
| M-025 | Already claimed on reload | chain state shows claimed |
| M-026 | Missing distributor config | safe disabled state |
| M-027 | Proof endpoint queried for unrelated wallet | returns only public eligibility fields |
| M-028 | Raw signature leaked | must be absent |
| M-029 | Internal notes leaked | must be absent |
| M-030 | Production deployment command executed automatically | must never occur |

### If deadline exists

| ID | Scenario | Expected |
|---|---|---|
| MD-001 | Claim before deadline | success |
| MD-002 | Claim after deadline | revert |
| MD-003 | Recovery before deadline | revert |
| MD-004 | Recovery after deadline by authorized owner | success |
| MD-005 | Recovery by unauthorized wallet | revert |
