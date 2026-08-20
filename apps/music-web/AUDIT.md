# Moodify Product Architecture Audit

> **Status: HISTORICAL AUDIT — SUPERSEDED FOR PRODUCT IDENTITY AND BOUNDARY**
>
> This document records the repository assessment made on 2026-08-13. Its two-public-product model and “The Ear of AI” public identity were superseded by `docs/canon/CURRENT_CANON.md` and `docs/canon/PRODUCT_BOUNDARY.md`. Current external product: **Moodify Music / Moodify Player**. Ear is an internal system. Engineering observations remain historical evidence unless reverified.

Task: `MFY-MUSIC-COMMERCIAL-V1-001`  
Date: 2026-08-13  
Phase: A — read-only architecture audit

## Executive conclusion

Moodify should be delivered as two user-facing products on one shared platform:

- **Moodify Ear** — auditory-intelligence workspace for production cases,
  measurement, judgment, intervention, verification, and evidence.
- **Moodify Music** — listening and creator-network product for publishing,
  discovery, following, collecting, support intent, and licensing intent.

At the time of this audit, the then-canonical product identity was **The Ear of AI**. Moodify Music was treated as a
distribution and relationship surface; it must not replace the auditory
intelligence core or turn experimental measurements into public truth.

The current repository is not ready for the commercial-v1 implementation as a
single coding pass. The Music Web is a validated listening prototype, the
Android app is primarily an Ear client with several disconnected commercial UI
mockups, and the canonical backend only persists auditory jobs. There is no
shared commercial account, creator, catalog, follow, favorite, passport, or
licensing data authority yet.

## Canonical product boundary

| Product | Surfaces | Responsibility |
| --- | --- | --- |
| Moodify Ear | Web + desktop client; selected existing Android capability may be retained | `Listen -> Represent -> Judge -> Intervene -> Verify -> Learn` |
| Moodify Music | Web + iOS/Android app | Listen, publish, discover, follow, collect, support, license inquiry |
| Shared platform | API, identity, catalog, object storage, domain contracts | One user identity, creator identity, track ID, version, rights state, and publication state |

The existing post-processing code remains the **Auditory Intervention
Laboratory**, a subsystem of Ear rather than the identity of either product.

## Repository map

### Moodify Music Web

Canonical source: `apps/music-web`

- Vinext/Next-compatible React 19 application built with Vite.
- Current UI is one client-rendered listening page with a fixed player.
- Five real Cadeau10 tracks are catalogued in source; audio binaries are
  deployment assets and are excluded from Git.
- Audio origin is configurable through `NEXT_PUBLIC_AUDIO_BASE_URL`.
- Drizzle and Cloudflare integration scaffolding exists, but the canonical
  schema is intentionally empty.
- `.openai/hosting.json` declares neither D1 nor R2.
- Optional ChatGPT identity-header helpers exist but are not used by the page
  and do not establish a cross-platform Moodify account system.
- There are no creator, track-detail, publish, account, follow, favorite,
  support, or licensing routes.

Classification: **canonical Music prototype**, suitable as the Web baseline.

### Android application

Canonical source: `apps/android`

- Native Kotlin/Jetpack Compose, minSdk 26, targetSdk 36.
- Media3/ExoPlayer queue playback, seeking, and authenticated audio streaming
  already exist.
- Pair-token storage uses Android Keystore-backed AES/GCM.
- A real HTTP client supports Ear health, pairing, projects, uploads, jobs,
  results, pairwise judgment, and human decisions.
- The active navigation is Home / Process / Cases: this is an **Ear workflow**.
- Creator Center, Search, Publish, Copyright, Collaboration, and analytics
  screens exist, but many use hard-coded data, empty click handlers, or are not
  wired into the active navigation.
- There is no consumer account login, creator-follow API, favorite API,
  persistent public catalog, background playback service, or commercial data
  source proven by the inspected code.

Classification: **canonical Ear-oriented native client plus reusable Music UI
experiments**. Do not rename the whole app in place. Preserve the Ear data and
processing vertical slice; extract reusable design/player ideas into a separate
Music mobile application.

### Moodify Ear backend

Canonical source: `moodify-core-package`

- Python/FastAPI API with canonical auditory identity.
- Publicly inspected endpoints cover health, enqueueing auditory jobs, polling
  status/results, synchronous analysis, and reopening production cases.
- Upload validation includes suffix allowlisting, a size limit, streamed disk
  writes, unique server filenames, queue capacity, and cleanup on failure.
- SQLite persists only the node job queue (`jobs` table) with leases, attempts,
  failure state, case paths, and timestamps.
- Production Case, Measurement Record, Evidence Artifact, Rule, queue, worker,
  human-review, and experimental auditory packages are already present.
- This database and state machine must not be expanded into an accidental
  consumer social database.

