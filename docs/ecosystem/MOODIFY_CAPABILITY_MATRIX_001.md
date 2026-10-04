# Moodify Capability Matrix 001

> **Status:** Strategy input — **not** runtime truth.
> **Companion to:** `MOODIFY_CAPABILITY_ECOSYSTEM_MAP_001.md`
> **Baseline:** read-only audit of `codex/ecosystem-001-capability-map` @ `01edc902`, 2026-10-04
> **Provider columns** are *candidates to evaluate*, never adopted dependencies.

**Legend**

```text
Status    CANONICAL · IMPLEMENTED_NOT_CANONICAL · PARTIAL · EXPERIMENTAL · ABSENT · LEGACY
Posture   BUILD · INTEGRATE · DELEGATE · DEFER
Diff      integration difficulty: LOW · MED · HIGH · N/A
Priority  P0 (blocks the Agent layer) · P1 (needed soon) · P2 (later) · P3 (not now)
Type      library · CLI · model · API · binary · standard · DAW · protocol
```

---

## A. Capability table

| Capability ID | Domain | Current Status | Posture | Candidate Provider | Type | L/C | Input | Output | License | Diff | Pri | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `audio.decode` | INGEST | CANONICAL | BUILD | ffmpeg / ffprobe | binary | Local | file | samples + probe | LGPL/GPL build-dependent | — | P0 | Already canonical; subprocess arg arrays, never shell strings |
| `audio.probe` | INGEST | CANONICAL | BUILD | ffprobe | binary | Local | file | container/stream facts | as above | — | P1 | Recorded as `FileProbe` |
| `audio.convert` | INGEST | PARTIAL | INTEGRATE | ffmpeg | binary | Local | audio | audio | as above | LOW | P1 | Only WAV transcode exists today; no lame/opus/aac |
| `metadata.read` | INGEST | PARTIAL | INTEGRATE | mutagen / ffprobe | library / binary | Local | file | tags | MIT / as above | LOW | P2 | Only internal JSON metadata; **no ID3/Vorbis/MP4 tags anywhere** |
| `stem.separate` | SEPARATE | EXPERIMENTAL | **INTEGRATE** | `adefossez/demucs` v4.1.0 | model | Local | audio | 4 stems | **MIT** (code+weights) | MED | **P0** | Maintained fork, not the Meta repo; v4.1.0 dropped torchaudio for inference |
| `stem.separate` (cloud) | SEPARATE | IMPLEMENTED_NOT_CANONICAL | INTEGRATE | LALAL.AI API v1 | API | Cloud | audio | ≤10 stems | commercial, **SINGLE_SOURCE_ACCEPTED** | LOW | P1 | `stems/client.py` exists; `CONNECTED_UNTESTED`; per-stem billing |
| `vocal.extract` | SEPARATE | PARTIAL | INTEGRATE | htdemucs_ft | model | Local | audio | vocal | MIT | LOW | P1 | Best-in-family vocal SDR; LALAL splitter as cloud fallback |
| `accompaniment.extract` | SEPARATE | PARTIAL | INTEGRATE | demucs (residual) | model | Local | audio | instrumental | MIT | LOW | P2 | Cheap once `stem.separate` exists |
| `audio.analyze` | UNDERSTAND | **CANONICAL** | **BUILD** | own | library | Local | audio | metric record | GPL-3.0-only | — | **P0** | The trust layer. 31 registered metrics, 5 authority classes |
| `loudness.measure` | UNDERSTAND | CANONICAL | BUILD | own (BS.1770-5 / EBU 3341) | standard | Local | audio | LUFS | GPL-3.0-only | — | P0 | **Oracle-verified** vs pyloudnorm + ffmpeg ebur128 (HOTFIX 000) |
| `level.meter` | UNDERSTAND | CANONICAL | BUILD | own (BS.1770-5 true peak) | standard | Local | audio | dBFS | GPL-3.0-only | — | P1 | 4× oversampled; documented as a close approximation |
| `stereo.analyze` | UNDERSTAND | CANONICAL | BUILD | own | library | Local | audio | correlation/width | GPL-3.0-only | — | P1 | |
| `spectrum.analyze` | UNDERSTAND | CANONICAL | BUILD | own (STFT) | library | Local | audio | descriptors + PNG | GPL-3.0-only | — | P1 | Registry labels several entries ESTIMATOR/PROXY — honest |
| `rhythm.analyze` | UNDERSTAND | **PARTIAL** | **INTEGRATE** | `madmom-infer` / `beat_this` | library | Local | audio | tempo, beats, downbeats | BSD code; **madmom weights CC BY-NC-SA** | MED | **P0** | `tempo_bpm` field exists, **never assigned**; grep `beat_track` = 0 hits |
| `harmony.analyze` | UNDERSTAND | **ABSENT** | INTEGRATE | `madmom-infer` / `lv-chordia` | model | Local | audio | chord segments | see rhythm row | HIGH | P1 | No chord/key code in `moodify/` core |
| `structure.analyze` | UNDERSTAND | **PARTIAL** | **INTEGRATE** | `all-in-one-infer` | model | Local | audio | labelled sections | verify (bundles demucs-infer) | HIGH | **P0** | `StructureContext` exists; **0 construction sites** |
| `instrument.identify` | UNDERSTAND | ABSENT | INTEGRATE | PANNs CNN14 | model | Local | audio | instrument tags | verify (AudioSet-derived) | MED | P2 | 527 classes; YAMNet if speed beats accuracy |
| `pitch.analyze` | UNDERSTAND | EXPERIMENTAL | INTEGRATE | pyworld / Parselmouth | library | Local | audio | F0 track | modified BSD / GPL | MED | P1 | Only `mamse002` CQT estimator; explicitly "估计量≠感知音高" |
| `midi.transcribe` | TRANSCRIBE | IMPLEMENTED_NOT_CANONICAL | INTEGRATE | Basic Pitch 0.4.0 | model | Local | audio | MIDI | **Apache-2.0** | LOW | **P0** | CLI-only from the desktop shell; Canon: `IMPLEMENTED_NOT_MERGED` |
| `notes.transcribe` | TRANSCRIBE | ABSENT | INTEGRATE | Basic Pitch note events | model | Local | audio | note list | Apache-2.0 | LOW | P2 | Runner already emits `--save-note-events` |
| `chords.transcribe` | TRANSCRIBE | **ABSENT** | INTEGRATE | lv-chordia | model | Local | audio | chord labels | verify | HIGH | P2 | Depends on `harmony.analyze` |
| `score.generate` | TRANSCRIBE | IMPLEMENTED_NOT_CANONICAL | INTEGRATE | music21 → MusicXML 4.0 | library | Local | MIDI | MusicXML | BSD-3 | LOW | P1 | **music21 is not declared in any pyproject** — an undeclared runtime dep |
| `lyrics.align` | TRANSCRIBE | **ABSENT** | INTEGRATE | WhisperX + wav2vec2/MMS_FA | model | Local | audio + lyrics | timed lyrics | verify (per-model) | HIGH | P1 | 2026 consensus: Demucs vocal isolate → ASR for coarse → forced alignment for timing |
| `clip.repair` | REPAIR | IMPLEMENTED_NOT_CANONICAL | INTEGRATE | own primitive / VoiceFixer | library / model | Local | audio | repaired audio | GPL-3.0-only | MED | P1 | Peak repair only — **not true declipping**; identity-gated |
| `noise.reduce` | REPAIR | **ABSENT** | INTEGRATE | ARN/denoise models | model | Local | audio | audio | verify | HIGH | P2 | Engine explicitly routes to `INTERVENTION_NOT_SUPPORTED_V0_1` |
| `source.restore` | REPAIR | **ABSENT** | INTEGRATE | AERO / RESTORE / GACELA | model | Local | audio | audio | verify (per-model) | HIGH | P2 | AERO=super-res; GACELA=inpainting; RESTORE targets 78 RPM — relevant to Classic Reconstruction |
| `timing.correct` | REPAIR | **ABSENT** | DEFER | DAW / Melodyne-class | — | — | audio | audio | — | HIGH | P3 | grep `quantize`/`warp`/`time_stretch` = 0 hits; needs `rhythm.analyze` first |
| `pitch.correct` | ARRANGE | **ABSENT** | INTEGRATE | pyworld + PSOLA | library | Local | audio + F0 | tuned audio | modified BSD | HIGH | P2 | No pitch-shift/autotune code anywhere in `src/` |
| `edit.apply` | ARRANGE | EXPERIMENTAL | BUILD | own (`intervention/`) | library | Local | audio + plan | audio | GPL-3.0-only | — | P1 | Pre-registered primitive contracts with scope/max-strength/identity-risk |
| `mix.plan` | MIX | PARTIAL | BUILD | own (Mix Graph) | library | Local | metrics | graph | GPL-3.0-only | — | P1 | `mix_graph` self-labels EXPERIMENTAL |
| `mix.render` | MIX | EXPERIMENTAL | BUILD | own + pedalboard | library | Local | graph | audio | GPL-3.0-only / AGPL? verify pedalboard | — | P1 | `NodeProvider` already enforces determinism per node type |
| `master.plan` | MASTER | PARTIAL | BUILD | own | library | Local | metrics | plan | GPL-3.0-only | — | P1 | |
| `master.render` | MASTER | **LEGACY** | BUILD | `v01_*` presets | library | Local | audio | audio | GPL-3.0-only | — | P1 | Legacy path is what the desktop `local.js` backend actually calls |
| `delivery.encode` | MASTER | PARTIAL | INTEGRATE | ffmpeg | binary | Local | audio | encoded | as ingest row | LOW | P2 | **WAV only today** |
| `audio.verify` | VERIFY | **CANONICAL** | **BUILD** | own | library | Local | 2× audio | before/after evidence | GPL-3.0-only | — | **P0** | "Machine evidence only… no listening-quality claims" |
| `evidence.bundle` | VERIFY | **CANONICAL** | **BUILD** | own | library | Local | artifacts | evidence bundle | GPL-3.0-only | — | **P0** | 7 modules incl. conflicts, epistemic, completeness |
| `judgment.evaluate` | VERIFY | CANONICAL | **BUILD** | own + authority layer | library | Local | metrics | findings + decision | GPL-3.0-only | — | **P0** | `HUMAN_REQUIRED`/`INCONCLUSIVE` boundary is product-defining |
| `delivery.export` | DELIVER | IMPLEMENTED_NOT_CANONICAL | BUILD | own `data_plane` | library | Local | audio | R/W | GPL-3.0-only | LOW | P1 | Delivery contract CANONICAL; only WAV encoding exists |
| `metadata.write` | DELIVER | ABSENT | DEFER | mutagen | library | Local | audio + tags | tagged audio | MIT | LOW | P3 | Needs a product decision on which tags matter |
| `daw.exchange` | INTEROPERATE | **ABSENT** | **DELEGATE** | AAF (AMWA) / proj. files | standard | External | session | session | — | HIGH | P3 | **Reaper has no native AAF/OMF**; AAF drops routing/colour |
| `plugin.host` | INTEROPERATE | ABSENT | DELEGATE | DAW host / pedalboard | standard | External | plugin | audio | — | HIGH | P3 | Being a *client* is optional; being a *host* is a different product |
| `notation.exchange` | INTEROPERATE | PARTIAL | INTEGRATE | MusicXML 4.0 | standard | Local | score | MusicXML | W3C CG, open | LOW | P2 | 270+ programs; "mature but hard to evolve" = dependability |
| `provider.route` | EXECUTE | **ABSENT** | **BUILD** | own | protocol | Local | capability + policy | provider | GPL-3.0-only | HIGH | **P0** | The control point; no router exists |
| `project.persist` | EXECUTE | **ABSENT** (on `main`) | **BUILD** | own (`moodify.project`) | library | Local | manifest | project dir | GPL-3.0-only | — | **P0** | Implemented on `codex/project-model-001` (`4aba0f53`); `main` holds only stale `.pyc` |
| `job.execute` | EXECUTE | CANONICAL | BUILD | own (`moodify/node`) | library | Hybrid | job | result | GPL-3.0-only | — | P1 | Durable sqlite queue, leases, resource guards, unattended worker |
| `agent.expose` (MCP) | INTEROPERATE | **ABSENT** | **BUILD** | MCP protocol | protocol | Local | capability metadata | tool surface | spec-dependent | MED | P1 | No MCP server in-repo; ecosystem is crowded with DAW-control servers |

