# MOODIFY_LINUX_DOCKER_RELEASE_001.md

> **Repository:** `huliye24/moodify-ai`
> **Owner:** RELEASE ENGINEERING / MULTI-PLATFORM
> **Executor:** Cloud AI on a Linux build server
> **Dependency:** PR #38 — Windows RC packaging
> **Target:** Linux x64 Studio packages plus a verified Linux Docker CLI/Core image
> **Rule:** One Core, multiple interfaces. Package existing capability; do not create a second Core or a new cloud product.

## 0. Human direction

Moodify must be usable across Windows and Linux.

This task adds two distinct Linux delivery surfaces:

```text
Linux desktop user
→ Moodify Studio
→ AppImage + deb

Linux server / agent
→ Moodify CLI + Core
→ Docker image
```

Do not put the Electron GUI into Docker. A headless Linux server needs the CLI/Core execution surface, not a fake desktop.

The intended cross-platform architecture remains:

```text
                         Moodify Core
                       /              \
       CLI / Docker / Agents          Studio / App
              PROCESS                 Preview / Review
```

`CANON_CHANGE = NO`

Reason: this task packages existing interfaces for additional operating environments. It does not change product identity, state authority, evidence authority, DSP behavior, or the human/machine judgment boundary.

## 1. Non-negotiable product boundaries

- Preserve **Generated is not finished.**
- Preserve **One Core, Multiple Interfaces**.
- Linux Studio and Windows Studio must use the same `moodify-desktop` application code and the same Core contracts.
- Docker must invoke the canonical `moodify-core-package`; it must not contain a forked audio engine.
- The container may expose existing CLI/API/worker behavior only when runtime evidence confirms it.
- Do not invent a second job authority, orchestration system, processing state machine, or evidence schema.
- Do not move DSP logic into Electron, shell scripts, Docker entrypoints, or platform adapters.
- Do not claim perceptual quality from CI.
- Do not claim a fully self-contained Studio while Python/Core/FFmpeg remain external.
- Do not modify Android identity or `.github/workflows/release.yml`.
- Do not add accounts, social features, cloud storage, P2P, telemetry, licensing, updater, Kubernetes, or model weights.
- Do not publish a release tag or container image during Phase A.

## 2. Branch and worktree precondition

First inspect:

```bash
git fetch origin --prune
git status --short
git branch --show-current
git rev-parse origin/main
gh pr view 38 --repo huliye24/moodify-ai --json state,headRefOid,mergeCommit,url
```

Use a new clean worktree. Do not reuse the Windows release worktree.

Preferred branch:

```text
cloud/linux-docker-release-001
```

PR #38 currently contains the shared electron-builder configuration required by this task.

- If PR #38 is merged, branch from the updated `origin/main`.
- If PR #38 remains open, branch from `origin/codex/desktop-release-001` and open a clearly marked stacked PR with that branch as its temporary base.
- After #38 merges, rebase the Linux/Docker branch onto current `origin/main`, retarget its PR to `main`, and rerun all verification.
- Do not copy or reimplement #38 manually.

Record the exact base SHA in the final report.

## 3. Phase A deliverables

Produce source-controlled release engineering for:

```text
Moodify Studio Linux x64 AppImage
Moodify Studio Linux x64 deb
SHA256SUMS.txt
RELEASE_MANIFEST.json
Linux release notes

Moodify CLI/Core Linux Docker image
OCI image archive or digest evidence
container manifest/SBOM when practical
Docker usage documentation
```

Expected Linux Studio filenames:

```text
Moodify_Studio_1.0.0-rc.1_Linux_x64.AppImage
Moodify_Studio_1.0.0-rc.1_Linux_amd64.deb
```

Use deterministic names. Never allow one target to overwrite another.

Phase A must build and test artifacts but must not publish a GitHub Release or push a production container tag.

## 4. Reality audit before implementation

Inspect and report the current state of:

