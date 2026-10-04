# LINUX_DOCKER_RELEASE_001 — Execution Report

**Date:** 2026-10-04
**Branch:** `cloud/linux-docker-release-001`
**Executor:** cloud build node `yisu-6a7bcb73aac20` / `103.144.246.242`
(Ubuntu 22.04.2 LTS, headless Linux x64, 4 vCPU, 7.7 GB RAM, 40 GB free at start)

**Delivery-line outcomes:**

```text
LINUX_STUDIO_PASS
DOCKER_CLI_NOT_RUN
```

This report is written against task section 23. Sections whose work has not been performed are
marked **NOT RUN** rather than omitted or estimated — a blank in this document means "not done", and
nothing here is extrapolated from a neighbouring result.

---

## EXECUTIVE RESULT

The **Linux Studio delivery line is built, packaged and verified**: five real defects were found and
fixed, both distribution targets were produced from a clean checkout on the cloud build node, and the
highest-risk item — a native module compiled for the wrong ABI — was closed with runtime proof inside
the packaged Electron runtime rather than by inspection.

The **Docker CLI/Core delivery line has not been started.** Its audit (§4, below) is complete and
found real breakage, but no image has been built for delivery and no container contract has been
verified.

No product logic, DSP behaviour, Core contract, workflow semantics or evidence schema was changed.
`CANON_CHANGE = NO`. Nothing was merged, tagged or published.

---

## BASE SHA / BRANCH / COMMITS / PR LINKS

| | |
|---|---|
| `origin/main` | `01edc902d72c15010dd86390dc0511fc03fb6323` |
| PR #38 | **OPEN** — head `06dce343cf362ce0da29aa01c8dcd5362f7d2f74`, base `main`, no merge commit |
| Branch point (task §2) | `origin/codex/desktop-release-001` @ `06dce343cf362ce0da29aa01c8dcd5362f7d2f74` |
| Work branch | `cloud/linux-docker-release-001` (stacked on `codex/desktop-release-001`) |
| PR | **not opened yet** |
| CI runs | **none yet** — the desktop workflow triggers on pull requests |

Commits:

```text
eabe5f34  feat(desktop): package Moodify Studio for Linux x64 (AppImage + deb)
20141f11  docs(release): record the Linux Studio packaging results
```

Because PR #38 is not merged, the task's "stacked PR with `codex/desktop-release-001` as temporary
base" rule applies. PR #38 was **not** re-implemented or copied — the Linux work branches directly
from its head.

**Line-ending hazard, checked explicitly.** The authoring checkout is Windows with
`core.autocrlf=true` and the repository has no `.gitattributes`, so every working-tree file is CRLF.
A CRLF shell script or `RUN` line is a silent Linux breakage, so the committed blob was compared
against the Linux checkout:

```text
git show HEAD:Dockerfile | sha256sum            → 791d9487eadf6ff22ab8dd42c1e2e7d14093c84a07473a0939178b977e73a8da
sha256sum Dockerfile            (on Linux node) → 791d9487eadf6ff22ab8dd42c1e2e7d14093c84a07473a0939178b977e73a8da
```

Identical. Committed content reaches Linux as LF.

---

## CURRENT DOCKER REALITY AUDIT (task §4)

Every answer below is runtime evidence collected on the cloud node against `origin/main`
(`01edc902`), which is identical to the working branch for all Docker paths
(`git diff origin/main -- Dockerfile docker-compose.yml moodify-core-package/` is empty).

### Q1 — Does the current Dockerfile build from a clean checkout?

**YES.** `nice -n 19 docker build -t moodify-audit-current:prod --target production .` finished with
`BUILD_EXIT=0` after 31 steps.

```text
image id   sha256:8893d3a8dbf81bb6b0d2d0c335b3d24aed0060ba88cbd016b4218bf746af523d
tag        moodify-audit-current:prod
size       1.61 GB
layers     13
base       python:3.11-slim → PYTHON_VERSION=3.11.17
user       moodify (non-root)
```

