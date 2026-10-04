# Moodify Capability Ecosystem Map 001

> **Status:** Strategy input — **not** runtime truth.
> **Code changes:** none. This document adds no dependency, no provider and no schema.
> **Date:** 2026-10-04
> **Branch of record:** `codex/ecosystem-001-capability-map` @ `01edc902`
> **Companions:** `MOODIFY_CAPABILITY_MATRIX_001.md`, `MOODIFY_PROVIDER_MANIFEST_DRAFT_001.md`
> **Canon:** this document does not change Canon. It proposes; humans decide.

---

## 1. Executive Thesis

Moodify should not try to be the best implementation of every music capability.
It should become **the layer through which many capabilities are discovered,
called, combined, replaced and upgraded.**

```text
Do not compete with every capability.
Become the place where capabilities connect.
```

**The 2026 maintenance landscape empirically proves this thesis.** During this
research, three of the most obvious candidate engines showed exactly the failure
mode the thesis predicts:

| Engine | 2026 reality | Consequence if Moodify had coupled to it directly |
| --- | --- | --- |
| Demucs | `facebookresearch/demucs` is in limited-maintenance mode; the maintained line is the author's own fork (`adefossez/demucs` v4.1.0, Jul 2026), which **removed torchaudio for inference** and moved weights to HuggingFace safetensors | A repo-level dependency would have broken on the migration |
| madmom | PyPI release ~8 years stale, Cython extensions fail on modern Python/numpy; **pretrained models are CC BY-NC-SA 4.0 (non-commercial)** | A "just pip install madmom" integration is both unbuildable and commercially unsafe |
| MSAF | Still updated, but a 2026 project found it **fails to import on modern SciPy** | Section detection would silently break on a dependency bump |

Every one of those is an argument for the same architecture:

```text
        Model changes                 Capability persists
   ┌──────────────────────┐      ┌──────────────────────────┐
   │ demucs → bs-roformer │      │      stem.separate       │
   │ basic-pitch → next   │  ⇒   │    midi.transcribe       │
   │ whisper → next       │      │      lyrics.align        │
   └──────────────────────┘      └──────────────────────────┘
```

**The strategic formula:**

```text
Models change.
Capabilities persist.
Protocols coordinate.
Projects accumulate state.
Ecosystems compound.
```

The test of this document is one question: *when a better model appears, does
Moodify get stronger, or obsolete?*

---

## 2. Current Moodify Reality

A read-only audit of this branch (`01edc902`) established the baseline. Detail
lives in `MOODIFY_CAPABILITY_MATRIX_001.md`; the shape is:

| Status | Count | Domains |
| --- | ---: | --- |
| **CANONICAL** | 7 | audio decode · auditory analysis · loudness/true-peak/stereo/spectral · audio verification · provenance & evidence contracts · cloud node/queue · local execution |
| **IMPLEMENTED_NOT_CANONICAL** | 6 | MIDI transcription (basic-pitch CLI) · MusicXML/score (music21) · A/B comparison · clipping peak-repair · delivery/export (WAV-only) · agent integration (Codex + DeepSeek) |
| **PARTIAL** | 5 | pitch detection · beat/tempo · song structure · metadata · capability registry |
| **EXPERIMENTAL** | 3 | stem separation (local DSP) · mixing (`mix_graph`) · mastering/finishing |
| **LEGACY** | 1 | `v01_*` preset finishing (still the path the desktop backend calls) |
| **ABSENT** | 8+ | timing correction · chord/harmony (core) · instrument recognition · lyrics alignment · noise reduction / restoration · DAW integration · plugin host · **Project Model** |

**Honest reading of this table.** Moodify's strength is concentrated in the
**trust layer** — measurement, evidence, provenance, verification — which is
exactly the layer this document argues it should own. Its weakness is
concentrated in the **content engines** — transcription, structure, restoration
— which is exactly the layer this document argues it should integrate rather
than build.

That is a favourable starting position: the strategy asks Moodify to double
down where it is already strong.

Three findings that must not be smoothed over:

