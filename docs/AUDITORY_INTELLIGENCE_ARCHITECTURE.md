# Auditory Intelligence Architecture

## 1. System Identity

Moodify is an Auditory Intelligence System.

Its purpose is not merely to alter audio. Its purpose is to establish a repeatable loop for hearing, representing, judging, intervening, verifying and learning.

```text
Audio Source
   |
   v
LISTEN
   |
   v
REPRESENT
   |
   v
JUDGE
   |
   +--------------------+
   |                    |
   | intervention needed?
   |                    |
   +---- yes ----------> INTERVENE
   |                       |
   |                       v
   +--------------------> VERIFY
                           |
                           v
                         LEARN
                           |
                           v
                       NEXT CASE
```

## 2. Capability Layers

### Listen

Responsibilities:

- source identity;
- decoding;
- sample-rate/channel awareness;
- source integrity;
- repeatable ingest.

### Represent

Responsibilities:

- waveform;
- spectral measurements;
- loudness;
- dynamics;
- phase;
- stereo/channel behavior;
- residuals;
- transient behavior;
- musical structure when available.

### Judge

Responsibilities:

- diagnosis;
- anomaly detection;
- constraint evaluation;
- uncertainty;
- human-authority escalation.

### Intervene

Responsibilities:

- controlled processing;
- reversible or traceable parameterization;
- candidate creation;
- experimental comparison.

This is where legacy “post-processing” functionality belongs.

### Verify

Responsibilities:

- before/after comparison;
- invariant checks;
- regression checks;
- evidence packaging;
- quality gates.

### Learn

Responsibilities:

- treatment records;
- production cases;
- measurement records;
- feedback;
- benchmark updates;
- rule updates;
- new research questions.

## 3. WSE / MSE / PPE

### WSE — Wave-Spectral Evolution

WSE is the acoustic/physical measurement discipline.

Its output should increasingly become structured Measurement Records rather than isolated plots.

### MSE — Musical-Structural Engineering

MSE is the musical representation discipline.

It may use MIDI, score, beat, phrase, section, lyric and role information. It should not be conflated with raw spectrum measurement.

### PPE — Production Process Engineering

PPE governs the production process itself.

It owns:

- cases;
- states;
- gates;
- authority boundaries;
- evidence requirements;
- deterministic outputs;
- failure/recovery;
- packaging;
- production readiness.

## 4. Current vs Target Architecture

The current v0.1 Python pipeline may remain:

```text
Import -> Analyze -> Diagnose -> Process -> Export
```

This is a valid narrow implementation.

The full auditory-intelligence architecture should evolve around it incrementally.

Do not replace stable code with architectural theater.

## 5. Canonical Convergence Rule

A new subsystem may join the canonical mainline only if:

1. its responsibility is unique;
2. it has an explicit input/output contract;
3. it does not create a competing authority;
4. it has verification;
5. its outputs can become evidence or assets;
6. failure behavior is defined.