**Row count: 45.**

---

## B. Capability contracts — priority capabilities

Semantic boundaries only. Sound Protocol 0.3 formalises these later; no JSON
Schema is defined here.

### `stem.separate`
```text
Description     Split a mixed recording into named stems.
Inputs          audio asset (project-relative)
Outputs         N named stem assets + manifest (provider id/version, params hash,
                source sha256, per-stem peak/RMS)
Parameters      target set · quality tier · determinism preference
Requirements    local: model weights present. cloud: credentials + network.
Providers       demucs.local · lalal.cloud · future
Evidence        source sha256 · per-stem digest · provider + version · elapsed
Failure modes   DEPENDENCY_MISSING · PROVIDER_UNAVAILABLE · UNSUPPORTED_FORMAT ·
                RESOURCE_LIMIT · AUTH_REQUIRED · RATE_LIMITED · EXECUTION_FAILED
Project state   adds stem assets; records the separation event in provenance
```

### `rhythm.analyze`
```text
Description     Estimate tempo, beats and downbeats.
Inputs          audio asset
Outputs         tempo_bpm (float) · beat times · downbeat times · confidence
Parameters      tempo prior range · minimum confidence to emit
Requirements    local model weights
Providers       madmom-infer · beat_this
Evidence        input sha256 · algorithm + version · confidence
Failure modes   DEPENDENCY_MISSING · INVALID_INPUT · EXECUTION_FAILED ·
                QUALITY_GATE_FAILED
Project state   populates the currently-unassigned tempo_bpm / beat fields
```

