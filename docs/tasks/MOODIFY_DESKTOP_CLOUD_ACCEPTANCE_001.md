# MOODIFY_DESKTOP_CLOUD_ACCEPTANCE_001.md

> **Repository:** `huliye24/moodify-ai`
> **Executor:** DeepSeek on the cloud verification server
> **Scope:** Moodify Studio 1.0.0-rc.1 Windows artifact acceptance
> **PR:** `#38` — Desktop release 001 — Windows RC packaging
> **Workflow run:** `37131909433`
> **Rule:** Test the existing release artifact. Do not change product logic, merge PRs, or create a release tag.

## 0. Objective

Verify that the Windows artifacts produced by PR #38 can be downloaded, authenticated by hash, installed or launched, and exercised against the existing external Moodify runtime.

This cloud test is useful for reproducible installation and runtime verification, but it does **not** replace human listening judgment. The final perceptual decision remains:

```text
HUMAN_CHECK_REQUIRED
```

`CANON_CHANGE = NO`

## 1. Hard safety boundaries

Do not:

- merge PR #36, #37, or #38;
- create or push `desktop-v1.0.0-rc.1`;
- publish or edit a GitHub Release;
- change Core DSP, Studio workflow semantics, presets, Android, Cloud Node, or product Canon;
- commit EXE files or generated test output to Git;
- upload private audio unless the owner explicitly approved that exact file;
- install model weights, Demucs, a new Python distribution, or unrelated system services;
- claim listening quality from automated checks or from a server without a usable audio path.

If a packaging defect is found, stop after collecting evidence. Do not make a broad product fix inside this acceptance task.

## 2. Required environment

This task requires a genuine interactive Windows x64 environment:

- Windows 10/11 x64 or Windows Server with Desktop Experience;
- an active interactive RDP/console session;
- permission to install and uninstall a per-user NSIS application;
- enough free disk space for the approximately 380 MB Actions artifact and unpacked application;
- GitHub CLI authentication or another authorized way to download private Actions artifacts;
- a usable audio output path if playback is to be checked;
- for the full pipeline: Python 3.10–3.12, Moodify Core 1.0.0-rc.1, and FFmpeg/FFprobe;
- optionally Basic Pitch for MIDI and music21 for MusicXML/score.

If the server is Linux, headless-only, or has no interactive Windows desktop, report:

```text
BLOCKED_WRONG_ENVIRONMENT
```

Do not substitute Wine or Linux cross-compilation for Windows acceptance.

## 3. Artifact authority

Use only the artifact from:

```text
repository: huliye24/moodify-ai
workflow run: 37131909433
artifact id: 11277277129
artifact name: moodify-studio-466f42bab20b02dee743cafc9efeb6ccd32cac93-windows-x64
PR head commit: 368dc687c8c1ec8314e2c32be70e971fd1d94f80
CI merge commit recorded in manifest: 466f42bab20b02dee743cafc9efeb6ccd32cac93
```

Expected contents:

```text
Moodify_Studio_1.0.0-rc.1_Setup_x64.exe
Moodify_Studio_1.0.0-rc.1_Portable_x64.exe
RELEASE_MANIFEST.json
SHA256SUMS.txt
```

Expected CI values:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Setup EXE | 190,267,613 | `2cf5ff420b8e574acddeb3ca1be8d949e1b7dd3f998627f7d8b10588b42a41be` |
| Portable EXE | 190,036,032 | `018bfbf3d6ac01a57012b35704aebcbf6c9f94d98fe714e14ba1b75ba231039a` |
| Manifest | 650 | `79d75795fd315c6ec82f0a74c83dca93f311424318bbe4a64b8420b8f970eaa0` |

The Actions archive itself has digest:

```text
sha256:6fb36a3a9ebd0add68ca3ee3440ee56fb00b0b87d584f8f2293c7cb08347e989
```

## 4. Download

Use a new temporary directory outside the repository. Do not place binaries in the Git worktree.

Example:

```powershell
$AcceptanceRoot = Join-Path $env:TEMP "moodify-studio-rc1-acceptance"
if (Test-Path -LiteralPath $AcceptanceRoot) {
    throw "Acceptance directory already exists; inspect it before choosing a new path: $AcceptanceRoot"
}
New-Item -ItemType Directory -Path $AcceptanceRoot | Out-Null

gh run download 37131909433 `
  --repo huliye24/moodify-ai `
  --name moodify-studio-466f42bab20b02dee743cafc9efeb6ccd32cac93-windows-x64 `
  --dir $AcceptanceRoot
