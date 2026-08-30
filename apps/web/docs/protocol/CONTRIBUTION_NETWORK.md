# Moodify Protocol — Contribution Network

**Package:** `MOOD-GENESIS-006`  
**Version:** `v1.0.0`  
**Status:** Active  
**Last Updated:** 2026-08-27

---

## 1. Overview

The Contribution Network is Moodify Protocol's first contribution economy. It establishes a complete workflow for participants to earn **Reputation** and **pending MOOD rewards** through useful protocol work.

### Core Principle

MOOD should be earned through useful protocol contribution, not artificial trading behavior.

### Workflow

```
Task → Submission → Review → Reputation → Pending MOOD Reward
```

**Important:** No automatic token transfer occurs in this package. All MOOD rewards remain in `pending` status until included in a future distribution snapshot.

---

## 2. Concepts

### 2.1 Task

A Task represents work that the protocol needs. Tasks are created by admins and include:

- Title, summary, and description
- Category (code, audio-testing, dataset, research, documentation, translation, bug-report, community, other)
- Requirements and evidence instructions
- Default reward points and MOOD amount
- Optional deadline and max approvals cap

### 2.2 Submission

A Submission represents what a participant did to complete a Task. Submissions include:

- Summary of work completed
- Evidence text (free-form description)
- Evidence URLs (up to 10 links, including GitHub PR/commit URLs)
- Revision number (incremented on resubmission)

### 2.3 Reputation

Reputation is:
- **Non-transferable** — tied to the participant's identity
- **Off-chain** in v1 — stored as events in the database
- **Append-only** — never deleted, only adjusted via new events
- **Not a token** — cannot be traded or transferred

The source of truth is the `reputation_events` table. The `reputation_score` field on `genesis_participants` is a cached aggregate that must equal the sum of all `points_delta` for that participant.

### 2.4 MOOD Allocation

Pending MOOD rewards are:
- Recorded in `reward_events` with status `pending`
- Not automatically transferred to wallets
- Consumable by future distribution snapshots (Package 004/005)
- Exact arithmetic using 18 decimal places

---

## 3. Status Models

### 3.1 Task Status

| Status | Description |
|--------|-------------|
| `draft` | Task is being prepared, not visible to public |
| `active` | Task is open for submissions |
| `paused` | Task temporarily not accepting submissions |
| `completed` | Task finished, no more submissions accepted |
| `archived` | Task hidden from public catalog |

**Public visibility:** Only `active`, `paused`, and `completed` tasks are visible to the public.

### 3.2 Submission Status

| Status | Description |
|--------|-------------|
| `submitted` | Initial state, awaiting review |
| `under_review` | Admin is reviewing |
| `changes_requested` | Admin requested modifications |
| `approved` | Submission accepted, rewards recorded |
| `rejected` | Submission declined |
| `withdrawn` | Contributor cancelled submission |

**Valid Transitions:**
```
submitted → under_review
submitted → withdrawn
under_review → changes_requested
under_review → approved
under_review → rejected
changes_requested → submitted (resubmission)
```

### 3.3 Reward Status

| Status | Description |
|--------|-------------|
| `pending` | Awaiting inclusion in distribution snapshot |
| `included_in_snapshot` | Added to a distribution batch |
| `distributed` | Tokens transferred to wallet |
| `cancelled` | Reward voided (with audit record) |

---

## 4. Data Model

### 4.1 contribution_tasks

| Field | Type | Description |
|-------|------|-------------|
| `id` | text | Primary key (UUID) |
| `slug` | text | Unique URL-friendly identifier |
| `title` | text | Task title |
| `summary` | text | Short description |
| `description` | text | Full description |
| `category` | text | Controlled enum (see §2.1) |
| `status` | text | Task status |
| `requirements` | text | Requirements text |
| `evidence_instructions` | text | How to submit evidence |
| `reward_points_default` | integer | Default reputation points |
| `reward_mood_default` | text | Default MOOD reward (decimal) |
| `reward_mood_atomic_default` | text | Default MOOD (atomic units) |
| `deadline` | text | Optional ISO timestamp |
| `max_approvals` | integer | Optional approval cap |
| `allow_duplicate_submissions` | boolean | Allow multiple submissions per participant |
| `terms_version` | text | Terms acknowledged |
| `created_by` | text | Admin actor ID |
| `created_at` | text | Timestamp |
| `updated_at` | text | Timestamp |
| `published_at` | text | When first activated |