```text
Dockerfile
docker-compose.yml
deployment/local.md
deployment/cloud.md
moodify-core-package/pyproject.toml
moodify-core-package/requirements.txt
moodify-desktop/package.json
moodify-desktop/package-lock.json
moodify-desktop/src/main.js
moodify-desktop/src/backends/**
.github/workflows/desktop-release.yml
```

Answer with runtime evidence:

1. Does the current Dockerfile build from a clean checkout?
2. Does its health check pass?
3. Does the default `uvicorn moodify.api.main:app` command start?
4. Does `moodify-api` have a real `/health` route matching Compose?
5. Does `python -m moodify.node.cli worker --port 8001` exist and start?
6. Does Compose become healthy, or does it encode historical/target behavior that is not implemented?
7. Which current Python dependencies require native Linux libraries?
8. Which desktop runtime paths assume Windows?
9. Does `@openai/codex` install its Linux x64 platform package from the current lockfile?
10. How must `node-pty` be compiled for Electron 33 on Linux?

Do not treat the presence of a Dockerfile as proof that Docker is supported.

## 5. Linux native-module constraint

The current Windows release uses:

```json
"npmRebuild": false
```

because `node-pty` 1.1.0 ships a verified Windows x64 prebuild. Do not assume the same for Linux.

The observed `node-pty` package does not provide the same Linux prebuild set. Linux packaging must prove that its native module is compiled for Electron 33, not merely for the host Node.js ABI.

Implement the smallest target-specific solution that preserves Windows behavior. For example, after verifying electron-builder 26 behavior, Linux packaging may override configuration conceptually as:

```text
electron-builder --linux ... --config.npmRebuild=true
```

or perform an explicit Electron rebuild before packaging.

Required proof:

- clean `npm ci` on Ubuntu;
- Linux build dependencies are explicitly installed in CI;
- `node-pty` native module loads under the packaged Electron runtime;
- a PTY can spawn a real shell and capture a known output string;
- Windows workflow still passes without requiring Visual Studio Build Tools.

Do not solve Linux by globally breaking the verified Windows packaging path.

## 6. Linux Studio packaging

Extend the existing `moodify-desktop` electron-builder configuration rather than creating a second desktop project.

Add scripts conceptually equivalent to:

```text
pack:linux
dist:linux
```

Required targets for RC1:

```text
AppImage x64
deb amd64
```

Do not add rpm, Snap, Flatpak, ARM, or macOS in this task unless all required native dependencies are proven and the human explicitly expands scope.

Use:

```text
productName = Moodify Studio
version = 1.0.0-rc.1
category = AudioVideo or an evidence-supported desktop category
```

Preserve `asar: false` for RC1 unless a complete, tested cross-platform `asarUnpack` policy is proven for:

- Python helper scripts;
- `node-pty` native binaries;
- `@openai/codex` Linux executable;
- all paths resolved from `src/main.js`.

Correct and inspectable beats compact.

Use the existing Moodify brand. Do not design a new Linux identity. Electron Linux icons may use a deterministic square PNG derived from the authoritative symbol, but first obey repository ignore and generated-artifact rules.

## 7. Linux Studio runtime boundary

Linux Studio RC1 may remain an external-runtime shell if that is the verified reality.

Document exact requirements, expected to include:

```text
x86_64 Linux with glibc compatible with the build target
desktop session with X11 or Wayland support
Python 3.10–3.12
Moodify Core 1.0.0-rc.1 importable
FFmpeg / FFprobe
Basic Pitch optional
music21 optional
system audio output for playback
```

Do not silently install Python, Core, FFmpeg, optional packages, or model weights on first launch.

Do not claim that AppImage makes the external audio runtime self-contained.

## 8. Linux Studio CI

Prefer extending the existing desktop release workflow into explicit platform jobs while preserving its proven Windows job:

```text
windows-x64
linux-x64
release (tag only, waits for both)
```

Alternatively, use a separate Linux workflow during Phase A if that reduces risk. Explain the final design.

Linux job:

```text
runs-on: ubuntu-latest
Node.js 20
required compiler/native packages
npm ci
npm test
Linux node-pty Electron rebuild
npm run pack:linux
headless packaged-runtime smoke
npm run dist:linux
manifest + checksums
Actions artifact upload
```