1. **`moodify/project/` on this branch contains only stale `.pyc` files.** The
   Project Model is implemented on branch `codex/project-model-001`
   (`4aba0f53`), not merged to `main`. The accumulation substrate this document
   treats as central is **not yet in `main`.**
2. **`auditory/inventory.py` is stale** — its classification map names modules
   (`capability_registry`, `transcription`, `score_engine`, `adapters`, `ports`)
   that do not exist on this branch. A capability map built by trusting that
   file would be fiction.
3. **`tempo_bpm` and `StructureContext` have no producer.** `structure.py`
   defines `tempo_bpm` at line 41 and serialises it at line 75; nothing ever
   assigns it. grep for `Section(` / `StructureContext(` returns zero
   construction sites. Types ≠ capability.

---

## 3. Capability Taxonomy

Twelve stable domains. The taxonomy is provider-neutral by construction — no
domain name refers to a vendor.

```text
01 INGEST       audio.decode · audio.probe · audio.convert · metadata.read
02 SEPARATE     stem.separate · vocal.extract · accompaniment.extract
03 UNDERSTAND   audio.analyze · loudness.measure · level.meter · stereo.analyze
                rhythm.analyze · harmony.analyze · structure.analyze
                instrument.identify · pitch.analyze
04 TRANSCRIBE   midi.transcribe · notes.transcribe · chords.transcribe
                score.generate · lyrics.align
05 REPAIR       clip.repair · noise.reduce · source.restore · timing.correct
06 ARRANGE      pitch.correct · edit.apply
07 MIX          mix.plan · mix.render
08 MASTER       master.plan · master.render · delivery.encode
09 VERIFY       audio.verify · evidence.bundle · judgment.evaluate
10 DELIVER      delivery.export · metadata.write
11 INTEROPERATE daw.exchange · plugin.host · notation.exchange
12 EXECUTE      job.execute · provider.route · project.persist
```

### Stable capability IDs

Rule: **`domain.operation`, intent not vendor.** Provider identity lives
*below* the boundary, never in the ID.

```text
BAD                          GOOD
demucs.run                   stem.separate
basic_pitch.run              midi.transcribe
ffmpeg.convert               audio.convert
whisper.align                lyrics.align
```

This matters more than it looks. `midi.transcribe` survives Basic Pitch being
replaced. `basic_pitch.run` does not — it embeds a vendor assumption into every
call site, every stored job, and every Agent prompt.

---

## 4. Build / Integrate / Delegate

Postures: **BUILD** (Moodify owns the logic/contract) · **INTEGRATE** (stable
capability, external engine behind an adapter) · **DELEGATE** (a mature
ecosystem owns the interaction surface) · **DEFER** (not now).

### BUILD — 9 capabilities

The selection rule: *would this be more valuable if a model got better?*
Building a model fails that test. Building the layer that models plug into
passes it.

| Capability | Why Moodify must own it |
| --- | --- |
| `project.persist` (Song Project) | The accumulation substrate. Every other decision depends on state surviving. Already begun (`codex/project-model-001`). |
| `evidence.bundle` | Moodify's differentiator is *trustworthy* evidence, not loud processing. Already CANONICAL. |
| `judgment.evaluate` + authority boundary | The `HUMAN_REQUIRED` / `INCONCLUSIVE` boundary is product-defining. Never outsourced. |
| `audio.verify` | Verification is worthless if the verifier is a vendor the vendor supplies. |
| `audio.analyze` (measurement) | The trust layer. Already CANONICAL, standards-backed. |
| **Capability Registry + IDs** | The directory the whole thesis needs. Today: specialised registries only, plus a stale inventory. |
| **Provider Router + selection policy** | Decides *which* engine; the control point of the ecosystem. |
| **Production Graph / execution planner** | Orders capabilities; owns determinism and checkpoints. |
| **Protocol (MSP → 0.3)** | The contract Agents speak. Vendor-neutral by construction. |

### INTEGRATE — 15 capabilities

Everything where two or more implementations can compete behind one contract.