There is **no `.dockerignore`**, so the daemon receives the entire working tree: `du -sh .` = 403 MB,
of which `.git` alone is 313 MB. Waste, not failure — addressed by this branch's `.dockerignore`.

### Q2 — Does its health check pass?

**YES**, and the result is recorded verbatim because it is misleading if summarised:

```text
docker run --rm moodify-audit-current:prod python -c "import moodify; print('OK')"
→ HEALTHCHECK OK /app/src/moodify/__init__.py     (exit 0)
```

This check only proves the *package imports*. It does not touch the API, the queue, or any route, so
it would report `healthy` for a container whose web server is dead. It is also wrong in kind: the
image's default command is a long-running API, so the check should probe that API.

### Q3 — Does the default `uvicorn moodify.api.main:app` command start?

**YES.** The container reached `Up (healthy)` and logged:

```text
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started parent process [1]
INFO:     Application startup complete.        (× 4 workers)
```

**A static reading predicted the opposite and was wrong.** The image installs dependencies from
`moodify-core-package/requirements.txt`, which omits `matplotlib`, `jsonschema` and `PyYAML` that
`pyproject.toml` pins; that looked like a guaranteed `ImportError` at startup. The API imports lazily
and starts cleanly. Runtime evidence overrode the inference. The divergence between the two
dependency lists remains a real latent packaging defect even though it does not bite today, and it is
carried forward as a known limitation rather than quietly fixed under a packaging task.

### Q4 — Does `moodify-api` have a real `/health` route matching Compose?

**YES.** Probed from inside the running container:

```json
{"status":"ok","product":"Moodify","version":"1.0.0-rc.1","identity":"The Ear of AI",
 "queue":{"QUEUED":0,"RUNNING":0,"SUCCEEDED":0,"FAILED":0}}
```

The route is `@app.get("/health")` in `moodify-core-package/src/moodify/api/main.py`, with an alias at
`/api/v1/health`, and it returns live queue counts. The Compose health check
(`python -c "import httpx; httpx.get('http://localhost:8000/health')"`) targets it correctly, and
`httpx` is installed.

### Q5 — Does `python -m moodify.node.cli worker --port 8001` exist and start?

**NO. This is broken.** The `worker` subcommand is declared with **no arguments**:

```python
sub.add_parser("worker")          # moodify-core-package/src/moodify/node/cli.py
```

while Compose passes `--port 8001`. Reproduced on the host venv **and** inside the built image:

```text
$ python -m moodify.node.cli worker --port 8001
usage: cli.py [-h] {init,enqueue,jobs,retry,recover,status,health,worker} ...
cli.py: error: unrecognized arguments: --port 8001
EXIT=2
```

Two further defects sit behind it:

- the worker is a polling loop (`run_forever(config)`), **not** a server — so `ports: 8001:8001` and
  `MOODIFY_WORKER_URL=http://moodify-worker:8001` describe an HTTP endpoint that does not exist;
- `moodify-api` declares `depends_on: moodify-worker`. It is the list form, so Compose waits for
  *start*, not health: `docker compose up` will not hang, it will run an API in front of a worker
  that has already exited 2.

### Q6 — Does Compose become healthy, or does it encode target behaviour that is not implemented?

It encodes behaviour that is **not implemented**. `docker compose config --quiet` succeeds (one
warning: the top-level `version:` attribute is obsolete and ignored), so the file is syntactically
valid and *appears* to work — while `moodify-worker` crash-loops under `restart: unless-stopped`.

Host finding that constrains verification: **`127.0.0.1:8000` is already bound** by the production
`moodify-api` systemd unit, and Compose publishes `8000:8000`. On this node `docker compose up` will
fail to bind. That is an environment fact about the node, not a defect in the Compose file.

### Q7 — Which Python dependencies require native Linux libraries?

