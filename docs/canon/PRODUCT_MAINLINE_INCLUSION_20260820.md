# Product Mainline Inclusion — 2026-08-20

**Status:** execution inventory; not an independent authority

**Authority:** `AGENTS.md` → `docs/canon/*` → verified runtime evidence

**CANON_CHANGE:** NO — this inventory implements Canon v1.1

## Purpose

Define the bounded product-facing scope that should enter the future GitHub convergence change without sweeping the current dirty worktree wholesale into `main`.

## Include as product mainline

| Scope | Paths | Required verification |
|---|---|---|
| Repository public truth | `README.md`, `AGENTS.md`, `docs/canon/`, `docs/brand/public/`, `docs/REPOSITORY_STATUS.md` | Canon guard, link check, authority review |
| Android player | `apps/music-android/` source, Gradle wrapper/config, unit tests | unit tests, debug build, manifest and playback-failure review |
| Web Player | `apps/music-web/` source, lockfile, tests, bounded public fixtures | build, contract tests, rendered-page tests, no bundled audio |
| Music service | `moodify-music-package/` source, migrations, tests | service test suite, migration dry run where configured, security matrix |
| Product and Company sites | `ops/web_origin/site/rongjingmusic/`, `ops/web_origin/site/rongjingwenchuan/`, scoped nginx/deploy checks | static tests, route/assets check, nginx syntax in deployment environment |
| Public Form evidence | `docs/public-form/` and small text/JSON evidence required to explain the accepted change | package acceptance and brand lint |

## Include separately as internal production scope

These are important, but should not be mixed into a public-surface change without their own verification boundary:

- `moodify-core-package/` Ear, reconstruction, data/control/compute-plane changes;
- `apps/ear-workbench/` internal operator surface;
- `ops/data_node/`, Ear API/worker services, and cloud-production operations;
- canonical schemas and evidence contracts required by those systems.

## Do not include as ordinary source

- `.codex_tmp/`, `.workbuddy/`, `temp/`, browser capture directories, local runtime state;
- APK files, tarballs, deployment bundles, generated build directories;
- private or copyrighted audio bodies;
- secrets, invite codes, signing keys, database exports, server-local configuration;
- experimental outputs without a bounded evidence purpose and provenance record.

## Merge discipline

1. Resolve the exact file list from the dirty worktree.
2. Preserve unrelated user changes; never stage the whole repository.
3. Run the verification listed for each scope.
4. Record unverified deployment claims as `UNVERIFIED`, `BLOCKED`, or `UNRESOLVED`.
5. Stage only reviewed paths with explicit authorization.
6. Commit, push, and PR creation each require separate authorization.

## Current unresolved items

- `play.rongjingmusic.com` deployment and `.xyz` redirect/retention policy;
- current PolarDB reachability and authoritative production data path;
- verified cloud production traffic for the complete Ear/reconstruction chain;
- Android device-path evidence for the current uncommitted playback changes;
- final separation of source, release binaries, and large evidence artifacts in the current worktree.