### 4.2 contribution_submissions

| Field | Type | Description |
|-------|------|-------------|
| `id` | text | Primary key (UUID) |
| `task_id` | text | FK to contribution_tasks |
| `participant_id` | text | FK to genesis_participants |
| `status` | text | Submission status |
| `summary` | text | Work summary |
| `evidence_text` | text | Free-form evidence |
| `evidence_urls_json` | text | JSON array of URLs |
| `revision_number` | integer | Submission version |
| `submitted_at` | text | Timestamp |
| `updated_at` | text | Timestamp |
| `reviewed_at` | text | When last reviewed |
| `reviewer_id` | text | Admin actor ID |
| `review_note` | text | Reviewer comment |

### 4.3 contribution_review_events

Append-only audit log of all review actions.

| Field | Type | Description |
|-------|------|-------------|
| `id` | text | Primary key |
| `submission_id` | text | FK to submission |
| `actor_id` | text | Who performed the action |
| `event_type` | text | created, status_change, changes_requested, approved, rejected, withdrawn, reopened, reward_change |
| `old_status` | text | Previous status (if applicable) |
| `new_status` | text | New status (if applicable) |
| `points_delta` | integer | Reputation points awarded |
| `reward_mood` | text | MOOD reward (decimal) |
| `reward_atomic` | text | MOOD reward (atomic) |
| `reason` | text | Explanation |
| `created_at` | text | Timestamp |

### 4.4 reputation_events

Source of truth for Reputation scores.

| Field | Type | Description |
|-------|------|-------------|
| `id` | text | Primary key |
| `participant_id` | text | FK to genesis_participants |
| `submission_id` | text | Optional FK to submission |
| `event_type` | text | approval, rollback, manual_adjust |
| `points_delta` | integer | Can be positive or negative |
| `reason` | text | Explanation |
| `actor_id` | text | Admin who recorded |
| `created_at` | text | Timestamp |

### 4.5 reward_events

Pending MOOD reward ledger.

| Field | Type | Description |
|-------|------|-------------|
| `id` | text | Primary key |
| `participant_id` | text | FK to genesis_participants |
| `submission_id` | text | FK to submission |
| `task_id` | text | FK to task |
| `reward_mood` | text | MOOD amount (decimal) |
| `reward_atomic` | text | MOOD amount (atomic) |
| `status` | text | pending, included_in_snapshot, distributed, cancelled |
| `reason` | text | Approval reason |
| `approved_by` | text | Admin actor ID |
| `distribution_snapshot_id` | text | Set when included in batch |
| `created_at` | text | Timestamp |

---

## 5. Exact Arithmetic

MOOD uses 18 decimal places. All reward calculations must use exact integer arithmetic.

### Conversion

```
atomic = floor(decimal * 10^18)
```

### Storage

- `reward_mood`: Human-readable decimal string (e.g., "100.5")
- `reward_atomic`: Integer string in atomic units (e.g., "100500000000000000000")

### Validation

- Negative rewards are rejected
- Rewards exceeding 30 characters are rejected
- Floating-point arithmetic is never used for token amounts

---

## 6. Anti-Abuse Controls

### 6.1 Prohibited Rewards

The system must NOT reward:
- Trading volume
- Buying MOOD
- Holding MOOD
- Fake referrals
- Wallet farming
- Social spam

### 6.2 Controls

| Control | Implementation |
|---------|------------------|
| Registration required | Only Genesis Participants can submit |
| Duplicate submissions | Configurable per-task; blocked by default |
| Max approvals | Optional per-task cap |
| Self-review | Prohibited (admin cannot approve own submission) |
| Rate limiting | Built into submission creation |
| Evidence validation | URLs validated, max 10 links |
| Genesis allocation separation | Contribution rewards never overwrite Genesis allocation |

