# Moodify Product Constitution

**Document ID:** MFY-PRODUCT-CONSTITUTION-001  
**Version:** 1.0  
**Date:** 2026-08-14  
**Status:** APPROVED BASELINE — approved by human product authority 2026-08-14  
**Scope:** Moodify brand, official website, Moodify Ear, Moodify Music, and their shared boundaries

## 1. Purpose

This constitution defines what Moodify is before further technical expansion. It is the product-level frame within which product design, research, engineering, operations, and communication must operate.

It does not discard the repository's existing technical assets. It assigns them to the correct product role and prevents implementation history from deciding future product identity.

## 2. Core identity

Moodify is:

> **The Ear of AI — an Auditory Intelligence System.**

Its foundational question is:

> **Can machines learn to hear?**

Its canonical auditory loop is:

```text
Listen -> Represent -> Judge -> Intervene -> Verify -> Learn
```

Moodify exists because generating sound and hearing sound are different capabilities. A system that produces audio is not thereby able to understand what happened, judge it responsibly, verify an intervention, or learn from evidence.

## 3. Product family

Moodify has one master brand, one official website, and two products.

```text
Moodify
├── Official Website — explains the category, vision, products, and evidence
├── Moodify Ear — auditory intelligence, judgment, verification, and learning
└── Moodify Music — discovery, listening, creation, publication, and connection
```

The official website is the public entrance to the product family. It is not a third application and must not duplicate the working surfaces of Ear or Music.

### 3.1 Official Website

**Purpose:** make Moodify understandable and credible.

The website owns:

- category definition and brand narrative;
- the relationship between Moodify, Ear, and Music;
- public explanation of the auditory loop;
- carefully qualified research and evidence communication;
- navigation into the two products.

It does not own production cases, music publication state, or application workflows.

### 3.2 Moodify Ear

**Purpose:** enable machines and people to listen, represent, judge, intervene, verify, and learn from sound through traceable evidence.

Ear owns:

- source identity and ingest integrity;
- auditory and musical representation;
- measurement, diagnosis, uncertainty, and judgment;
- controlled intervention experiments;
- before/after verification;
- Production Cases, Measurement Records, Evidence Artifacts, and Rules;
- failure, recovery, reproducibility, and learning loops.

Ear is not an automatic-mastering product, preset browser, generic audio editor, or a black-box quality score.

### 3.3 Moodify Music

**Purpose:** create a music environment centered on works, creators, listening, provenance, and meaningful connection.

Music owns:

- user and creator identity within the product experience;
- tracks, immutable versions, albums, libraries, playlists, and publication;
- discovery, playback, collection, following, and creator relationships;
- Creation Passport declarations;
- support, licensing, or collaboration intent workflows.

Music is not an Ear dashboard, an audio-processing console, or a public ranking of experimental Ear metrics.

### 3.4 Auditory Intervention Laboratory

Existing DSP and post-processing capabilities are retained as the:

> **Auditory Intervention Laboratory**

It is an Ear subsystem used to create controlled candidates and evidence. It is not Moodify's product identity and is not the backend parent of Moodify Music.

## 4. Shared product promise

All Moodify surfaces must express the following promises:

1. **Hearing before intervention.** Do not change sound without a stated reason.
2. **Evidence before claims.** Do not call a result better without inspectable support.
3. **Uncertainty before false confidence.** State limits, missing evidence, and unresolved judgment.
4. **Human authority where required.** Machine judgment may recommend or decide within an approved scope; unresolved listening judgment must escalate rather than disappear.
5. **Traceability before convenience.** Important state changes and claims must be attributable and recoverable.
6. **Learning before feature accumulation.** A case should leave reusable knowledge, not only an output file.
7. **Product boundaries before code reuse.** Shared infrastructure must not create shared authority by accident.

## 5. Authority model

Authority is divided by domain.

| Domain | Authority |
|---|---|
| Product identity and boundary | This constitution after human approval |
| Ear case lifecycle | Canonical `ProductionCase` state machine |
| Ear measurements | Versioned measurement contracts and implementations |
| Ear machine judgment | Versioned algorithm/rule within its declared validation scope |
| Unresolved perceptual judgment | Designated human reviewer or explicit `human_required` state |
| Music publication | Music publication state and authorized creator action |
| Music ownership | Music identity and ownership service |
| Public claims | Product owner plus publish-safe evidence gate |

