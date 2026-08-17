# Reconstruction Boundaries

**Part of:** [CLASSIC_RECONSTRUCTION_CONSTITUTION.md](CLASSIC_RECONSTRUCTION_CONSTITUTION.md) (v1.0)
**Status:** LIVE

This document defines the boundary between what may be changed and what must be preserved, and the decision model used at every reconstruction step.

---

## 1. Artistic Identity（艺术身份）

Artistic identity is the set of qualities that make a recording itself. It is **preserved by default** and includes, without limitation:

- singer identity, vocal timbre, phrasing, vibrato, emotional delivery;
- melody, harmony;
- arrangement identity, instrument character, groove;
- intentional saturation, intentional distortion, intentional reverb;
- intentional stereo placement;
- period-specific aesthetic;
- deliberate lo-fi texture;
- deliberate dynamic behavior.

These must not be modified merely because "modern standards look more advanced".

## 2. Technical Limitation（可恢复的技术限制）

A technical limitation is a defect of the recording chain, not of the performance. It includes, without limitation:

- transfer noise;
- accidental hiss / hum;
- recoverable bandwidth loss;
- avoidable masking;
- clipped or damaged transfers;
- encoding artifacts;
- unnecessary phase defects;
- limited low-end extension caused by the technical chain;
- intelligibility loss;
- accidental stereo collapse;
- recoverable dynamics damage;
- medium / transfer limitations.

> **Technical limitation is not equivalent to oldness. 老，不等于错。**

Oldness alone is never a justification for intervention.

## 3. Four-State Decision Model

Every candidate intervention resolves to exactly one state:

### PRESERVE
The feature is detected but belongs to the recording's artistic identity or period aesthetic. **Do not modify.**

### RECONSTRUCT
There is sufficient evidence that the feature is a recoverable technical limitation. It may enter controlled processing.

### BYPASS
There is not enough reason to believe processing would be better. **Keep the original signal.**

### HUMAN_REQUIRED
The machine cannot safely distinguish artistic choice from technical limitation. **Escalate to human judgment.**

### Decision rules

1. Default state is **PRESERVE / BYPASS** — intervention must earn its way in.
2. `UNKNOWN` must never resolve to a stronger preset; it resolves to `BYPASS` or `HUMAN_REQUIRED`.
3. A `HUMAN_REQUIRED` decision must be surfaced, never suppressed to keep the loop unattended.

## 4. Reconstruction vs Remaster

Traditional automatic mastering is preset-led:

```text
Stereo → EQ → Compression → Limiter → Loudness
```

Moodify reconstruction is decision-led:

```text
Listen → Understand → Identify limitation → Identify identity
  → Decide → Intervene only if justified → Verify → Render
```

> **Reconstruction is decision-led, not preset-led.**

## 5. Evidence Philosophy

Every reconstruction should be able to answer:

```text
What limitation was identified?
What evidence supported it?
What was changed?
Why was it safe to change?
What was preserved?
What changed after processing?
Did any guardrail fail?
Was human review required?
```

(P02 defines these questions only; the Evidence schema itself is not changed by this document.)
