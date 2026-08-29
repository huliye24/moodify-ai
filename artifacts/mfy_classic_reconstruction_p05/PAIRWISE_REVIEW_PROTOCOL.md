# MFY-CR-P05 — Pairwise Identity Review Protocol

Established (not executed in P05 — no human listening this session; recorded
for P06+ calibration).

## Dual question

Each pairwise comparison asks BOTH questions independently:

```text
Q_a. Which sounds better?
Q_b. Which preserves the original identity better?
```

The two answers may differ (e.g. "B sounds better; A preserves identity
better") — that divergence is exactly the trade-off Moodify must learn.

## Vocabulary

```text
SAME / SLIGHT_DRIFT / CLEAR_DRIFT / UNSURE
```

per candidate vs SOURCE, plus the five minimal questions from GUARD_MODEL.md.

## Integration

- Reuses the existing pairwise/human review machinery (补丁包09 pairwise
  engine, MFY-HUMAN-REVIEW-001) — no second review system.
- Identity review is a GATE: even if B sounds better, B with identity drift is
  not auto-approved.
- Review records feed threshold calibration (THRESHOLD_SOURCES.md).

## Real listening corpus (P06 plan)

3-5 legally-owned/authorized recordings with distinct character:
vocal-centered, dense arrangement, narrow stereo, dynamic recording,
noisy/old transfer. Manifest only in git — no commercial audio committed.
