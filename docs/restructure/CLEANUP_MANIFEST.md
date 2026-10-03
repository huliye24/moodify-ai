# CLEANUP_MANIFEST — MOODIFY_NETWORK_RESTRUCTURE_001

**Baseline:** `c11bc7f5` · **Safety tag:** `pre-network-restructure-2026-10-03` · **Branch:** `deepseek/moodify-network-restructure-001`
**Date:** 2026-10-03

Every path removed from the mainline is recorded here with the dependency check that
justified it. Git history retains everything; nothing in this restructure rewrites history.

Recover any path from the safety tag:

```bash
git checkout pre-network-restructure-2026-10-03 -- <path>
```

## Classification vocabulary

| Class | Meaning |
|---|---|
| `CANONICAL` | Declared authority. Must not move without a Canon change. |
| `ACTIVE` | Live, referenced by CI/runtime/runbook. Stays in the mainline. |
| `MIGRATE` | Content preserved by moving it to a new canonical owner first. |
| `ARCHIVE` | Leaves the mainline; kept on disk or recoverable from git history. |
| `REMOVE` | Leaves the mainline; no replacement. |
| `UNRESOLVED` | Cannot be decided from repo evidence. Escalated to `HUMAN_DECISION_REQUIRED`. |

## Deletion preconditions (applied to every entry below)

Before any path was removed, all four checks were run and recorded:

1. `git grep -n "<path-or-module>"` across the whole repo, excluding the path itself
2. `rg "<module-or-package-name>"` for filesystem-level references
3. Read of all five `.github/workflows/*.yml` for CI dependency
4. Read of root `Dockerfile`, `docker-compose.yml`, `ops/`, `deployment/`, `scripts/` for deployment/runtime dependency

---

## Phase 0 — Safety line

| Path | Class | Reason | Replacement | Dependency check | Action | Commit |
|---|---|---|---|---|---|---|
| `pre-network-restructure-2026-10-03` (tag) | `CANONICAL` | Recovery point for the entire pre-restructure tree | — | n/a | created | _pending_ |
| `docs/restructure/BEFORE_TREE.txt` | `CANONICAL` | 2841-line baseline listing of all 2760 tracked files | — | n/a | created | _pending_ |
| `docs/restructure/CLEANUP_MANIFEST.md` | `CANONICAL` | This file | — | n/a | created | _pending_ |

---

## Phase 1 — Uncontroversial residue

