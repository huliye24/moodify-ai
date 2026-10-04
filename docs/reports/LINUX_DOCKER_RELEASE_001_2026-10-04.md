# LINUX_DOCKER_RELEASE_001 — Execution Report

> **Status:** Phase A in progress. This file is the running record; it is completed at the end.
> **Branch:** `cloud/linux-docker-release-001`
> **Executor:** cloud build node `yisu-6a7bcb73aac20` / `103.144.246.242` (Ubuntu 22.04.2, headless Linux x64)

---

## BASE SHA / BRANCH / COMMITS

| | |
|---|---|
| `origin/main` | `01edc902d72c15010dd86390dc0511fc03fb6323` |
| PR #38 state | **OPEN** — head `06dce343cf362ce0da29aa01c8dcd5362f7d2f74`, base `main`, no merge commit |
| Branch point (per task §2) | `origin/codex/desktop-release-001` @ `06dce343cf362ce0da29aa01c8dcd5362f7d2f74` |
| Work branch | `cloud/linux-docker-release-001`, stacked on `codex/desktop-release-001` |

Since PR #38 is **not merged**, the task's "stacked PR with `codex/desktop-release-001` as temporary
base" rule applies. PR #38 is a public repository; no manual re-implementation of it was performed —
the Linux work branches directly from its head.

**Line-ending note.** The authoring checkout is Windows with `core.autocrlf=true` and there is no
`.gitattributes`. Working-tree files are CRLF while the *committed blobs* are LF — verified by
comparing `git show HEAD:Dockerfile | sha256sum` (`791d9487…`) against the Linux checkout
(`791d9487…`, identical). Committed content therefore reaches Linux with LF. This was checked
explicitly because a CRLF shell script or Dockerfile `RUN` line would be a silent Linux breakage.

---

## CURRENT DOCKER REALITY AUDIT (task §4)

All answers below are backed by runtime evidence collected on the cloud node, not by reading files.
The site under test is `origin/main` (`01edc902`), which is identical to the working branch for every
Docker-related path (`git diff origin/main -- Dockerfile docker-compose.yml moodify-core-package/`
is empty).

### Q1 — Does the current Dockerfile build from a clean checkout?

**YES.** `nice -n 19 docker build -t moodify-audit-current:prod --target production .` completed with
`BUILD_EXIT=0`, 31 steps.

```text
image id   sha256:8893d3a8dbf81bb6b0d2d0c335b3d24aed0060ba88cbd016b4218bf746af523d
tag        moodify-audit-current:prod
size       1.61 GB
layers     13
base       python:3.11-slim → PYTHON_VERSION=3.11.17
user       moodify  (non-root ✓)
```

**Build context is unignored.** There is no `.dockerignore`, so the daemon receives the whole working
tree — `du -sh .` = **403 MB**, of which `.git` alone is **313 MB**. This is waste, not failure; it is
fixed in this branch.

### Q2 — Does its health check pass?

**YES**, and the answer is surprising, so it is recorded verbatim rather than summarised.

```text
docker run --rm moodify-audit-current:prod python -c "import moodify; print('OK', moodify.__file__)"
→ HEALTHCHECK OK /app/src/moodify/__init__.py       (exit 0)
```

Caveat worth keeping: this "health check" only proves that the *package imports*. It does not touch
the API, the queue, or any route. It would report `healthy` for a container whose web server is dead.
It is also wrong in kind — the image's default command is a long-running API, so the health check
should probe that API.

### Q3 — Does the default `uvicorn moodify.api.main:app` command start?

**YES.** The container reached `Up N seconds (healthy)` and logged:

```text
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started parent process [1]
INFO:     Application startup complete.   (× 4 workers)
```

Worth recording: a static reading of the tree predicted this would fail. The image installs
dependencies from `moodify-core-package/requirements.txt`, which omits `matplotlib`, `jsonschema` and
`PyYAML` that `pyproject.toml` pins. The prediction was wrong — the API imports lazily and starts
cleanly. **Runtime evidence overrides static inference**, and the divergence between the two
dependency lists remains a real latent packaging defect even though it does not bite today.

### Q4 — Does `moodify-api` have a real `/health` route matching Compose?