`stem.separate` · `midi.transcribe` · `score.generate` · `lyrics.align` ·
`rhythm.analyze` · `harmony.analyze` · `structure.analyze` ·
`instrument.identify` · `pitch.analyze` · `pitch.correct` · `clip.repair` ·
`noise.reduce` · `source.restore` · `audio.convert` · `delivery.encode`

### DELEGATE — 6 capabilities

| Capability | Who owns it | Why |
| --- | --- | --- |
| `daw.exchange` | DAW vendors | No safe round-trip exists to reimplement. AAF does not carry routing, colour or session structure; Reaper has no native AAF/OMF at all. |
| DAW editing UI | Ableton / Logic / Reaper / Cubase / FL / Pro Tools / Studio One | A decade of interaction design. Out of scope by every reading of Canon. |
| `plugin.host` | The DAW host, or `pedalboard` inside Python | Hosting VST3/CLAP is a runtime problem the host already solved. |
| Notation editing / engraving | MuseScore et al. | `score.generate` (INTEGRATE) is the interchange; the editor is theirs. |
| General media player UI | The Player app already covers Moodify's case | `moodify-desktop` + Player exist; a general player is not the product. |
| Cloud object storage | Aliyun OSS / S3 | Already delegated in practice (`data_plane`). |

### DEFER — 5

`timing.correct` · immersive/ADM delivery · AAF/OMF interchange ·
shipping VST3/CLAP plugins · plugin marketplace.

**Reasoning for the two most tempting defers:**

- **AAF/OMF** — genuinely useful for DAW handoff, but no in-repo demand yet and
  the ecosystem is still painful (Reaper = paid third-party extension or a beta
  converter; Pro Tools owns the format). Revisit when a real user asks.
- **Shipping a plugin** — `docs/ecosystem-roadmap.md` already places "DAW
  Plugins (VST/AU/AAX)" in *Phase 3, Q1–Q2 2027*. This document concurs and
  recommends **not moving it earlier**, because a plugin is a second product
  surface (one Core, two interfaces — a plugin would be a third).

---

## 5. Provider Architecture

```text
        Agent / CLI / API / GUI
                  │
                  ▼
            Capability ID            ← stable, vendor-free, versioned
                  │
                  ▼
            Capability Contract      ← inputs, outputs, evidence, failures
                  │
                  ▼
            Provider Router          ← selection policy (§ below)
                  │
     ┌────────────┼─────────────┐
     ▼            ▼             ▼
  Local        Cloud       External App
  Model         API           / DAW
```

The caller requests `stem.separate`. It does **not** request `run demucs`.
Explicit provider selection remains possible (`prefer: "lalal.cloud"`) but is
never the default path — otherwise the abstraction is decorative.

```text
stem.separate
      │
      ▼
Provider Router
      ├── demucs.local      (local, MIT, GPU-optional)
      ├── lalal.cloud       (cloud, commercial, 10-stem)
      └── future.provider
```

**Router responsibilities (defined here, implemented later):** resolve
capability → eligible providers → filter by policy → order by preference →
execute → normalise output into the capability contract → record the provider
identity and version into provenance.

**Router non-responsibilities:** it does not know what a stem is, does not
parse audio, does not judge quality. It routes.

### Provider selection policy — dimensions

```text
quality · latency · cost · privacy · offline availability · GPU availability
license · file duration · target set · determinism · provider health
user preference
```

A future request is declarative, not imperative:

```json
{
  "operation": "stem.separate",
  "policy": { "privacy": "local_only", "quality": "high" }
}
```

The router resolves that to an eligible local provider, or returns
`PROVIDER_UNAVAILABLE` — **never** silently escalating to cloud. A privacy
policy that can be silently violated is not a policy.

---

## 6. Local / Cloud Strategy

| Nature | Capabilities | Rationale |
| --- | --- | --- |
| **LOCAL** | decode, analyze, measure, verify, evidence, judgment, project, mix/master render, clip.repair | Privacy, determinism, zero marginal cost, offline. This is the trust layer — it must run on the user's machine. |
| **CLOUD** | heavy separation (BS-RoFormer-class), commercial licensed models, elastic batch | Large models and licensed capabilities do not belong in a desktop install. |
| **HYBRID** | stem.separate, midi.transcribe, source.restore, lyrics.align | The same capability has a weak-local and a strong-cloud implementation. **This is where the router earns its keep.** |

