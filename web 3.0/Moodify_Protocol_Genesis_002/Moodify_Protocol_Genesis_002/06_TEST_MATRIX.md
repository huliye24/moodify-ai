# Test Matrix
## Genesis Registration

| ID | Scenario | Expected |
|---|---|---|
| G-001 | Valid wallet, valid nonce, valid signature | participant created |
| G-002 | Same wallet registers again | existing participant returned or duplicate rejected safely |
| G-003 | Wrong signer signs message | rejected |
| G-004 | Wrong chain ID | rejected |
| G-005 | Expired nonce | rejected + retry possible |
| G-006 | Reused nonce | rejected |
| G-007 | Random/invalid nonce | rejected |
| G-008 | Malformed wallet address | rejected |
| G-009 | Signature altered after signing | rejected |
| G-010 | Message fields altered | rejected |
| G-011 | Two concurrent register requests same wallet | only one participant created |
| G-012 | Two users concurrently register | distinct participant numbers |
| G-013 | Wallet user rejects signature | UI recovers cleanly |
| G-014 | User disconnects mid-flow | UI returns safe state |
| G-015 | Network changes mid-flow | stale signature flow invalidated/restarted |
| G-016 | Server unavailable | actionable error shown |
| G-017 | Already registered wallet revisits | existing Participant ID shown |
| G-018 | Address checksum/casing differs | treated as same wallet |
| G-019 | Client submits fake allocation | ignored/rejected |
| G-020 | Client submits fake participant number | ignored/rejected |

### Security checks

- nonce entropy is sufficient;
- nonce TTL enforced server-side;
- uniqueness constraint tested;
- no secret or private key in git diff;
- no `eth_sendTransaction` required;
- no `approve()` interaction;
- no raw SQL built from untrusted input;
- no signature string interpolation ambiguity.

### Manual smoke test

Use a development/test wallet only.

1. open `/genesis`;
2. connect wallet;
3. switch to BNB Chain;
4. request registration;
5. inspect exact message;
6. sign;
7. verify Participant ID;
8. refresh;
9. verify same Participant ID;
10. attempt second registration and confirm no duplicate row.
