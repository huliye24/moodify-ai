# Decay and Persistence

## Persistence

Persistence is intended to distinguish:

```text
one-time contribution
```

from:

```text
sustained verified participation
```

## Minimum evidence

A persistence score should require multiple time-separated verified contributions or an approved longitudinal rule.

If there is insufficient history:

```text
persistence = null
persistenceStatus = INSUFFICIENT_HISTORY
```

Do not award a positive persistence score simply because one contribution exists.

## Decay

Do NOT introduce reputation decay by default.

Decay is a governance/policy choice and can strongly affect contributor rights later.

If an existing approved decay policy exists, reuse it.

Otherwise:

```text
decayEnabled = false
HUMAN_DECISION_REQUIRED if decay is requested
```

## Why

Historical contribution should not silently disappear because a developer stopped contributing for a short period.

Current activity can later be represented separately from historical reputation.
