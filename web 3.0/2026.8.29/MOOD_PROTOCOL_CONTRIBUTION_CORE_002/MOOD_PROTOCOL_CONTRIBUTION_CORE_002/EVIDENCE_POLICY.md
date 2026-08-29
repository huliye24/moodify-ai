# Evidence Policy

## Principle

Every material contribution claim must be backed by evidence that another reviewer can inspect.

## Evidence object

Recommended shape:

```json
{
  "evidenceId": "evidence-...",
  "type": "git_commit",
  "uri": "https://...",
  "digest": "sha256:...",
  "observedAt": "2026-08-29T00:00:00Z",
  "metadata": {},
  "verification": {
    "status": "unverified",
    "method": null,
    "verifiedAt": null,
    "verifiedBy": null
  }
}
```

## Evidence classes

### Code

Possible evidence:
- commit SHA
- PR URL
- diff hash
- passing CI/test artifact

### Documentation / research / design

Possible evidence:
- immutable file hash
- repository path + commit SHA
- content-addressed artifact
- approved review

### Data

Possible evidence:
- dataset manifest
- content hash
- provenance description
- license/provenance proof
- validation report

Never upload private or unlicensed data just to satisfy evidence.

### Compute

Possible evidence:
- job identifier
- provider-neutral compute receipt
- workload hash
- output artifact hash
- public or redacted billing/usage evidence where appropriate

Do not require secrets or billing credentials.

### Infrastructure

Possible evidence:
- IaC commit
- reproducible deployment manifest
- monitoring/test artifact
- public endpoint verification where safe

## Verification states

```text
unverified
verified
rejected
inconclusive
```

Machine verification must state the rule used.

Human verification must state reviewer identity or repository-authorized reviewer reference.

## Minimum evidence

Policy decides minimum evidence by category.

A contribution with no evidence cannot become `verified`.

## External links

External URLs are references, not truth.

Where practical, record:
- stable identifier
- content hash
- commit SHA
- timestamp

## Sensitive material

Never place in evidence:
- private key
- seed phrase
- API secret
- session cookie
- unredacted credential
- private user audio/data without explicit authority
