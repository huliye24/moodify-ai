# MHP-449: Acoustic CT Visual Grammar Spec

**Status**: completed
**Direction**: ECHAIN-MOODIFY-ACOUSTIC-CT-007 / NEM-MOODIFY-ACOUSTIC-CT-SYSTEM-023 / System Plan-6A: Visual Standardization / S1 (Execution)
**Depends on**: MHP-448
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Context

Moodify should produce visual diagnostic evidence the way medical imaging produces a scan sheet. Raw audio needs a pre-treatment acoustic scan PDF, processed audio needs a post-treatment scan PDF, and operators need a visual before/after report that makes treatment depth and quality risk immediately visible.

## Goal

Complete `Acoustic CT Visual Grammar Spec` as a state-converting AEP for Acoustic CT reporting. The work should make audio quality easier to inspect, compare, explain, and archive.

## Expected Output

`reports/echain_moodify_acoustic_ct_007/mhp_449_acoustic_ct_visual_grammar_spec.md`

## Execution Notes

- Treat the PDF as an internal industrial diagnostic artifact, not a marketing page.
- Prefer objective visual plates: spectrogram, frequency balance, waveform dynamics, stereo image, loudness, transient risk, and MRS/gate overlays.
- Ensure raw scan and processed scan share the same visual scale where comparison matters.
- Preserve compatibility with Runtime report bundles, MRS scoring, Craft Memory, and Operator Console.

## Acceptance Criteria

- The expected output exists or the HOLD reason is documented.
- The visual result can be regenerated from command/config/input paths.
- The report makes at least one treatment effect easier to see than numeric metrics alone.
- The next MHP can start without reconstructing context.

## Brand Requirement

The visual grammar must define brand placement, logo clear space, page header hierarchy, and diagnostic plate layout.

Canonical logo asset:

```text
assets/brand/moodify_logo_symbol_original_white_canvas_1254.png
```
