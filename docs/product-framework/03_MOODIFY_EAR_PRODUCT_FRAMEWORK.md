# Moodify Ear Product Framework

**Document ID:** MFY-EAR-PRODUCT-FRAMEWORK-001  
**Version:** 1.0  
**Date:** 2026-08-14  
**Status:** APPROVED BASELINE — approved by human product authority 2026-08-14  
**Product:** Moodify Ear

**Approval record:** approved 2026-08-14 by human product authority (huliye24) as Phase 1 baseline, no modification; see DECISION_LOG D-003 and GOVERNANCE_RECONCILIATION_REPORT.

## 1. Product definition

> **Moodify Ear is an auditory intelligence product that turns sound into inspectable judgment, controlled intervention, verification, and reusable evidence.**

Ear serves the master Moodify loop:

```text
Listen -> Represent -> Judge -> Intervene -> Verify -> Learn
```

Its primary output is not a processed file or a single score. Its primary output is a trustworthy account of what happened, what was judged, what changed, whether the intended condition improved, what remains uncertain, and what can be reused.

## 2. Target users

### 2.1 Primary users

- audio and music researchers;
- producers and engineers investigating a sound;
- AI audio teams evaluating generated output;
- designated reviewers responsible for listening decisions;
- operators running repeatable auditory cases.

### 2.2 Secondary users

- product teams consuming approved evidence;
- institutions evaluating auditory models or pipelines;
- Moodify Music creators who request an analysis through a bounded exchange.

Ear should not assume that every user understands signal processing. Technical depth must be progressively disclosed while authority and uncertainty remain clear at the first layer.

## 3. Jobs to be done

Users come to Ear to:

1. establish that a source is intact and identifiable;
2. understand what happened acoustically and structurally;
3. identify anomalies, constraints, and uncertainty;
4. decide whether intervention is justified;
5. create controlled alternatives without losing provenance;
6. compare source and candidates against a declared objective;
7. make or escalate a judgment;
8. preserve evidence and recover from failure;
9. reuse the case in future rules, benchmarks, or research.

## 4. Canonical product objects

| Object | Meaning | Authority |
|---|---|---|
| Source | Immutable identity and ingest facts for audio under study | Ear ingest contract |
| Production Case | Bounded auditory task with objective, state, outputs, and closure | Canonical case state machine |
| Representation | Structured waveform, spectral, loudness, phase, dynamics, and musical views | Versioned representation methods |
| Measurement Record | Values produced under a named method/version | Measurement contract |
| Judgment | Explicit finding, severity, confidence, evidence, and authority | Versioned rule/algorithm or human review |
| Intervention Plan | Reasoned, bounded change proposal | Ear plan contract |
| Candidate | Traceable result of an intervention | Case + asset identity |
| Verification Record | Before/after comparison, invariant checks, and outcome | Verification contract |
| Evidence Artifact | Durable link from a claim to reproducible observation | Evidence manifest |
| Rule | Versioned operational rule accepted from evidence | Rule governance |

Charts are views of evidence; they are not evidence by themselves. A processed file without its case, parameters, method versions, and verification is not a reusable Ear asset.

## 5. End-to-end user journey

### 5.1 Introduce source

The user adds one source or selects an existing immutable asset.

Ear shows:

- filename and safe display identity;
- duration, format, sample rate, channels;
- SHA-256 or stable asset reference;
- ingest integrity and privacy state;
- explicit analysis objective.

Failure behavior: unsupported, corrupt, missing, or duplicate inputs are explained without creating a misleading valid case.

### 5.2 Listen

Ear validates the source and begins a Production Case.

The primary screen shows instrument state, elapsed work, current stage, and whether user action is required. Technical logs remain secondary.

### 5.3 Represent

Ear produces complementary views across three disciplines:

- **WSE:** waveform, spectrum, loudness, dynamics, phase, channels, residuals, transients;
- **MSE:** beat, tempo, section, phrase, lyrics, roles, MIDI/score when available;
- **PPE:** source lineage, methods, versions, state history, failures, and recovery.

Absence of an MSE representation must be stated as unavailable, not inferred from unrelated WSE metrics.

### 5.4 Judge

The first judgment layer answers:

- What was detected?
- Why does it matter for the stated objective?
- Which evidence supports it?
- How confident is the system?
- What could invalidate the conclusion?
- Does the next step require a human?

Avoid one-dimensional “quality” scoring. Findings should be specific and inspectable.

### 5.5 Intervene

Intervention is optional and justified by a finding. The Auditory Intervention Laboratory may create controlled candidates such as conservative, balanced, and exploratory alternatives.

Every candidate records:

- intervention rationale;
- parameterization and engine version;
- source identity;
- intended target;
- safety constraints;
- deterministic or declared stochastic behavior.

The user can choose no intervention when evidence does not justify change.

### 5.6 Verify

Verification compares the source and candidates against the declared objective while checking invariants and unintended consequences.

It must distinguish:

- measured change;
- rule-based judgment;
- perceptual preference;
- unresolved uncertainty;
- failure to verify.

Loudness, level, or metric gain alone must not masquerade as perceptual improvement.

### 5.7 Decide and close

Possible outcomes:

- verified within an approved machine-decision scope;
- human review required;
- no intervention justified;
- inconclusive;
- failed with a recoverable path;
- rejected because evidence or invariants are insufficient.