**The governing asymmetry:** local is the default; cloud is opt-in and
*explicitly declared*. The repository already behaves this way — the desktop
cloud backend "is not implemented, and says so" rather than silently falling
back to local. That instinct should be generalised into policy: **never
silently cross the local/cloud boundary in either direction.** A user who chose
`local_only` for privacy must not have their audio uploaded because a local
model scored lower.

---

## 7. DAW / Plugin / Standard Ecosystem

### DAW relationship

Moodify is not a DAW and should not become one. The relationship is
**produce → hand over → receive back**, through files and protocol.

| DAW | Plausible surface | Evidence status |
| --- | --- | --- |
| Pro Tools | AAF (native), WAV/BW64, re-import | AAF is Avid's native interchange |
| Logic Pro | MusicXML, WAV, FCPXML-adjacent | via converter tooling |
| Cubase / Nuendo | MusicXML, WAV, VST3 | — |
| Ableton Live | WAV, MIDI, MCP control servers exist | MCP ecosystem active |
| FL Studio | WAV, MIDI, VST3 (+ CLAP from 21.3) | CLAP support reported |
| Reaper | WAV, MIDI, **no native AAF/OMF** | third-party extensions only |
| Studio One | WAV, MusicXML, VST3 (+ CLAP) | CLAP support reported |

**Recommendation:** the durable interchange for Moodify is **audio + MIDI +
MusicXML + a manifest**, with AAF DEFERRED. A handoff that survives is worth
more than a handoff that round-trips.

> **Evidence caveat.** DAW feature rows above come from vendor/community
> documentation gathered 2026-10-04 and are **not** verified by Moodify
> testing. They are planning inputs, not claims of support. No DAW integration
> exists in the repository today (ABSENT).

### Standards

| Standard | Problem it solves | Relevant now? | After |
| --- | --- | --- | --- |
| **ITU-R BS.1770 / EBU R128** | Loudness & true peak | **Yes — already core** | IMPLEMENTED |
| **EBU Tech 3342** | Loudness range | Yes — already core | IMPLEMENTED |
| **MusicXML 4.0** | Notation interchange | Yes | **INTEGRATE now** (`score.generate`) |
| **MNX** | Next-gen notation (W3C CG; MuseScore implements it) | Watch | LATER |
| **MIDI** | Note/timing interchange | Yes | INTEGRATE now |
| **ADM / ITU-R BS.2076** | Object/immersive metadata | Not yet | DEFER (no immersive path) |
| **BWF/BW64 (ITU-R BS.2088)** | Long-form container | Watch — Netflix requires BWAV ADM for dubbing delivery | DEFER |
| **VST3** | Plugin interchange (SDK now MIT) | No | DEFER — we are a client, not a host |
| **CLAP** | Plugin interchange, open governance | No | DEFER |
| **ARA** | DAW↔plugin audio access | No | NEVER (requires being a plugin) |
| **AAF / OMF** | Session interchange | Marginal | DEFER (see §4) |
| **OSC** | Live control | No | DEFER |
| **MCP** | **Agent tool access** | **Yes — highest-leverage** | **INTEGRATE (§8)** |

**MusicXML is a W3C Community Group standard** (since July 2015), latest release
**4.0 (June 2021)**, with 4.1 in planning as of the July 2026 co-chair meeting —
mature, broadly supported, and hard to evolve. That is the correct kind of
dependency: boring and stable. MEI is the scholarly alternative with far lower
commercial adoption; not recommended.

---

## 8. Agent Ecosystem

```text
Agent (Codex / Claude Code / ChatGPT / local / workflow engine)
                  │
                  ▼
        moodify capabilities        ← discoverable, typed, versioned
                  │
                  ▼
        capability metadata + schema
                  │
                  ▼
        operation request (MSP)
                  │
                  ▼
          provider router
                  │
                  ▼
   result + evidence + project state
```

