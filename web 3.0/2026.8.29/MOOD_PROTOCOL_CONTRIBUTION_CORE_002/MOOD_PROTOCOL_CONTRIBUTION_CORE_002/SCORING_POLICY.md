# Scoring Policy Boundary

## Required dimensions

MPF-002 recognizes five score dimensions:

| Dimension | Meaning |
|---|---|
| contribution | amount / substance of work |
| impact | protocol usefulness or reach |
| quality | correctness, rigor, maintainability |
| persistence | sustained or repeated contribution |
| early | early-stage contribution factor |

## Important distinction

These are **reputation dimensions**, not token amounts.

Do not use terminology such as:
- payout
- APY
- reward amount
- claim amount
- token entitlement

inside the core scoring output.

## Score representation

Recommended:

```json
{
  "quality": {
    "value": 82,
    "scale": "0-100",
    "ruleId": "quality.v1",
    "evidenceIds": ["evidence-1"],
    "source": {
      "type": "human_review",
      "id": "reviewer-public-id"
    }
  }
}
```

## Aggregation

If an authoritative repository policy already specifies approved weights:
- reuse them;
- pin exact policy version;
- test them.

If approved weights do not exist:
- DO NOT invent them;
- preserve all five dimension scores;
- set aggregate to `null`;
- policy status remains `draft`;
- report `HUMAN_DECISION_REQUIRED`.

## Persistence

Persistence must not be guessed from one contribution.

It should be derived from auditable history, such as:
- accepted contribution count in a defined window;
- active contribution periods;
- repeated verified work.

The exact formula must live in versioned policy.

## Early

"Early" must use an objective epoch or protocol milestone boundary.

It must not depend on whether a reviewer personally considers someone "early".

## Manual scores

Manual scoring is allowed only when:
- the dimension genuinely needs judgment;
- reviewer and evidence are recorded;
- score scale is bounded;
- policy version is pinned.

## Score reproducibility

Machine-derived scores must be reproducible.

Human-derived scores must be auditable even if they are not mathematically reproducible.
