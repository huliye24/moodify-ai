# PRODUCT CANON V3 — Alignment Report

**Date:** 2026-10-03
**Task:** `MOODIFY_PRODUCT_DEFINITION_AND_EXECUTION_001` — TASK 001 (Canon Realignment Only)
**Branch:** `deepseek/moodify-network-restructure-001`
**Base:** this task was executed on top of the 15-commit network restructure, by explicit human
decision of 2026-10-03, because the task document's assumed base (`main` @ `c11bc7f5`) is no
longer the working reality.
**Scope:** documentation only. **No network, Android, cloud, or Core code was added.**

---

## 1. Files changed

### New authority files

| File | Purpose |
|---|---|
| `docs/canon/PRODUCT_DEFINITION_V3.md` | Product Canon v3: five layers, the first product loop, App as Personal Music Node, §6 DEFINED-vs-IMPLEMENTED, §8 conflict record |
| `docs/canon/TECHNOLOGY_PRINCIPLES.md` | Technology priority order, V1 exclusions, commercialization quality definition |

### New report

| File | Purpose |
|---|---|
| `docs/reports/PRODUCT_CANON_V3_ALIGNMENT_2026-10-03.md` | This file |

### Updated

| File | Change |
|---|---|
| `AGENTS.md` | Added a **Product Direction** section: the five-layer model plus the five points agents must understand, and the two unresolved items that must not be treated as settled. Minimum necessary — the rest of the file is unchanged from the restructure. |
| `docs/REPOSITORY_STATUS.md` | Status header → Canon v3.0. Added a dated **Product Canon v3 — 2026-10-03** section with a `DEFINED/TARGET` vs `IMPLEMENTED` table. |
| `README.md` | Replaced the three-concept section with the five-layer model, added the first product loop and the strategy line, and **disambiguated the term "Network"**. Existing quick-start commands and implemented-capability statements are untouched. |
| `docs/canon/CANON_CHANGELOG.md` | Added a `CANON_CHANGE = YES` entry with why / evidence / affected authority files / conflicts / migration / rollback. |

**No file was deleted.** No historical document was rewritten. Per task spec §21, documents that
conflict with v3 are left intact and overridden by authority, not silently edited.

---

## 2. Verification performed

| Check | Result |
|---|---|
| `git diff --check` | clean |
| Repo-wide search for transfer implementation | **no match** — confirms §6 of V3 is accurate |
| Conflicting top-level product definitions | searched live canon + root; findings in §3 below |
| Statements checked against repository reality | all §6 status claims verified (see §2.1) |

### 2.1 Every factual claim in V3 §6, verified

```text
moodify-core-package/          679 tracked files, pyproject name=moodify version=1.0.0-rc.1   VERIFIED
moodify protocol validate|process   subcommands present                                       VERIFIED
moodify-desktop/               name=moodify-desktop version=1.0.0-rc.1 devDep electron ^33   VERIFIED
                               scripts == {"start": "electron ."}  (no DSP, shell only)        VERIFIED
apps/android                   namespace com.moodify.app,      versionCode 20, 2.0.0          VERIFIED
apps/music-android             namespace com.moodify.music,    versionCode 3,  2.0.1          VERIFIED
```

Implementation search (`publish to my library` / `lan sync` / `pairing token` /
`local transfer` / `/sync`) across `*.py`, `*.kt`, `*.js`, `*.ts`:

```text
→ zero matches.  The first product loop does not exist.  V3 says so.
```

---

## 3. Known conflicts

Recorded rather than resolved. Per task spec §21, current Canon authority overrides older
text; older text is preserved.

### 3.1 Creator-side primary surface: CLI or Studio? — **GENUINE CONFLICT**

| Source | Says |
|---|---|
| `docs/canon/CURRENT_CANON.md` §1 (v2.1, 2026-09-23) | Creator Side = **Moodify CLI**; "CLI 是首要执行接口" |
| `docs/canon/PRODUCT_DEFINITION_V3.md` §1 (v3.0) | Creator Side = **Moodify Studio** |

**Interim treatment (NOT a resolution):** CLI and Studio are both Creator-side and are not a
second product identity — CLI is the automation/agent interface (`PROCESS`), Studio is the
human workspace (`PROCESS`), both calling one Core. This is consistent with the restructure's
own README and with `AGENTS.md`.

**But "which is the primary outward Creator-side product surface" is undecided.**
→ `HUMAN_DECISION_REQUIRED` (see §5).

### 3.2 The word "Network" means two different things — **TERM COLLISION**