Use `xvfb-run` only for a minimal launch smoke. Headless launch evidence may prove that Electron starts and loads the renderer; it does not prove visual correctness, playback quality, or human usability.

Do not let the Linux job publish during pull requests.

## 9. Linux package inspection

Inspect the unpacked application and both distribution targets.

Verify that the packaged application contains or resolves:

```text
package.json and Electron entrypoint
renderer assets
scripts/dsp_separate.py
scripts/midi_to_musicxml.py
Linux node-pty native module
@openai/codex Linux x64 executable/package
```

Confirm `src/main.js` runtime paths resolve to real files under the unpacked application tree.

Required smoke checks:

- AppImage exists, is non-empty, and has expected ELF/AppImage identity;
- deb exists, is non-empty, and `dpkg-deb --info` succeeds;
- deb package metadata uses Moodify Studio identity;
- unpacked Electron application starts under `xvfb-run` without an immediate missing-module error;
- `node-pty` spawns `/bin/sh` or `/bin/bash` and captures a known marker;
- Codex Linux executable exists and can return its version/help without starting an interactive session;
- manifest hashes match the actual artifacts.

Do not claim audio UI acceptance from Xvfb.

## 10. Docker product boundary

Docker is the Linux server/agent execution surface:

```text
input mounted read-only
→ Moodify CLI/Core
→ processing/evidence
→ output mounted read-write
```

The first supported container must be a headless CLI/Core image. API and worker modes may be preserved only if existing commands are verified.

Do not put Electron, Xvfb, a browser, or a remote desktop server into the production image.

Do not bake private audio, API keys, credentials, server addresses, or model weights into image layers.

## 11. Dockerfile requirements

Repair or replace the current Docker build only as required by runtime evidence.

Required properties:

- current supported Python version, initially Python 3.11 unless package metadata proves otherwise;
- FFmpeg, FFprobe, and required audio system libraries installed explicitly;
- canonical `moodify-core-package` installed from this repository;
- non-root runtime user;
- deterministic working, input, output, evidence, and temporary paths;
- useful OCI labels including source repository, revision, version, and license;
- no editable install in the final production image unless technically required and explained;
- no build compiler/cache retained in the runtime layer;
- no secrets in environment defaults or layers;
- PID 1 receives signals correctly;
- clear CLI entrypoint or documented command invocation;
- health check only when a long-running API mode is actually used;
- `.dockerignore` prevents `.git`, node_modules, builds, private audio, cases, evidence, local environments, and large generated artifacts from entering build context.

Prefer one well-defined image with explicit commands over several drifting images.

## 12. Container CLI contract

Provide documented examples using mounted directories, conceptually:

```bash
docker run --rm \
  --user <non-root> \
  -v /host/input:/input:ro \
  -v /host/output:/output \
  ghcr.io/huliye24/moodify:<version> \
  moodify --help
```

Then prove at least one repository-supported processing path with a small authorized fixture.

The container result must preserve:

- actual parameter record;
- evidence artifact;
- input/output hashes where the existing contract provides them;
- explicit review-required or human-required state;
- non-zero exit on invalid input or failed processing;
- no overwrite of an existing attempt unless the existing contract permits it.

Do not invent new CLI semantics solely for Docker. If the current CLI is insufficient, document the smallest adapter required and keep it outside Core behavior.

## 13. Docker Compose truth audit

The current Compose declares `moodify-api` and `moodify-worker`. Validate every command, port, health check, dependency, and volume.

For each service, classify:

```text
VERIFIED_SUPPORTED
EXPERIMENTAL
BROKEN_STALE
TARGET_NOT_IMPLEMENTED
```

If a service is broken or aspirational:

- do not fake it;
- either repair it with a minimal packaging-only change backed by tests, or
- remove it from the default Compose path and document why;
- do not delete historical capability without preserving the record required by repository policy.

The default `docker compose up` path must not wait forever on a nonexistent worker or false health check.

## 14. Docker verification matrix

