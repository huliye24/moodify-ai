# TOMORROW STUDIO RUNBOOK — 2026-08-01 Commercial Recording Session

**Prepared:** 2026-07-31 by DSK-MFY-STUDIO-PREP-004
**Tool Version:** 0.1.0
**Status:** READY_WITH_LIMITS — requires engineer review before use

---

## Phase 0 — Before Leaving Home (30 min before departure)

- [ ] Verify laptop battery charged; bring charger
- [ ] Verify external SSD available and formatted (NTFS/exFAT)
- [ ] Verify audio interface and cables packed
- [ ] Print or screenshot this runbook
- [ ] Confirm session brief YAML is ready (use template: `tools/studio_session_prep/templates/session_brief.example.yaml`)

## Phase 1 — Arrival at Studio (first 30 min)

- [ ] Power on all equipment; verify signal path
- [ ] Launch DAW; set project to agreed sample rate (default: **48 kHz / 24-bit**)
- [ ] Test record 10s silence; verify file format (WAV)
- [ ] **Run `session-init`** to create session directory and manifest:
  ```powershell
  cd E:\moodify
  python -m tools.studio_session_prep.studio_prep session-init \
    --brief <path/to/brief.yaml> \
    --output-dir D:/studio_session/<session-date>
  ```
- [ ] Review the generated `RECORDING_DAY_CHECKLIST.md` in the session directory
- [ ] Configure DAW naming template to match the spec
- [ ] Test record with performer; verify peak < -6 dBFS target
- [ ] Confirm headphone mixes for all performers

## Phase 2 — Each Recording Take

- [ ] Announce take number verbally (recorded in audio)
- [ ] Record at least 3s pre-roll silence
- [ ] Monitor input meters during entire take (peak < -6 dBFS)
- [ ] After stop: immediately save/name file according to naming template
- [ ] **Run `asset-verify`** on the recorded file:
  ```powershell
  python -m tools.studio_session_prep.studio_prep asset-verify \
    --manifest D:/studio_session/<date>/manifest.json \
    --output-dir D:/studio_session/<date>/verify_take<N>
  ```
- [ ] Note any issues (clicks, dropouts, distortion) in session notes
- [ ] If take is bad: mark as rejected in notes; do NOT delete file

## Phase 3 — After Recording Session (before leaving studio)

- [ ] Verify all planned takes are recorded and verified
- [ ] **Run WSE analysis on reference takes** (optional, for immediate feedback):
  ```powershell
  python -m tools.studio_session_prep.studio_prep wse-analyze \
    --input <path/to/take.wav> \
    --output-dir D:/studio_session/<date>/wse_analysis
  ```
- [ ] Generate candidate plans (informational only at this stage):
  ```powershell
  python -m tools.studio_session_prep.studio_prep candidate-plan \
    --wse-profile D:/studio_session/<date>/wse_analysis/wse_profile.json \
    --output-dir D:/studio_session/<date>/candidate_plans
  ```
- [ ] Write session notes: performer comments, noteworthy moments, issues

## Phase 4 — Backup Before Leaving Studio

- [ ] **Backup 1 (SSD):** Copy entire session directory to external SSD
- [ ] **Backup 2 (NAS/Cloud):** Copy to second location if available
- [ ] Verify backup: run `asset-verify` on a sample of backed-up files
- [ ] Lock/read-only all original take files
- [ ] Confirm no files left in temp/scratch locations
- [ ] Photograph physical log (whiteboard, notes, DAW screenshot)
- [ ] Sign off: engineer confirms all deliverables captured

## Phase 5 — Post-Production (next day or later)

1. **Ingest** assets from backup to processing workstation
2. **WSE Analyze** all takes:
   ```powershell
   python -m tools.studio_session_prep.studio_prep wse-analyze \
     --input <take.wav> --output-dir <output/wse_takeN>
   ```
3. **Generate Candidate Plans** for each take:
   ```powershell
   python -m tools.studio_session_prep.studio_prep candidate-plan \
     --wse-profile <output/wse_takeN/wse_profile.json> \
     --output-dir <output/plans_takeN>
   ```
4. **Generate Candidates** (EXPLICIT STEP — requires `--execute-candidates` flag):
   ```powershell
   # Dry-run first (default, no audio processed):
   # Use candidate_adapter.run_all_candidates() from Python directly
   
   # To actually execute:
   python -c "
   from tools.studio_session_prep.candidate_adapter import run_all_candidates
   run_all_candidates('<source.wav>', '<plans/candidate_plans.json>', '<output/candidates>', execute=True)
   "
   ```
5. **Compare Candidates:**
   ```powershell
   python -m tools.studio_session_prep.studio_prep candidate-compare \
     --candidates-dir <output/candidates> \
     --output-dir <output/comparison>
   ```
6. **Human Review** (MANDATORY):
   - Loudness-match all candidates
   - Listen on at least 2 systems (monitors + headphones)
   - Fill out `human_review.md` checklist
   - Do NOT assume louder = better
7. **Build Report:**
   ```powershell
   python -m tools.studio_session_prep.studio_prep report-build \
     --manifest <session/manifest.json> \
     --wse-profile <wse/wse_profile.json> \
     --comparison <comparison/comparison.json> \
     --output-dir <output/reports>
   ```
8. **Deliver:** Export selected candidate + report package to client

## Degradation / Fallback Procedures

| Situation | Action |
|-----------|--------|
| **Clipping detected** | Reduce input gain; set target peak to -10 dBFS; re-record |
| **High noise floor** | Check cables, preamp, grounding; note in session log |
| **Phase issues (L/R correlation < 0.3)** | Check mic placement, cable polarity; flag take for mono check |
| **Take lost/deleted** | Check backup immediately; if not backed up, re-record |
| **Tool dependency failure** | Use manual checklist (`RECORDING_DAY_CHECKLIST.md`) + offline SHA-256 (`certutil -hashfile`) + paper notes |
| **pyloudnorm not available** | LUFS will be null in WSE profile; use RMS as proxy (documented as proxy, not standard) |
| **Candidate processing fails** | Error recorded in run_info.json; workflow can continue with other candidates |

## Important Warnings

1. **Commercial delivery decisions must be made by the engineer, not the tool.** Moodify does not auto-select Final.
2. **LRA, true peak, phase, and masking are unavailable.** Null values do not indicate safety.
3. **Spectral differences are technical measurements, not subjective quality ratings.**
4. **Loudness-match before any A/B listening comparison.** Louder ≠ better.
5. **All candidate plans are processing hypotheses.** They require human review and explicit `--execute-candidates`.

---

**Runbook prepared by:** DSK-MFY-STUDIO-PREP-004 (automated pipeline)
**Next action:** Review this runbook with the recording engineer before the session.
