# Moodify Product Constitution

**Document ID:** MFY-PRODUCT-CONSTITUTION-001  
**Version:** 2.0  
**Date:** 2026-08-14  
**Status:** SUPERSEDED FOR PRODUCT IDENTITY AND BOUNDARY — retained as 2026-08-14 governance history

**Scope:** Moodify public product, internal auditory system, playback result, authority and release boundaries

> **Authority notice (2026-08-20):** `AGENTS.md` and `docs/canon/*` supersede this document for current product identity and external/internal boundaries. Current external product: **Moodify Music / Moodify Player**; Ear remains internal. Non-conflicting engineering and judgment principles remain reference material.

## 1. Purpose

This constitution defines what Moodify is before further technical or visual expansion. It supersedes the v1 public topology in which Moodify Ear and Moodify Music were presented as parallel public products.

The change is a reclassification, not a deletion:

```text
PUBLIC
Official Website -> Moodify Music

INTERNAL
Moodify Ear + Auditory Intervention Laboratory + rendering/playback infrastructure
```

Existing research, Production Cases, Evidence, measurements, interventions, tests and recovery systems remain valuable. They no longer require ordinary users to understand or operate them.

## 2. Core identity

Moodify remains:

> **The Ear of AI — an Auditory Intelligence System.**

Its foundational internal question remains:

> **Can machines learn to hear?**

Its canonical internal loop remains:

```text
Listen -> Represent -> Judge -> Intervene -> Verify -> Learn
```

For ordinary users, the product promise is simpler:

> **Moodify listens before you do.**

```text
SOURCE -> MOODIFY -> PLAY
```

The internal loop explains how Moodify works. It is not a burden placed on the user.

## 3. Supreme product test

Moodify must first stand when the screen is removed.

> **If brand story, visual polish, technical reports and feature count disappear, leaving only sound, is Moodify still worth using?**

The product stands only when the answer is **YES**.

Value order:

```text
1. Sound result
2. Result stability and repeatability
3. Playback experience
4. Internal evidence, authority and recovery
5. Visual and brand expression
```

Visual design earns the first opening. Sound earns the return.

Claims about better listening require level-matched, randomized and identity-blind listening evidence. Brand, filenames, processing labels and technical metrics must not reveal the candidate during judgment.

## 4. Product topology

### 4.1 Official Website

The official website is the public entrance, not a third product.

It owns:

- the shortest truthful explanation of Moodify;
- entry into Moodify Music;
- a small amount of qualified, publish-safe evidence;
- contact, privacy and company context.

It must not:

- present Ear as a parallel consumer product;
- require users to understand WSE, MSE, PPE, ProductionCase or Evidence internals;
- use technical complexity as a substitute for audible value;
- claim an automated per-track rendering capability that the deployed path does not yet provide.

### 4.2 Moodify Music — the only public product

Moodify Music is:

> **A player that listens to music before it plays music.**

Its first public axis is:

```text
Library -> Track -> Now Playing -> Play
```

Music owns public identity, catalogue, immutable track versions, library, playback and the minimum creator/source intake required to supply listening-ready works.

Community, social, licensing, playlists and creator administration are subordinate capabilities. They do not receive public prominence unless evidence shows they directly strengthen the Source-to-Play experience.

Music must not expose Ear measurements, experimental rankings, DSP graphs, presets or internal confidence as a consumer burden.

### 4.3 Moodify Ear — internal research and production system

Moodify Ear is:

> **Moodify's internal system for auditory research, source analysis, Production Cases, judgment, intervention, verification, evidence and playback decisions.**

Ear owns:

- source identity and ingest integrity;
- auditory and musical representation;
- measurement, diagnosis, uncertainty and bounded machine judgment;
- controlled intervention and BYPASS decisions;
- before/after verification;
- Production Cases, Measurement Records, Evidence Artifacts and Rules;
- failure, recovery, reproducibility and learning;
- internal operator and reviewer workflows.

Ear Workbench, Case, Result, Compare, Evidence, Human Review and System Status remain internal operator/research surfaces. They are not public consumer launch surfaces.

Internalization must be implemented through classification, routing, identity and access control—not by deleting Ear authority or hiding unsecured public endpoints with CSS.

### 4.4 Auditory Intervention Laboratory

Existing DSP and post-processing capabilities remain the **Auditory Intervention Laboratory**, an internal Ear subsystem for controlled candidates and evidence.

It is not Moodify's public identity, a preset product, or permission to alter every track.

## 5. Source and playback result

The source is immutable and must not be irreversibly overwritten.

```text
SOURCE AUDIO
    -> internal listening and judgment
    -> optional intervention or BYPASS
    -> verification
    -> PLAYBACK-READY VERSION
    -> PLAY
```

A playback-ready version may include a processed asset, rendering profile, playback metadata, device/output policy and verification provenance. The exact implementation must follow verified repository reality; this constitution does not authorize inventing a second rendering system.

Every track is judged independently. Valid outcomes include:

- meaningful intervention;
- gain-only preparation;
- subtle rendering;
- **BYPASS**.

Every track should be judged does not mean every track must be changed. Moodify must not create a fixed house coloration.

## 6. Shared promises

1. **Hearing before intervention.** Do not change sound without a stated reason.
2. **Sound before story.** Brand and technical language cannot substitute for audible value.
3. **Evidence before claims.** Do not call a result better without suitable evidence.
4. **BYPASS before forced difference.** No change is a successful result when change is not justified.
5. **Uncertainty before false confidence.** State limits and unresolved judgment internally.
6. **Human authority where required.** Machine authority is limited to validated, versioned and authorized scope.
7. **Source preservation before convenience.** Original assets remain identifiable and recoverable.
8. **Traceability before scale.** Important decisions and outputs must be reproducible.
9. **Learning before feature accumulation.** Cases should leave reusable knowledge.
10. **Quiet public surface, rigorous internal system.** Complexity belongs inside Moodify.

