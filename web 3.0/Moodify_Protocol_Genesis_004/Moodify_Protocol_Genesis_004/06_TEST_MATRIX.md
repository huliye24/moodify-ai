# Test Matrix
## Distribution Engine

| ID | Scenario | Expected |
|---|---|---|
| D-001 | Valid allocated participants | snapshot succeeds |
| D-002 | DB rows returned in different order | same root |
| D-003 | Duplicate wallet | hard fail |
| D-004 | Same wallet different casing | hard fail as duplicate |
| D-005 | Duplicate participant number | hard fail |
| D-006 | Malformed EVM address | hard fail |
| D-007 | Rejected participant with allocation | excluded or fail per validated rule |
| D-008 | Reviewed but not allocated | excluded |
| D-009 | Zero allocation | excluded/fail consistently |
| D-010 | Negative allocation | hard fail |
| D-011 | 18 decimal amount | valid |
| D-012 | >18 decimals | hard fail |
| D-013 | Scientific notation | reject or explicit normalization |
| D-014 | Total equals pool ceiling | valid |
| D-015 | Total exceeds pool ceiling by 1 atomic unit | hard fail |
| D-016 | Wrong MOOD contract config | hard fail |
| D-017 | Wrong chain ID | hard fail |
| D-018 | Same dataset run twice | same root |
| D-019 | Every generated proof | verifies |
| D-020 | Modified claim amount with same proof | verification fails |
| D-021 | Modified wallet with same proof | verification fails |
| D-022 | Modified participant # with same proof | verification fails |
| D-023 | Existing snapshot ID, same data | explicit safe behavior |
| D-024 | Existing snapshot ID, changed data | refuse overwrite |
| D-025 | Dry run | no DB mutation / no chain write |
| D-026 | CSV export | deterministic |
| D-027 | JSON export | deterministic canonical rows |
| D-028 | Export includes internal note | must be absent |
| D-029 | Export includes signature/nonce | must be absent |
| D-030 | Manifest hash mismatch | validation fails |

### Manual review

Before any future production use:

1. generate dry run;
2. inspect participant count;
3. inspect total MOOD;
4. sample 3 wallet allocations;
5. compare against Genesis Admin;
6. verify root with local verifier;
7. inspect distribution report;
8. inspect checksums;
9. confirm no chain transaction occurred.
