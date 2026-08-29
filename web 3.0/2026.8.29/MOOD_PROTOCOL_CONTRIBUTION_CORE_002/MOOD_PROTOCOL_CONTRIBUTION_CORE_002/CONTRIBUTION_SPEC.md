# Contribution Record Specification

## Required record

```json
{
  "schemaVersion": "1.0.0",
  "contributionId": "mood-contrib-...",
  "contributor": {
    "type": "wallet",
    "id": "0x..."
  },
  "category": "code",
  "title": "Short human-readable title",
  "description": "What changed and why it matters",
  "submittedAt": "2026-08-29T00:00:00Z",
  "evidence": [],
  "status": "submitted",
  "policyVersion": "draft",
  "contentFingerprint": "sha256:...",
  "review": null,
  "scores": null,
  "reputationEvidence": null,
  "supersedes": null
}
```

## Immutable fields after submission

At minimum:

- schemaVersion
- contributor identity
- category
- submittedAt
- original evidence content
- contentFingerprint

Additional evidence may be appended only via a recorded evidence amendment.

Never silently rewrite original evidence.

## Finalized record

Once finalized:

- no field may be mutated in place;
- corrections require a new record;
- the new record must point to the old record through `supersedes`;
- history must remain inspectable.

## Categories

Category eligibility and scoring rules belong in versioned policy.

The schema should validate category syntax while policy validates eligibility.

## Contributor identity normalization

Wallet IDs:
- normalize according to the target chain's canonical public-address rules;
- never normalize a private key because private keys are forbidden;
- retain original public input only if needed for audit.

GitHub or other identity types, if used:
- pin the provider type;
- use stable public identity where possible;
- do not treat display name as identity.

## Time

Use UTC ISO-8601 timestamps in canonical stored records.

Do not use local timezone-dependent timestamps for fingerprints.

## Superseding

Use:

```json
{
  "supersedes": "mood-contrib-old-id"
}
```

A superseding record must never erase the previous record.