No subsystem may silently promote an experimental metric into production truth, public music certification, copyright judgment, or creator ranking.

## 6. Ear–Music boundary

Ear and Music are separate products with limited, explicit exchange.

Permitted shared references:

- immutable asset or version ID;
- SHA-256 integrity value;
- Ear Production Case external reference;
- publish-safe Evidence Artifact reference and authority state;
- compatible request ID, error model, and contract versions.

Forbidden coupling:

- Music importing Ear internal auditory, orchestration, or intervention modules;
- Music reading or mutating Ear databases or case state;
- Ear mutating Music publication state;
- Ear experimental scores becoming public rankings or quality certification;
- Creation Passport being represented as Ear verification or legal ownership proof.

Cross-product analysis follows an exchange workflow only:

```text
requested -> processing -> evidence_ready -> human_reviewed -> optionally_attached
```

This workflow does not replace either product's authoritative state machine.

## 7. Product experience principles

Every primary surface must answer:

- Which user is this for?
- What single decision or action dominates this surface?
- Which product state is authoritative here?
- What evidence is visible now?
- What complexity is progressively disclosed?
- What happens when data is missing, uncertain, or failed?
- How does the user recover?

Moodify's visual character is quiet, exact, durable, and authoritative without spectacle. It uses restrained proportions, graphite fields, mineral text colors, one evidence/progress accent, low visual pressure, and charts that answer one question at a time.

## 8. Product development sequence

New development should follow this sequence:

```text
Product constitution
-> information architecture
-> critical user journeys
-> interaction prototype
-> state and evidence contracts
-> technical architecture
-> implementation
-> verification
-> reusable asset
```

A feature is not ready for implementation until it has:

- a named product and canonical subsystem;
- a user and case served;
- a dominant decision or outcome;
- authoritative state ownership;
- evidence and verification requirements;
- failure and recovery behavior;
- explicit non-goals.

## 9. Non-regression rules

Moodify must not regress into:

- automatic mastering as the master brand;
- a collection of presets presented as intelligence;
- a generic AI music feed;
- a social platform without an auditory or musical thesis;
- a dashboard of unvalidated metrics;
- a second authoritative state machine;
- a system that removes required human listening authority by omission;
- a product that hides failure or uncertainty behind visual polish.

## 10. Repository placement

| Surface or capability | Canonical location |
|---|---|
| Product framework | `docs/product-framework/` |
| Ear backend | `moodify-core-package/` |
| Ear native client | `apps/android/` |
| Music web/PWA | `apps/music-web/` |
| Music mobile | `apps/music-android/` |
| Music service | `moodify-music-package/` |
| Shared contracts | `docs/contracts/`, `schemas/canonical/` |
| Operations | `ops/` |
| Historical task packs | `补丁包/` |

## 11. Approval and precedence

The full product framework is an **approved baseline** (human product authority, 2026-08-14). It must still never silently override a frozen scientific or data contract; any conflict requires the recorded-decision process below.

### Approval record

| Field | Value |
|---|---|
| Document | MFY-PRODUCT-CONSTITUTION-001 v1.0 |
| Approved by | Human product authority (huliye24) |
| Date | 2026-08-14 |
| Resolution | Accepted as Phase 1 baseline without modification |
| Evidence | Four framework files reviewed and accepted together (43/44 包审阅)；DECISION_LOG D-002/D-003；artifacts/phase1_launch/GOVERNANCE_RECONCILIATION_REPORT.md |
| Next review | On any material change to product identity, boundary, or authority model |

### Judgment-authority decision (approved 2026-08-14, D-002)

> Machine authority is limited to a validated, versioned and explicitly authorized scope. Out-of-scope, insufficient-evidence, uncertain or unresolved perceptual cases escalate to human judgment or close as inconclusive/failed.

This decision resolves the prior conflict between `docs/PHASE1_CONSTITUTION.md` and root `AGENTS.md`. The affected authority documents and public README were amended together; the deterministic reviewer remains canonical within its approved technical scope.

## 12. Definition of done

Work is complete only when it can answer:

- What user and case does this serve?
- Which product owns it?
- What is measured or observed?
- What evidence is produced?
- How is the result verified?
- Who or what has authority?
- What happens on uncertainty or failure?
- Can the result improve the next case?
