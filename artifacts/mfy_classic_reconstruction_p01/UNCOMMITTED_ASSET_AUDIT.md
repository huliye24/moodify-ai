# MFY-CR-P01 — Uncommitted Asset Audit

Audit commands: `git status` / `git diff` / `git diff --cached` / `git ls-files --others --exclude-standard`.
Classification A-E as defined in 01_TASK.md section 4.

## A. REQUIRED_FOR_CURRENT_BASELINE (converged in Commit 1)

| Asset | Why required | Tests / boundary |
|---|---|---|
| apps/music-android .../player/PlaybackController.kt | source of released 2.0.1 APK; untracked since foundation commit | no app unit tests exist (recorded) |
| apps/music-android .../ui/MoodifyMusicApp.kt | same | same |
| apps/music-android .../res/ (7 launcher icon files) | manifest references @mipmap/ic_launcher; clean-clone build needs them | build verified: assembleDebug PASS after un-ignore |
| apps/music-android MainActivity.kt / AndroidManifest.xml / build.gradle.kts / gradle.properties | working-tree truth of released app (external-audio open/send intents, versionName 2.0.1) | assembleDebug PASS |
| apps/music-android gradlew/gradlew.bat/gradle/wrapper/* deletions | working-tree truth: build tooling moved off wrapper (cached gradle 8.14 + Android Studio JBR) | build verified with cached distribution; tooling decision -> UNRESOLVED |
| apps/music-android/.gitignore + root .gitignore | build-artifact ignore patterns; P01 governance additions (.claude/, *.tsbuildinfo, res un-ignore) | verify: res dry-run adds all 7 icons |
| moodify-core-package auditory/judgment.py + tests/auditory/test_comparison.py | format-invariant BLOCKING guards (duration/channels/sample_rate) companion to stems capability (72c47c4d) | test in full suite PASS (692 green) |
| apps/music-web/assets/cadeau10-album1.json | asset manifest tracks re-encoded wav (bytes/sha256) | web tests PASS |
| apps/music-web/package-lock.json | lockfile name fix + dependency prune | npm build PASS |
| docs/reference/TENCENT_CLOUD_SERVER.md deletion | Tencent cloud expired 2026-08-12 (project decision) | n/a |
| sync_cloud.sh deletion | Tencent sync script, obsolete | n/a |
| ops/cloud_capabilities/ (README + 2 runners + requirements) | deployed capability on LA (/opt/moodify/capabilities) | deployment evidence md accompanies |
| tests/ear_batch/*.py (3 files) | tests for tracked ops/ear_batch module | 9 passed |
| artifacts/audiolla_cloud_deploy_001 (1 md) | deployment evidence | n/a |
| artifacts/cloud_capabilities (1 md) | deployment evidence | n/a |
| artifacts/ear_batch/ (5.8M json/md) | Ear batch run evidence | n/a |
| artifacts/mfy_data_foundation_001_rev2 (14 md + 1 txt) | data foundation evidence | n/a |
| artifacts/mfy_mobile_audio_capability_baseline_001 (6 files) | Android audio path baseline evidence | device tests recorded inside |
| artifacts/mfy_music_creator_lifecycle_001 (1 md) | creator lifecycle evidence | n/a |
| apps/music-web/artifacts/mfy_surface_subtraction_001 (1 txt) | tsc baseline record | n/a |
| deliverables/releases docs (rc2/2.0.0/3.0.0/3.1.0 manifests, sha256, notes, readmes, disclaimers) | release records — same convention as already-tracked 2.0.0 release | n/a |

## B. GENERATED_OR_RUNTIME_ONLY (NOT committed — recorded)

- .codex_tmp/ (tars, wavs, screenshots, node_modules, catalogue.json) — codex scratch/temp
- temp/ (beta invite, audit dir incl. polardb_app.env, dist backups) — runtime/temp
- artifacts/ear_pilot_001/ (326M: wav/npz/png/json) — pilot runtime bundle
- artifacts/mfy_infra_foundation_001/ (244M incl. log archive gz) — log bundle
- artifacts/production_cases/ (62M: case json/npz/png/jsonl) — node case runtime store
- apps/music-web/tsconfig.tsbuildinfo — incremental build cache (now gitignored)
- **/__pycache__/ — bytecode
- deliverables APK/zip/pdf binaries + Moodify_Music_2.0.1_Android_20260816.apk-only dir — release binaries

## C. SECRET_OR_ENVIRONMENT_BOUND (never committed — verified out)

- temp/moodify_audit/polardb_app.env — PolarDB credentials (0600 local file; temp/ untracked)
- No other key-shaped / credential patterns found in untracked candidates
  (scan: sk-…, AKIA…, BEGIN PRIVATE, password=, api_key=; single hit was a doc reference
  to the env file path above)
- Root .gitignore already blocks tc_key*, id_*, *.ppk

## D. EXPERIMENTAL_NOT_READY (NOT committed)

- None identified in the uncommitted set. (Spatial hearing / MAMSE research remains committed
  in artifacts/ per existing convention; nothing new here.)

## E. UNKNOWN (NOT committed — HUMAN_DECISION_REQUIRED)

1. **Gradle wrapper deletion** — keep as working-tree truth (build via cached gradle 8.14 +
   Android Studio JBR) or restore gradlew for self-contained builds? Kept + documented for now.
2. **Large evidence bundles offline storage** — ear_pilot_001 (326M), mfy_infra_foundation_001
   (244M), production_cases (62M) stay local/offline; decision needed on authoritative offline
   location (LA server? archive disk?).
3. **.codex_tmp/ ownership** — codex scratch dir (~300M incl. node_modules); safe to delete?
4. **Dual Android lines** — apps/android (com.moodify.app, releases 3.x) vs apps/music-android
   (com.moodify.music, release 2.0.1): which is the canonical P02 product line?