### `structure.analyze`
```text
Description     Segment a song into labelled sections and boundaries.
Inputs          audio asset
Outputs         Section[] (label, start, end, confidence)
Parameters      minimum section length · confidence threshold
Requirements    local model weights (heavy)
Providers       all-in-one-infer
Evidence        input sha256 · model version · boundary confidence
Failure modes   DEPENDENCY_MISSING · RESOURCE_LIMIT · QUALITY_GATE_FAILED ·
                REVIEW_REQUIRED (low confidence)
Project state   constructs StructureContext — currently 0 construction sites
```

### `midi.transcribe`
```text
Description     Convert audio to MIDI note events with pitch bend.
Inputs          audio asset (source or an isolated stem)
Outputs         MIDI file + note-event list
Parameters      onset/frame thresholds · minimum note length · pitch-bend on/off
Requirements    basic-pitch runtime (currently an undeclared external venv)
Providers       Basic Pitch 0.4.0
Evidence        input sha256 · model version · note count
Failure modes   DEPENDENCY_MISSING · UNSUPPORTED_FORMAT · EXECUTION_FAILED
Project state   adds a transcription asset under the project's transcription domain
```

### `evidence.bundle`
```text
Description     Assemble a verifiable evidence package for a result.
Inputs          measurement records · artifacts · provenance
Outputs         bundle + completeness/conflict/epistemic assessment
Parameters      required-artifact set
Requirements    none beyond Core
Providers       own (BUILD)
Evidence        hashes of every member artifact
Failure modes   INVALID_INPUT · EXECUTION_FAILED
Project state   attaches an evidence bundle to the operation that produced it
```

