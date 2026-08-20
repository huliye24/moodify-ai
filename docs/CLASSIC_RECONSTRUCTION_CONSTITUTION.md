# Classic Reconstruction Constitution

**Version:** 1.0
**Date:** 2026-08-17
**Status:** LIVE — the canonical product-and-technology constitution of the Classic Reconstruction phase (MFY-CR-P02)
**Authority:** root `AGENTS.md` → this constitution → auditory/production canonical docs
**Supersedes for product definition:** any earlier document that claims Moodify's outward product is "The Ear of AI". Ear remains the internal foundation (see below).
**Related:** [RECONSTRUCTION_BOUNDARIES.md](RECONSTRUCTION_BOUNDARIES.md) · [ARTISTIC_IDENTITY_POLICY.md](ARTISTIC_IDENTITY_POLICY.md) · [STEREO_FIRST_POLICY.md](STEREO_FIRST_POLICY.md) · [LISTENING_ENVIRONMENT_ARCHITECTURE.md](LISTENING_ENVIRONMENT_ARCHITECTURE.md) · [PHASE1_CONSTITUTION.md](PHASE1_CONSTITUTION.md) (internal data foundation, unchanged)

---

## Article I — Identity

Moodify is a **reconstruction-first listening environment**（以云端重建为核心的听觉环境）.

Its public experience is:

```text
Choose
  ↓
Reconstruct
  ↓
Play
```

Moodify's internal intelligence remains rooted in auditory understanding. The Ear is the brain of reconstruction, not the product surface.

## Article II — Ear

Moodify Ear is **internal auditory intelligence**. It exists to:

- listen;
- represent;
- judge;
- preserve evidence;
- express uncertainty;
- decide whether intervention is justified;
- know when **not** to intervene.

Ear is not required to be a public product. The product is the hearing experience, not the measurement surface.

## Article III — Reconstruction

Classic Reconstruction is:

> **the controlled modernization of a recording's technical realization while preserving its artistic identity, historical character, and essential musical intent.**

经典音乐重建，是在保存作品艺术身份、时代气质与核心创作意图的前提下，对其技术实现进行受控的现代化。

It is **not**:

- AI remake;
- AI cover;
- re-generation;
- voice replacement;
- automatic mastering;
- simple remaster preset;
- universal enhancement;
- "make old songs modern".

## Article IV — Identity

Artistic identity has priority over technical improvement.

If an improvement damages identity:

> reject the improvement.

Identity cannot be traded away because "modern standards look more advanced".

## Article V — Uncertainty

Uncertainty reduces intervention（不确定时，少做，而不是多做）.

When uncertain:

```text
BYPASS
or
HUMAN_REQUIRED
```

not:

```text
stronger processing
```

`UNKNOWN → apply strongest preset` is forbidden.

## Article VI — Stereo First

Stereo is the default source of truth（stereo-first, stems-on-demand）.

Stem separation is invoked only when:

1. a specific limitation cannot be addressed safely in stereo;
2. separation is likely to create more benefit than artifact risk;
3. the result can be verified.

Reasons: separation has monetary cost; separation can introduce artifacts; bleed can damage identity; many era limitations are stereo-visible; separation is a means, not a product identity.

Forbidden: "every track must be separated".

## Article VII — No Uniform Modernity

Modern does not mean louder, brighter, wider, cleaner, heavier or more compressed.

Moodify does not force every recording into one contemporary aesthetic. `clean_master` and every other preset are **intervention candidates**, never default truth.

## Article VIII — Evidence

Every intervention should be able to answer:

- what limitation was identified;
- what evidence supported it;
- what was changed;
- why it was safe to change;
- what was preserved;
- what changed after processing;
- whether any guardrail failed;
- whether human review was required.

## Article IX — Human Authority

Machines may detect, estimate, rank and propose.

Machines do not automatically possess final artistic authority. One authoritative ProductionCase / Evidence / state machine and human listening authority remain as defined in root `AGENTS.md` and `PHASE1_CONSTITUTION.md` — this constitution creates no second authority system.

## Article X — Listening Environment

Reconstruction creates the source for Moodify playback.

The Listening Environment determines how that source reaches a real device and a real listener:

```text
Reconstruction
  ↓
Rendering
  ↓
Device
  ↓
Human Hearing
```

The final product is not the file. The final product is the hearing experience. **Reconstruction result ≠ final hearing result.**

## Article XI — Product Simplicity

Internal complexity does not justify interface complexity.

The user should not be forced to understand stems, LUFS, phase, spectral descriptors, evidence graphs, model versions or processing plans. The system handles complexity so the user can press:

> Play.

## Article XII — North Star

> **Does this make the song better to hear without making it less itself?**

它是否让这首歌更好听，同时仍然是它自己？

Any reconstruction capability that cannot answer this question cannot automatically enter production.

---

## Decision Model

The four-state model is defined in [RECONSTRUCTION_BOUNDARIES.md](RECONSTRUCTION_BOUNDARIES.md):

```text
PRESERVE
RECONSTRUCT
BYPASS
HUMAN_REQUIRED
```

## Future Concepts

Recorded but not authorized in this phase:

```text
FUTURE
NOT_AUTHORIZED_IN_P02
```

- device-specific EQ
- HRTF / headphone profiles / adaptive room correction
- proprietary container / encrypted playback / private-key music objects
- ¥1 per reconstruction / official Moodify Edition / catalogue licensing