## 7. Authority model

| Domain | Authority |
|---|---|
| Product identity and public/internal boundary | This constitution after human approval |
| Public product | Moodify Music |
| Ear case lifecycle | Canonical `ProductionCase` state machine |
| Ear measurements | Versioned measurement contracts and implementations |
| Machine judgment | Versioned rule within its declared validated scope |
| Unresolved perceptual judgment | Designated human reviewer or explicit `human_required` |
| Music publication and ownership | Music service and authorized creator action |
| Source integrity | Immutable ID/version plus cryptographic integrity evidence |
| Playback-ready selection | One declared, versioned authority; no client guessing |
| Public claims | Human product authority plus publish-safe evidence gate |
| Public release GO | Human product authority |

No experimental metric may silently become production truth, a public quality score, copyright judgment or creator ranking.

## 8. Music–Ear boundary

Music depends on Ear as an internal production capability, not through direct code or database coupling.

Permitted exchange:

- immutable asset/version ID and SHA-256;
- Ear Production Case external reference;
- publish-safe Evidence Artifact reference and authority state;
- processing/request status, request ID, error and contract version;
- declared playback-ready asset/profile reference when implemented and verified.

Forbidden coupling:

- Music importing Ear auditory, orchestration or intervention internals;
- Music reading or mutating Ear databases or case state;
- Ear mutating Music publication state;
- Music clients inventing a rendering decision;
- Ear experimental scores becoming public rankings or certification;
- Creation Passport being represented as Ear verification or legal proof.

Existing bounded exchange states remain valid until intentionally superseded:

```text
requested -> processing -> evidence_ready -> human_reviewed -> optionally_attached
```

They do not replace either system's authoritative state machine.

## 9. Release model

The public release candidate contains:

- Official Website;
- Moodify Music public web surface;
- verified public media and playback path;
- Music mobile only when independently ready.

Internal production dependencies may include:

- Ear API and worker;
- ProductionCase and Evidence storage;
- human review;
- intervention/verification pipeline;
- playback-ready asset preparation;
- backup, recovery, security and observability.

Ear consumer landing pages and public Workbench reachability are not public release criteria. Ear reliability, evidence integrity, security, recovery and correct output remain release-blocking whenever they affect Music playback.

## 10. Development and subtraction rule

Every public feature must answer:

> **Does this directly improve Source -> Moodify -> Play?**

If not, it must be internalized, deferred, demoted or removed from the public surface. Existing implementation effort is not a reason for public prominence.

Development sequence:

```text
Sound hypothesis
-> blind listening protocol
-> source/result contract
-> internal production path
-> playback path
-> failure and recovery
-> minimal public interaction
-> visual refinement
```

## 11. Non-regression rules

Moodify must not regress into:

- automatic mastering as the public identity;
- presets presented as intelligence;
- a fixed Moodify sound;
- forced processing where BYPASS is correct;
- a generic AI music feed or social platform;
- an Ear metrics dashboard exposed as Music;
- a second authoritative rendering or state machine;
- public technical theatre unsupported by blind listening;
- visual polish that hides failure, uncertainty or raw playback;
- deletion of internal evidence merely because Ear is no longer public.

## 12. Repository placement

| Surface or capability | Classification | Canonical location |
|---|---|---|
| Product framework | AUTHORITY | `docs/product-framework/` |
| Official website | PUBLIC ENTRY | `ops/web_origin/site/rongjingmusic/` |
| Music web/PWA | PUBLIC PRODUCT | `apps/music-web/` |
| Music Android | PUBLIC CANDIDATE | `apps/music-android/` |
| Music service | PUBLIC PRODUCT SERVICE | `moodify-music-package/` |
| Ear backend | INTERNAL CANONICAL | `moodify-core-package/` |
| Ear native client | INTERNAL OPERATOR | `apps/android/` |
| Ear Workbench | INTERNAL OPERATOR | `apps/ear-workbench/` |
| Intervention Laboratory | INTERNAL RESEARCH/PRODUCTION | Ear intervention modules and tools |
| Shared contracts | SHARED BOUNDARY | `docs/contracts/`, `schemas/canonical/` |
| Operations | SHARED/INTERNAL | `ops/` |
| Historical task packs | PROCESS/HISTORICAL | `补丁包/` |

## 13. Approval and precedence

Version 2.0 supersedes version 1.0 wherever v1 describes Ear and Music as parallel public products. It does not silently override frozen scientific, data, state-machine or authority contracts.

| Field | Value |
|---|---|
| Document | MFY-PRODUCT-CONSTITUTION-001 v2.0 |
| Approved by | Human product authority (huliye24) |
| Date | 2026-08-14 |
| Resolution | Moodify Music is the only public product; Moodify Ear is internal research and production authority |
| Supreme test | Product value must survive removal of brand, UI, reports and feature count |
| Next review | Any material change to sound promise, public topology, rendering authority or human authority |

The approved judgment boundary remains:

> Machine authority is limited to a validated, versioned and explicitly authorized scope. Out-of-scope, insufficient-evidence, uncertain or unresolved perceptual cases escalate to human judgment or close as inconclusive/failed.

## 14. Definition of done

Work is complete only when it can answer:

- Does it improve the sound result, playback path or their reliability?
- What source and user case does it serve?
- Is it public product or internal capability?
- Which system owns the authoritative state?
- What evidence is produced?
- How is the audible result verified without identity bias?
- Is BYPASS allowed?
- What happens on uncertainty or failure?
- Is the source preserved?
- Can the result improve the next case?
