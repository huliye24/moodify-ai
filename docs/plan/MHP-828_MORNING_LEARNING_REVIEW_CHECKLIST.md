# MHP-828: Morning Learning Review Checklist

**Status**: done
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-SYSTEM-044 / System Plan-6A: Standardization / P2 (Execution)
**Depends on**: MHP-827
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Provide a structured checklist for the operator's morning review of last night's data loop output.

## Morning Learning Review Checklist

### 1. Runtime Health (30 seconds)

- [ ] Task success rate ≥ 95%? ___ / ___ = ___%
- [ ] Fatal errors? If yes, note root cause: _____________
- [ ] Missing artifacts? List: _____________
- [ ] Queue depth healthy? Pending: ___ Done: ___ Failed: ___

### 2. Scoring Calibration (1 minute)

- [ ] Score direction agreement rate ≥ 85%? ___%
- [ ] Disagreeing presets (list): _____________
- [ ] Max sign-disagreement magnitude: ___
- [ ] Any new presets showing disagreement for the first time? Yes / No

**Action**: If agreement rate < 85% for 2+ consecutive nights, schedule an MRS calibration session.

### 3. Craft/Preset Quality (1 minute)

- [ ] Flag rate ≤ 30%? ___%
- [ ] Flag types observed: _____________
- [ ] Any preset triggered the same flag 3+ nights in a row? Yes / No
- [ ] Per-preset delta stats show drift? Yes / No

**Action**: If a preset triggers the same flag 3+ nights, block it for the affected sample class until review.

### 4. Operator Decision (1 minute)

- [ ] Decision: PASS / HOLD / REWORK
- [ ] If HOLD: what's blocking? _____________
- [ ] If REWORK: what needs to change in the pipeline? _____________
- [ ] Next MHP direction: _____________

### 5. Learning Trends (1 minute)

- [ ] Compared to last night: improvement / stable / regression
- [ ] Agreement rate trend (last 3 nights): ___ → ___ → ___
- [ ] Flag rate trend (last 3 nights): ___ → ___ → ___
- [ ] Task success rate trend (last 3 nights): ___ → ___ → ___

### 6. Actions for Tonight

- [ ] Top action from recommendations: _____________
- [ ] Any preset to block or promote? _____________
- [ ] Any scoring weight to adjust? _____________
- [ ] Queue size for tonight: ___ tasks

### Sign-Off

- Operator: _____________
- Date: _____________
- Time to complete review: ___ minutes

## Acceptance Criteria

- Checklist covers all four optimization loops. ✅
- Each section has concrete metrics with thresholds. ✅
- Trend tracking is explicit (3-night window). ✅
- Sign-off block is present. ✅
