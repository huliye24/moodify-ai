# MOOD CONTRIBUTION 016 — Anti-Abuse

**Authority:** 016 TASK.md Phase N

## v1 protections

| Vector | Protection |
|--------|-----------|
| Self-review | `isSelfReview()` rejects (INV-016-02). |
| Spam submissions | `MAX_OPEN_SUBMISSIONS_PER_RESIDENT = 5`. |
| Bad evidence URLs | `validateEvidence()` rejects `javascript:`, `data:`, `file:`. |
| Duplicate approval | Submission ID tracked; second approval is a no-op (INV-016-09). |
| Duplicate reward | One reward per submission (INV-016-05). |
| Duplicate reputation | One reputation grant per submission (INV-016-04). |
| Reviewer note leak | Public serializers strip `reviewerNote` (INV-016-10). |
| Self-issued verified role | Out of scope — belongs to 015 Passport. |
| Plagiarised evidence | Out of scope — requires content moderation. |
| Bot flood | Out of scope — requires rate-limit middleware. |
| Multiple wallets per resident | Allowed by design — many `WalletIdentity` per `Resident`. |

## Limits

- 20 evidence items per submission.
- 5 open (non-terminal) submissions per Resident.
- Length caps per evidence type.

## What 016 does NOT do

- ❌ Persistent rate limiting.
- ❌ IP-based throttling.
- ❌ Wallet reputation scoring.
- ❌ Bot detection.
- ❌ Wallet-deduplication enforcement (Resident may bind multiple wallets).

These belong to 022 (Security) and 017 (Observatory). 016 deliberately does
not block on them; it documents the gap.