### The finding that should shape this section

**A crowded MCP ecosystem for music production already exists in 2026.** During
research, MCP servers were found for REAPER (~181 tools), Waveform (150+),
Ableton (two independent implementations), Csound, SuperCollider, plus cloud
generation services — with active maintenance into 2026 and one project
tracking MCP protocol revision `2026-07-28`.

Three consequences, in order of importance:

1. **Moodify should not build DAW control.** It is already being built, several
   times, by others. This converts `daw.exchange` from "maybe build" to a
   confident **DELEGATE**.
2. **Moodify should be reachable over MCP.** Being callable by Codex, Claude
   Code, ChatGPT agents and workflow engines is the cheapest distribution
   channel available, and it is the interface layer the Agent Production Layer
   presupposes.
3. **Moodify's differentiation is not tool count.** 181 DAW tools exist. What
   does not exist in that ecosystem is *evidence, provenance, measurement
   authority and a project that accumulates state*. That is the gap Moodify
   occupies.

No MCP server exists in this repository today. The recommendation is a
**read-only capability + measurement MCP surface first** — exposing
`audio.analyze`, `evidence.bundle`, `project.persist` — before any mutating
surface. Read-only agents can be wrong without damaging anything.

---

## 9. Provider Replaceability

The goal: **the capability is stable, the provider is swappable, the project
stays readable.**

```text
GOOD                            BAD
project.json  ── capability     project.json  ── "demucs_params"
CLI  ── stem.separate           CLI ── moodify demucs separate
graph ── capability node        graph ── demucs internal tensor shapes
```

### Anti-lock-in rules

1. **No vendor names in capability IDs.** `stem.separate`, never `demucs.run`.
2. **No vendor parameters in canonical project state.** Provider parameters live
   under a namespaced, provider-identified block that a reader may ignore. The
   canonical record stores *what was produced*, not *how*.
3. **Provenance records provider identity + version** — so an old result stays
   interpretable after the provider is replaced, and a better provider can
   re-run the same capability and be compared against the old evidence.
4. **The render path never depends on provider internals.** A capability node
   consumes and produces contract-shaped artifacts only.
5. **No provider is required for the core loop.** A project must still open,
   verify and export with every optional provider uninstalled.
6. **Every capability has ≥2 candidate providers, or an explicit
   `SINGLE_SOURCE_ACCEPTED` note.** Single-sourced capabilities are a named risk,
   not a silent default. (Real example: LALAL.AI is currently the only cloud
   stem provider in-repo — that is `SINGLE_SOURCE_ACCEPTED` with a documented
   risk, not a neutral fact.)

Rule 5 is the load-bearing one. It is what makes the ecosystem survivable: if
losing a provider can brick a project, the abstraction failed.

---

## 10. Capability Certification

Concept: **Moodify Compatible** — a provider qualifies by passing its
capability contract. Not built in this task; defined here so today's
architecture does not preclude it.

A `stem.separate` provider must pass:

```text
input validation          accepts the declared formats; rejects the rest loudly
output asset contract     produces contract-shaped stems + manifest
channel / sample-rate     preserves declared channel count and sample rate
error contract            maps failures into Moodify failure codes (§13 of matrix)
provenance                records provider id, version, parameters hash, input sha256
deterministic metadata    same input + same version -> same recorded metadata
integration tests         runnable by Moodify, in Moodify's harness
```

Certification levels, deliberately coarse:

```text
EXPERIMENTAL       passes input/output validation only
COMPATIBLE         passes the full contract
VERIFIED           COMPATIBLE + measured against a reference on fixed fixtures
```

Note what certification is **not**: it is not a quality ranking, and passing it
never means "good separation". Quality is measured per-project, against the
user's own material, and reported as evidence. A certified provider is a
*trustworthy collaborator*, not a *good one*.

---

## 11. Developer Ecosystem

Goal: a third party can add a provider **without touching Moodify's core**.