| Dependency | Native requirement | Supplied by |
|---|---|---|
| `numpy`, `scipy` | BLAS/LAPACK, libgfortran | manylinux wheels |
| `soundfile` | **system `libsndfile1`** | `apt-get install libsndfile1` — present |
| `librosa` | numba/llvmlite wheels | wheels |
| `pedalboard` | C++/JUCE extension, libstdc++/libgcc | manylinux wheel |
| `pydantic` | `pydantic-core` Rust extension | wheel |
| `matplotlib` | libfreetype/libpng | wheel |
| `PyYAML` | optional libyaml | wheel |
| `ffmpeg` / `ffprobe` | **system binaries** | `apt-get install ffmpeg` — present |

The Dockerfile's two explicit system packages correctly cover the only genuinely system-level
dependencies.

### Q8 — Which desktop runtime paths assume Windows?

Four, all in `moodify-desktop/src/main.js`:

| Line (before) | Code | Effect |
|---|---|---|
| 106 | `pty.spawn(process.env.ComSpec \|\| 'powershell.exe', [])` | `ComSpec` unset on Linux → `powershell.exe` → **embedded terminal cannot start** |
| — | `const PYTHON = process.env.MOODIFY_PYTHON \|\| 'python'` | stock Linux has no `python` → **every Core call fails ENOENT** |
| 509 | `path.join(VENVS[venvName], 'Scripts', 'python.exe')` | Linux venvs use `bin/python` → silent fallback |
| 607 | `path.join(VENVS['basic-pitch'], 'Scripts', 'basic-pitch.exe')` | same |

Line 181 already handled the platform correctly
(`process.platform === 'win32' ? 'codex.exe' : 'codex'`) and was used as the pattern.

`scripts/test-studio.js` had the same interpreter default, so on Linux the test harness died with
`spawn python ENOENT` **before a single test ran** — `npm test` could never have been green there.

### Q9 — Does `@openai/codex` install its Linux x64 platform package from the current lockfile?

**YES.** The lockfile carries the full platform matrix as optional dependencies:

```text
@openai/codex-linux-x64   version=0.160.0-linux-x64   os=['linux'] cpu=['x64'] optional=true
@openai/codex-darwin-x64  @openai/codex-darwin-arm64
@openai/codex-win32-x64   @openai/codex-win32-arm64   @openai/codex-linux-arm64
```

Confirmed at runtime after `npm ci` on the node: `node_modules/@openai/codex-linux-x64` PRESENT. No
packaging change was needed for the Codex runtime.

### Q10 — How must `node-pty` be compiled for Electron 33 on Linux?

See **LINUX NATIVE-MODULE SOLUTION**. `node-pty@1.1.0` declares `hasInstallScript: true`, builds via
`binding.gyp` against `node-addon-api ^7.1.0`, and has **no `os`/`cpu` restriction** — so `npm ci`
compiles it for the **host Node** ABI (115), which Electron 33 cannot load (Electron 33 is ABI 130).

---

## LINUX STUDIO ARCHITECTURE

One desktop project, extended — not a second one.

```text
moodify-desktop/               ← the same application code as Windows
  package.json                 ← + linux / deb targets, + pack:linux / dist:linux
  src/main.js                  ← platform-conditional shell + venv + interpreter resolution
  scripts/derive-linux-icon.js ← derives the Linux icon from the authoritative .ico
  renderer/assets/icon.png     ← 256x256, derived, committed (whitelisted brand asset path)

moodify-core-package/          ← untouched; still the only Core
```

Targets for RC1, and nothing beyond them: **AppImage x64** and **deb amd64**. No rpm, Snap, Flatpak,
ARM or macOS. `productName` and version are unchanged (`Moodify Studio`, `1.0.0-rc.1`).

`asar: false` is preserved, per task §6: correctness and inspectability beat compactness for RC1, and
no complete cross-platform `asarUnpack` policy has been proven for the Python helper scripts, the
`node-pty` native binary, the Codex executable, and every path `src/main.js` resolves.

**Icon provenance.** The tree's square assets are unusable — `moodify_icon_64.png` is 64×64
(electron-builder wants ≥256) and `moodify_logo.png` is 420×126, while `moodify_watermark.png` is not
the application symbol. The authoritative symbol is already committed as `moodify_icon.ico`, so
`scripts/derive-linux-icon.js` lifts its largest square PNG-backed frame (256×256) out of it.
Deterministic: same input bytes, same output bytes. `.gitignore` line 271 whitelists
`moodify-desktop/renderer/assets/*.png` explicitly as *"Brand assets for the one-shell product"*, so
the derived icon is committed on that path rather than force-added past the repo-wide `*.png` rule.

