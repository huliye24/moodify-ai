# Database Schema
## Genesis Registration

Use the repository's existing Drizzle/D1 conventions if confirmed by audit.

### `genesis_participants`

Suggested logical fields:

```text
id
participant_number
wallet_address
wallet_address_normalized
joined_at
status
nickname_optional
contribution_score
allocation_mood
claim_status
signature_version
terms_version
created_at
updated_at
```

For Package 002, only fields needed by registration must be actively used.

Recommended initial values:

```text
status = registered
contribution_score = 0
allocation_mood = 0
claim_status = unallocated
```

Do not allow the client to set those values.

### `genesis_nonces`

Suggested fields:

```text
id
wallet_address_normalized
nonce
issued_at
expires_at
used_at
chain_id
terms_version
created_at
```

Nonce may be stored hashed if the implementation can still safely reconstruct/validate the signing message.

### Constraints

Required database guarantees:

```text
UNIQUE(genesis_participants.wallet_address_normalized)
UNIQUE(genesis_participants.participant_number)
UNIQUE(genesis_nonces.nonce)
```

Add indexes appropriate for:
- wallet lookup;
- nonce lookup;
- expiration cleanup.

### Participant numbering

Public IDs should be stable and monotonic.

Example display:

```text
Genesis Participant #0001
Genesis Participant #0002
```

The DB should store an integer participant number, while formatting with leading zeros happens in the UI.

Do not:
- use wallet address as participant number;
- use row count + 1 outside a transaction;
- recycle participant numbers after deletion.

### Migration

Create a non-destructive migration.

Before applying:
- inspect current D1 migration pattern;
- run migration locally/dev first if the project supports it;
- do not drop or rename unrelated tables.

### Data retention

Nonce rows may be periodically cleaned after expiration/use, but cleanup is not required in this package if it would expand scope.

Participant registrations are persistent protocol records.