**YES.** Probed from inside the running container:

```json
{"status":"ok","product":"Moodify","version":"1.0.0-rc.1","identity":"The Ear of AI",
 "queue":{"QUEUED":0,"RUNNING":0,"SUCCEEDED":0,"FAILED":0}}
```

The route exists at `moodify-core-package/src/moodify/api/main.py` (`@app.get("/health")`), with an
alias at `/api/v1/health`, and returns live queue counts. The Compose health check
(`python -c "import httpx; httpx.get('http://localhost:8000/health')"`) targets it correctly and
`httpx` is installed.

### Q5 — Does `python -m moodify.node.cli worker --port 8001` exist and start?

**NO. This is broken.** The `worker` subcommand is declared with **no arguments**:

```python
sub.add_parser("worker")          # node/cli.py
```

while Compose passes `--port 8001`. Runtime proof, both on the host venv and inside the built image:

```text
$ python -m moodify.node.cli worker --port 8001
usage: cli.py [-h] {init,enqueue,jobs,retry,recover,status,health,worker} ...
cli.py: error: unrecognized arguments: --port 8001
EXIT=2
```

Two further defects sit behind that one:

- the worker is a polling loop (`run_forever(config)`), **not** a server — so `ports: 8001:8001` and
  `MOODIFY_WORKER_URL=http://moodify-worker:8001` describe an HTTP endpoint that does not exist;
- `moodify-api` declares `depends_on: moodify-worker`. Because it is the list form, Compose waits only
  for *start*, not health — so `docker compose up` will not hang, but it will run an API in front of a
  worker that has already exited 2.

### Q6 — Does Compose become healthy, or does it encode target behaviour that is not implemented?

It encodes behaviour that is **not implemented**. `docker compose config --quiet` succeeds (with one
warning: the top-level `version:` attribute is obsolete and ignored), so the file is syntactically
valid and will *appear* to work — while `moodify-worker` crash-loops under `restart: unless-stopped`.

Additional host finding relevant to verification: **`127.0.0.1:8000` is already bound** on this node
by the production `moodify-api` systemd unit. Compose publishes `8000:8000`. Any `docker compose up`
on this host will therefore fail to bind; verification must use an override or avoid the published
port. This is an environment fact about the node, not a defect in the Compose file.

### Q7 — Which current Python dependencies require native Linux libraries?

| Dependency | Native requirement | Supplied by |
|---|---|---|
| `numpy`, `scipy` | BLAS/LAPACK, libgfortran | manylinux wheels (self-contained) |
| `soundfile` | **system `libsndfile1`** | `apt-get install libsndfile1` — present ✓ |
| `librosa` | numba/llvmlite release wheels | wheels |
| `pedalboard` | C++/JUCE extension, `libstdc++`/`libgcc` | manylinux wheel |
| `pydantic` | `pydantic-core` Rust extension | wheel |
| `matplotlib` | libfreetype/libpng | wheel |
| `PyYAML` | optional libyaml | wheel |
| `ffmpeg`/`ffprobe` | **system binaries** | `apt-get install ffmpeg` — present ✓ |

The Dockerfile's two explicit system packages (`libsndfile1`, `ffmpeg`) correctly cover the only two
genuinely *system*-level dependencies.

### Q8 — Which desktop runtime paths assume Windows?

Three hard-coded Windows assumptions in `moodify-desktop/src/main.js`:

| Line | Code | Effect on Linux |
|---|---|---|
| 106 | `pty.spawn(process.env.ComSpec \|\| 'powershell.exe', [])` | `ComSpec` unset on Linux → tries to exec `powershell.exe` → **embedded terminal cannot start** |
| 509 | `path.join(VENVS[venvName], 'Scripts', 'python.exe')` | Linux venvs use `bin/python` → path never exists → silent fallback |
| 607 | `path.join(VENVS['basic-pitch'], 'Scripts', 'basic-pitch.exe')` | same |

Line 181 already handles the platform correctly
(`process.platform === 'win32' ? 'codex.exe' : 'codex'`) and is the pattern the other two should follow.

### Q9 — Does `@openai/codex` install its Linux x64 platform package from the current lockfile?

