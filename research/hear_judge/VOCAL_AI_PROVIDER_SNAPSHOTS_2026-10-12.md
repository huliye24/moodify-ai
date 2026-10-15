# Vocal AI Provider Snapshots — 2026-10-12

**Status:** EXPERIMENTAL / INTERNAL RESEARCH  
**Canon change:** NO  
**Authority:** external models are replaceable Providers (Hands); Moodify Judge remains the only judgment authority.

## Purpose

The snapshots below support experiments on AI-singing naturalness, local vocal repair, singing-voice conversion and controlled vocal reconstruction. They are not integrated into Moodify Core and are not evidence that a processed vocal is better.

The working hypothesis is narrower than “all artificialness comes from vocals”:

- AI vocals often dominate perceived artificialness because identity, articulation, breath, pitch transition, timing and expression are coupled in one signal.
- Instrument and accompaniment defects can still matter and must not be excluded without evidence.
- A Provider output becomes a candidate only. It must preserve lyrics, melody, timing, identity and intended expression, then pass technical verification and loudness-matched blind comparison.

## Local snapshots

The repositories are shallow clones under ignored local storage:

`E:\moodify\third_party\vocal_ai\`

| Provider | Local directory | Source | Pinned commit | Code license | Intended experimental role |
|---|---|---|---|---|---|
| Amphion | `Amphion` | <https://github.com/open-mmlab/Amphion> | `26f6883110181f1dbfe95c70a7c7dbaf4de5f42a` | MIT | Primary research framework for singing voice editing, SVC, style conversion and controllable reconstruction. |
| DiffSinger | `DiffSinger` | <https://github.com/openvpi/DiffSinger> | `ba031f6f2f969373b49a926cf8b007e9ae48834f` | Apache-2.0 | Score-conditioned singing synthesis/reconstruction; useful when note, phoneme and timing control are required. |
| RVC WebUI | `RVC` | <https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI> | `81eed5e8f68b6bed1789f682fe78cdd324495afc` | MIT | Mature baseline for timbre conversion and artifact comparison; not a general naturalness repair guarantee. |
| Seed-VC | `Seed-VC` | <https://github.com/Plachtaa/seed-vc> | `51383efd921027683c89e5348211d93ff12ac2a8` | GPL-3.0 | Zero-shot singing voice conversion using a short reference; internal research candidate for vocal reconstruction. |

## License and model-weight boundary

- The table records repository code licenses only. Model weights, datasets, vocoders and subcomponents can have separate terms and must be checked before download or use.
- No model weights or datasets were downloaded in this snapshot step.
- Seed-VC is retained for internal research under GPL-3.0. It must not be copied into Moodify Core without a separate architecture and distribution review.
- Voice references require authorization. Identity cloning without the performer/rightsholder's permission is outside the allowed production workflow.

## Provider selection order for the first experiment

1. Use the isolated LALAL lead-vocal stem as the common input; do not diagnose vocal quality from the full mix alone.
2. Select one short, clearly defective phrase and preserve an untouched baseline excerpt.
3. Start with Amphion singing voice editing if the defect is local and the original identity should be retained.
4. Use Seed-VC as an independent reconstruction challenger only when an authorized reference voice exists.
5. Use DiffSinger only when score/phoneme-conditioned regeneration is justified; it is a larger intervention than local repair.
6. Keep RVC as a baseline/provider comparison, not as the default winner.
7. Loudness-match, anonymize and compare exactly one challenger against the current baseline.
8. Accept only if technical checks pass and no protected property is degraded; otherwise keep the original.

## Required evidence for every future run

- input audio hash and time range;
- Provider name, repository commit and model-weight identity/hash;
- environment, command/configuration, random seed and GPU/runtime;
- authorized reference identity and usage scope, when applicable;
- preservation targets: lyrics, melody, timing, singer identity, breath and expression;
- before/after objective checks and localized artifact findings;
- loudness-matched blind comparison result;
- final decision: accept challenger, retry, or keep original.

## Current factual status

The code snapshots are present. Dependencies, CUDA compatibility, model weights and inference have **not** been installed or verified. Therefore the Providers are `AVAILABLE_AS_SOURCE`, not `RUNNABLE` or `PRODUCTION_READY`.
