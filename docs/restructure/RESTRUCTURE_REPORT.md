# MOODIFY_NETWORK_RESTRUCTURE_001 — Report

**Date:** 2026-10-03 · **Branch:** `deepseek/moodify-network-restructure-001`
**Baseline:** `c11bc7f5` · **Safety tag:** `pre-network-restructure-2026-10-03`
**Tracked files:** 2760 → **1538** (−44%)

> The task spec (§40) says this is not about producing cleaner software, but about turning a
> private repository into a public system that keeps producing the next version. This report
> is written to that standard: it records what was removed, what was deliberately kept, what
> was **not** resolved, and — where the spec's own premises turned out to be wrong — the
> evidence that contradicts them.

---

## Verification

| Gate | Result |
|---|---|
| `ruff check src tests ../tests` | **clean** (before and after) |
| `pytest -q tests ../tests` | **1197 passed, 5 skipped, 0 failed** — before *and* after |
| `pytest -m v01` | **265 passed, 5 skipped** |
| `python scripts/check_repo_structure.py` | **OK** (1538 tracked files, 5 checks) |
| Structural guard negative tests | planting `moodify-qa/probe.py` and a second `moodify` entry point each fail the guard as intended |

**Zero regressions.** The full suite was run to completion on the pre-restructure tree and
again after Phase 1; the counts are identical.

Recovery of any removed path:

```bash
git checkout pre-network-restructure-2026-10-03 -- <path>
```

---

## 1. What historical residue was removed?

24 paths left the mainline. Full per-path justification, including the dependency check run
for each, is in [`CLEANUP_MANIFEST.md`](CLEANUP_MANIFEST.md).

**Removed outright (git history retains):**

| Path | Files | What it was |
|---|---:|---|
| `windows版本开发/` | 330 | MFD-001…010 Windows work packages. Verified **zero source files** (255 md / 36 json / 24 txt / 15 csv). |
| `审查包/` | 373 | W01/W02 audit corpus, after migrating 9 authority artifacts to `docs/evidence/`. |
| `products/` | 32 | Four product scaffolds. All 23 `__init__.py` were **0 bytes**. |
| `moodify-qa/` | 26 | Second public product; `core/metrics.py` was a verbatim copy of `moodify.auditory.loudness`. Shipped a committed 45 KB SQLite file. |
| `engine/` | 19 | Facade that **reversed** the dependency direction via `sys.path.insert`. |
| `moodify-pulse/` | 18 | Fourth competing product identity. |
| `demo/` | 12 | Duplicate pipeline whose `moodify` console command collided with Core's. |
| `plugins/` | 9 | Unbuilt surface; its CI file sat outside `.github/workflows/` and never ran. |
| `sdk/` | 9 | Placeholder client returning `id="placeholder-id"` and `NotImplementedError`. |
| `moodify-qa-desktop/` | 8 | Third Electron shell, downstream of the dead QA service. |
| `shared/` | 7 | Migration map; **every `.py` was 0 bytes**. |
| `apps/ear-workbench/android/` | 24 | Kotlin with no Gradle files — not buildable. |
| `phys-lab/` | 1 | Bash launcher; the science lives in Core's `moodify.physics`. |
| `dashboard.html`, `cloud_status.py` | 2 | 3.0-era cloud dashboard and its status API. |
| `scan_err.txt`, `.codex_tmp/` | 2 | Scratch. |

**Left the mainline but kept on disk (never deleted):**

| Path | Files | Why kept on disk |
|---|---:|---|
| `web 3.0/` | 37 un-tracked (25,491 on disk) | Its **untracked** portion is a live contract authority — see §2. |
| `protocol/` → `mood-web3-protocol/` | 113 | Live token infrastructure, not residue — see §14. |
| `apps/web/` | 201 | The MOOD dApp. |
| `e2e/staging/` | 6 | Its staging specs. |
| 5 Web3 docs from `docs/protocol/` | 5 | Moved to `mood-web3-protocol/docs/`. |

