# Reputation Attestation Policy

## Purpose

Allow a reviewer or authorized verifier to attest that a reputation snapshot corresponds to specific inputs and policy.

## Example

```json
{
  "attestationVersion": "1.0.0",
  "snapshotId": "mood-rep-...",
  "snapshotFingerprint": "sha256:...",
  "attestor": {
    "type": "protocol_reviewer",
    "id": "public-reviewer-id"
  },
  "method": "repository_record",
  "createdAt": "...",
  "evidence": []
}
```

## MPF-003 boundary

Attestation may be:
- local signed artifact if repository already has safe signing infrastructure;
- repository commit evidence;
- reviewer record.

Do not require blockchain attestation.

Do not request wallet private keys.

## What attestation does NOT mean

It does not automatically:
- raise reputation;
- grant governance;
- grant MOOD;
- grant ownership;
- create payout rights.