```text
provider package
├── manifest            declares identity, capabilities, runtime, license
├── capability decls    which contracts it implements
├── schemas             its own parameter/artifact shapes
├── runtime reqs        python/node/binary, GPU, model weights
├── adapter             the code that calls the engine
└── tests               contract tests
```

A future command would be `moodify provider install <package>`.
**Not implemented, not designed in detail here.** The only purpose of this
section is to make sure today's decisions do not foreclose it — which is why
§5's contract-first router and §9's anti-lock-in rules come first.

The manifest sketch lives in `MOODIFY_PROVIDER_MANIFEST_DRAFT_001.md`, labelled
**DRAFT**. It is exploratory and must not be treated as canonical.

---

## 12. Top 5 Ecosystem Gaps

Derived from the audit, not from ambition. Ordered by leverage.

### 1. Provider abstraction + capability registry — *blocks everything else*
Today: several specialised registries (`measurement_registry`,
`intervention/registry`, `mix_graph` providers, desktop backend registry) and
one **stale** inventory that names modules which do not exist. There is no
place to declare "`stem.separate` exists, these providers implement it, these
are the failure codes". Without it, every integration in this document is bespoke.

### 2. Structure & rhythm understanding — *types with no producers*
`structure.py` defines `tempo_bpm` and `StructureContext`; nothing assigns them.
grep for `Section(`/`StructureContext(` = 0 construction sites. The Agent
Production Layer cannot make production decisions about a song whose sections
and tempo it cannot perceive. This is the largest *capability* gap relative to
strategic need.

### 3. Project Model not in `main` — *the accumulation layer is unmerged*
Implemented on `codex/project-model-001` (`4aba0f53`); `moodify/project/` on
this branch holds only stale `.pyc`. Until it merges, every capability in this
map has nowhere durable to attach its state, and the "Projects accumulate
state" clause of the thesis is unrealised.

### 4. Transcription domain — *the weakest strategic area*
MIDI (`basic-pitch` CLI) and score (`music21`) are IMPLEMENTED_NOT_CANONICAL and
invoked as external tools from the desktop shell only; `lyrics.align` is ABSENT;
`chords.transcribe` is ABSENT. Canon records Basic Pitch as
`IMPLEMENTED_NOT_MERGED`. This is the domain where the Agent most needs
structure and where Moodify currently has the least.

### 5. Stem separation without a canonical boundary — *three half-paths, no contract*
Three disjoint things exist: a LALAL.AI cloud client (`stems/client.py`,
10-stem catalog, `CONNECTED_UNTESTED`), a self-described preview-grade local DSP
script (`dsp_separate.py`), and a **declared-but-absent** Demucs extra
(`PLANNED_ONLY`, weights never downloaded). No single `stem.separate` contract
unifies them — so the caller must know which one it is talking to, which is
exactly what §5 exists to prevent.

---

## 13. Recommended Next Steps

Exactly one next task is recommended — see the final report. The shape of the
sequence after that:

```text
1. Capability Registry + IDs + failure vocabulary   (contract layer)
2. Project Model merged to main                     (state layer)
3. Provider contract + router skeleton              (routing layer)
4. First INTEGRATE: rhythm.analyze + structure.analyze  (proves the pattern)
5. Read-only MCP surface                            (distribution)
```

Step 4 deliberately picks *understanding* over *separation*. Separation is the
crowded, GPU-heavy, licence-messy domain; understanding is where Moodify's
measurement authority is already strongest and where the gap is largest.

---

## 14. What Moodify Must Never Rebuild Without a Strong Reason

Scope discipline. Each of these is a multi-year product owned by someone else:

| Do not rebuild | Why not |
| --- | --- |
| **A full DAW** | Interaction design measured in decades. Moodify's value is upstream of the DAW, not inside it. |
| **A general-purpose notation editor** | MuseScore owns it and is free. We generate MusicXML; they edit it. |
| **A general media player** | The Player interface covers Moodify's listening case. A general player is a different product. |
| **A plugin marketplace** | Two-sided markets need a platform-scale audience Moodify does not have. |
| **Generic cloud storage** | Already delegated (Aliyun OSS / S3). |
| **A generic social network** | Not the product. Distribution, not differentiation. |
| **A foundation audio model** | The single most expensive and most quickly obsoleted thing available. The entire thesis of this document is that Moodify should *consume* these, not produce them. |
| **DAW control surfaces** | Already being built several times over as MCP servers (§8). |
| **A second Core / DSP engine** | Canon already forbids it: *One Core, Multiple Interfaces.* |

