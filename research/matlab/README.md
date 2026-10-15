# Moodify MATLAB Research Laboratory

**Status:** EXPERIMENTAL  
**Runtime:** MATLAB R2023b or newer  
**Canon impact:** `CANON_CHANGE = NO`

This directory turns Moodify hypotheses into reproducible MATLAB studies with
measured data, charts, machine-readable metadata, and explicit pass/inconclusive
states. It is a research and evidence-generation layer, not a second Core, a
second Judge authority, or proof that an experimental result is production truth.

MATLAB is the preferred backend for research figures and new acoustic experiments.
The publication and credibility rules are defined in
[`FIGURE_STANDARD.md`](FIGURE_STANDARD.md).

## Run it

From MATLAB:

```matlab
cd('E:/moodify/research/matlab')
summary = run_all();
```

From PowerShell (headless):

```powershell
matlab -batch "cd('E:/moodify/research/matlab'); run_all"
```

Outputs are written to `outputs/<campaign>/<iteration>/<study>/` and include
CSV data, PNG charts, MAT workspaces, and JSON results. `outputs/` is intentionally
ignored by Git because generated artifacts must not enter the repository.
Each study uses an explicit `mt19937ar` random stream seeded from the campaign
configuration so a recorded iteration can be reproduced.

## Long campaign

```matlab
cfg = moodifylab.defaultConfig();
cfg.maxIterations = Inf;
cfg.maxDurationHours = 24 * 30;
cfg.pauseSeconds = 60;
cfg.campaignName = "wavefield_month_01";
summary = moodifylab.runCampaign(cfg);
```

The runner writes `campaign_status.json` after every study. Create a file named
`STOP` in this directory to stop cleanly between studies. On a cloud machine,
keep generated outputs on attached storage and version only reviewed, compact
evidence artifacts through the repository's evidence process.

## Initial studies

| ID | Question | Boundary |
|---|---|---|
| `S001` | How much error does a 24-bit WAV write/read transport introduce? | Engineering baseline; not a perceptual claim |
| `S002` | Can two microphone channels uniquely determine a 3D wavefield? | Constructive non-uniqueness counterexample; simulated free field only |
| `S003` | How sensitive are binary Judge decisions to a threshold? | Synthetic calibration example; thresholds are not production values |

## Adding a study

Add a function under `studies/` with signature `result = studyXXX_name(ctx)`,
register it in `+moodifylab/runStudy.m`, and write every claimed metric to the
study output directory. A result must say `PASS`, `FAIL`, or `INCONCLUSIVE` and
must state its limitations.

Private audio belongs in `data/private/` (ignored). Never commit private audio,
secrets, or large generated results.

## Production feedback loop

MATLAB experiments may be prompted by a production case, but the experiment and
the delivery decision remain separate. The first documented loop is
[`2026-10-11_STEM_RECONSTRUCTION_CONSERVATIVE_REPAIR.md`](../../docs/production/cases/2026-10-11_STEM_RECONSTRUCTION_CONSERVATIVE_REPAIR.md).
It records why score transcription is not automatically tuning authority, why
full-vocal resynthesis requires a no-op roundtrip gate, and why local conservative
repair must retain an original/A/B listening decision. Use the reusable
[`STEM_RECONSTRUCTION_CHECKLIST.md`](../../docs/production/templates/STEM_RECONSTRUCTION_CHECKLIST.md)
when preparing the next song.