**Runtime boundary (unchanged, and documented rather than papered over).** Linux Studio RC1 is an
external-runtime shell. It requires an existing local Moodify runtime; it installs nothing on first
launch. Requirements: x86_64 Linux, a desktop session with X11 or Wayland, Python 3.10–3.12 with
Moodify Core 1.0.0-rc.1 importable, FFmpeg/FFprobe, optionally Basic Pitch and music21, and system
audio output for playback. `MOODIFY_PYTHON` pins a specific interpreter; the default is `python` on
Windows and `python3` on POSIX.

---

## LINUX NATIVE-MODULE SOLUTION

**SOLVED, and verified inside the packaged Electron runtime.**

The first approach considered was the one the task suggests:

```text
electron-builder --linux ... --config.npmRebuild=true
```

It was **abandoned, on evidence**. electron-builder reported on an unmodified run:

```text
• skipped dependencies rebuild  reason=npmRebuild is set to false
```

`npmRebuild` is a top-level key, not a per-platform one, so it cannot be flipped for Linux alone
while leaving the verified Windows path alone — and the override's effect is not inspectable from the
command line. The failure mode is the dangerous kind: a package that builds cleanly and only breaks
when the embedded terminal is opened.

The adopted solution is an explicit step built from the toolchain already present:

```json
"rebuild:electron": "electron-builder install-app-deps",
"pack:linux":  "npm run icon:linux && npm run rebuild:electron && electron-builder --linux --x64 --dir",
"dist:linux":  "npm run icon:linux && npm run rebuild:electron && electron-builder --linux AppImage deb --x64"
```

Top-level `npmRebuild` stays `false`, so the verified Windows path is untouched. Build log:

```text
• executing @electron/rebuild  electronVersion=33.4.11 arch=x64 buildFromSource=false
• preparing       moduleName=node-pty arch=x64
• finished        moduleName=node-pty arch=x64
• completed installing native dependencies
```

**Proof of ABI, not of intent.** Host Node is ABI 115; Electron 33 is ABI 130. Loading the module
under the packaged runtime is the only check that distinguishes them, because a wrong-ABI module
fails to load at all:

```text
$ ELECTRON_RUN_AS_NODE=1 ./moodify-desktop /root/linux-release-001/pty_smoke.js
electron  : 33.4.11
node      : 20.18.3
module ABI: 130
pty output: "MOODIFY_PTY_MARKER_42\r\nerr-marker"
exit code : 0
PTY_SMOKE_PASS
```

A real PTY spawned a real `/bin/sh`, the marker was captured from stdout, a second marker from
stderr, and the child's exit code came back as 0.

**Windows is unaffected**: the workflow does not run `rebuild:electron`, `npmRebuild` is still `false`,
and node-pty's verified Windows x64 prebuild is still what ships — so the Windows job still needs no
Visual Studio Build Tools.

---

## APPIMAGE RESULT + SIZE + SHA256

```text
file    Moodify_Studio_1.0.0-rc.1_Linux_x64.AppImage
bytes   273,613,480
sha256  61503e1827b36b50e475b3e90439e8ffc1c429734719305f44b5a4909cadaad7
```

- `file` → `ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter
  /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.18, stripped`
- AppImage magic at offset 8 verified: bytes `41 49 02` (`AI`, type 2).
- `--appimage-extract` → exit 0, complete `squashfs-root` with `AppRun`.

Naming: electron-builder renders `${arch}` as `x86_64` for AppImage but `x64` elsewhere, so the
required filename could not be produced from the macro. The Linux name uses a literal `x64`; RC1 is
x64-only, so that is exact. **Adding ARM later requires per-target names.**

---

## DEB RESULT + SIZE + SHA256