| Where | Means |
|---|---|
| `GOVERNANCE.md`, `docs/governance/NETWORK.md`, `MAINTAINERS.md` (restructure, earlier the same day) | **Moodify Network = the open collaboration network** |
| `PRODUCT_DEFINITION_V3.md` §1 | **Network = the product layer connecting personal music nodes** |

Both are now live Canon documents using the same proper noun for different concepts. This is
exactly the class of ambiguity that made a directory named `protocol/` hold a different
protocol.

**Mitigation applied:** `README.md` now states the collision explicitly under
"Two different things called 'Network'", and V3 §1 and §8 use the product-layer meaning
consistently. **Renaming is not done** — it would touch governance documents and is a human
call. → `HUMAN_DECISION_REQUIRED`.

### 3.3 App definition: expansion, not conflict

`CURRENT_CANON.md` calls App the **Listening Interface**; V3 calls it a **Personal Music
Node**. Judged an **extension**: `PLAY` remains the core action, and since V1 implements only
My Library + Playback, V1 App behaviour matches the v2.1 description. Recorded in V3 §8.2.

### 3.4 No other conflicts found

Searched live canon and root documents for `Shared Core`, `one Core, two interfaces`,
`four product`, `四个平级`, `Ear of AI`, `Web3`, `token economy`. All remaining hits are either
already-marked historical/deprecated statements or the legitimate
`One Core, Multiple Interfaces` invariant (which V3 preserves). No stray "four-product
platform" narrative survives in live authority documents.

---

## 4. Future implementation gaps

Ordered by the roadmap in the task document. **None of these exists today.**

| Gap | Roadmap stage | Notes |
|---|---|---|
| Studio "Publish to My Library" action | V1 | No publish concept anywhere in `moodify-desktop/` |
| Track package + `manifest.json` (`moodify.track/0.1`) | V1 | Schema not yet created; task spec §9 gives a proposed shape |
| LAN HTTP sync service + pairing token | V1 | Task spec §10 gives the proposed 12-step flow |
| Android receive + local library (SQLite) | V1 | Task spec §11 gives the proposed model |
| Canonical Android client decision | **blocks V1** | Two competing trees; see §5 |
| Account + device registration | V1.1 | — |
| Friend share + relay/object storage | V1.2 | May reuse `moodify-music-package/` assets |
| Social graph | V1.3 | — |
| Creator feedback (A/B share, timestamp comments) | V1.4 | Connects back to the Evidence loop |
| Open network / public profiles / third-party clients | V2 | — |

**Dependency note:** the V1 transfer work cannot sensibly start before the canonical Android
client is chosen, because the receiver is half the loop.

---

## 5. HUMAN_DECISION_REQUIRED

| # | Question | Why it is not an engineering decision |
|---|---|---|
| 1 | **Which Android client is canonical — `apps/android` or `apps/music-android`?** | Evidence contradicts: both trees build; `apps/android` is `com.moodify.app` v2.0.0 (matches the shipped release manifests), `apps/music-android` is the one `release.yml` builds and the one whose feature set the 3.1.0 notes describe. Product boundary → human sovereignty (`AGENTS.md` L71). **Blocks V1.** Task 002 per the task document. |
| 2 | **Creator-side primary surface: CLI or Studio?** | Changes outward product identity. See §3.1. |
| 3 | **Resolve the "Network" term collision** (§3.2) | Touches governance documents; a naming/product decision. |
| 4 | **Scaffold `manifest.json` v0.1 fields before or after the transport works?** | Minor, but it defines a wire contract; the task spec §9 proposes a shape and §9 says grow only when a feature needs it. |

Items 2 and 3 are new, created by this task. Item 1 is carried over and now has a deadline
(it blocks V1).

### Carried over from the restructure (still open)

`deploy.yml` disposition · `moodify.contribution` in Core · `moodify_runtime/` future ·
4.0 GB git history · `moodify-desktop` Windows packaging. See
[`../restructure/RESTRUCTURE_REPORT.md`](../restructure/RESTRUCTURE_REPORT.md) §14.

---

## 6. Compliance with TASK 001 constraints (§20)

| Forbidden | Done? |
|---|---|
| delete legacy Android | **No** — neither tree touched |
| add server / login / social graph / account / cloud storage / WebSocket / P2P | **No** |
| rewrite Core | **No** |
| rewrite desktop | **No** |
| introduce Flutter / React Native | **No** |
| change audio algorithms | **No** |
| mass-delete historical directories | **No** — zero files deleted in this task |

Task 001 §23 stop condition: **no work on Task 002 was started.** The next task should be
written after re-auditing the merged `main`, not from the task document's assumptions.
