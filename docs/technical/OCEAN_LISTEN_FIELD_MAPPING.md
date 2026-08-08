# Ocean → Moodify Field Mapping

| Ocean field | Moodify field | Status |
|---|---|---|
| `classification` | `classification` | sensor observation |
| `bpm` | `global_features.bpm` | observed |
| `key` | `global_features.key` | observed |
| `segments` | `global_features.energy_segments` | observed |
| `brightnessTrend` | `global_features.brightness_trend` | heuristic |
| `percussiveRatio` | `global_features.percussive_ratio` | measured feature |
| `vocalCoverage` | `global_features.vocal_coverage` | measured feature |
| `instruments` | `global_features.instruments` | model inference |
| `notes` | `notes` | model inference |
| `velocity` | `model_confidence_proxy` | **not loudness** |
| `dynamics.mean_rms` | note acoustic energy | measured |
| `stemTimeline` | `stems.activity_timeline` | inferred from separated stems |
| `stemNotes` | `stems.notes` | model inference |
| `unifiedTimeline` | `stems.unified_timeline` | derived |
| `voiceProfile` | `voice.profile` | experimental |
| `f0Data` | `voice.f0` | model estimate |
| `vibrato` | `voice.vibrato` | experimental |
| `voiceSegments` | `voice.segments` | experimental label |
| `voiceTimbre` | `voice.timbre` | experimental label |
| `voiceTexture` | `voice.texture` | experimental label |
| `speechAnalysis` | `voice.speech` | experimental |
| `lyrics` | `lyrics` | external/model source |
| `spectrogram` | `artifacts[]` | visual evidence |

## Critical semantic correction

Ocean's raw MIDI `velocity` comes from basic-pitch confidence. It must not be
used as an acoustic-loudness value. The bridge keeps the original field for
traceability and adds:

- `model_confidence_proxy`;
- `acoustic_energy_score`, when RMS exists;
- `evidence_score`;
- `selection_status = candidate`.

The bridge never destructively removes notes.