```text
file    Moodify_Studio_1.0.0-rc.1_Linux_amd64.deb
bytes   207,655,196
sha256  bc6272c86a34d93f0048a2833baef0b704b380e95412a47527231c1fc0d596c9
```

`dpkg-deb --info` succeeds — Debian binary package, format 2.0:

```text
Package: moodify-desktop              Version: 1.0.0~rc.1
Architecture: amd64                   Installed-Size: 715048
Maintainer: 文川院 / Moodify 声音实验室
Vendor: 文川院 / Moodify 声音实验室
Homepage: https://github.com/huliye24/moodify-ai
Depends: libgtk-3-0, libnotify4, libnss3, libxss1, libxtst6, xdg-utils,
         libatspi2.0-0, libuuid1, libsecret-1-0
Recommends: libappindicator3-1
Section: default                      Priority: optional
```

`Version: 1.0.0~rc.1` is Debian's own normalisation of `1.0.0-rc.1` — `~` sorts before the release,
which is the correct pre-release ordering, not a packaging error. `Section: default` is
electron-builder's fallback; the `.desktop` entry carries the real category from `linux.category`
(`AudioVideo`). Desktop entry present at `./usr/share/applications/moodify-desktop.desktop`.

Two build failures were hit and fixed on the way here, both packaging-only:

- **`Please specify project homepage`** — the deb target hard-fails without `homepage`. Set to
  `https://github.com/huliye24/moodify-ai`, the URL the repository already declares in `CITATION.cff`.
- **`configuration.linux.desktop` schema rejection** — electron-builder 26.15.3 does not accept the
  nested `desktop` object; `linux.category` already produces the desktop entry, so the block was
  removed rather than worked around.

`FFmpeg`, `FFprobe`, Python, Core and model weights are deliberately **not** dependencies of the
package. Installing them silently would contradict the documented runtime boundary (`Generated is not
finished` is about process, but the same honesty applies to what a package claims to provide).

---

## PACKAGED TREE INSPECTION

`dist-electron/linux-unpacked` = **700 MB**, of which `resources/app/node_modules` = **436 MB**
(the Codex binary alone is 289 MB).

Every path `src/main.js` resolves at runtime, checked against the real tree:

| Expected | Result |
|---|---|
| `resources/app/package.json` | PRESENT |
| `resources/app/src/main.js` | PRESENT |
| `resources/app/renderer/index.html` | PRESENT |
| `resources/app/renderer/assets/icon.png` | PRESENT (derived) |
| `resources/app/scripts/dsp_separate.py` | PRESENT |
| `resources/app/scripts/midi_to_musicxml.py` | PRESENT |
| `resources/app/node_modules/node-pty/build/Release/pty.node` | PRESENT |
| `@openai/codex-linux-x64` | PRESENT |

`TOOLS_ROOT` resolves to `resources/app/scripts` and both helper scripts are there.

Codex on Linux:

```text
vendor/x86_64-unknown-linux-musl/bin/codex   ELF 64-bit LSB pie, static-pie linked, 289 MB
$ codex --version  →  codex-cli 0.160.0     (exit 0, non-interactive)
$ codex --help     →  usage text printed    (exit 0)
```

This matches `resolveCodexExe()` in `src/main.js`, which scans `node_modules/@openai/codex-*/vendor`
and selects the `codex` / `codex.exe` leaf by platform — the packaged layout is exactly the one it
expects.

> **Correction to an interim finding.** An intermediate check in this session reported
> `@openai/codex-linux-x64 MISSING` from the packaged tree. That was **a bug in the check script**,
> which guessed a `bin/` layout; the package is present and complete under
> `vendor/x86_64-unknown-linux-musl/`. The false reading is recorded here rather than quietly dropped,
> and it is a reminder that a path-shaped assertion can fail while the thing it describes is fine.

`VENVS['basic-pitch']` and `VENVS['score']` resolve to `resources/app/../../.venv-*`, which exist in
neither the Windows nor the Linux package. That is the documented external-runtime boundary, not a
packaging gap: `pyExe()` falls back to the configured interpreter, and the MIDI stage reports an
honest "not found" failure when basic-pitch is absent.

