# LINUX_STUDIO_HOTFIX_RECONCILE_001

**Date:** 2026-10-04
**Branch:** `cloud/linux-docker-release-001`
**Executor:** cloud build node `yisu-6a7bcb73aac20` / `103.144.246.242` (Ubuntu 22.04.2, headless Linux x64)

---

## Summary

The Linux Studio branch was reconciled with HOTFIX 000's runtime-safety semantics. Linux Studio now
satisfies both requirements at once: a missing dedicated runtime fails explicitly with
`DEPENDENCY_MISSING` and never falls back to a generic interpreter, **and** dedicated venvs are found
on POSIX at all.

Two defects were introduced by the naive combination and are fixed here:

1. **The forbidden fallback was still present on the Linux side.** The branch carried
   `return fs.existsSync(exe) ? exe : PYTHON;` inside `pyExe()`. On Linux that would have run the
   separation/MIDI chain on the system interpreter and surfaced a librosa/sklearn/pandas ABI
   traceback instead of "dependency missing" — the exact defect HOTFIX 000 exists to remove.
   `pyExe()` was deleted rather than adapted.

2. **HOTFIX 000's runtime table hardcoded Windows layouts** (`Scripts/python.exe`,
   `Scripts/basic-pitch.exe`). Left as-is, every real Linux venv would have looked absent, turning a
   *present* runtime into a false `DEPENDENCY_MISSING` — the mirror-image failure. The layout is now
   derived once from `process.platform`.

A third problem was repaired because it would have hidden the second: `test-runtime.js` created
`Scripts/python.exe` fixtures and asserted against the same paths, so the suite would have passed on
Linux while the resolver was wrong in the field — **a green test asserting the bug**.

No Docker, worker, Project Model, CLI 2.0, Sound Protocol 0.3, GUI or DSP work was performed.

---

## Integration Method

**Merge** (not rebase, not cherry-pick), per task §4: the Linux branch had already been pushed, so
its published history was not rewritten.

```text
merge commit      4ea6122a  "Merge HOTFIX 000 into the Linux Studio branch"
branch merged     codex/hotfix-000-measurement-correctness
commits merged    ca0c4805  fix(auditory): correct stereo loudness and channel-domain metrics (HOTFIX 000)
                  d6fc1921  docs(reports): add the HOTFIX 000 implementation report
                  d6e3e8ed  docs(auditory): correct the stated 44.1 kHz K-weighting error
                  f9c7e348  docs(reports): add the HOTFIX 000 final-cleanup report
```

**Repository state differed from the task brief and is recorded as found:**

| Brief said | Actual |
|---|---|
| hotfix branch `codex/hotfix-000-measurement-correctness` | exists, but **local-only** (never pushed). Checked out at `E:\moodify-local`. |
| hotfix commit `ca0c4805…` | correct, and it is the **oldest** of four; the branch head is `f9c7e348`. |
| Linux branch point `codex/desktop-release-001 @ 06dce343` | that was the head when this work began; PR #38 has since advanced to **`54d77b0a`**. The Linux branch is still based on `06dce343`. |

Merge base of the two lines: `01edc902` (`origin/main`), the same point PR #38 branched from.

The hotfix carries Core measurement changes alongside its desktop runtime work, so PR A's diff
includes them. They are **integration, not new development** — no Core algorithm was written or
modified in this task. Flagged as a review consideration below.

---

## Runtime Semantics

Final behaviour, verified on Linux:

| Path | Behaviour |
|---|---|
| **generic Core** | `MOODIFY_PYTHON` if set, else `python` on Windows / `python3` on POSIX. Used by `runPython()`, the `env` IPC probe, and the pipeline. Unchanged by reconciliation. |
| **basic-pitch** | Resolved from `MOODIFY_VENV_BASIC_PITCH`, else `<repo>/.venv-basic-pitch`; entry point `<dir>/bin/python`, tool `<dir>/bin/basic-pitch` (POSIX) or `Scripts\*.exe` (Windows). |
| **score** | Resolved from `MOODIFY_VENV_SCORE`, else `<repo>/.venv-score`; entry point `bin/python` / `Scripts\python.exe`. |
| **missing dedicated runtime** | `RuntimeMissingError`, `code: "DEPENDENCY_MISSING"`, `runtime: "<name>"`, candidate directories listed. **No executable is returned and no child process is spawned.** |
| **environment overrides** | Explicit and validated: the override names the *same* dedicated venv, and it is still required to exist. An override is not a licence to substitute an arbitrary interpreter. |