### `provider.route`
```text
Description     Resolve a capability + policy to an eligible provider.
Inputs          capability id · policy (privacy, quality, cost, determinism…)
Outputs         provider handle + rationale, or an explicit refusal
Parameters      policy dimensions (§5 of the map)
Requirements    a capability registry
Providers       own (BUILD)
Evidence        records the selection rationale alongside the result
Failure modes   PROVIDER_UNAVAILABLE · DEPENDENCY_MISSING ·
                UNSUPPORTED_FORMAT (no eligible provider)
Project state   none — routing is not persisted as project state
```

---

## C. Failure vocabulary

Structured failure is part of the ecosystem contract. Provider tracebacks are
**never** the primary interface; they may be attached as developer detail.

```text
DEPENDENCY_MISSING      a required runtime/model/binary is absent
PROVIDER_UNAVAILABLE    provider known but unreachable or not eligible
INVALID_INPUT           input violates the capability contract
UNSUPPORTED_FORMAT      format outside the declared set
RESOURCE_LIMIT          memory/disk/GPU/time exceeded
AUTH_REQUIRED           credentials absent or rejected
RATE_LIMITED            provider throttled the caller
EXECUTION_FAILED        provider ran and failed
QUALITY_GATE_FAILED     output failed a declared gate
REVIEW_REQUIRED         result is uncertain; human authority needed
```

`DEPENDENCY_MISSING` is already implemented in the desktop shell (HOTFIX 000,
`moodify-desktop/src/runtime.js`) — the first entry of this vocabulary to exist
in code, and the pattern the rest should follow: a stable code, a clear
identity, and no silent fallback.

---

## D. Reading the matrix honestly

Three caveats a reader should carry:

1. **"Candidate Provider" is a research lead, not a recommendation to adopt.**
   Licences were checked at the level this task allows: enough to flag the traps
   (madmom weights and Open-Unmix UMXL weights are **CC BY-NC-SA — non-commercial**;
   BS-RoFormer's licence is unclear), not enough to certify any of them.
2. **Status is audit-derived for `main` only.** Project Model and HOTFIX 000
   corrections live on unmerged branches. Anything marked ABSENT here may exist
   elsewhere — verify before planning work around it.
3. **Model licences are separate from code licences.** This is the single most
   common trap in this domain, and several rows above are marked "verify"
   precisely because the code is permissive while the weights may not be.
