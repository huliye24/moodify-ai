# Task Specification
## Contribution Network

### 1. Mission

Build the first contribution economy for Moodify Protocol.

The system must separate four concepts:

1. **Task** — what the protocol needs.
2. **Submission** — what a participant did.
3. **Reputation** — non-transferable contribution history.
4. **MOOD Allocation** — provisional token reward for approved work.

Do not collapse these into one generic "points" table.

### 2. Public route

Create:

`/contribute`

Required sections:

#### A. Contribution overview
Explain:
- what contributors can do;
- how review works;
- how Reputation differs from MOOD;
- that MOOD allocation is not guaranteed until approved;
- that contribution rewards are not investment returns.

#### B. Task catalog
Show active tasks with:

- title;
- category;
- short description;
- difficulty/effort indicator if approved by project design;
- reward points;
- provisional MOOD reward;
- status;
- deadline if any;
- number of submissions if public;
- eligibility requirements.

#### C. Task detail
Show:

- full task description;
- acceptance criteria;
- expected evidence;
- reward logic;
- review process;
- deadline;
- terms/version;
- submit CTA.

#### D. Submission flow
Allow participant to submit:

- short summary;
- evidence URL(s);
- text evidence;
- optional GitHub PR/commit URL;
- optional file reference if existing upload infrastructure supports it.

Do not add arbitrary file storage if current project does not support it safely.

#### E. My contributions
Participant can see:

- submitted;
- under review;
- changes requested;
- approved;
- rejected;
- Reputation earned;
- pending MOOD allocation;
- audit/history.

### 3. Contribution categories v1

Use a controlled enum/config:

```text
code
audio-testing
dataset
research
documentation
translation
bug-report
community
other
```

Do not allow arbitrary category strings in production.

### 4. Task statuses

Recommended:

```text
draft
active
paused
completed
archived
```

Public users should only see appropriate public statuses.

### 5. Submission statuses

Recommended:

```text
submitted
under_review
changes_requested
approved
rejected
withdrawn
```

Required transition validation:

```text
submitted → under_review
under_review → changes_requested
under_review → approved
under_review → rejected
changes_requested → submitted
submitted → withdrawn
```

Do not silently overwrite review history.

### 6. Reputation

Reputation is:

- non-transferable;
- off-chain in v1;
- tied to participant identity;
- append-only through reputation events;
- not a token;
- not redeemable 1:1 automatically unless future canon says so.

Recommended participant field:

```text
reputation_score
```

But the source of truth must be `reputation_events`.

Each event:

```text
id
participant_id
submission_id
event_type
points_delta
reason
created_at
actor_id
```

Aggregate score may be cached but must be reproducible from events.

### 7. MOOD reward model

Package 006 supports **pending MOOD allocation** only.

It must not send tokens automatically.

Each approved submission may produce a reward event:

```text
reward_events
```

Suggested fields:

```text
id
participant_id
submission_id
task_id
reward_mood
reward_atomic
status
reason
created_at
approved_by
distribution_snapshot_id_optional
```

Recommended status:

```text
pending
included_in_snapshot
distributed
cancelled
```

Package 006 should only create `pending` after approval.

Package 004/005 or later distribution runs may consume these reward events.

### 8. Reward exactness

MOOD decimals = 18.

Use exact arithmetic.

Never use floating point for MOOD rewards.

Task reward may be:
- fixed;
- bounded;
- admin-set on approval.

Preferred v1:
- fixed suggested reward on task;
- reviewer confirms final reward at approval;
- changes require reason + audit.

Do not create algorithmic dynamic pricing based on MOOD market price.

### 9. Task creation/admin

Create secure admin tooling consistent with Package 003.

Preferred route:

`/admin/contributions`

Admin can:

- create task;
- edit draft;
- publish/activate task;
- pause;
- archive;
- review submissions;
- request changes;
- approve/reject;
- assign final Reputation points;
- assign final pending MOOD reward;
- view participant history;
- view audit history.

Every sensitive mutation must be server-authorized.

### 10. Task fields

Recommended logical fields:

```text
id
slug
title
summary
description
category
status
requirements
evidence_instructions
reward_points_default
reward_mood_default
reward_mood_atomic_default
deadline_optional
max_approvals_optional
terms_version
created_by
created_at
updated_at
published_at
```