---

## 7. API Endpoints

### 7.1 Public Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/contribution/tasks` | GET | List active tasks |
| `/api/contribution/tasks/[idOrSlug]` | GET | Get task detail |
| `/api/contribution/submissions` | GET | List my submissions (requires address param) |
| `/api/contribution/submissions` | POST | Create new submission |
| `/api/contribution/me` | GET | Get participant info and reputation |

### 7.2 Admin Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/contribution/admin/tasks` | GET | List all tasks |
| `/api/contribution/admin/tasks` | POST | Create new task |
| `/api/contribution/admin/tasks/[idOrSlug]` | GET | Get task detail |
| `/api/contribution/admin/tasks/[idOrSlug]` | PUT | Update task |
| `/api/contribution/admin/submissions` | GET | Review queue with filters |
| `/api/contribution/admin/submissions/[id]` | GET | Submission detail |
| `/api/contribution/admin/submissions/[id]/transition` | POST | Review action (approve/reject/etc) |
| `/api/contribution/admin/submissions/[id]/note` | POST | Append internal note |
| `/api/contribution/admin/metrics` | GET | Dashboard metrics |

---

## 8. Reward Export

### Command

```bash
npm run contributions:rewards-export
```

### Output Format (CSV)

```csv
participant_number,wallet_address,reward_mood,reward_atomic,source_reward_event_ids
1,0x1BB3115D43E397f7bb586F090831B02cA639e73E,100.0,100000000000000000000,uuid1;uuid2
```

### JSON Companion

```json
{
  "schema": "moodify-contribution-rewards-v1",
  "generatedAt": "2026-08-27T00:00:00.000Z",
  "sourceGitCommit": "abc123...",
  "summary": {
    "participants": 10,
    "rewardEvents": 15,
    "totalMood": "1500.0",
    "totalAtomic": "1500000000000000000000"
  },
  "rewards": [...]
}
```

---

## 9. Integration

### 9.1 Genesis Identity (Package 002)

- Reuses Genesis Participant identity
- No separate wallet identity system
- Wallet address comes from Genesis registration

### 9.2 Admin Authorization (Package 003)

- Uses existing admin authentication
- Server-side authorization enforced
- Admin identity recorded in audit events

### 9.3 Distribution (Package 004/005)

- `reward_events` table is the handoff point
- Distribution snapshots consume `pending` rewards
- After distribution, status updated to `distributed`

---

## 10. Privacy

### Public Data

- Task catalog (active tasks only)
- Participant's own submissions
- Participant's Reputation score
- Participant's pending MOOD (own only)

### Private Data (Admin only)

- Internal review notes
- Draft tasks
- Rejected submission reasons
- Admin identity details

### Never Exposed

- Wallet signatures
- Nonces
- Raw private keys
- Other participants' submission details

---

## 11. Human Policy Gates

Before enabling public production rewards, human protocol leadership should approve:

1. Task categories and descriptions
2. Reward ranges and maximums
3. Total contribution reward budget per epoch
4. Who can review submissions
5. Whether contributor profiles are public
6. Evidence/IP terms
7. Distribution cadence

If these are not approved, the system:
- Continues to function with development fixtures
- Keeps production reward publishing disabled
- Reports the missing policy

---

## 12. Safety Statement

**MOOD-GENESIS-006 does NOT:**
- Automatically transfer MOOD tokens
- Sign transactions
- Request private keys
- Deploy reward contracts
- Implement staking/yield
- Make token-price promises
- Use market price in reward formula
- Auto-approve high-value rewards solely with AI
- Overwrite Genesis allocation with contribution rewards

---

## 13. Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | 2026-08-27 | Initial release |

---

## See Also

- `MOOD-GENESIS-002`: Genesis Participant Registration
- `MOOD-GENESIS-003`: Admin Authorization
- `MOOD-GENESIS-004`: Distribution Engine
- `MOOD-GENESIS-005`: Airdrop & Treasury