The last row is the one most at risk from enthusiasm. Every provider in this
document is an **engine Moodify calls**, never a second authority for what a
measurement means.

---

## 15. What Moodify Should Own

> Which layers become **more** valuable as external models improve?

This is the central ecosystem question, and it has a sharp answer.

| Layer | More valuable as models improve? | Verdict |
| --- | --- | --- |
| **Project Model** | **Yes** — better models produce more artifacts to accumulate; the project is where the compounding happens | **OWN** |
| **Capability IDs + registry** | **Yes** — every new provider needs a slot to occupy; the directory's value grows with the number of providers | **OWN** |
| **Schemas / contracts** | **Yes** — more providers means more divergence to normalise | **OWN** |
| **Provider routing + selection** | **Yes** — the value of routing is proportional to the number of viable engines | **OWN** |
| **Protocol** | **Yes** — more providers × more agents = more coordination value | **OWN** |
| **Production Graph** | **Yes** — more capabilities means more sequencing decisions to get right | **OWN** |
| **Provenance / evidence** | **Yes — most of all.** A stronger model makes its outputs *less* self-evidently trustworthy, not more. Evidence is how you tell a better result from a more confident one | **OWN** |
| **Verification** | **Yes** — same reason; and it must never be vendor-supplied | **OWN** |
| **Developer SDK** | **Yes** — it is how provider count grows | **OWN** |
| **GUI** | **No** — a shell over capabilities; its value tracks capability count only indirectly | INTEGRATE/MAINTAIN |
| **DSP models** | **No — inversely.** Every model Moodify owns is one it must maintain against a field that moves faster than it can | **NEVER OWN** |

### The inverse-value principle

```text
Model quality          ↑↑↑
Trustworthiness of     ↓  (a more fluent model is more plausibly wrong)
any single output

⇒ the value of evidence, verification and provenance RISES as model
  quality rises. That is Moodify's durable position.
```

This is the same lesson HOTFIX 000 taught at measurement scale — *a
plausible-but-wrong number is more dangerous than a loud failure* — applied at
ecosystem scale. A vendor that returns a confident, wrong stem is not caught by
having a better vendor. It is caught by having a verification layer.

---

## 16. Ecosystem North Star

```text
                    AGENTS
                      │
                      ▼
              MOODIFY CAPABILITIES
                      │
                      ▼
              SOUND PROTOCOL
                      │
                      ▼
              PROVIDER ROUTER
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
      LOCAL         CLOUD        EXTERNAL
      MODEL          API            DAW
        │             │             │
        └─────────────┼─────────────┘
                      ▼
                SONG PROJECT
                      │
                      ▼
             EVIDENCE · PROVENANCE
                      │
                      └──────────▶ back to AGENTS
```

### Why this becomes more defensible as the ecosystem grows

1. **More providers → the router matters more**, not less. A single-provider
   router is overhead; a ten-provider router is leverage.
2. **More providers → the project becomes the only stable thing.** Users
   accumulate projects, not models; migrating providers must never mean
   migrating work.
3. **More agents → the protocol becomes the contract.** Agents that learn
   `stem.separate` keep working when Demucs is replaced by something better —
   which is the *entire* point.
4. **More projects → evidence compounds.** Measurement history across many
   projects is something no single model vendor possesses.
5. **The flywheel closes:**

```text
More Providers → More Capabilities → More Agent Use → More Projects
      ↑                                                      │
      └──────────── More Integrations ◀──────────────────────┘
```

**What Moodify must own for that loop to be durable:** capability IDs, schemas,
the Project Model, provider contracts, the Production Graph, evidence and
provenance, compatibility tests, and developer documentation. Notably, *every
one of those is a document or a contract, not a model.* That is not a
coincidence — it is the strategy.