| Path | Class | Reason | Replacement | Dependency check | Action | Commit |
|---|---|---|---|---|---|---|
| `products/` (32) | `REMOVE` | Four empty product scaffolds (`master` `qa` `rating` `supply`). All 23 `__init__.py` are **0 bytes**; only other content is 4 `config.yaml` ending `migration: status: "PHASE_A_STRUCTURE_CREATED"`. Directly contradicts `AGENTS.md` "no second public product identity". | Capabilities already live in `moodify-core-package/src/moodify/`; the `config.yaml` files cite it as their own `source` | Zero hits in all 5 workflows, root `Dockerfile`, `docker-compose.yml`, `ops/`, `deployment/`. `products/supply/config.yaml:20` points at `shared/contracts` — itself a 0-byte shell. Core imports none of it. | _pending_ | _pending_ |
| `shared/` (7) | `REMOVE` | Migration map only. **Every `.py` is 0 bytes**; `README.md` declares each future module will be copied from `moodify-core-package/src/moodify/` | Already exists in Core (`contracts/`, `authority/`, `safety/`, `node/`, `api/`) | Referenced only by `products/supply/config.yaml:20` (also removed). No import anywhere. | _pending_ | _pending_ |
| `sdk/` (9) | `REMOVE` | Placeholder SDK. `client.py:88` returns `id="placeholder-id"`, 5× `# Future: Actual API call`, 3× `raise NotImplementedError` | Core's real surfaces (`moodify.api`, `moodify.release_cli`) | Zero hits in workflows, Dockerfile, `ops/`, `deployment/`. `plugins/vst` CMake default `MOODIFY_SDK_DIR` resolves to `plugins/sdk`, not this path. **Caveat:** external downloader usage is not provable from the repo. | _pending_ | _pending_ |
| `plugins/` (9) | `REMOVE` | Unbuilt plugin surface. `plugins/github-action/plugin-ci.yml` sits **outside** `.github/workflows/`, so GitHub never executes it; zero references to `plugin-ci`. VST template needs un-vendored JUCE. | — | No workflow, no `ops/`, no `deployment/`, no import. | _pending_ | _pending_ |
| `phys-lab/` (1) | `REMOVE` | Single `run_suite.sh` launcher hardcoding `cd /home/ubuntu/moodify`. Zero audio/DSP logic. | Science lives in Core's `moodify.physics` | Dependency runs the other way: `moodify-core-package/src/moodify/physics/reliable_runner.py:90` hardcodes `/home/ubuntu/phys-lab/test_audio/piano.wav` → dangling constant fixed in the same change | _pending_ | _pending_ |
| `moodify-qa/` (26) | `REMOVE` | Standalone "Moodify QA API" — a second public product identity. `core/metrics.py` is a **verbatim copy** of `moodify.auditory.loudness` (diff shows comment-only differences). Ships a committed 45 KB `qa_storage.db`. Its 0–100 score model was explicitly rejected (`docs/plan/2026-10-02_MSP02…:114`). | `moodify-core-package/src/moodify/auditory/` | Zero hits in all 5 workflows, root Dockerfile/compose, `ops/`, `deployment/`, `scripts/`. Sole consumer is `moodify-qa-desktop` (removed together). | _pending_ | _pending_ |
| `moodify-qa-desktop/` (8) | `REMOVE` | Third Electron desktop shell (of three), and it sits downstream of the already-dead QA service — `package.json` `build.extraResources` bundles `../moodify-qa`. No audio logic at all. | `moodify-desktop/` is the surviving shell | Zero hits in workflows, `ops/`, `scripts/`, `deployment/`. Prior reduction plans assumed it was untracked; it **is** tracked (`4e2c1e28`), so `git rm -r` is required. | _pending_ | _pending_ |
| `windows版本开发/` (330) | `REMOVE` | Historical MFD-001..010 Windows work packages. **Zero source code** — 255 `.md`, 36 `.json`, 24 `.txt`, 15 `.csv`; count of `.js/.ts/.tsx/.py/.sh/.ps1/.bat/.html/.css` = 0. | Superseded by the direct Electron build in `moodify-desktop/` (`docs/REPOSITORY_STATUS.md`, 2026-10-02) | No canonical doc cites it; no code cites it; the single `MFD-0` hit outside the dir is an inventory row in the recovery report. `moodify-desktop/` has zero `MFD`/`W01`/`W02` references. | _pending_ | _pending_ |
| `apps/ear-workbench/android/` (17) | `REMOVE` | Kotlin sources with **no `build.gradle.kts`, no `settings.gradle.kts`, no wrapper** — not a buildable project. Its own README calls it an archive of `apps/android` that is "不公开、不构建、不进入任何公开发布产物". | `apps/android` | Not referenced by any workflow. The 8 HTML workbench pages are **kept** (`.gitignore` un-ignores them as canonical app source). | _pending_ | _pending_ |
| `scan_err.txt` (1) | `REMOVE` | 0-byte tracked file | — | No references | _pending_ | _pending_ |
| `.codex_tmp/` (1) | `REMOVE` | `read_roadmap.mjs` agent scratch.  Already gitignored (`.gitignore:23`) but 1 file remained tracked. | — | No references | _pending_ | _pending_ |
| `engine/` (19) → 4 files `MIGRATE` to Core | `MIGRATE` | A facade that **reverses the dependency direction**: `engine/_compat.py` + `engine/adapters/_bootstrap.py` do `sys.path.insert(0, "moodify-core-package/src")`. Core never imports `engine`. This is the "second Core" `AGENTS.md` forbids. | Core, after lifting `acoustic_analysis/issue_detection.py`, `scoring_engine/recommendations.py`, `music_understanding/commercial_insight.py`, `report_schema/schema.py` + `moodify_intelligence_report.schema.json` | Only `demo/` imports `engine`. Both removed together. | _pending_ | _pending_ |
| `demo/` (12) | `REMOVE` | Independent re-implementation with **no analysis logic of its own** (its README says so). Critically: `demo/pyproject.toml:17` declares `moodify = "demo.cli:main"`, **colliding with Core's `moodify = "moodify.release_cli:main"`** — installing both makes the `moodify` command resolve differently by install order. | Core CLI | Its only dependency was `engine/`. Zero CI/ops references. | _pending_ | _pending_ |

