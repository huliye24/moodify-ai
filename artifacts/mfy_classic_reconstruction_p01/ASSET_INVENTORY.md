# MFY-CR-P01 — Canonical Inventory

Classification values: CANONICAL / SUPPORTED_EXTERNAL / EXPERIMENTAL / LEGACY / RUNTIME_ONLY / UNRESOLVED.

| # | Surface | Location | Status | Notes |
|---|---|---|---|---|
| 1 | Auditory Core | moodify-core-package/src/moodify/auditory | CANONICAL | judgment risk-flag guards converged in Commit 1 |
| 2 | Contracts | moodify-core-package/src/moodify/contracts | CANONICAL | |
| 3 | Authority | moodify-core-package/src/moodify/authority | CANONICAL | incl. ProductionCase / evidence system |
| 4 | Data Factory | moodify-core-package/src/moodify/data_factory | CANONICAL | Data Protocol v1 frozen; ruff F401 fix in Commit 1 |
| 5 | Processing | moodify-core-package/src/moodify/processing | CANONICAL | |
| 6 | Node / Worker | moodify-core-package/src/moodify/node + ops/data_node | CANONICAL | deployed 120.55.191.146 (Aliyun) |
| 7 | Web Origin / BFF | apps/music-web + ops/web_origin | CANONICAL | deployed 103.144.246.242 (LA); nginx + node env.example tracked |
| 8 | Android Player (new line) | apps/music-android (com.moodify.music) | CANONICAL | released 2.0.1; player/ ui/ res/ untracked -> converged Commit 1; no unit tests |
| 9 | Android (legacy line) | apps/android (com.moodify.app) | CANONICAL | released 2.0.0/3.0.0/3.1.0; which line is canonical for P02 -> UNRESOLVED |
| 10 | Stems / LALAL | moodify-core-package/src/moodify/stems + api/routes/stems.py | CANONICAL | commit 72c47c4d (unpushed); tests in full suite PASS |
| 11 | Audiolla | external cloud service + artifacts/audiolla_cloud_deploy_001 | SUPPORTED_EXTERNAL | LA deployment evidence committed in Commit 1 |
| 12 | Cloud Capabilities (Basic Pitch / MuseScore) | ops/cloud_capabilities + artifacts/cloud_capabilities | CANONICAL | deployed /opt/moodify/capabilities on LA; scripts + evidence committed in Commit 1 |
| 13 | Storage | PolarDB MySQL pc-bp1112f8t24wdta5t + LA disk | SUPPORTED_EXTERNAL | VPC peering pending (pre-existing blocker, R06) |
| 14 | Tests (core) | moodify-core-package/tests | CANONICAL | 692 pass / 5 skip |
| 15 | Tests (ear_batch) | tests/ear_batch | CANONICAL | 9 pass; converged Commit 1 |
| 16 | Tests (music-web) | apps/music-web/tests | CANONICAL | 36 pass |
| 17 | Runtime-only assets | temp/ (incl. polardb_app.env), .codex_tmp/, LA /opt/moodify runtime | RUNTIME_ONLY | never in git; env file holds DB credentials (out of scope of commits) |
| 18 | Large evidence bundles | artifacts/ear_pilot_001 (326M), artifacts/mfy_infra_foundation_001 (244M), artifacts/production_cases (62M) | RUNTIME_ONLY / UNRESOLVED | too heavy for git; offline storage decision -> UNRESOLVED |
| 19 | Release records | deliverables/releases (manifests, sha256, notes, readmes) | CANONICAL | docs committed in Commit 1; APK/zip/pdf binaries stay out (RUNTIME_ONLY) |
| 20 | Legacy / historical | docs/reference/TENCENT_CLOUD_SERVER.md, sync_cloud.sh | LEGACY | deleted in Commit 1 (Tencent expired) |
