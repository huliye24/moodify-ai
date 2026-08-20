# GitHub Convergence Commit Plan — 2026-08-20

**Status:** execution plan; not an independent authority

**Authority:** `AGENTS.md` → `docs/canon/*` → verified runtime evidence

**CANON_CHANGE:** NO — this plan publishes and implements the already approved Canon v1.1 / Public Form v0.1

## Goal

Move the current product truth and verified product surfaces toward GitHub `main` without staging the dirty worktree wholesale, mixing internal production work into public-brand changes, or committing local runtime data.

Each batch below is independently reviewable. Stage, commit, push, and PR creation remain separate authorized actions.

## Batch 1 — Repository authority and public truth

Include:

- `AGENTS.md`
- `README.md`
- `.gitignore`
- `docs/canon/`
- `docs/brand/public/`
- `docs/REPOSITORY_STATUS.md`
- `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md`
- the explicit supersession headers in `docs/PHASE1_CONSTITUTION.md`, `docs/design/`, and `docs/product-framework/`

Required checks:

- `python scripts/canon_guard.py`
- README local-link check
- brand-language conflict scan
- `git diff --check`

Do not include product binaries, runtime cases, browser state, or unrelated implementation changes.

## Batch 2 — Public Form sites

Include:

- `ops/web_origin/site/rongjingmusic/`
- `ops/web_origin/site/rongjingwenchuan/`
- `ops/web_origin/site/check_site.mjs`
- `ops/web_origin/site/check_company_site.mjs`
- scoped changes to `ops/web_origin/nginx/`, `verify_origins.sh`, `README.md`, and `PRODUCTION_TOPOLOGY.md`
- `docs/public-form/package-02` through the accepted Public Form packages required to explain the resulting surface

Required checks:

- Product Home static tests
- Company Home static tests
- local route and asset validation
- shell syntax
- `nginx -t` only in an environment with the target Nginx configuration

Review deleted legacy assets explicitly. Their removal must be explained as Public Form replacement, not general cleanup.

## Batch 3 — Web Player

Include:

- `apps/music-web/` source, tests, lockfile, and bounded public fixtures
- no real audio body under `public/audio/`

Required checks:

- `npm test`
- artifact validation
- no-deploy-audio validation
- public navigation and capability-gating tests

Creator Studio remains a secondary capability-gated surface. Drafts, console, and inbox must not return to first-layer Player navigation.

## Batch 4 — Android Player

Include:

- `apps/music-android/README.md`
- Android source and resources
- unit tests
- Gradle wrapper, wrapper properties, and build configuration

Required checks:

- `gradlew test`
- debug assembly
- manifest review for external audio intents, permissions, and services
- secret/signing-material scan

Do not include APKs, signing keys, private audio, `local.properties`, `.gradle/`, or `app/build/`.

Device-path or bit-perfect claims require device evidence; JVM tests and a successful APK build are insufficient.

## Batch 5 — Music service

Include:

- `moodify-music-package/` source, tests, migrations, and README

Required checks:

- full pytest suite
- data-authority and security-matrix tests
- migration review and dry run where a safe test database is configured

Do not claim current PolarDB reachability from package tests.

## Batch 6 — Internal production systems

Handle separately after the public product baseline is reviewable:

- Ear and reconstruction changes in `moodify-core-package/`
- control/data/compute-plane work
- `apps/ear-workbench/`
- data-node and internal service operations
- scoped, curated evidence packages

This batch requires its own state-machine, evidence-authority, failure, recovery, and runtime verification review. It must not silently create a second Job authority or expose internal complexity as public product value.

## Explicit exclusions

Never stage as ordinary source:

- `.codex_tmp/`, `.workbuddy/`, `temp/`, browser profiles and caches;
- `node_modules/`, `.gradle/`, build output, pytest caches and bytecode;
- APKs, tarballs, deployment snapshots and database dumps;
- raw production cases, idempotency stores, private audio and bulk pilot outputs;
- API keys, private keys, tokens, invite codes, signing material or server-local secrets;
- generated numerical arrays unless a bounded canonical fixture explicitly requires them.

## Authorization sequence

For every batch:

1. show the exact candidate path list and diff summary;
2. run the required checks;
3. obtain authorization to stage those exact paths;
4. inspect the staged diff;
5. obtain authorization to commit;
6. obtain authorization to push;
7. create or update at most one convergence PR only when explicitly authorized.
