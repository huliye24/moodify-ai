# Data Model
## Contribution Network

Adapt names/columns to existing Drizzle/D1 conventions.

### `contribution_tasks`

Suggested:

```text
id
slug
title
summary
description
category
status
requirements_json
evidence_instructions
reward_points_default
reward_mood_default
reward_mood_atomic_default
deadline
max_approvals
terms_version
created_by
created_at
updated_at
published_at
```

Constraints:
- unique slug;
- controlled category;
- controlled status;
- non-negative rewards;
- deadline nullable;
- max_approvals nullable/non-negative.

### `contribution_submissions`

```text
id
task_id
participant_id
status
summary
evidence_text
evidence_urls_json
revision_number
submitted_at
updated_at
reviewed_at
reviewer_id
```

Indexes:
- task_id
- participant_id
- status
- submitted_at

### `contribution_review_events`

Append-only:

```text
id
submission_id
actor_id
event_type
old_status
new_status
points_delta
reward_mood
reward_atomic
reason
created_at
```

### `reputation_events`

Append-only source of truth:

```text
id
participant_id
submission_id
event_type
points_delta
reason
actor_id
created_at
```

### `reward_events`

Append-only reward ledger:

```text
id
participant_id
submission_id
task_id
reward_mood
reward_atomic
status
reason
approved_by
created_at
distribution_snapshot_id
```

Allowed initial statuses:

```text
pending
included_in_snapshot
distributed
cancelled
```

### Aggregate fields

If `genesis_participants` has:

```text
contribution_score
```

it may be retained as a cached aggregate.

But source of truth is reputation events.

Add consistency tests:

```text
participant.contribution_score
==
SUM(reputation_events.points_delta)
```

where architecture supports materialized aggregate.

### Exact token storage

Preferred:
- store canonical human-readable decimal string if needed for UI;
- store `reward_atomic` as integer string;
- never rely on SQLite REAL.

### Migration rules

- additive;
- non-destructive;
- preserve all Genesis participant/admin/distribution data;
- do not renumber participants;
- do not rewrite previous allocations.
