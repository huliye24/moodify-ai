# MFY-CR-P05 — Guard Model

## Guard states

```text
PASS            no change beyond the identity boundary observed
CAUTION         change approaching the boundary (no clear breach)
HUMAN_REQUIRED  machine cannot distinguish artistic improvement vs identity drift
REJECT          clear boundary breach or technical destruction
NOT_MEASURABLE  no reliable method for this dimension (v0.1: IG-03)
```

## Overall decision (veto semantics, no averaging)

```text
Any REJECT                     -> REJECT
Any HUMAN_REQUIRED, or
  IG-03 unmeasured + any change-> HUMAN_REQUIRED
Any CAUTION (measured)         -> CAUTION
otherwise                      -> PASS
```

- A critical identity failure can never be averaged away
  (REJECT + everything-PASS still REJECTs).
- In v0.1 IG-03 is always NOT_MEASURABLE, so any non-PASS dimension escalates
  to HUMAN_REQUIRED: PASS_WITH_CAUTION overall is unreachable by design until
  a validated reverb detector exists. Documented, not a bug.
- SOURCE is always a legal result. If A/B/C all drift: SOURCE wins.

## Per-dimension triggers (v0.1, PROVISIONAL budgets)

| Trigger | State |
|---|---|
| IG-01 mid-band proxy drift > budget | HUMAN_REQUIRED |
| IG-02 dynamic flattening (LRA/crest/PLR) beyond budget | REJECT |
| IG-02 approaching budget (60 %) | CAUTION |
| IG-03 (always) | NOT_MEASURABLE |
| IG-04 width/side boost beyond budget; mono→wide | REJECT |
| IG-05 low-end boost beyond budget | REJECT |
| IG-06 loudness jump > 3 LU; new clipping introduced | REJECT |
| IG-06 loudness approaching 1.5 LU | CAUTION |

## Human review escalation

When overall = HUMAN_REQUIRED the verdict carries the minimal question set
(human never sees 50 metrics):

```text
Q1. Does this still sound like the same recording?
Q2. Did any core character disappear?
Q3. Does anything sound artificially modernized?
Q4. Is the improvement worth the change?
Q5. SOURCE / A / B / C preference?
```

Answers vocabulary: SAME / SLIGHT_DRIFT / CLEAR_DRIFT / UNSURE.