Closure produces a case summary and evidence manifest. It does not erase alternative candidates or failure traces required for reproducibility.

### 5.8 Learn

Eligible cases may update:

- benchmark sets;
- measurement calibration;
- failure catalogues;
- theory notes;
- candidate Rule proposals;
- accepted versioned Rules after governance.

One successful case does not automatically create a production rule.

## 6. Information architecture

```text
Moodify Ear
├── Home / Instrument State
├── New Listening Case
├── Cases
│   ├── Overview
│   ├── Representations
│   ├── Judgments
│   ├── Interventions
│   ├── Verification
│   ├── Evidence
│   └── History / Recovery
├── Evidence Library
├── Benchmarks
├── Rules
└── Settings / System Status
```

Research or engineering-only tooling may live behind an explicit Laboratory area. It must not dominate the primary product path.

## 7. Core screens for the first coherent release

### 7.1 Ear home

First-layer order:

1. `MOODIFY / THE EAR OF AI`;
2. instrument state: ready, listening, judging, waiting for human, or blocked;
3. primary action: introduce one source;
4. canonical loop;
5. recent cases with evidence authority state.

No engagement metrics or generic dashboard tiles.

### 7.2 New case

One source, one objective, privacy/retention acknowledgement, and a clear start action. Advanced profiles remain collapsed unless needed.

### 7.3 Active case

Show current stage, completed stages, pending work, authoritative state, and safe cancellation/recovery. Do not expose an indeterminate spinner as the only feedback.

### 7.4 Case result

Lead with findings and decision status, followed by evidence and methods. Parameters support a judgment; they are not the headline.

### 7.5 Compare

Synchronize playback where supported, normalize comparison responsibly, expose the exact comparison question, and separate measured differences from preference.

### 7.6 Evidence detail

Show claim, source, method/version, observations, authority, limitations, integrity values, and export/reference controls.

## 8. Judgment and human authority

Ear distinguishes four levels:

| Level | Meaning | Allowed outcome |
|---|---|---|
| Measurement | Reproducible observation under a named method | Report fact within tolerance |
| Rule judgment | Deterministic conclusion under an approved rule scope | Decide only within that scope |
| Model inference | Probabilistic interpretation | Report confidence and limits |
| Human listening judgment | Designated perceptual or product authority | Final decision where required |

Machine operation may be unattended for validated, bounded cases. It must not eliminate the `human_required`, `inconclusive`, or `failed` outcomes to make the loop appear autonomous.

## 9. Evidence and verification standard

Every completed case should preserve, where applicable:

- source identity and integrity hash;
- objective and configuration;
- state history and authority transitions;
- measurement profile and implementation versions;
- structured measurements;
- judgment findings with evidence links;
- intervention rationale and parameters;
- candidate identities;
- before/after comparisons and invariant checks;
- human review record when required;
- manifest hashes, environment facts, and failure traces;
- closure outcome and reuse eligibility.

## 10. Failure and recovery

| Failure | Product behavior | Recovery |
|---|---|---|
| Invalid source | Do not begin a valid case | Replace or repair source |
| Decode/measurement failure | Mark stage failed; retain safe diagnostics | Retry compatible stage/version |
| Worker interruption | Preserve authoritative state and idempotency | Resume from last valid checkpoint |
| Candidate generation failure | Preserve source and successful candidates | Retry failed candidate or close partial |
| Verification invariant failure | Block improvement claim | Inspect, revise intervention, or reject |
| Evidence packaging failure | Case cannot be called complete | Rebuild manifest from preserved records |
| Judgment uncertainty | No forced verdict | Escalate to human or close inconclusive |

Failures are learning assets when safely captured; they are not hidden success states.

## 11. Ear–Music interaction

Music may request Ear analysis through a bounded service contract. Ear returns status and stable evidence references, not internal database access.

Before Music may display evidence, it must be explicitly marked publish-safe and, where required, human-reviewed. Ear never changes a track's publication state, and its experimental metrics never automatically rank, certify, or reject a musical work.

## 12. First-release scope

Required:

- source ingest with integrity identity;
- one authoritative Production Case lifecycle;
- WSE minimum representation set;
- explicit findings and uncertainty;
- controlled candidate creation where justified;
- before/after verification;
- evidence manifest and case export/reference;
- failure and recovery states;
- human-review pathway where required.

Deferred:

- universal aesthetic scoring;
- automatic public certification;
- broad third-party plugin ecosystem;
- uncontrolled autonomous rule updates;
- full DAW replacement;
- social or music catalogue features;
- claims that MSE exists where only WSE measurement is available.

## 13. Product success measures

Initial Ear success is not daily engagement. It is whether users can trust and reuse its work.

Measure:

- percentage of cases with complete evidence manifests;
- reproducibility across supported environments;
- measurement validity and version coverage;
- recovery success after interruption;
- rate and reasons for inconclusive or human-required outcomes;
- time from source to an understandable finding;
- reviewer agreement within declared scopes;
- number of cases accepted into benchmarks or rule research;
- escaped unsupported claims or authority violations, target zero.

## 14. Implementation gate

An Ear feature may enter development only if it states:

- the auditory-loop stage served;
- the WSE, MSE, or PPE discipline involved;
- the Production Case and user outcome;
- authoritative input/output contracts;
- evidence produced;
- verification and failure behavior;
- authority and escalation boundary;
- how the result can improve a later case.