### Dangling references repaired in Phase 1

| Path | Fix | Commit |
|---|---|---|
| `moodify-core-package/src/moodify/physics/reliable_runner.py:90` | Remove hardcoded `/home/ubuntu/phys-lab/test_audio/piano.wav` | _pending_ |
| `.gitignore` — `!moodify_runtime/operator_console.html` | File does not exist | _pending_ |
| `.gitignore` — `!apps/music-web/public/moodify-logo.png` | `apps/music-web` was renamed to `apps/web` | _pending_ |
| `.gitignore` — `工程经验层/*` block (L77-84) | Repointed at the new governance home | _pending_ |

---

## Phase 2 — Evidence preservation

`审查包/` is **not residue**. `docs/canon/AUTHORITY_ORDER.md:10` places the W01-P00
Evidence Index at **authority tier 4**. The evidence below is migrated *before* the
source directory leaves the mainline.

| Path | Class | Reason | Replacement | Dependency check | Action | Commit |
|---|---|---|---|---|---|---|
| `审查包/W01-P00_REPORTS_2026-08-17/raw_scan/LA_103_144_246_242_scan.txt` | `MIGRATE` | E13 — full read-only node scan of the LA production VPS. **Only copy in the repo.** No second copy exists anywhere. | `docs/evidence/cloud/` | Cited by `08_EVIDENCE_INDEX.md` E13 | _pending_ | _pending_ |
| `审查包/W01-P00_REPORTS_2026-08-17/raw_scan/HZ_120_55_191_146_scan.txt` | `MIGRATE` | E14 — same for the Hangzhou node. **Only copy.** | `docs/evidence/cloud/` | Cited by E14 | _pending_ | _pending_ |
| `审查包/W01-P00_REPORTS_2026-08-17/08_EVIDENCE_INDEX.md` | `MIGRATE` | **The "W01-P00 Evidence Index" named by `AGENTS.md:101` and `docs/canon/AUTHORITY_ORDER.md:10` as authority tier 4.** Registers E01–E27. | `docs/evidence/` | Directly named by 2 canonical docs | _pending_ | _pending_ |
| `审查包/W01-P00_REPORTS_2026-08-17/05_MOODIFY_TRUTH_TABLE.csv` + `.md` | `MIGRATE` | E27 — 51-row schema-validated fact table; basis of the `docs/REPOSITORY_STATUS.md` capability table | `docs/evidence/` | Referenced as the truth table | _pending_ | _pending_ |
| `审查包/W01-P00_REPORTS_2026-08-17/03_CLOUD_INFRASTRUCTURE_REALITY.md` | `MIGRATE` | Backs `docs/canon/CURRENT_ARCHITECTURE.md §1` (LA/HZ roles, PolarDB ×3, OSS NOT_PROVISIONED) | `docs/evidence/cloud/` | Cited by canon | _pending_ | _pending_ |
| `审查包/审查包 8.18完成/W01-P01_REPORTS_2026-08-17/01_CANONICAL_DECISION_REGISTER.md` | `MIGRATE` | CD-001..CD-016 — the decision record behind Canon v1.0 identity convergence. No tracked copy outside `审查包/`. | `docs/evidence/decisions/` | Cited by `docs/REPOSITORY_STATUS.md:12` and `docs/canon/CANON_CHANGELOG.md:186` | _pending_ | _pending_ |
| `审查包/W01-P00_REPORTS_2026-08-17/07_CURRENT_SYSTEM_MAP.mmd` | `MIGRATE` | System map referenced by the reality snapshot | `docs/evidence/` | Cited by W01-P00 | _pending_ | _pending_ |
| `审查包/W01-P00_Moodify_Project_Reality_Snapshot_2026-08-17/.../scripts/readonly_node_scan.sh` | `MIGRATE` | The generator for E13/E14 — without it the scans are not reproducible | `docs/evidence/cloud/` | Sole copy | _pending_ | _pending_ |
| `审查包/` (remainder, ~374 files) | `ARCHIVE` | Task packages and acceptance reports. `artifacts/` is already gone, so several `docs/REPOSITORY_STATUS.md` pointers already dangle; retaining the audit corpus in the mainline no longer serves the 60-second comprehension goal. Git history preserves it. | `docs/evidence/` (selected) + git history | 11 canonical/governance citations repointed **before** removal | _pending_ | _pending_ |
| `docs/ARCHIVE_INDEX.md` | `CANONICAL` | Missing prerequisite named by `AI_CONTEXT_OPTIMIZATION.md` and `docs/reduction/EXECUTION_PLAN_V1.md` Phase 2.2.1 | — | Required before archival per the repo's own plan | _pending_ | _pending_ |
| `工程经验层/` (5) | `MIGRATE` | **Not residue.** Contains canonical governance constraints ME-001 (起源先于功能), ME-002 (证据门控发展), ME-003 (整体一致性) — the same evidence-gated discipline this restructure builds on. Deliberately whitelisted in `.gitignore`. | `docs/governance/constraints/` | Zero code dependency; all constraints `PROPOSED`, no gate wired | _pending_ | _pending_ |