---

## Appendix — External research notes and provenance

External claims in this document were gathered on **2026-10-04** from vendor
documentation, official repositories and standards bodies. Community sources
(forums) were used only for implementation experience, never as authoritative
specification, and are marked below where used. **Nothing in this appendix is
an adopted dependency** — §27 of the task forbids adoption, and no dependency
was added.

**Key sources consulted**

- Stem separation benchmark & model comparison (Hugging Face dataset, CC-BY):
  [StemSplit benchmark 2026](https://huggingface.co/datasets/StemSplitio/stem-separation-benchmark-2026)
- Demucs maintained line and v4.1.0 release notes:
  [adefossez/demucs](https://github.com/adefossez/demucs/blob/main/docs/release.md) ·
  [facebookresearch/demucs](https://github.com/facebookresearch/demucs)
- Basic Pitch (Apache-2.0, v0.4.0): [spotify/basic-pitch](https://github.com/spotify/basic-pitch)
- MIR tooling, incl. modernised madmom reimplementation:
  [openmirlab/madmom-infer](https://github.com/openmirlab/madmom-infer) ·
  [CPJKU/madmom](https://relatedrepos.com/gh/CPJKU/madmom) ·
  [all-in-one-infer](https://pypi.org/project/all-in-one-infer/)
- Audio restoration / super-resolution:
  [slp-rl/aero](https://hyper.ai/ja/papers/2211.12232#code) ·
  [andimarafioti/GACELA](https://ar5iv.labs.arxiv.org/html/2005.05032) ·
  [haoheliu/voicefixer](https://inferri.com/zh-CN/projects/cmmfotjyv00spgsh4o7muycn1)
- Pitch tooling: [pyworld](https://www.repoportal.com/tr/jeremycchsu-python-wrapper-for-world-vocoder) ·
  [WORLD](https://github.com/mmorise/World) ·
  [groxaxo/autotune-ai](https://github.com/groxaxo/autotune-ai)
- Plugin formats and 2026 governance changes:
  [VST3/AU/AAX/CLAP guide](https://www.antarestech.com/de/blog/vst3-au-aax-clap-plugin-formats-2026) ·
  [VST SDK open-sourced (MIT) — community report](https://gearspace.com/threads/steinberg-makes-vst-open-source-under-mit-license.1456743/)
- Interchange: [AAF vs OMF](https://www.forte-ai.com/blog/what-is-an-omf-file-and-why-modern-post-uses-aaf-instead) ·
  [Reaper AAF/OMF — community](https://gearspace.com/threads/finally-omf-aaf-support-in-reaper.1463594/)
- Notation standards: [W3C Music Notation CG minutes, July 2026](https://www.w3.org/community/music-notation/2026/07/27/co-chair-meeting-minutes-july-27-2026/) ·
  [MusicXML](https://en.m.wikipedia.org/wiki/Music_XML)
- Immersive: [ITU-R BS.2076-3](https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.2076-3-202502-I!!PDF-R.pdf) ·
  [Netflix BWAV ADM guidance](https://partnerhelp.netflixstudios.com/hc/en-us/articles/38234663714835-BWAV-ADM-Creation-Guidelines-for-Dubbing)
- MCP music ecosystem: [xDarkzx/Reaper-MCP](https://github.com/xDarkzx/Reaper-MCP) ·
  [waveform-MCP](https://github.com/jarmstrong158/waveform-MCP) ·
  [ableton-mcp-extended](https://pypi.org/project/ableton-mcp-extended/)
- Cloud stem APIs: [LALAL.AI business solutions](https://www.lalal.ai/business-solutions/) ·
  [2026 API comparison — community](https://dev.to/stevecase430/ai-stem-splitter-api-comparison-2026-stemsplit-vs-lalalai-vs-moises-with-benchmarks-372l)

**Confidence notes.** Commercial pricing figures conflict across sources and
should be re-verified before any decision. Moises' public developer API status
is **contradicted** between sources — treat as unverified. DAW capability rows
are planning inputs, not Moodify-tested facts.