Run from a clean checkout on Linux:

```text
docker build
docker image inspect
docker run as non-root
Core import
CLI --help/version
FFmpeg and FFprobe availability
read-only input mount
writable output mount
one real fixture workflow
evidence existence and schema validation
invalid-input failure
SIGTERM/graceful exit for long-running mode
docker compose config
docker compose build
docker compose up + health only for verified services
docker compose down
```

Record:

- image ID;
- image size;
- exact source commit;
- base image digest when available;
- runtime user UID/GID;
- command exit codes;
- produced evidence paths and hashes;
- container logs with secrets redacted.

## 15. Container security and reproducibility

At minimum:

- generate an SBOM using a maintained tool available in CI, or explain why blocked;
- scan the final image for known critical/high vulnerabilities;
- distinguish base-image vulnerabilities from Moodify code findings;
- fail publication on unresolved critical vulnerabilities unless the human explicitly accepts a documented exception;
- pin GitHub Actions to stable major versions at minimum;
- use GitHub OIDC/token permissions narrowly;
- make PR builds read-only and never push images;
- do not use privileged containers;
- do not mount the Docker socket;
- do not run the production image as root.

Do not claim “secure” merely because a scanner found zero items.

## 16. Container registry and tags

During Phase A, build and test only. Upload an OCI archive or workflow artifact if needed for review.

Before implementing public GHCR publication, write:

```text
HUMAN_DECISION_REQUIRED — CONTAINER TAG AUTHORITY
```

Recommend one explicit tag namespace that cannot collide with Android `v*` or desktop `desktop-v*`, for example:

```text
container-v1.0.0-rc.1
```

The human must approve:

- registry path;
- public/private visibility;
- tag namespace;
- whether API/worker modes are part of the supported image contract.

Do not publish `latest` for an RC.

## 17. Unified release coordination

Linux Studio belongs to the same Moodify Studio release as Windows. A future `desktop-v1.0.0-rc.1` tag should produce one GitHub prerelease containing both operating systems.

Avoid two workflows racing to create or edit the same GitHub Release.

Preferred final topology:

```text
desktop-v* tag
  ├── Windows build job
  ├── Linux build job
  └── one release job after both succeed
```

The release job should download verified job artifacts, verify version/tag consistency, and publish one prerelease.

Do not implement tag publication until:

- Windows workflow remains green;
- Linux workflow is green;
- release coordination is tested without publishing;
- human approves Phase B.

## 18. Documentation

Create or update:

```text
docs/releases/MOODIFY_STUDIO_1_0_RC1.md
docs/releases/MOODIFY_STUDIO_LINUX_1_0_RC1.md
docs/deployment/DOCKER.md or the canonical existing Docker deployment document
docs/reports/LINUX_DOCKER_RELEASE_001_<date>.md
```

Document honestly:

- supported OS and architecture;
- AppImage/deb installation and launch;
- external runtime requirements;
- Docker CLI usage with mounts;
- API/worker status based on actual verification;
- unsigned Linux package status;
- known limitations;
- exact test evidence;
- manual Linux GUI and audio check still required.

Do not market Docker as the Studio UI or claim Linux packages are self-contained when they are not.

## 19. Required tests

Run all relevant existing tests plus packaging checks:

```bash
cd moodify-desktop
npm ci
npm test
npm run pack:linux
npm run dist:linux

cd ..
python scripts/check_repo_structure.py
git diff --check
```

Also rerun or wait for the existing Windows workflow after shared package configuration changes.

Windows regression acceptance:

```text
contracts pass
pipeline 33/33 or documented current baseline
Studio 21/21 or documented current baseline
Windows Setup exists
Windows Portable exists
Windows package still loads node-pty prebuild
```

Linux acceptance:

```text
Linux tests pass
node-pty Electron ABI smoke passes
AppImage exists and launches under Xvfb
deb validates and installs in a clean disposable environment
packaged runtime tree is complete
checksums and manifest match
```

Docker acceptance:

```text
clean build succeeds
non-root runtime succeeds
Core import succeeds
CLI smoke succeeds
one fixture flow produces evidence
invalid input fails explicitly
Compose truth audit completed
SBOM and vulnerability report produced
```

## 20. Manual Linux check

After CI artifacts are available, report:

```text
HUMAN_CHECK_REQUIRED
```

On a real Linux desktop, a human must:

1. launch the AppImage;
2. install the deb;
3. confirm window, icon, fonts, layout, and file picker;
4. open authorized real audio;
5. run Detect and Diagnose;
6. run quick separation when runtime allows;
7. check playback and A/B audio routing;
8. close and reopen;
9. uninstall the deb;
10. confirm the AppImage remains independently runnable.

Xvfb or container smoke does not replace this check.

## 21. Expected files to change

Likely:

```text
moodify-desktop/package.json
moodify-desktop/package-lock.json
.github/workflows/desktop-release.yml
Dockerfile
docker-compose.yml
.dockerignore
docs/releases/MOODIFY_STUDIO_1_0_RC1.md
docs/releases/MOODIFY_STUDIO_LINUX_1_0_RC1.md
deployment/local.md or canonical Docker documentation
docs/reports/LINUX_DOCKER_RELEASE_001_<date>.md
```

Allow small packaging-only scripts when they eliminate duplicated CI logic.

Do not commit:

```text
AppImage
deb
OCI tar
Docker image layers
node_modules
dist-electron
private audio
generated evidence
scanner caches
```

Before adding every non-Python file:

```bash
git check-ignore -v <path>
```

## 22. Pull request structure

Prefer two reviewable PRs if the changes remain separable:

```text
PR A — Linux Studio packaging
PR B — Docker CLI/Core runtime
```

If both must share a small release-metadata utility, keep that utility minimal and explain the dependency. Do not create duplicate release frameworks.

Suggested titles:

```text
Linux release 001 — Studio AppImage and deb
Container release 001 — CLI/Core Docker runtime
```

Each PR body must include:

```text
WHY
CURRENT REALITY
WHAT CHANGED
ARTIFACTS
TESTS
RUNTIME BOUNDARY
SECURITY / SIGNING
WINDOWS REGRESSION STATUS
WHAT WAS NOT CHANGED
HUMAN CHECK REQUIRED
```

Do not auto-merge.

## 23. Required final execution report

Return one Markdown report containing:

```text
EXECUTIVE RESULT
BASE SHA / BRANCH / COMMITS / PR LINKS
CURRENT DOCKER REALITY AUDIT
LINUX STUDIO ARCHITECTURE
LINUX NATIVE-MODULE SOLUTION
APPIMAGE RESULT + SIZE + SHA256
DEB RESULT + SIZE + SHA256
PACKAGED TREE INSPECTION
HEADLESS LAUNCH RESULT
DOCKER IMAGE RESULT + ID + SIZE
CLI/CORE CONTAINER RESULT
COMPOSE SERVICE CLASSIFICATION
SBOM / VULNERABILITY RESULT
WINDOWS REGRESSION RESULT
CI RUN LINKS
KNOWN LIMITATIONS
HUMAN_DECISION_REQUIRED ITEMS
HUMAN_CHECK_REQUIRED
RECOMMENDATION
```

Use one primary outcome per delivery line:

```text
LINUX_STUDIO_PASS
LINUX_STUDIO_BLOCKED
LINUX_STUDIO_FAIL

DOCKER_CLI_PASS
DOCKER_CLI_BLOCKED
DOCKER_CLI_FAIL
```

Do not collapse an external-runtime blocker into a packaging pass, and do not collapse a successful build into a GUI/audio acceptance pass.

## 24. Phase A stop condition

Stop after:

- Linux Studio PR artifact build succeeds;
- Docker image build and CLI/Core verification succeeds;
- Windows packaging regression remains green;
- artifacts, hashes, manifests, SBOM, and reports are available;
- PR or PRs are open and attached;
- no release/tag/image publication has occurred.

Report the exact manual Linux checks and container-tag decisions still required.

Wait for human review before Phase B publication.