---

## Phase 3 — Web3 line leaves the mainline (human decision, 2026-10-03)

The `MOOD Protocol` line is **live infrastructure, not residue**: `protocol/mainnet.json`
declares an EVM/BSC mainnet token `MOOD` at `0x1BB3115D43E397f7bb586F090831B02cA639e73E`
(33,000,000 supply, trading on PancakeSwap). Per the 2026-10-03 decision, it **leaves the
mainline but is never deleted from disk**.

| Path | Class | Reason | Replacement | Dependency check | Action | Commit |
|---|---|---|---|---|---|---|
| `protocol/` (113) | `ARCHIVE` | The MOOD Protocol in its entirety — `mainnet.json`, contribution/reputation/node-registry/protocol-api (all self-titled "MOOD Protocol …"). **No Moodify Sound Protocol inside it**, contrary to the task spec's §3.5 assumption. | Renamed on disk to `mood-web3-protocol/`; Sound Protocol gets a fresh `protocol/` | No workflow references it. Owned by the `codex/mood-*` branch family (~20 branches). | `git rm -r --cached` + disk rename | _pending_ |
| `apps/web/` (201) | `ARCHIVE` | The MOOD Web3 dApp — airdrop, genesis, treasury, token page, WalletConnect, `MoodGenesisDistributor.sol`, Foundry, Drizzle migrations. Binds `apps/web/lib/mood-token.ts` to the deployed BEP-20 contract. | Kept on disk | `deploy.yml` builds it → **the `deploy.yml` decision is escalated, not made here**. `ops/web_origin` runbook deploys it. | `git rm -r --cached` | _pending_ |
| `e2e/staging/` (6) | `ARCHIVE` | Entirely Web3 staging specs (`03-treasury-read`, `05-token-regression`, …) | Kept on disk | No workflow references it | `git rm -r --cached` | _pending_ |
| `docs/protocol/{MAINNET,ADDRESSES,MAINNET_EVIDENCE,MOOD_TOKEN,GENESIS_REGISTRATION}.md` (5) | `ARCHIVE` | Web3 protocol docs | `docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md` + `_0_2.md` **stay** — the directory is mixed | `GENESIS_REGISTRATION.md:7` already pointed at an untracked path | move on disk to `mood-web3-protocol/docs/` + untrack | _pending_ |
| `MOOD_PROTOCOL_FOUNDATION_001_COMPLETE.md` (root) | `ARCHIVE` | Completion report for `protocol/mainnet.json` | Kept on disk | Root-level stale work product | move + untrack | _pending_ |
| `scripts/validate-mainnet-config.mjs`, `scripts/generate-mainnet-lock.mjs` (2) | `ARCHIVE` | MOOD protocol tooling | Kept on disk | Owned by the Web3 line | move + untrack | _pending_ |
| `moodify-core-package/src/moodify/contribution/` (14) | `UNRESOLVED` | A MOOD Protocol contribution layer **inside the real Core**, with 3 schema copies. Its contract authority was fixed by a 2026-09-29 human ruling (`docs/audits/2026-09-29_GATE3…:40`). | — | Has live tests (`tests/contribution_test.py`) | **Not touched.** Escalated. | — |