**Root directory:** 22 tracked files → **13**. The five superseded work products moved to
`docs/archive/2026-10/`; two cloud-state files turned out to be *registered evidence* (E18)
and went to `docs/evidence/cloud/` instead.

## 2. What was **not** deleted, and why

This is the part most worth reading, because several of these were nearly deleted.

**`web 3.0/`'s untracked half is load-bearing.** It holds
`MOOD_PROTOCOL_CONTRIBUTION_CORE_002/003` schemas (draft 2020-12, with the `allOf` guards
forbidding `tokenAmount` / `payout` / `claimAmount` / `vesting`), plus `CONTRIBUTION_SPEC.md`
and `REPUTATION_MODEL.md`. A 2026-09-29 human ruling
(`docs/audits/2026-09-29_GATE3_CONTRIBUTION_PREEXISTING_FAILURES.md:40`) named that package
the **contract authority** for shipped code in `moodify-core-package/src/moodify/contribution/`.
**There is no tracked copy of `CONTRIBUTION_SPEC.md` or `REPUTATION_MODEL.md` anywhere.**
Deleting the directory would have silently re-opened the gap that ruling closed. This is why
un-tracking ≠ deletion, and why the distinction is recorded in `.gitignore` with a
`DO NOT DELETE` warning.

**`审查包/` was canon authority, not clutter.** `docs/canon/AUTHORITY_ORDER.md:10` places the
W01-P00 Evidence Index at **authority tier 4**; `AGENTS.md:101` says the same. Its
`raw_scan/LA_*.txt` and `HZ_*.txt` are the **only** HIGH-confidence captures of the two
production nodes — no second copy exists. Migrating before removing was mandatory (task spec
§3.6), not cautious.

**`moodify_runtime/`** — ~1,550 lines of unique commerce/pricing/settlement/refund logic plus
a 938-line test. No Core equivalent; it is the server side of `apps/music-android`'s P09/P10
clients. Kept.

**`treatment_records/`** — the only surviving provenance for the MHP-026 preset-calibration
experiment. Its source audio is gitignored, so the records *are* the evidence. Kept.

**`moodify-music-package/`** — referenced by `ops/schema_dry_run.py` and a production runbook;
unique schema authority with 19 tests. Kept.

**Both Android clients** — the evidence contradicts itself; see §14 item 1. Neither was touched.

## 3. Which capabilities reached a single owner?

| Capability | Was | Now |
|---|---|---|
| Defect classification | `engine/acoustic_analysis/issue_detection.py` (7 hardcoded thresholds) | `moodify-core-package/src/moodify/diagnosis/defect_classifier.py` (18 parameters, 3 severities, 4 priorities) |
| Recommendation / craft | `engine/scoring_engine/recommendations.py` (7-entry map) | `moodify-core-package/src/moodify/knowledge/craft_chains.py` (8 emotions × 15 DSP params, with contraindications) |
| Quality measurement | `moodify-qa/core/*` (verbatim copy of Core) | `moodify-core-package/src/moodify/auditory/` |
| `analyze` command | Core **and** `demo` | `moodify.release_cli:main` only |
| Core contracts | `schemas/canonical/` + `engine/report_schema/` + `moodify.contracts` | `moodify.contracts` → generated into `schemas/canonical/` |
| Desktop shell | `moodify-desktop` + `moodify-pulse` + `moodify-qa-desktop` | `moodify-desktop` |

**Deviation from the approved plan, recorded.** The plan called for lifting four `engine/`
files into Core. Comparing each against what Core already ships reversed that decision —
every one was the *weaker* duplicate, so migrating would have created a second authority
inside Core, which `AGENTS.md` L112–114 forbids. `moodify.intelligence-report.v1` has **zero**
references in Core and its own docstring describes it as the contract shared by "QA, Master,
Rating, Supply" — the four-product identity this project prohibits. Nothing was migrated;
`engine/` and `demo/` were removed. Losing `demo`'s `moodify analyze` cost nothing: Core's
canonical `moodify analyze` was verified working.

## 4. Are duplicate CLIs still present?

