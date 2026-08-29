# Anti-Gaming Policy

## Goal

Reduce obvious manipulation without turning reputation into invasive surveillance.

## Required controls

### Eligible-state filter

Only approved MPF-002 terminal records may count.

### Duplicate-input guard

The same contribution ID/fingerprint cannot be counted twice.

### Cross-epoch reuse guard

A contribution cannot be counted as new work in multiple epochs unless policy explicitly treats it as continuing work.

### Reviewer provenance

Human-scored inputs retain reviewer source.

### Self-review observability

Self-review is flagged when policy requires independent review.

### Snapshot reproducibility

A high reputation snapshot must be reproducible from exact inputs.

### Identity-link caution

Do not merge two contributors because they seem similar.

## Not allowed

- covert device fingerprinting
- browser tracking
- biometric scoring
- social graph scraping
- private-message analysis
- KYC by default

## Suspicious case handling

Use:

```text
INCONCLUSIVE
NEEDS_REVIEW
INSUFFICIENT_EVIDENCE
```

rather than silent penalties.
