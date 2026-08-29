# MFY-CR-P02 — Constitution Decisions

Decisions fixed in P02 (all recorded formally in
`docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md` and its policy documents).

## 1. Product definition

```text
Moodify = a reconstruction-first listening environment（以云端重建为核心的听觉环境）
User experience = Choose -> Reconstruct -> Play
```

## 2. Layer responsibilities

| Layer | Responsibility |
|---|---|
| Moodify Ear | internal intelligence: listen, represent, judge, evidence, uncertainty, decide when NOT to intervene |
| Moodify Reconstruction Cloud | controlled intervention: diagnose, decide, stereo-first processing, optional stems, reconstruct, rebounce, verify |
| Moodify Listening Environment | playback, decode, device/output adaptation, song-specific rendering, local library; future encrypted playback |

## 3. Classic Reconstruction definition

> Controlled modernization of a recording's technical realization while
> preserving its artistic identity, historical character and essential musical
> intent. 经典音乐重建，是在保存作品艺术身份、时代气质与核心创作意图的前提下，对其技术实现进行受控的现代化。

Forbidden readings: AI remake, AI cover, re-generation, voice replacement,
automatic mastering, simple remaster preset, universal enhancement,
"make old songs modern".

## 4. Decision model

```text
PRESERVE       — detected feature belongs to identity/period aesthetic; do not modify
RECONSTRUCT    — sufficient evidence of a recoverable technical limitation; may enter controlled processing
BYPASS         — not enough reason processing is better; keep original signal
HUMAN_REQUIRED — machine cannot safely distinguish artistic choice vs technical limitation; escalate
```

Default state is PRESERVE/BYPASS; `UNKNOWN` never resolves to a stronger preset.

## 5. Uncertainty principle

> Uncertainty should reduce intervention, not increase it.
> 不确定时，少做，而不是多做。

`UNKNOWN → BYPASS` or `HUMAN_REQUIRED`; `UNKNOWN → strongest preset` is forbidden.

## 6. Stereo-first

`Stereo-first, stems-on-demand` is formal policy. Stems allowed only when:
(1) limitation cannot be addressed safely in stereo; (2) benefit > artifact risk;
(3) result verifiable. Reasons recorded: monetary cost, artifacts, bleed damage,
stereo-visible limitations, separation is a means not identity.
"For every track must be separated" is forbidden.

## 7. Identity doctrine

`Preserve Identity Before Improve Sound` — six requirements formalized
(explicit target, explainable reason, verifiable before/after, no identity
damage, rollback on failure, uncertainty may bypass).

## 8. No universal modernization

All-louder / brighter / wider / cleaner / more-compressed / heavier-bass /
more-forward-vocals are forbidden as universal defaults. Presets are
**intervention candidates**, never truth; `clean_master` is not the default
product answer.

## 9. Reconstruction vs Remaster

Reconstruction is **decision-led**, not preset-led:
`Listen -> Understand -> Identify limitation -> Identify identity -> Decide ->
Intervene only if justified -> Verify -> Render`.

## 10. Authority placement

```text
Human instruction
  ↓
Root AGENTS authority (updated minimally)
  ↓
Classic Reconstruction Constitution (new, docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md)
  ↓
Auditory/Production canonical docs (unchanged)
  ↓
Runtime behavior/tests
  ↓
Experimental docs
  ↓
Historical docs
```

No second ProductionCase / Evidence / state machine was created.

## 11. Future concepts (recorded, NOT_AUTHORIZED_IN_P02)

device-specific EQ, HRTF, headphone profiles, adaptive room correction,
proprietary container, encrypted playback, private-key music objects,
¥1 per reconstruction, official Moodify Edition, catalogue licensing.

## 12. North Star

> **Does this make the song better to hear without making it less itself?**
> 它是否让这首歌更好听，同时仍然是它自己？
