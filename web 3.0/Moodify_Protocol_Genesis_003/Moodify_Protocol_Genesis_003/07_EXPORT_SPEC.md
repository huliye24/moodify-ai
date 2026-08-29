# Export Specification
## Genesis Admin v1

Exports produced by Package 003 are inputs for human review and Package 004.

They are **not** transaction files.

## CSV

Recommended headers:

```text
participant_number
wallet_address
status
contribution_score
allocation_mood
joined_at
updated_at
```

Sort order:

1. participant_number ascending.

Encoding:

UTF-8.

No localized number formatting in canonical export.

Example:

```csv
participant_number,wallet_address,status,contribution_score,allocation_mood,joined_at,updated_at
1,0x...,allocated,10,1000,2026-08-26T12:00:00Z,2026-08-26T13:00:00Z
```

## JSON

Suggested:

```json
{
  "schema": "moodify-genesis-admin-export-v1",
  "exportedAt": "...",
  "participants": []
}
```

Participant fields:

- participantNumber
- walletAddress
- status
- contributionScore
- allocationMood
- joinedAt
- updatedAt

## Forbidden export fields

Never include:

- raw wallet signature;
- nonce;
- internal admin note;
- admin session;
- auth token;
- IP address;
- private user profile data unrelated to distribution.

## Integrity metadata

Optional but recommended:

- rowCount
- totalAllocationMood
- sourceGitCommit
- schemaVersion
