# Moodify MATLAB Figure Standard

**Status:** EXPERIMENTAL research standard  
**Backend:** MATLAB R2023b+  
**Scope:** research figures and new acoustic experiments

MATLAB is the preferred backend for Moodify research figures and new acoustic
experiments. Existing production Python code is not automatically invalidated or
rewritten. A MATLAB method must pass numerical, performance, and evidence-parity
checks before replacing an established Core implementation.

## Credibility contract

A credible figure must disclose:

1. the one-sentence conclusion it supports;
2. the source data or generating study;
3. physical units and coordinate definitions;
4. sample count and aggregation method;
5. uncertainty or an explicit `NOT_REPORTED` state;
6. calibration status;
7. limitations and failure conditions;
8. MATLAB version, random seed, and export timestamp.

MATLAB is a high-quality numerical and rendering environment. It is not, by
itself, evidence that a result is correct.

## Export contract

`moodifylab.saveFigure` produces all of the following from the same figure:

- 600 DPI PNG for review and web use;
- vector PDF for papers;
- editable-text SVG for design and publication workflows;
- MATLAB FIG for full editing;
- JSON figure manifest containing the scientific contract and runtime provenance.

Defaults are a white background, Arial, restrained 7.5–8 pt typography, outward
ticks, open axes, 0.75 pt axes, and at least 1.1 pt data lines. Color must encode
meaning consistently; red/green alone must not carry a scientific distinction.

## Analysis boundary

New WSE, MSE, acoustics, wavefield, calibration, sensitivity, and numerical
simulation studies should be authored in MATLAB when MATLAB offers the clearer or
more reliable method. Product runtime migration remains evidence-gated:

```text
MATLAB hypothesis
  -> reproducible study
  -> source data + figures + limitations
  -> comparison against current implementation
  -> human review
  -> optional Core migration
```

Research code must not become a second DSP or Judge authority merely because its
figures are publication quality.