The two questions are kept structurally separate: *which OS layout does a venv use* (answered
per-platform) and *may a missing dedicated runtime fall back to a generic interpreter* (always no).
Conflating them is what produced the silent fallback on Linux.

`python3` is used **only** for the generic Core interpreter. It never substitutes for a
capability-specific runtime.

---

## Files Changed

Reconciliation-specific:

```text
moodify-desktop/src/main.js               merged: hotfix contract kept, pyExe() deleted
moodify-desktop/src/runtime.js            NEW from hotfix, then platform-aware layout
moodify-desktop/scripts/test-runtime.js   NEW from hotfix, then platform-aware fixtures + 3 checks
moodify-desktop/package.json              merged: hotfix test script + Linux targets kept
```

Carried in by the merge (not authored here): `moodify-core-package/src/moodify/auditory/loudness.py`,
`…/metrics.py`, `tests/auditory/test_measurement_channel_domain.py`,
`tests/auditory/test_measurement_correctness.py`, `docs/HOTFIX_000_MEASUREMENT_CORRECTNESS.md`,
`docs/reports/2026-10-04_HOTFIX_000_*.md`.

No file was changed in Docker, worker, Project Model, CLI, Sound Protocol, GUI or DSP.

---

## Linux Tests

Run on the cloud node after the merge:

```text
$ node scripts/check-contracts.js
✓ Studio 合约检查通过（DOM id 126 · 桥接 54 · IPC 52 · 事件 5）        exit 0

$ node scripts/test-pipeline.js
33 passed, 0 failed                                                   exit 0

$ node scripts/test-studio.js
21 passed, 0 failed                                                   exit 0

$ node scripts/test-runtime.js
all runtime checks passed                                             exit 0
```

Baselines match the previously verified ones exactly (Studio 21, Pipeline 33). The runtime suite grew
**12 → 15**; the three additions are described under Runtime Negative Test.

Same four suites on Windows: contracts pass, pipeline 33/33, studio 21/21, runtime 15/15.

---

## Runtime Negative Test

**What was tested:** the resolver itself, and the resolver *as it ships in the package*.

Resolver level, on Linux, with no dedicated venv present:

```text
basic-pitch -> {"ok":false,"code":"DEPENDENCY_MISSING","runtime":"basic-pitch",
                "reason":"缺少必需的 Moodify 外部运行时：basic-pitch（…）",
                "candidates":["/root/linux-release-001/repo/.venv-basic-pitch"]}
NEG_PASS basic-pitch
score       -> {"ok":false,"code":"DEPENDENCY_MISSING","runtime":"score", …}
NEG_PASS score
```

Each run asserts, and would fail on: `ok` true, a wrong code, a result carrying `exe`, or the failure
serialising any `python`/`python3` token.

**Packaged level** (§23) — the real resolver that ships inside `resources/app`, run under the packaged
Electron, no env override, `.venv-*` absent:

```text
runtime "basic-pitch"
  declared dir exists : false
  result              : {"ok":false,"code":"DEPENDENCY_MISSING",…}
  ok   DEPENDENCY_MISSING, no executable, no generic interpreter
runtime "score"
  ok   DEPENDENCY_MISSING, no executable, no generic interpreter
RUNTIME_FAIL_SMOKE_PASS
```

The failure is a structured result, not a deep import/ABI traceback, and no `python3` is spawned.

Two of the three new unit checks target exactly this:

- *absent runtime fails with DEPENDENCY_MISSING and no executable, deterministically* — uses a
  provably-absent candidate so the outcome does not depend on what is installed on the machine;
- *default candidates never fall back to a system interpreter* — every candidate is an absolute
  directory, none names an interpreter, and the entry point stays venv-relative.

---

## Runtime Positive Test

A temporary fixture venv, built on the host's real conventions, with no Basic Pitch installed:

```text
resolved python: /tmp/mfy-pos-Oybbl1/bin/python
resolved tool  : /tmp/mfy-pos-Oybbl1/bin/basic-pitch
POS_PASS
```