**YES.** The lockfile carries the full platform matrix as optional dependencies:

```text
@openai/codex-linux-x64   version=0.160.0-linux-x64   os=['linux'] cpu=['x64'] optional=true
@openai/codex-darwin-x64  @openai/codex-darwin-arm64
@openai/codex-win32-x64   @openai/codex-win32-arm64   @openai/codex-linux-arm64
```

`npm ci` on Linux will install `@openai/codex-linux-x64` automatically. No packaging change is needed
for the Codex runtime.

### Q10 — How must `node-pty` be compiled for Electron 33 on Linux?

`node-pty@1.1.0` declares `hasInstallScript: true` and `binding.gyp`-based `node-addon-api ^7.1.0`,
with **no `os`/`cpu` restriction** — so it builds from source everywhere. The Windows release sets
`npmRebuild: false` because the package ships a verified Windows x64 prebuild. That shortcut cannot be
assumed for Linux: the native module must be compiled **against Electron 33's ABI**
(`NODE_MODULE_VERSION` for Electron 33), not the host Node 20 ABI that `npm ci` would otherwise build
against. This is proven in the "LINUX NATIVE-MODULE SOLUTION" section below.

---

## LINUX STUDIO ARCHITECTURE

_Pending — completed with the packaging change._

## LINUX NATIVE-MODULE SOLUTION

**Outcome: SOLVED, and verified inside the packaged Electron runtime.**

The Windows release ships `npmRebuild: false` because node-pty 1.1.0 carries a verified Windows x64
prebuild. The first attempt at a Linux equivalent used a CLI override:

```text
electron-builder --linux ... --config.npmRebuild=true
```

That was **abandoned, with evidence**. electron-builder itself reported, on a run without the fix:

```text
• skipped dependencies rebuild  reason=npmRebuild is set to false
```

The override's effect cannot be inspected from the command line, and the failure mode — a package
that builds cleanly and only breaks when the embedded terminal is opened — is exactly the kind of
defect a release acceptance is supposed to catch. `npmRebuild` is a top-level (not per-platform) key,
so flipping it for Linux alone was not available either.

The adopted solution is an explicit, inspectable step built from the toolchain already present:

```json
"rebuild:electron": "electron-builder install-app-deps",
"pack:linux":  "npm run icon:linux && npm run rebuild:electron && electron-builder --linux --x64 --dir",
"dist:linux":  "npm run icon:linux && npm run rebuild:electron && electron-builder --linux AppImage deb --x64"
```

Top-level `npmRebuild` stays `false`, so the verified Windows path is untouched byte-for-byte.

Runtime proof from the build log:

```text
• executing @electron/rebuild  electronVersion=33.4.11 arch=x64 buildFromSource=false
• preparing       moduleName=node-pty arch=x64
• finished        moduleName=node-pty arch=x64
• completed installing native dependencies
```

**Proof the module is built for Electron's ABI, not the host Node ABI.** The host Node is ABI 115;
Electron 33 is ABI 130. Loading the module under the packaged runtime is the only check that
distinguishes them, because a wrong-ABI module fails to load at all:

```text
$ ELECTRON_RUN_AS_NODE=1 ./moodify-desktop /root/linux-release-001/pty_smoke.js
electron  : 33.4.11
node      : 20.18.3
module ABI: 130
pty output: "MOODIFY_PTY_MARKER_42\r\nerr-marker"
exit code : 0
PTY_SMOKE_PASS
```

A real PTY spawned a real `/bin/sh`, the known marker was captured from stdout, a second marker was
captured from stderr, and the child's exit code came back as 0.

## APPIMAGE RESULT + SIZE + SHA256

```text
file    Moodify_Studio_1.0.0-rc.1_Linux_x64.AppImage
bytes   273,613,480
sha256  61503e1827b36b50e475b3e90439e8ffc1c429734719305f44b5a4909cadaad7
```

- `file` → `ELF 64-bit LSB executable, x86-64, … dynamically linked, interpreter
  /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.18, stripped`
- AppImage magic verified at offset 8: bytes `41 49 02` (`AI`, type 2).
- `--appimage-extract` → exit 0, produced a complete `squashfs-root` with `AppRun`.