**No — the `moodify` collision is resolved.**

Before: two packages declared `moodify` —
`moodify-core-package → moodify.release_cli:main` and `demo → demo.cli:main`. Installing both
made the command resolve by install order. `moodify-core-package/setup.py` even carried a
comment documenting that this had already happened once.

Now, exactly one tracked declaration:

```text
moodify-core-package/pyproject.toml
  moodify                  = "moodify.release_cli:main"     <- canonical
  moodify-node             = "moodify.node.cli:main"        <- subsystem CLI, distinct name
  moodify-reconstruction   = "moodify.reconstruction_job.cli:main"
```

`moodify-music-package/pyproject.toml` declares no scripts. One residual hazard remains
**outside the repository**: the untracked stale fork `_github_moodify_ai/moodify-core-package/`
declares `moodify.cli:main` under Apache-2.0. It is not tracked and cannot be fixed from git;
the guard deliberately ignores it. Worth deleting from disk by the owner.

## 5. Are duplicate schemas still present?

**Partially resolved, and one duplication is knowingly unresolved.**

Before: `contribution.schema.json`, `evidence.schema.json`, and
`reputation-evidence.schema.json` each existed in **4 copies**, two of them live and differing
in `$schema` dialect (draft-07 vs 2020-12) while sharing one `$id`.

Now: 8 `.schema.json` files with two owners —

| Owner | Count | Notes |
|---|---:|---|
| `schemas/canonical/` | 5 | Generated from `moodify.contracts` by `scripts/generate_canonical_schemas.py`. Do not hand-edit. |
| `moodify-core-package/src/moodify/contribution/schema/` | 3 | **The remaining duplication.** |

The contribution schemas are a Python mirror of the MOOD Protocol layer. Removing or
relocating them is escalated, not decided here — see §14 item 3.

[`protocol/schemas/README.md`](../../protocol/schemas/README.md) now states the schema owner
map and the concrete harm it prevents.

## 6. Are duplicate apps still present?

**Yes — one unresolved duplication, plus one deliberate retention.**

- **Two Android clients remain**: `apps/android` (70 files) and `apps/music-android` (40).
  This is the single most consequential unresolved item; see §14 item 1.
- `apps/ear-workbench` (12) is kept: it is internal research tooling, its HTML is
  `.gitignore`-protected as canonical app source, and the temporal-texture baseline covers it.
  Its non-buildable `android/` archive was removed.

The web and desktop duplication is resolved: `apps/web` left the mainline (Web3 line), and of
three Electron shells only `moodify-desktop` remains — now also the **only** npm `package.json`
in the repository.

## 7–9. Canonical paths

| Layer | Canonical path | Evidence |
|---|---|---|
| **Core** | `moodify-core-package/` (679 files, package `moodify` v1.0.0-rc.1) | Declared in `AGENTS.md` "One Core, Multiple Interfaces"; enforced by the structure guard; **not renamed** — task spec §3.3 forbids it and a rename would break 679 files of imports plus all five workflows |
| **Protocol** | `protocol/` for structure (specs/schemas/conformance/mips); specification text in `docs/protocol/MOODIFY_SOUND_PROTOCOL_0_{1,2}.md` | The spec text stays where it has always lived so existing links resolve |
| **Studio** | `moodify-desktop/` (21 files, Electron shell, no DSP) | Task spec §3.4; orchestrates Core via `python -m moodify.release_cli` |

## 10. How the Network receives external contributions

`GOVERNANCE.md §5`, and `CONTRIBUTING.md` for the practical path.

```text
Fork → Experiment → Evidence → MIP / PR → Review → Canonical Moodify
```

Eleven contribution types are recognised, only the first of which is code:
`CODE · PROTOCOL · CASE · REVIEW · BENCHMARK · DATASET · DOCUMENTATION · RESEARCH · BUG ·
PLUGIN · INTEGRATION`.