Optional future fields should not be overbuilt.

### 11. Submission fields

Recommended:

```text
id
task_id
participant_id
status
summary
evidence_text
evidence_urls_json
submitted_at
updated_at
reviewed_at
reviewer_id
review_note
revision_number
```

Avoid storing duplicated sensitive profile data.

### 12. Review history

Create append-only review events:

```text
contribution_review_events
```

Fields:

```text
id
submission_id
actor_id
event_type
old_status
new_status
points_delta
reward_mood
reason
created_at
```

No normal UI delete.

### 13. Anti-abuse rules

At minimum:

- participant must be registered;
- duplicate submission to same task can be limited/configured;
- max approvals can be enforced;
- self-review prohibited unless explicitly allowed in dev;
- reviewer cannot approve malformed evidence;
- obvious duplicate evidence may be flagged;
- rate limit submission creation;
- exact wallet identity comes from Genesis registration, not user-entered wallet text.

Do not create pseudo-Sybil metrics using trading behavior.

### 14. GitHub contribution support

If GitHub connector/API integration already exists in repo, or can be added cleanly:
- allow PR/commit evidence links;
- validate URL shape;
- optionally store repository/PR metadata.

Do not require GitHub OAuth for v1 unless existing auth makes it easy.

Package 006 must remain usable for non-code contributions.

### 15. Audio-testing contribution support

Support a category-specific evidence schema only if consistent with current Moodify audio workflow.

Examples:
- test session ID;
- listening test result ID;
- uploaded report ID;
- benchmark result link.

Do not fabricate audio-scoring functionality.

### 16. Dataset/research contributions

Allow evidence links and structured metadata where useful.

Do not accept content rights implicitly.

If dataset contributions may include licensing/IP:
- display a clear rights/permission acknowledgment;
- record terms version;
- do not assume Moodify owns uploaded content.

### 17. Public reputation profile

Optional but recommended:

`/contributors/[participantNumber]`

Public fields only:

- Genesis Participant #;
- public display name if opted in;
- Reputation score;
- approved contribution count;
- approved categories;
- badges if derived from real events.

Do not expose:
- wallet unless participant consent/public policy allows it;
- internal notes;
- rejected submission reasons unless designed public;
- signatures;
- nonces;
- admin identity.

If privacy policy is unclear, skip public profile in v1 and keep `/contribute` + "My Contributions".

### 18. Dashboard metrics

Admin dashboard:

- active tasks;
- submissions awaiting review;
- approved submissions;
- total Reputation issued;
- pending MOOD allocation;
- top contribution categories;
- pending rewards not yet snapshotted.

Public metrics should be factual and not gamified excessively.

### 19. Integration with Package 003

Participant identity:
- reuse Genesis Participant;
- do not create second wallet identity system.

Allocation:
- Package 003 provisional allocation may represent Genesis allocation;
- Package 006 rewards must be distinguishable from Genesis allocation.

Recommended separation:
- Genesis allocation remains in existing field/event;
- contribution rewards live in `reward_events`.

Do not overwrite Genesis allocation with contribution rewards.

### 20. Integration with Package 004/005

Package 006 must expose a deterministic query/export for pending approved rewards that future distribution snapshots can consume.

Recommended script/API:

```text
npm run contributions:rewards-export
```

Output:

```text
participant_number
wallet_address
reward_mood
reward_atomic
source_reward_event_ids
```

Do not merge into Package 004 automatically unless existing architecture already supports distribution batches.

### 21. Documentation

Create:

`docs/protocol/CONTRIBUTION_NETWORK.md`

Document:
- contribution model;
- categories;
- status lifecycle;
- Reputation semantics;
- MOOD reward semantics;
- admin review;
- anti-abuse;
- privacy;
- distribution handoff.

### 22. Explicit non-goals

Do not implement:
- auto token transfers;
- staking;
- yield;
- buy-to-earn;
- trade-to-earn;
- referral farming;
- NFT rewards;
- DAO voting;
- complex quadratic reputation;
- on-chain reputation;
- automated AI-only approval;
- dynamic token pricing;
- social spam tasks.