```

Record the actual download directory.

## 5. Integrity verification

Perform all checks before launching either EXE.

1. Confirm all four expected files exist.
2. Confirm the two EXEs are non-empty.
3. Confirm the first two bytes of both EXEs are `MZ`.
4. Recalculate SHA-256 with `Get-FileHash -Algorithm SHA256`.
5. Verify every line of `SHA256SUMS.txt` against the actual files.
6. Parse `RELEASE_MANIFEST.json` and verify:

```text
product = Moodify Studio
version = 1.0.0-rc.1
platform = windows
arch = x64
channel = rc
code_signed = false
runtime_mode = external
commit = 466f42bab20b02dee743cafc9efeb6ccd32cac93
```

7. Run `Get-AuthenticodeSignature` on both EXEs. Expected state is `NotSigned`.

Any hash, size, manifest, or PE mismatch is:

```text
FAIL_ARTIFACT_INTEGRITY
```

Stop without launching the artifact and preserve the evidence.

## 6. Environment inventory

Record, without inventing missing capabilities:

```powershell
[System.Environment]::OSVersion.VersionString
$env:PROCESSOR_ARCHITECTURE
python --version
python -c "import moodify; print(moodify.__file__)"
ffmpeg -version
ffprobe -version
```

Also test optional dependencies separately:

```powershell
python -c "import basic_pitch; print('basic_pitch available')"
python -c "import music21; print('music21 available')"
```

Missing optional dependencies are not a release failure. Missing required external runtime components must be recorded as:

```text
BLOCKED_EXTERNAL_RUNTIME
```

Do not conceal the missing component and do not claim the affected pipeline stage passed.

## 7. Setup installer acceptance

Run the installer from the interactive desktop.

Verify and capture evidence for:

1. Windows opens the installer.
2. SmartScreen or the installer reports an unsigned/Unknown publisher boundary as expected.
3. Normal installer UI appears.
4. Installation directory can be selected.
5. Installation completes without an installer error.
6. Start Menu entry exists.
7. Desktop shortcut exists when selected.
8. Uninstall entry exists in Windows Apps/registry.
9. Installed Moodify Studio launches and shows its main window.
10. The application icon and primary interface render visibly.

Do not treat the expected unsigned warning as a failure. A crash, missing main window, missing packaged file, or installer error is a failure.

## 8. Functional Studio acceptance

Use a non-private test audio file that is already authorized for this server. Record its filename, duration, format, sample rate, channel count, and SHA-256. Do not commit or upload the audio.

Exercise only what the environment actually supports:

1. Open the real audio file.
2. Run **Detect**.
3. Confirm a real Core report/evidence artifact is produced or located.
4. Run **Diagnose**.
5. Confirm diagnosis is a projection of Core evidence and does not invent facts.
6. Run quick separation.
7. Confirm the UI labels the result as preview-grade and does not claim mastering-grade separation.
8. Confirm failure states are visible if an external dependency is unavailable.
9. Close Moodify Studio normally.
10. Reopen it and confirm the application remains launchable.

If the complete external runtime is available, also attempt:

```text
Detect → Diagnose → Separate → MIDI → Plan → Finish
```

Preserve the authoritative workflow rules:

- deep Plan remains locked until stems and MIDI exist;
- MusicXML does not substitute for MIDI;
- deep Finish requires a written plan artifact;
- quick stereo finish requires explicit human opt-in;
- quick finish does not unlock Plan;
- AI plans, Core executes, human decides.

Do not change a lock or bypass a stage just to make the test pass.

## 9. Portable acceptance

After closing the installed application:

1. Launch `Moodify_Studio_1.0.0-rc.1_Portable_x64.exe`.
2. Confirm the main window and icon render.
3. Open the same authorized audio file.
4. Run Detect if the external runtime is available.
5. Confirm the portable build does not require the installed Start Menu shortcut.
6. Close it normally.

Record whether installer and portable behavior differ.

## 10. Uninstall and residue check

1. Uninstall the installed Moodify Studio through the normal Windows uninstall path.
2. Confirm the uninstall completes.
3. Confirm the installed executable and shortcuts are removed.
4. Do not delete user audio, Core evidence, or unrelated runtime data.
5. Record any application residue; distinguish harmless user data from failed uninstall residue.

## 11. Evidence to collect

Create a timestamped acceptance folder outside Git containing:

```text
environment.txt
artifact_hashes.txt
manifest_copy.json
install_notes.md
functional_notes.md
portable_notes.md
uninstall_notes.md
screenshots/
logs/
```

Screenshots should cover:

- unsigned/Unknown publisher boundary;
- installer UI;
- installed Studio main window;
- loaded audio;
- Detect result;
- Diagnose result;
- separation result or honest dependency failure;
- portable main window;
- uninstall completion.

Redact usernames, tokens, private paths, private audio titles, and secrets before sharing evidence.

## 12. Result classification

Use exactly one primary outcome:

```text
PASS_CLOUD_ACCEPTANCE
PASS_SHELL_ONLY_EXTERNAL_RUNTIME_BLOCKED
BLOCKED_WRONG_ENVIRONMENT
BLOCKED_EXTERNAL_RUNTIME
FAIL_ARTIFACT_INTEGRITY
FAIL_INSTALLER
FAIL_INSTALLED_LAUNCH
FAIL_PORTABLE_LAUNCH
FAIL_FUNCTIONAL_PIPELINE
FAIL_UNINSTALL
```

`PASS_CLOUD_ACCEPTANCE` requires integrity, installer, installed launch, available functional stages, portable launch, and uninstall to pass. It still does not replace human perceptual review.

## 13. Required final report

Return one Markdown report with:

```text
EXECUTIVE RESULT
SERVER ENVIRONMENT
ARTIFACT SOURCE
HASH AND MANIFEST VERIFICATION
INSTALLER RESULT
INSTALLED LAUNCH RESULT
FUNCTIONAL PIPELINE RESULT
PORTABLE RESULT
UNINSTALL RESULT
EXTERNAL RUNTIME INVENTORY
EVIDENCE PATHS
FAILURES / BLOCKERS
HUMAN_CHECK_REQUIRED
RECOMMENDATION: READY_FOR_HUMAN_REVIEW or NOT_READY
```

For every failed or blocked stage, include:

- exact command or action;
- exit code when applicable;
- concise error excerpt;
- screenshot/log path;
- whether the cause is packaging, external runtime, environment, or unknown;
- the smallest recommended next action.

Do not write “all passed” if only file existence was checked.

## 14. Release gate after cloud testing

Even if this task passes, do **not** merge or tag automatically.

The release tag remains forbidden until a human confirms all four conditions:

```text
PR #36 merged
PR #37 merged
PR #38 merged
manual Windows launch/listening check passed
```

Cloud acceptance provides repeatable technical evidence. The human retains release authority and listening judgment.