Naming note: electron-builder renders `${arch}` as `x86_64` for AppImage but `x64` elsewhere, so the
required filename could not be produced from the macro. The Linux artifact name uses a literal `x64`
(RC1 is x64-only); adding ARM later would require per-target names.

## DEB RESULT + SIZE + SHA256

```text
file    Moodify_Studio_1.0.0-rc.1_Linux_amd64.deb
bytes   207,655,196
sha256  bc6272c86a34d93f0048a2833baef0b704b380e95412a47527231c1fc0d596c9
```

`dpkg-deb --info` succeeds — Debian binary package, format 2.0.

```text
Package: moodify-desktop        Version: 1.0.0~rc.1
Architecture: amd64             Installed-Size: 715048
Maintainer: 文川院 / Moodify 声音实验室
Vendor: 文川院 / Moodify 声音实验室
Homepage: https://github.com/huliye24/moodify-ai
Depends: libgtk-3-0, libnotify4, libnss3, libxss1, libxtst6, xdg-utils, libatspi2.0-0, libuuid1, libsecret-1-0
Recommends: libappindicator3-1
Section: default                Priority: optional
```

`Version: 1.0.0~rc.1` is Debian's own normalisation of `1.0.0-rc.1` — `~` sorts before the release,
which is the correct pre-release ordering, not a packaging mistake. `Section: default` is
electron-builder's fallback; the `.desktop` entry carries the real `Categories` value from
`linux.category` (`AudioVideo`).

Desktop entry present at `./usr/share/applications/moodify-desktop.desktop`.

## PACKAGED TREE INSPECTION

`dist-electron/linux-unpacked` = **700 MB**, of which `resources/app/node_modules` = **436 MB**
(dominated by the 289 MB Codex binary).

Every path `src/main.js` resolves at runtime was checked against the real tree:

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

`TOOLS_ROOT` resolves to `resources/app/scripts` — both helper scripts are there.

Codex on Linux:

```text
vendor/x86_64-unknown-linux-musl/bin/codex   ELF 64-bit LSB pie, static-pie linked, 289 MB
$ codex --version  →  codex-cli 0.160.0        (exit 0, non-interactive)
$ codex --help     →  usage text printed       (exit 0)
```

This matches `resolveCodexExe()` in `src/main.js`, which scans `node_modules/@openai/codex-*/vendor`
and selects the `codex` / `codex.exe` leaf by platform — the packaged layout is the one it expects.

`VENVS['basic-pitch']` and `VENVS['score']` resolve to `resources/app/../../.venv-*`, which do not
exist in either the Windows or the Linux package. That is the documented external-runtime boundary,
not a packaging gap: `pyExe()` falls back to the configured interpreter, and the MIDI stage reports
an honest "not found" failure when basic-pitch is absent.

## HEADLESS LAUNCH RESULT

```text
$ xvfb-run -a ./moodify-desktop --no-sandbox --disable-gpu   (30 s timeout)
PROCESS_ALIVE_AFTER_18s = yes
missing-module / crash markers: (none)
```

The unpacked Electron application **starts and stays up** under Xvfb with no `MODULE_NOT_FOUND` and
no crash. Per the task, this proves only that Electron starts and loads — it says nothing about
visual correctness, playback, or usability, and no such claim is made.

`--no-sandbox` was used because the build ran as root in a container-like context; it is a launch
flag for the smoke test, not a change to the product.

## DOCKER IMAGE RESULT + ID + SIZE

_Pending — current-baseline image recorded above for comparison._

## CLI/CORE CONTAINER RESULT

_Pending._

## COMPOSE SERVICE CLASSIFICATION

_Pending._

## SBOM / VULNERABILITY RESULT

_Pending._

## WINDOWS REGRESSION RESULT

_Pending._

## CI RUN LINKS

_Pending._

## KNOWN LIMITATIONS

_Pending._

## HUMAN_DECISION_REQUIRED ITEMS

_Pending._

## HUMAN_CHECK_REQUIRED

```text
HUMAN_CHECK_REQUIRED
```

## RECOMMENDATION

_Pending._