Classification: **canonical Ear authority**. Reuse published evidence and track
version references through explicit integration contracts; do not couple
Music tables directly to the Ear queue database.

### Web origins and deployment

Canonical deployment material: `ops/web_origin`

- Nginx, systemd, Cloudflare Tunnel, timestamped releases, and symlink rollback
  are established.
- `rongjingmusic.com` currently serves the Ear workspace and proxies `/api/` to
  the FastAPI service.
- `rongjinwenchuan.xyz` currently proxies to the Music service on port 3100.
- `rongjingwenchuan.com` is a separate static product site.
- Music Web is deployed as a timestamped application release; the current
  repository lacks a committed first-class Music deployment script.
- Current WAV delivery is from the application release, not proven object
  storage. It works for the demo but is not the target publication design.

Classification: **reusable operations baseline requiring naming cleanup and a
reproducible Music release path**.

### Desktop/history

- Repository history and generated artifacts show a prior Moodify Pulse
  Electron-shaped client, but no current tracked authoritative desktop source
  was identified in the inspected canonical app directories.
- Historical processing UI must not override the Android/FastAPI verified
  behavior.
- A new `apps/ear-desktop` should only be created after locating and auditing a
  viable source package; it should wrap Ear workflows, not Music.

## Current technical stack

| Area | Verified state |
| --- | --- |
| Music Web | React 19, Vinext, Vite, TypeScript, CSS/Tailwind import |
| Music DB | Drizzle scaffold only; no canonical tables or migration |
| Music auth | Optional hosting-header helper only; not wired |
| Music media | Public HTTPS WAV URLs; deployment-release storage |
| Music player | Browser `<audio>` with play/pause, queue navigation, seek, ended-next |
| Android | Kotlin, Jetpack Compose, Media3 ExoPlayer, HttpURLConnection |
| Android auth | Ear device pairing token, not a user account |
| Ear API | FastAPI |
| Ear state | SQLite job queue plus filesystem evidence/cases |
| Hosting | Nginx + systemd + Cloudflare Tunnel, timestamped releases |

## Eight-capability gap matrix

| Capability | Existing evidence | Status | Required action |
| --- | --- | --- | --- |
| Discover | Music Web renders five local catalogue entries; Android has demo Home/Search | Partial/demo | Define public discover query and creator-aware ranking surfaces |
| Creator Space | Android has hard-coded Creator Center UI | UI experiment | Add canonical creator profile model, `/c/{handle}`, public API, ownership rules |
| Publish | Ear upload works; Android publish screens are mostly mock UI | Split/partial | Build Music upload-to-object-storage flow and publication state; preserve optional cover |
| Follow | Demo buttons and fake counts only | Missing | Add authenticated idempotent relationship model/API and privacy rules |
| Favorite | Local React state only | Missing | Add authenticated durable model/API; reconcile anonymous-to-user state later |
| Creation Passport | Task specification only; Ear has richer evidence but different semantics | Missing | Add creator declaration/version record; explicitly state it is not copyright certification |
| Support | UI language exists; no verified transaction or intent persistence | Missing | Start with honest `support_intents`; never mark paid without provider evidence |
| License Intent | No implementation | Missing/high priority | Add public/authenticated inquiry form, abuse controls, creator inbox, state transitions |

## Reuse / modify / defer / missing

### Reuse

- `apps/music-web` visual system, responsive layout, black-vinyl artwork, and
  real browser-player behavior.
- Android Media3 playback concepts, API error taxonomy, secure local secret
  storage, internationalization structure, and selected Compose components.
- Ear canonical contracts, queue recovery, evidence retention, human authority,
  upload validation patterns, and deployment rollback.
- Existing origin host, systemd supervision, Nginx limits, and Cloudflare Tunnel.

### Modify

- Music information architecture: add creator as a first-class object without
  restoring promotional copy to the listening-first homepage.
- Android repository boundary: preserve current code as Ear-oriented; do not
  mix Music account/catalog state into the Ear pairing state.
- Media storage: move release WAVs to controlled object storage or a dedicated
  media origin with byte-range, MIME, cache, access, and rollback policy.
- Authentication: create one Moodify user identity usable by Web and mobile;
  hosting-only identity headers may be an adapter, not the domain authority.
- Deployment: commit separate, reproducible Ear and Music release procedures.

### Defer

- New model training and GPU services.
- Social activity feeds, comments, public popularity leaderboards, and complex
  recommendation training.
- Real-money support until provider accounts, webhook verification, refunds,
  and human authority exist.
- Microservices, marketplace breadth, CWC monetization, and public prompt data.
- iOS implementation until the shared Music domain/API contract is stable.

### Missing

