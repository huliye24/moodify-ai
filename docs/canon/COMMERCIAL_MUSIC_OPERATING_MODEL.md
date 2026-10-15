# COMMERCIAL MUSIC OPERATING MODEL — Phase 1

**Status:** CANONICAL DIRECTION / PARTIALLY IMPLEMENTED  
**Date:** 2026-10-08  
**CANON_CHANGE:** YES  
**Authority:** human decision → `AGENTS.md` → this document

## 1. Phase-one business definition

Moodify is Rongjing WenChuan's internal AI commercial-music production system. In this phase,
external B2B clients buy music and production service; they do not buy or operate Moodify.

> Moodify turns creative intent and generated audio into reviewed, traceable and deliverable
> commercial music.

This is a phase boundary, not a second product identity. Moodify Cloud remains the carrier,
Judge remains the core model, Wavefield remains the technical direction, and Core / Protocol
remain the shared foundation.

## 2. Product surfaces

| Surface | Phase-one role | Boundary |
|---|---|---|
| Studio | Internal production operating system | project/cue intake, candidates, finishing, review, delivery |
| Judge | Single quality and acceptance authority | technical + scene-fit evidence; never self-approves delivery |
| Cloud | Production memory and compute control plane | projects, assets, jobs, versions, evidence; deployment claims require runtime proof |
| Play | First-party catalogue and client review | only Rongjing WenChuan-controlled works and explicitly shared review sets |
| Core / Protocol | Shared technical foundation | not a second public product |

Paused for phase one: general consumer accounts, UGC uploads, social graph, recommendation feed,
creator marketplace, public Studio SaaS and a general-purpose listener app. Existing code is not
mass-deleted; it is classified and removed from the active product path gradually.

### Operator-first correction (2026-10-08)

Studio is operated by a trained internal team. It does not need to hide professional controls to
minimise consumer learning cost. It should optimise for repeatable throughput, precision, batch
operation, inspectability and recoverability. Dense tables, multi-panel workspaces, keyboard
shortcuts, explicit parameters and specialised stages are allowed when they improve real work.

This does not authorise arbitrary feature accumulation. Every control must map to a production
fact, Core capability, evidence record or human decision. Interfaces may expose complexity; they
may not duplicate DSP, Judge, job or workflow authority.

### Website correction (2026-10-08)

The public website is primarily the team's own observation and publication window. It preserves
research documents, experiment images, evidence, works and familiar navigation. Customer
acquisition and transactions currently happen through Xiaohongshu, Douyin and Taobao. The website
is not required to act as a sales funnel and must not be collapsed into a B2B landing page merely
because the production business is B2B.

## 3. Canonical production object model

```text
Project
  └─ Cue (scene brief + delivery requirement)
       └─ Candidate (provider-neutral generated_audio)
            ├─ Rights Record
            ├─ Judge Before
            ├─ Production Graph / Mix Graph / renders
            ├─ Judge After
            ├─ Human Approval
            └─ Delivery Package → optional Play review set
```

Suno is an initial provider, not a domain object. The contract says `generated_audio` and records
the provider and source digest. Replacing a provider must not rewrite Project, Cue, Judge or
delivery history.

## 4. Hard gates

A candidate is not delivery-ready unless all of these facts exist for the same candidate:

1. a human-attributed Rights Record with referenced evidence;
2. Judge Before evidence;
3. Judge After with `ACCEPT` (or an explicit original-selection path in the finishing contract);
4. human approval;
5. the client's delivery specification is met by the produced package.

Audio processing cannot create, repair or infer commercial rights. `HUMAN_VERIFIED` means a named
person reviewed recorded evidence; it is not legal advice from Moodify.

## 5. Studio information architecture

Studio opens on Projects, not a generic upload surface. Within a Project, work is organised by
Cue. Upload/import belongs inside a Cue and creates a Candidate. The existing
`HEAR → JUDGE → ACT` capability chain remains, but it executes in business context:

```text
Client Brief → Cue → Candidate → Rights Gate → HEAR/JUDGE BEFORE
→ ACT/Production → JUDGE AFTER → Human Review → Delivery
```

The current deep finishing gates remain authoritative. This document does not pretend that
master-grade separation, per-stem tuning, scene-aware Judge-1 or automated mastering is complete.

The target operator workspace may expose these specialised areas without flattening them into a
consumer wizard:

```text
Project / Cue control room
Candidate and provenance intake
Rights and source ledger
HEAR / Judge evidence console
Stem, structure and score laboratory
Repair and tuning bench
Multi-track composition and mix graph
Wavefield and MATLAB experiment bridge
A/B/Original review and decision ledger
Batch queue, failures and retries
Delivery specification, package and manifest
```

The canonical workflow still comes from shared artifacts and gates. These are views and tools over
one production truth, not separate products or state machines.

## 6. Play boundary

Play is not a public music platform in phase one. Its sources are closed:

- approved Rongjing WenChuan catalogue releases;
- private client review sets created from a Project;
- no public uploads, creator profiles, followers, comments, rankings or recommendation feed.

Client review may collect comments and `APPROVED / REVISION_NEEDED`, but the result returns to the
same Cue evidence history; it does not become a separate social or job authority.

## 7. MATLAB laboratory

MATLAB remains an experimental laboratory for signal processing, wavefield, psychoacoustics and
calibration. Experiments must publish reproducible inputs, parameters, metrics, environment and
results. A MATLAB result may inform a rule or Core implementation only after review and evidence;
MATLAB does not become a second DSP/Judge authority and is not required in the production runtime.

## 8. Implementation and migration

Implemented in the first slice:

- immutable Core contracts for Project, Cue, Candidate, Rights, two Judge records and human
  approval;
- delivery readiness derived from evidence, not advanced by a mutable workflow status;
- hard failure on missing rights attribution/evidence or cross-candidate records.

Next implementation order:

1. Studio Project/Cue workspace and local artifact persistence;
2. Candidate import with provider-neutral provenance and Rights Gate;
3. connect existing HEAR/JUDGE and finishing artifacts to a Candidate;
4. delivery-package specification and hash manifest;
5. first-party Play catalogue plus private review sets;
6. Cloud persistence/queue only after its actual runtime and data authority are verified.

Migration is additive. Existing cases remain valid and can be linked to a Candidate explicitly;
there is no automatic reinterpretation of old cases. Rollback removes the new contract consumer
and UI entry points while retaining evidence files as inert records.

## 9. Success criteria

The phase is validated by one real web-series order flowing end to end. Product metrics are:

- brief-to-first-version time;
- first-pass acceptance rate;
- average revision count;
- delivery-spec pass rate;
- rights-complete rate;
- Judge/human agreement (with calibration scope stated);
- per-cue cost and project gross margin.

DAU, public registrations and catalogue scale are not phase-one success metrics.