> **Do not delete these from disk.** The untracked portion of `web 3.0/` holds
> `MOOD_PROTOCOL_CONTRIBUTION_CORE_002/003` schemas + `CONTRIBUTION_SPEC.md`, which the
> 2026-09-29 ruling named as the **contract authority** for shipped Core code. Un-tracking
> (not deletion) is what keeps that evidence reachable.

---

## Phase 4 — Pulse retirement

| Path | Class | Reason | Replacement | Dependency check | Action | Commit |
|---|---|---|---|---|---|---|
| `moodify-pulse/` (18) | `REMOVE` | Fourth competing product identity ("Moodify Pulse — AI Emotional Music Container"), banned by `PUBLIC_BRAND_CONSTITUTION.md §2.2`. Mock-driven UI, no audio engine. | `moodify-desktop/` | `release.yml build-windows` referenced it, **but that job cannot run**: `moodify-pulse/package-lock.json` does not exist (so `npm ci` and the `setup-node` npm cache both fail), `build/` is empty, and `build.extraResources` points at a non-existent `backend/moodify-server.exe`. Job removed in the same commit. | _pending_ | _pending_ |

### Pre-existing CI breakage (recorded, not introduced by this restructure)

| Symptom | Evidence |
|---|---|
| `release.yml build-android` cannot run | `apps/music-android/gradlew` and `apps/android/gradlew` are git mode **100644**, and the repo has **no `.gitattributes`** → `./gradlew assembleRelease` fails with Permission denied on `ubuntu-latest` |
| `release.yml build-windows` cannot run | missing `moodify-pulse/package-lock.json` (see above) |

`moodify-desktop/package.json` has only `"start": "electron ."` — no `electron-builder`,
no `dist` script, empty `build/`. Repointing the Windows job at it would create a *new*
failing job, so the job is removed and the packaging work is escalated instead.

---

## Escalated to HUMAN_DECISION_REQUIRED

| # | Question | Why it is not an engineering decision |
|---|---|---|
| 1 | `apps/android` (70) vs `apps/music-android` (40) — which is current? | Evidence contradicts. All 4 `RELEASE_MANIFEST.json` name `com.moodify.app` (= `apps/android`, `versionCode 20` matches exactly); the 3.1.0 notes describe features only `apps/music-android` implements. Both must not survive, but deleting the wrong one destroys the source of shipped APKs. `AGENTS.md` L71 reserves product boundaries to humans. |
| 2 | `deploy.yml` after `apps/web` leaves the mainline | `apps/web` is the source of the live site `play.rongjingmusic.com` (runbook-verified). Once untracked, CI can no longer build or deploy it. Choosing between retiring the site, keeping a CI exception, or moving it to its own repo is a product decision. |
| 3 | Core-embedded `moodify.contribution` (14 files) | Removing it reverses a 2026-09-29 human ruling that fixed 17 test failures and named an untracked package the contract authority. |
| 4 | `moodify_runtime/` (13) — ~1,550 lines of unique commerce logic + 938-line test | No Core equivalent; it is the server side of `apps/music-android`'s P09/P10 clients. `moodify-core-package/tests/contracts/test_architecture.py` currently **prohibits** Core from importing it, so absorbing it requires changing a guard. Migrate or abandon is a scope decision. |
| 5 | `.git` is 4.0 GB (99 M `runs.tar.gz`, 85 M bundles, 43 M dex, APKs, WAVs) | Task spec §3.1 forbids history rewrite, so this restructure leaves it. A 4 GB clone materially undercuts the public-collaboration goal. |
| 6 | Windows packaging for `moodify-desktop` | Needs `electron-builder` + icons + signing — new capability, and §3.4 protects the Studio from casual change. |