**Contribution is explicitly not measured in commits.** The **Review Network** — mix and
mastering engineers, producers, musicians, listeners, researchers — contributes perceptual
judgments, artifact reports, device-playback differences, and edge cases. Twenty documented
A/B judgments may outweigh a large patch, and a commit-count metric would systematically
undervalue exactly the people this project most needs.

## 11. How a MIP reaches ACCEPTED

`protocol/mips/MIP-0000-template.md` and `GOVERNANCE.md §6`:

```text
DRAFT → DISCUSSION → EXPERIMENTAL → EVIDENCE → ACCEPTED → IMPLEMENTED → RELEASED
```

**A proposal cannot reach `ACCEPTED` without a populated Evidence section.** Negative and
inconclusive results are valid evidence and must be recorded rather than suppressed — an
explicit anti-pattern rule (`ME-002`).

Required for: protocol, schema, Core behavior contract, governance, evidence format, public
compatibility. Ordinary bug fixes do not need a MIP.

**`MIP-0001` was deliberately left at `DRAFT`** rather than self-accepting, even though it
describes a structure created under explicit human instruction. A governance process that
exempted its own founding document from its own stages would not be worth adopting.
Ratification is the Steward's.

## 12. How Evidence accumulates

`docs/evidence/` (+ `docs/governance/NETWORK.md` §Evidence).

Layout: `cloud/` · `runtime/` · `decisions/`. Every accepted sound-affecting change should be
traceable to source hash, Core and protocol version, parameters, processing graph, before/after
metrics, A/B result, human review, agent version, timestamp, and reproducibility info.

The **confidence discipline** is the point. The W01-P00 Evidence Index registers E01–E27 with
source, timestamp, and confidence — and explicitly records what could **not** be verified:
E17 (PolarDB access) is `BLOCKED`, E18 is `MEDIUM` and was never reproducible. Where evidence
is insufficient the record says so rather than manufacturing certainty.

## 13. AI agent permissions and boundaries

Restated from `AGENTS.md`, now also codified in `GOVERNANCE.md §8`:

**Agents may:** implement, refactor, test, implement CLI and schemas, work on performance,
fix bugs, sync docs, search parameters, maintain CI, execute migrations — including running
benchmarks, generating tests, scanning regressions, assembling evidence, and implementing MIPs.

**Agents may not decide:** what sounds better, the commercial direction, core product
identity, or whether human listening judgment is replaced. Where a conflict is a
product-philosophy question, the agent must write `HUMAN_DECISION_REQUIRED`.

> **Agents have execution rights. They do not have product sovereignty.**

Enforced practically by the four gates and the structure guard, which an agent cannot bypass
by editing a document.

## 14. HUMAN_DECISION_REQUIRED

Six items. None was decided unilaterally.

**1. Which Android client is current — `apps/android` or `apps/music-android`?**
Evidence contradicts. All four `RELEASE_MANIFEST.json` files name `com.moodify.app`
(= `apps/android`, whose `versionCode = 20` matches the 2.0.0 manifest exactly). But the 3.1.0
release notes describe external-file handoff implemented **only** in `apps/music-android`, and
`release.yml` builds `apps/music-android`. Nothing in the tree records an `applicationId`
override. Both must not survive; deleting the wrong one destroys the source of shipped APKs.
`apps/android` holds migration-worthy code (6-locale i18n with a parity test, a pure gesture
FSM, brand assets).

**2. The web surface's deployment path.** `apps/web` was the source of the live site
`play.rongjingmusic.com`. Now that it is untracked, `.github/workflows/deploy.yml` — which
builds it — cannot succeed on merge. **`deploy.yml` was deliberately left unmodified**, since
retiring the site, relocating the workflow into the Web3 line, or keeping a CI exception is a
product decision. **Note: this means the branch will show a failing `deploy.yml` check until
this is resolved.**

**3. The MOOD Protocol layer inside Core** (`moodify-core-package/src/moodify/contribution/`,
14 files + 3 schemas). Removal reverses a 2026-09-29 human ruling and breaks
`tests/contribution_test.py`. Not touched.

