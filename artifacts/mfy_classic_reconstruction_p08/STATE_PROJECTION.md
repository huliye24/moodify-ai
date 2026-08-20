# MFY-CR-P08 — STATE PROJECTION

Product states are projections of the canonical ProductionCase lifecycle;
the canonical case is authoritative. The mapping below is enforced by the
engine (`engine.py`).

## Projection table

| Job status (product) | progress label | Canonical case lifecycle | Canonical authority | Meaning |
|---|---|---|---|---|
| QUEUED | Preparing | — (case not created yet) | — | accepted, waiting for worker |
| VALIDATING | Preparing | CREATED | SYSTEM | source checks + case binding |
| ANALYZING | Listening | ACTIVE | SYSTEM | decode/transcode |
| PLANNING | Reconstructing | ACTIVE | SYSTEM | objective planning (P04) |
| RECONSTRUCTING | Reconstructing | ACTIVE | SYSTEM | candidate rendering (P03-P05 chain) |
| VERIFYING | Verifying | ACTIVE | SYSTEM | identity guard + selection |
| HUMAN_REQUIRED | Verifying | AWAITING_HUMAN | HUMAN_REQUIRED | stopped; never auto-approved |
| SUCCEEDED | Ready | COMPLETED | ALGORITHM | candidate auto-selected |
| SOURCE_WINS | Ready | COMPLETED | ALGORITHM | original preserved (product result, not failure) |
| FAILED | Failed | FAILED (on case write) | SYSTEM | terminal failure |
| CANCELLED | Cancelled | CANCELLED | SYSTEM | operator/user cancel |

## Rules

- The product state never writes authority; it is derived at each stage
  boundary from pipeline outputs.
- `HUMAN_REQUIRED` is a stopping state: no automatic approval path exists.
  The operator CLI `review` makes the explicit decision (recorded as
  `HUMAN_APPROVED` authority state).
- Cancel: QUEUED/VALIDATING -> CANCELLED immediately; in-flight stages set
  `cancel_requested`, the engine checks at every stage boundary and stops
  before starting the next stage.

## Selection semantics (P04/P05 mapped to product)

1. Auto-approvable candidate (identity PASS/CAUTION + hard gates passed) and
   no MEDIUM-confidence objective entered planning -> SUCCEEDED (top candidate).
2. MEDIUM-confidence objective entered planning -> HUMAN_REQUIRED (P04:
   minimal-only + human review), even if a candidate looks auto-approvable.
3. No auto candidate but identity guard asks for review -> HUMAN_REQUIRED.
4. Otherwise -> SOURCE_WINS (no safe candidate; original preserved).

Per-candidate HUMAN_REQUIRED/REJECT disqualifies only that candidate — an
auto-approvable alternative still wins (P05 semantics).
