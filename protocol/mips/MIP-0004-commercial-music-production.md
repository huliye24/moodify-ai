# MIP-0004 — Commercial Music Production Records

```yaml
mip: 0004
title: Project, Cue, Candidate, Rights and Delivery Readiness records
author: Moodify maintainers
status: DRAFT
type: Core-Contract
created: 2026-10-08
requires: MIP-0002
supersedes: none
```

## Abstract

Defines additive Core contracts for Moodify's internal commercial-music production loop. The
records connect a client Project and Cue to provider-neutral generated audio, rights evidence,
Judge Before/After, human approval and delivery readiness. Readiness is derived from records and
does not introduce a second authoritative state machine.

## Motivation

The existing production case describes audio work but not the business context needed to deliver
music for a web series. A technically acceptable render can still be unusable because its rights
record is incomplete, its scene brief is absent, or nobody approved it. Conversely, DSP cannot
turn an unlicensed source into a licensed source.

## Contract surface

Reference implementation:
`moodify-core-package/src/moodify/contracts/commercial_music.py`.

Schema identifiers:

- `moodify.commercial.project/0.1`
- `moodify.commercial.cue/0.1`
- `moodify.commercial.candidate/0.1`
- `moodify.commercial.rights/0.1`
- `moodify.commercial.judge/0.1`
- `moodify.commercial.approval/0.1`
- `moodify.commercial.delivery-readiness/0.1`

`CandidateTrack.source_provider` is descriptive, not a closed provider enum. Suno may be recorded
there, but no downstream contract may require Suno specifically.

`RightsRecord.conclusion=HUMAN_VERIFIED` requires a terms reference, evidence references, reviewer
and review time. This is provenance and human accountability, not automated legal advice.

`DeliveryReadiness.ready` is true only when the same Candidate has human-verified rights, both
Judge phases, an accepting Judge After result, and explicit human approval. Consumers must derive
it again from the source records; the readiness document is a report, not authority.

## Compatibility and rollback

This is additive and does not change MSP/0.1 or MSP/0.2 wire jobs. Existing production cases stay
valid. Rollback removes consumers of these new records; old records remain readable JSON evidence.

## Evidence and acceptance

Current evidence is contract-level tests only. MIP remains `DRAFT` until one real project proves:

- at least one Project with multiple Cues;
- candidate/source hash linkage;
- a rights record backed by retained evidence;
- two Judge passes and human approval;
- delivery manifest hashes matching exported files;
- a revision returning through the same Cue without overwriting history.

## Security and privacy

Project names, briefs, client feedback and unreleased audio are confidential production data.
Cloud storage, review links and logs must default private. Public Play publication is a separate,
explicit human action and is not implied by approval for client delivery.

## Unresolved

- Delivery-package schema and client-specific specification vocabulary.
- Retention and access policy for client briefs and review links.
- Legal reviewer role names and jurisdiction-specific checklist content.
- Scene-fit Judge taxonomy and its human calibration protocol.