**4. `moodify_runtime/`** — migrate ~1,550 lines into Core, or abandon. Absorbing it requires
changing `moodify-core-package/tests/contracts/test_architecture.py`, which currently
*prohibits* Core from importing it.

**5. Git history is 4.0 GB** (99 MB `runs.tar.gz`, 85 MB bundles, 43 MB dex, APKs, WAVs;
316 commits). Task spec §3.1 forbids history rewrite, so this restructure left it untouched —
but a 4 GB clone materially undercuts the public-collaboration goal this work is in service of.

**6. Windows packaging.** `moodify-pulse` was removed and its broken CI job deleted, but the
approved plan was to *repoint* it at `moodify-desktop`. That was not done: `moodify-desktop`
has no `electron-builder`, no `dist` script, and no icons, so repointing would have swapped one
guaranteed-failing job for another while touching a tree task spec §3.4 protects. Adding that
tooling is a real feature task.

### Also worth an owner's attention

- **`moodify-pulse/` retains ~1.2 GB** of ignored build artifacts on disk (21,768 files).
  Regenerable, not source. Not deleted — removing files this task did not create is the
  owner's call.
- **`apps/*/gradlew` is git mode `100644`** and there is no `.gitattributes`, so the Android
  release job fails with Permission denied on `ubuntu-latest`. Pre-existing, not introduced here.
- **The untracked `_github_moodify_ai/`** fork (Apache-2.0) still declares a conflicting
  `moodify` console script and is invisible to the guard.
- **`.moodify/tt_baseline/report.json` was already stale** — it carries 161 entries for the
  long-gone `apps/music-web`. The temporal-texture guard compares against it.

---

## Premises in the task spec that the evidence contradicted

Recorded because acting on them as written would have caused harm.

| Spec claim | Reality |
|---|---|
| §6.1 Web3 material is historical residue; "REMOVE FROM MAIN" | It is **live infrastructure** — a deployed BEP-20 token with DEX trading. Moved out, never deleted. |
| §3.5 "`protocol/` is the current direction; distinguish Sound Protocol from old MOOD/Web3" | `protocol/` was the MOOD Protocol **in its entirety**. There was no Sound Protocol inside it; that lives in `docs/protocol/`. The Sound Protocol did not survive *within* `protocol/` — the directory was freed for it. |
| §5 `工程经验层/` should exit the mainline | It is a canonical governance layer (ME-001/002/003) deliberately `.gitignore`-whitelisted, and philosophically the same evidence-gated discipline this restructure builds on. **Migrated into `docs/governance/`, not deleted.** |
| §6.5 `moodify-pulse/` is a dead shell | Its CI job was already broken (missing lockfile), so the conclusion held — but for a different reason, and the job had to be repaired, not just the directory deleted. |
| §5 lists `moodify-qa/` etc. as high-confidence removals | Confirmed, but `apps/`, `审查包/`, and `web 3.0/` — which the spec also touches — all required evidence migration or disk retention first. |

## Deliverables

| File | Status |
|---|---|
| `docs/restructure/BEFORE_TREE.txt` | 2841 lines |
| `docs/restructure/AFTER_TREE.txt` | generated |
| `docs/restructure/CLEANUP_MANIFEST.md` | per-path classification + dependency check |
| `docs/restructure/RESTRUCTURE_REPORT.md` | this file |
| `GOVERNANCE.md` · `MAINTAINERS.md` | created |
| `docs/governance/NETWORK.md` | created |
| `docs/governance/constraints/` | ME-001…ME-003 migrated |
| `protocol/{specs,schemas,conformance,mips}/` | created |
| `protocol/mips/MIP-0000-template.md` · `MIP-0001-moodify-network-governance.md` | created |
| `docs/evidence/` + `docs/ARCHIVE_INDEX.md` | created |
| `scripts/check_repo_structure.py` + CI | created |
| `README.md` · `AGENTS.md` · `CONTRIBUTING.md` · `docs/REPOSITORY_STATUS.md` · `docs/canon/CANON_CHANGELOG.md` · `CITATION.cff` | updated |