- Canonical commercial database and migrations.
- Shared user/session/token authority for browser and native clients.
- Creator ownership and handle lifecycle.
- Public track catalog and immutable track-version linkage.
- Direct/signed media upload and object ownership verification.
- Publication moderation/review and takedown workflow.
- Follow, favorite, license-intent, and support-intent services.
- Creator inbox for licensing intent.
- Music mobile application boundary and package.
- Production privacy, retention, abuse prevention, observability, and backup
  definitions for commercial data.

## Data-authority recommendation

Introduce one commercial relational authority for Moodify Music. Do not reuse
the Ear node SQLite database. Initial tables should cover:

- users and sessions/identities;
- creator profiles;
- tracks and immutable track versions;
- creation passports linked to a track version;
- follows and favorites;
- license intents and support intents;
- minimal listen events;
- publication/audit state.

The Music record may reference an Ear `production_case_id` and an approved
`evidence_artifact_id`, but Music must only expose a deliberately published
subset. An experimental score is never a public quality certification.

Database choice should be made only after confirming the intended production
provider. The current D1 scaffold is not evidence that D1 has been selected,
and no verified MySQL schema was found in this audit.

## Target source layout

```text
apps/
  music-web/       # current canonical Music Web
  music-mobile/    # new consumer iOS/Android application
  ear-web/         # canonical Ear workspace when migrated
  ear-desktop/     # local-file and batch Ear client after source audit
  android/         # retain as Ear-oriented until migration is explicit

packages/
  music-domain/
  music-api-client/
  validation/
  design-tokens/
  player-core/

moodify-core-package/  # unchanged Ear authority
```

Do not create shared packages merely for directory symmetry. Extract only code
that has two real consumers and a stable contract.

## Recommended implementation order

1. **Freeze identity and ownership contracts.** Decide the production database,
   browser/native authentication adapter, user IDs, creator ownership, track IDs,
   version IDs, and publication states.
2. **Build one Music Web vertical slice.** Creator creates a music space,
   uploads without a cover, completes a basic passport, publishes, and obtains
   a public track URL.
3. **Complete the relationship/commercial slice.** A second user listens,
   enters the creator space, follows, favorites, submits a license intent, and
   the creator sees it.
4. **Create `music-mobile` against the same API.** Start with discover, creator
   space, mini/full player, follow, favorite, and durable login. Do not fork the
   backend or user model.
5. **Formalize Ear surfaces.** Migrate the current workspace into `ear-web` and
   the validated native/local workflows into an Ear client without weakening
   evidence and human-review gates.

## Twelve-step commercial-loop readiness

| Step | Current state |
| --- | --- |
| Creator login | Not available as a shared Moodify account |
| Establish creator space | Demo UI only |
| Upload without cover | Ear upload exists; Music upload missing |
| Basic passport | Missing |
| Publish | Missing |
| Listener opens public URL | Homepage only; no track route |
| Listener plays | Working demo player |
| Enter creator space | Missing |
| Follow | Missing |
| Favorite | Local browser state only |
| Submit license intent | Missing |
| Creator sees intent | Missing |

Result: **1 of 12 is production-shaped, 2 are partial, 9 are missing.** The
commercial-v1 milestone must not be declared complete until all twelve steps
produce durable, inspectable evidence.

## Principal migration risks

1. **Identity split:** Ear pairing tokens, hosting identity headers, and future
   mobile login could accidentally create three incompatible identities.
2. **State-machine duplication:** Music publication must not become a second
   authority for Ear processing jobs or evidence status.
3. **Product drift:** creator commerce could obscure The Ear of AI and turn the
   system into a generic social marketplace.
4. **Private-data leakage:** source audio, prompts, internal measurements, file
   paths, and experimental judgments must not become public catalog fields.
5. **Media delivery:** large WAVs in application releases lack a complete object
   lifecycle, range/MIME policy, and cost controls.
6. **Mock-to-production confusion:** existing Android commercial screens contain
   hard-coded counts and inactive buttons; they are design evidence, not working
   capabilities.
7. **Premature cross-platform rewrite:** rebuilding Web, iOS, Android, Ear Web,
   and desktop simultaneously would delay the first proven commercial loop.
8. **Human authority:** rights declarations, publication, takedown, and public
   claims need review and recovery paths.

## Phase A decision

Proceed to Phase B only with the following interpretation:

- preserve `apps/music-web` as the listening-first baseline;
- create `codex/moodify-music-commercial-v1-001` from the committed Music Web
  branch, not from unrelated dirty work;
- implement the Web 12-step vertical slice before a new mobile app;
- keep the current Android Ear workflow intact during the Music build;
- create Music mobile only after the identity, domain, and API contracts are
  executable;
- do not restore the removed promotional paragraphs to the Music homepage;
- do not claim experimental Ear evidence as public validation.

No commercial-v1 code, schema, migration, or new state machine was introduced
during this audit.
