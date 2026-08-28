# Test Matrix
## Genesis Admin

| ID | Scenario | Expected |
|---|---|---|
| A-001 | Unauthorized user opens admin | denied |
| A-002 | Authorized admin opens admin | allowed |
| A-003 | Search wallet | correct participant |
| A-004 | Search participant # | correct participant |
| A-005 | Filter registered | correct subset |
| A-006 | registered → reviewed | success + audit |
| A-007 | reviewed → eligible | success + audit |
| A-008 | reviewed → rejected | success + audit |
| A-009 | invalid transition | rejected |
| A-010 | score 0 → 10 | success + audit |
| A-011 | negative score | rejected |
| A-012 | allocation 0 → 1000 | success + audit |
| A-013 | negative allocation | rejected |
| A-014 | malformed allocation | rejected |
| A-015 | pool ceiling exceeded | rejected |
| A-016 | concurrent allocations near ceiling | total never exceeds ceiling |
| A-017 | reject allocated participant | explicit safe handling required |
| A-018 | add internal note | visible to admin |
| A-019 | public API attempts notes | notes absent |
| A-020 | CSV export | deterministic valid rows |
| A-021 | JSON export | deterministic schema/version |
| A-022 | export contains raw signature | must fail test / absent |
| A-023 | export contains internal note | must fail test / absent |
| A-024 | audit event edit | unsupported/denied |
| A-025 | audit event delete | unsupported/denied |
| A-026 | 1000 participants | usable table/pagination |
| A-027 | existing Package 002 rows after migration | preserved |

### Manual admin smoke test

1. sign in as authorized admin;
2. open `/admin/genesis`;
3. verify counts;
4. open Participant #0001;
5. mark reviewed with reason;
6. mark eligible with reason;
7. set contribution score;
8. set provisional allocation;
9. inspect audit timeline;
10. export CSV;
11. inspect export for sensitive-data leakage;
12. sign out;
13. verify route is no longer accessible.