The fixture created `bin/python` and `bin/basic-pitch` — POSIX layout — and the resolver found both.
This is the check that would have failed before the layout fix: the old table only ever looked in
`Scripts\`.

No Basic Pitch or music21 was installed on the build machine to satisfy this task.

---

## Linux Artifacts

Rebuilt after reconciliation; sizes changed from the pre-reconciliation build, as expected.

```text
Moodify_Studio_1.0.0-rc.1_Linux_x64.AppImage
  bytes   273,617,598
  sha256  c5d8a67dbff9efdcaf69da147de43f99c07acf074e30cb06cf2447e74cd272ff
  ELF 64-bit LSB executable, x86-64; AppImage magic 41 49 02 at offset 8

Moodify_Studio_1.0.0-rc.1_Linux_amd64.deb
  bytes   207,657,700
  sha256  a5a3b1620ae65fd93691e9631f30380a3928225eee350a39c62bb8985a9af3dc
  Debian binary package, format 2.0
```

deb identity unchanged: `Package: moodify-desktop`, `Version: 1.0.0~rc.1`, `Architecture: amd64`,
Maintainer/Homepage intact.

Packaged tree inspection — every runtime path `src/main.js` resolves is present:

```text
PRESENT  package.json                 PRESENT  renderer/index.html
PRESENT  src/main.js                  PRESENT  renderer/assets/icon.png
PRESENT  src/runtime.js               PRESENT  scripts/dsp_separate.py
PRESENT  src/preload.js               PRESENT  scripts/midi_to_musicxml.py
PRESENT  node_modules/node-pty/build/Release/pty.node
PRESENT  @openai/codex-linux-x64/…/bin/codex   (289 MB, static-pie)
```

Two things a reader should not misread:

- `scripts/test-runtime.js` is **not** in the package, and that is correct — `build.files` lists only
  the two Python helper scripts. Test scripts are not shipped.
- A grep for the forbidden pattern in the packaged `src/` matches **only a comment** in `runtime.js`
  that documents the removed implementation. With comment lines excluded there is **no code match**.
  The stale-fallback grep was run this way deliberately, because a naive grep reports a hit on the
  comment and would have been a false finding.

`resources/.venv-*` is absent, which is the documented external-runtime boundary, not a packaging gap.

---

## PTY Smoke

Same test as the pre-reconciliation verification, re-run against the rebuilt package:

```text
electron   : 33.4.11
node       : 20.18.3
module ABI : 130            (host Node on this machine is ABI 115)
pty output : "MOODIFY_PTY_MARKER_42\r\nerr-marker"
exit code  : 0
PTY_SMOKE_PASS
```

A real PTY spawned a real `/bin/sh`, the stdout marker and the stderr marker were both captured, and
the child exited 0. ABI 130 proves the module was built for Electron, not for the host Node.

`electron-builder install-app-deps` remains the packaging step; the build log still reports
`skipped dependencies rebuild reason=npmRebuild is set to false` for the packaging pass itself, with
the rebuild having already been done explicitly before it.

---

## Headless Smoke

```text
$ timeout 30 xvfb-run -a ./moodify-desktop --no-sandbox --disable-gpu
PROCESS_ALIVE_AFTER_18s = yes
missing-module / crash markers: (none)
```

No `MODULE_NOT_FOUND`, no crash. `--no-sandbox` is a smoke-launch flag for a root build context, not
a product change.

This proves Electron starts and loads. It does **not** prove visual correctness, audio quality,
playback correctness or human usability, and no such claim is made.

---

## Windows Regression

**Local** (Windows host, after the merge):

```text
contracts  pass
pipeline   33/33
studio     21/21
runtime    15/15
```

**CI** — PR #39 checks:

```text
windows-x64                            pass   2m33s
Studio contracts and processing chain  pass   49s
Python 3.11 quality and tests          pass   4m6s
Repository structure guard             pass   11s
temporal-texture                       fail   10s   ← PRE-EXISTING, NOT CAUSED BY THIS BRANCH
```

The Windows desktop-release job is **green**, so the shared-configuration change did not regress
Windows packaging.

**The `temporal-texture` failure is pre-existing and repo-wide.** It failed on the **12 previous
consecutive PR runs** across unrelated branches — `codex/desktop-release-001`,
`codex/repository-cleanup-001`, `deepseek/cloud-node-001`, `deepseek/studio-pipeline-realignment` —
going back to 2026-10-03T12:22, and it has **never run on `main`**. Its output is a baseline-drift
report (`{"new": 214, "new_errors": 21, "new_warnings": 97, "resolved": 192}`), not a failure of this
branch's tests. It is not fixed here: it is outside this task's scope and was failing before it.

The Windows release artifacts were **not** re-verified — the EXEs have not been rebuilt or
hash-checked since `06dce343`, and this PR does not claim otherwise.

---

## PR

```text
PR A   #39  Linux release 001 — Studio AppImage and deb
       https://github.com/huliye24/moodify-ai/pull/39
       base: codex/desktop-release-001   (stacked; retarget to main once #38 merges)
       head: cloud/linux-docker-release-001
```

Contains only PR A. No Docker work is included (task §25/§26).

---

## Deferred

Intentionally outside this task, not fixed here:

1. **Docker CLI/Core** — the entire delivery line. Its audit found `moodify-worker`'s Compose command
   broken (`worker --port 8001` → exit 2), the worker not being an HTTP server at all, a health check
   that only imports the package, an editable install in the production image, and a divergence
   between `requirements.txt` and `pyproject.toml`. All recorded in
   `docs/reports/LINUX_DOCKER_RELEASE_001_2026-10-04.md`; none touched here.
2. **PR B — Container release 001** — not opened, per §25.
3. **`temporal-texture` guard** — pre-existing repo-wide failure, unrelated to this branch.
4. **Windows release artifact re-verification** — the EXEs have not been rebuilt or re-hashed since
   `06dce343`.
5. **`asar`** — still disabled for RC1 (electron-builder warns on every build). Deliberate.
6. **`desktopName` / window association** — electron-builder warns it is unset, so some Linux
   desktops may not link the running window to its `.desktop` entry. Cosmetic.
7. **`.dockerignore`** — authored but deliberately left untracked; it belongs to the Docker task.
8. **HOTFIX 000's own publication.** The hotfix branch is local-only, so those four commits currently
   reach `origin` **only through PR A**. Whether HOTFIX 000 should also be pushed and reviewed
   independently is a decision for the owner — it is a P0 correctness fix that arguably should not
   land as a side effect of a Linux packaging PR.
9. **PR A's diff includes the hotfix's Core measurement changes** for the same reason. Reviewers
   should expect them.

---

## Commit

```text
4ea6122a  Merge HOTFIX 000 into the Linux Studio branch      ← reconciliation
<this report commit>  docs(release): record the HOTFIX 000 reconciliation
```

Pre-merge safety point: `98736ef2` (previous head of the Linux branch).

---

## Acceptance Gate

```text
[x] HOTFIX 000 runtime semantics are present in Linux Studio branch
[x] Linux generic Python resolution still works          (import moodify, exit 0)
[x] Linux dedicated venv paths use POSIX layout          (bin/python, bin/basic-pitch)
[x] missing dedicated runtime returns DEPENDENCY_MISSING (unit + packaged)
[x] no silent fallback to system python/python3 for dedicated runtimes
[x] desktop test suites pass                             (contracts, 33/33, 21/21, 15/15 — both hosts)
[x] Linux AppImage rebuild succeeds
[x] Linux deb rebuild succeeds
[x] node-pty PTY smoke passes in packaged Electron       (ABI 130, exit 0)
[x] Xvfb headless launch smoke passes
[x] packaged runtime failure semantics are verified      (RUNTIME_FAIL_SMOKE_PASS)
[x] Docker was not modified
[x] Project Model was not started
[x] CLI 2.0 was not started
[x] no new GUI feature was added
```

Windows CI: `windows-x64` **pass** on PR #39. The repo-wide `temporal-texture` gate is red but
pre-existing and unrelated.

```text
HUMAN_CHECK_REQUIRED
```

No human has launched the AppImage or installed the deb on a real Linux desktop. The ten-step manual
check in the release task remains outstanding, and no perceptual or usability claim is made.

**STOP.** No Docker, Project Model, CLI 2.0 or Sound Protocol 0.3 work was started. The intended next
product-development task remains TASK 001 — Project Model 0.1.
