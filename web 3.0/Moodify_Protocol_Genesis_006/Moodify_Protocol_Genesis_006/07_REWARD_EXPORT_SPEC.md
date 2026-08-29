# Reward Export Specification
## Contribution Rewards v1

### Purpose

Export approved pending rewards so they can later be included in a controlled distribution snapshot.

This export is not a transaction file.

### Recommended command

```bash
npm run contributions:rewards-export
```

### Inclusion

Include reward events with:

```text
status = pending
reward_atomic > 0
```

Exclude:
- cancelled;
- already included in snapshot;
- distributed;
- invalid participant;
- missing wallet.

### Canonical aggregation

Multiple reward events for the same participant may be aggregated for distribution, but source event IDs must remain traceable.

Recommended output:

```text
participant_number
wallet_address
reward_mood
reward_atomic
source_reward_event_ids
```

Sort:
1. participant number ascending.

### JSON companion

Recommended:

```json
{
  "schema": "moodify-contribution-rewards-v1",
  "generatedAt": "...",
  "sourceGitCommit": "...",
  "summary": {
    "participants": 0,
    "rewardEvents": 0,
    "totalMood": "0"
  },
  "rewards": []
}
```

### Integrity

Validate:
- wallet uniqueness after aggregation;
- event uniqueness;
- exact total;
- each event maps to approved submission;
- each participant exists;
- no reward already distributed.

### Privacy

Do not export:
- evidence body unless explicitly requested;
- internal review notes;
- signatures;
- nonces;
- admin session data.