---

## HEADLESS LAUNCH RESULT

```text
$ xvfb-run -a ./moodify-desktop --no-sandbox --disable-gpu     (30 s timeout)
PROCESS_ALIVE_AFTER_18s = yes
missing-module / crash markers: (none)
```

The unpacked Electron application **starts and stays up** under Xvfb with no `MODULE_NOT_FOUND` and
no crash. Per the task, this proves only that Electron starts and loads the renderer. It does **not**
prove visual correctness, playback quality, or usability, and no such claim is made. `--no-sandbox`
was used because the build ran as root; it is a smoke-test launch flag, not a product change.

---

## DOCKER IMAGE RESULT + ID + SIZE

**NOT RUN.** No delivery image has been built. The only image produced in this session is the audit
baseline of the *existing, unmodified* Dockerfile, retained for comparison:

```text
moodify-audit-current:prod
sha256:8893d3a8dbf81bb6b0d2d0c335b3d24aed0060ba88cbd016b4218bf746af523d
1.61 GB, 13 layers, base python:3.11-slim (3.11.17), user moodify
```

It is an audit artefact, not a deliverable, and it must not be read as the task's image result.

---

## CLI/CORE CONTAINER RESULT

**NOT RUN.** The `moodify --help` contract, the read-only-input / writable-output mount contract, the
fixture workflow, evidence-schema validation, invalid-input failure and SIGTERM handling have **not**
been exercised. No claim is made about any of them.

---

## COMPOSE SERVICE CLASSIFICATION

Classified from the §4 evidence; no service was repaired in this session.

| Service | Classification | Basis |
|---|---|---|
| `moodify-api` | **VERIFIED_SUPPORTED** | builds, starts (`Up (healthy)`), 4 workers, `/health` answers with live queue counts, health check matches the real route |
| `moodify-worker` | **BROKEN_STALE** | `worker --port 8001` exits 2 with `unrecognized arguments`; the subcommand takes no options and the worker is a polling loop, not an HTTP server, so `ports: 8001:8001` and `MOODIFY_WORKER_URL` describe an endpoint that does not exist |

Consequences recorded but **not yet acted on**: with `restart: unless-stopped` the worker crash-loops,
and `moodify-api` sits in front of it because `depends_on` waits for start rather than health. The
default `docker compose up` path therefore does not wait forever — it reports a healthy API and a
dead worker, which is arguably worse than hanging.

Per task §13, this is to be repaired with a minimal packaging-only change backed by tests, or removed
from the default path with the historical record preserved. **Neither has been done yet.**

---

## SBOM / VULNERABILITY RESULT

**NOT RUN.** No SBOM generated, no image scanned. No security claim of any kind is made — including
for the artifacts that *were* built, which are unsigned and unscanned.

---

## WINDOWS REGRESSION RESULT

**Partial — local baselines green, CI not yet run.**

Run locally on the work branch, after every change in this branch:

```text
node scripts/check-contracts.js   ✓ DOM id 126 · 桥接 54 · IPC 52 · 事件 5
node scripts/test-studio.js       21 passed, 0 failed
node scripts/test-pipeline.js     33 passed, 0 failed
```

These are exactly the §19 Windows baselines (`Studio 21/21`, `pipeline 33/33`), so nothing in this
branch moves them. The shared `moodify-desktop` configuration was changed, so the Windows workflow
**must** be observed green on the PR before this line can be closed — that has not happened yet, and
the Windows artifact has not been rebuilt or re-verified since `06dce343`.

Untested on Windows: that `npm run dist:win` still produces both EXEs under the amended
`package.json`, and that installing `@electron/rebuild`-style invocation changes nothing there (it
does not run in the Windows job).

---

## CI RUN LINKS

**None.** No PR has been opened, so no workflow has been triggered. The Linux job described in task
§8 has **not** been written yet; the Linux builds in this report were driven by a script on the build
node, which is evidence for the packaging but **not** a substitute for CI.

---

## KNOWN LIMITATIONS

