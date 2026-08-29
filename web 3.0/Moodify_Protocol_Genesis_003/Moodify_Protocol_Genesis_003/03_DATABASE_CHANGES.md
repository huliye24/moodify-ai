# Database Changes
## Genesis Admin

Adapt to current Drizzle/D1 conventions.

Package 002 is expected to have:

- `genesis_participants`
- `genesis_nonces`

Package 003 adds or extends:

## `genesis_participants`

Ensure support for:

```text
status
contribution_score
allocation_mood
updated_at
```

Do not trust client defaults.

Suggested initial values:

```text
status = registered
contribution_score = 0
allocation_mood = 0
```

## `genesis_admin_events`

Suggested logical schema:

```text
id
participant_id
actor_id
event_type
field_name
old_value
new_value
reason
metadata_json
created_at
```

Indexes:

- participant_id
- actor_id
- created_at
- event_type

## `genesis_admin_notes`

Suggested:

```text
id
participant_id
actor_id
body
created_at
```

Indexes:

- participant_id
- created_at

### Constraints

Recommended:

- participant foreign key where supported;
- contribution score >= 0;
- allocation >= 0;
- controlled status enum/check strategy compatible with D1/SQLite;
- audit rows not cascade-deleted accidentally.

### Migration rules

- non-destructive;
- preserve Package 002 registration data;
- do not recreate participant IDs;
- do not renumber existing participants;
- do not alter wallet uniqueness semantics.

### Transaction rules

Sensitive admin mutation should atomically:

1. read current value;
2. validate change;
3. update participant;
4. append audit event.

If atomic transaction support is constrained by deployment/runtime, document exact consistency model and implement safest available equivalent.