1. **`requirements.txt` and `pyproject.toml` disagree.** The image installs from the former, which
   omits `matplotlib`, `jsonschema` and `PyYAML` that the latter pins. The API happens to import
   lazily and start cleanly (verified), so this does not bite today — which is precisely why it is
   listed rather than fixed under a packaging task.
2. **The API image's health check is not a health check.** It imports the package and takes no view of
   the web server or the queue.
3. **No `.dockerignore` exists on `main`.** The audit build shipped a 403 MB context (313 MB of it
   `.git`) to the daemon. This branch adds one; it has not yet been exercised by a rebuild.
4. **The production image would contain an editable install** (`pip install -e /app`), which task §11
   forbids unless technically required and explained. Not yet addressed.
5. **The worker service is broken** (see COMPOSE SERVICE CLASSIFICATION).
6. **Linux Studio is an external-runtime shell.** The AppImage does *not* make the audio runtime
   self-contained, and this report does not claim it does.
7. **`asar` is disabled.** electron-builder warns about this on every Linux build; it is a deliberate
   RC1 choice, not an oversight.
8. **Window association may be imperfect on some desktops.** electron-builder warns that
   `desktopName` is unset, so some Linux desktops may not link the running window to its `.desktop`
   entry.
9. **The deb `Section` is `default`.** Cosmetic; `linux.category` sets the real `.desktop` category.
10. **The AppImage is 273 MB and the unpacked tree 700 MB**, dominated by the 289 MB Codex binary.
    Not a defect, but relevant to distribution cost.
11. **Nothing was verified on real hardware or a real desktop session.** See HUMAN_CHECK_REQUIRED.

---

## HUMAN_DECISION_REQUIRED ITEMS

### HUMAN_DECISION_REQUIRED — CONTAINER TAG AUTHORITY

Task §16 requires this before any GHCR publication. **Phase A has not published anything.**

The recommendation is that the container tag namespace must be disjoint from both existing release
namespaces — Android uses `v*`, desktop uses `desktop-v*`:

```text
container-v1.0.0-rc.1        ← proposed
```

To approve: registry path (`ghcr.io/huliye24/…`), public/private visibility, tag namespace, and
whether API/worker modes are part of the supported image contract at all. `latest` must not be
published for an RC.

### HUMAN_DECISION_REQUIRED — PR STRUCTURE

Task §2 names a single preferred branch (`cloud/linux-docker-release-001`, which this work uses) and
task §22 prefers two reviewable PRs *if the changes remain separable*. They are in fact fully
separable — the Docker work touches no desktop file and vice versa. **Awaiting a decision**: one
stacked PR, or `Linux release 001 — Studio AppImage and deb` plus
`Container release 001 — CLI/Core Docker runtime`.

---

## HUMAN_CHECK_REQUIRED

```text
HUMAN_CHECK_REQUIRED
```

Nothing in this report establishes how the Linux build looks, sounds or feels. On a real Linux
desktop a human must still:

1. launch the AppImage;
2. install the deb;
3. confirm window, icon, fonts, layout and file picker;
4. open authorized real audio;
5. run Detect and Diagnose;
6. run quick separation where the runtime allows;
7. check playback and A/B audio routing;
8. close and reopen;
9. uninstall the deb;
10. confirm the AppImage remains independently runnable.

Xvfb and container smoke do not replace this check.

---

## RECOMMENDATION

```text
LINUX_STUDIO_PASS            — packaging and the native-module boundary are verified
DOCKER_CLI_NOT_RUN           — audit complete, implementation not started
WINDOWS_REGRESSION_PENDING   — local baselines green, CI not yet observed
```

**Phase A stop condition is NOT yet satisfied**, because the Docker line has not begun and the
Windows workflow has not been observed on a PR. Recommend:

- treat the Linux Studio branch as ready for review once its PR exists and the Windows job is green;
- do not merge, tag, or publish anything — release authority remains human;
- decide the PR structure question above;
- authorise (or defer) the Docker CLI/Core implementation, noting that the audit has already found
  the worker service broken and the production image carrying an editable install.
