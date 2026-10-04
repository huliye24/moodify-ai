# MOODIFY_DESKTOP_LOCAL_ACCEPTANCE_001.md

> **Repository:** `huliye24/moodify-ai`
> **Executor:** DeepSeek on the owner's Windows computer
> **Scope:** Moodify Studio 1.0.0-rc.1 local installation and functional acceptance
> **PR:** `#38` — Desktop release 001 — Windows RC packaging
> **Workflow run:** `37131909433`
> **Rule:** Test the exact CI artifacts already downloaded locally. Do not merge or tag.

## 0. Objective

Perform the required local Windows acceptance for Moodify Studio 1.0.0-rc.1:

```text
integrity
→ installer
→ installed launch
→ real audio
→ Detect
→ Diagnose
→ quick separation
→ restart
→ portable launch
→ uninstall
```

Automate objective checks. Ask the human owner only for actions or judgments that genuinely require visible UI interaction or listening.

`CANON_CHANGE = NO`

## 1. Safety and authority

Do not:

- merge PR #36, #37, or #38;
- create or push `desktop-v1.0.0-rc.1`;
- publish a GitHub Release;
- change application code, Core DSP, presets, pipeline gates, Canon, Android, or Cloud Node;
- commit EXEs, audio, screenshots, logs, generated artifacts, or private paths;
- delete user audio or existing Moodify evidence;
- install model weights or unrelated dependencies merely to force a pass;
- describe automated signal checks as human listening approval.

If a defect is found, preserve evidence and report it. Do not silently patch the product during acceptance.

## 2. Local authority paths

Repository worktree:

```text
E:\moodify-codex-release
```

Downloaded Windows Actions artifact:

```text
E:\moodify-release-ci-37131909433
```

Expected files:

```text
E:\moodify-release-ci-37131909433\Moodify_Studio_1.0.0-rc.1_Setup_x64.exe
E:\moodify-release-ci-37131909433\Moodify_Studio_1.0.0-rc.1_Portable_x64.exe
E:\moodify-release-ci-37131909433\RELEASE_MANIFEST.json
E:\moodify-release-ci-37131909433\SHA256SUMS.txt
```

Expected CI identity:

```text
PR head: 368dc687c8c1ec8314e2c32be70e971fd1d94f80
CI merge commit: 466f42bab20b02dee743cafc9efeb6ccd32cac93
```

## 3. Start with a clean acceptance record

Create a new timestamped directory outside the Git repository, for example:

```powershell
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$AcceptanceRoot = "E:\moodify-local-acceptance-$Stamp"
New-Item -ItemType Directory -Path $AcceptanceRoot | Out-Null
New-Item -ItemType Directory -Path (Join-Path $AcceptanceRoot "screenshots") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $AcceptanceRoot "logs") | Out-Null
```

Record the exact path. Do not reuse an old result directory.

Before installing, record:

- Windows edition, version, and build;
- x64 architecture;
- current user type without exposing the username;
- available disk space;
- existing Moodify Studio installation, if any;
- active Python, Moodify Core, FFmpeg, FFprobe, Basic Pitch, and music21 status.

## 4. Artifact integrity — mandatory

Expected values:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `Moodify_Studio_1.0.0-rc.1_Setup_x64.exe` | 190,267,613 | `2cf5ff420b8e574acddeb3ca1be8d949e1b7dd3f998627f7d8b10588b42a41be` |
| `Moodify_Studio_1.0.0-rc.1_Portable_x64.exe` | 190,036,032 | `018bfbf3d6ac01a57012b35704aebcbf6c9f94d98fe714e14ba1b75ba231039a` |
| `RELEASE_MANIFEST.json` | 650 | `79d75795fd315c6ec82f0a74c83dca93f311424318bbe4a64b8420b8f970eaa0` |

Verify:

1. all four files exist;
2. both EXEs begin with `MZ`;
3. actual byte sizes match;
4. actual SHA-256 hashes match the table;
5. every entry in `SHA256SUMS.txt` recalculates correctly;
6. the manifest parses as JSON;
7. manifest product/version/platform/arch/channel/runtime/signing values are correct;
8. `Get-AuthenticodeSignature` reports `NotSigned`, matching the documented RC boundary.

Manifest authority:

```text
product = Moodify Studio
version = 1.0.0-rc.1
commit = 466f42bab20b02dee743cafc9efeb6ccd32cac93
platform = windows
arch = x64
channel = rc
code_signed = false
runtime_mode = external
```

On any mismatch, classify `FAIL_ARTIFACT_INTEGRITY`, stop, and do not launch the EXEs.

## 5. Local runtime inventory

Run and record exact results:

```powershell
python --version
python -c "import moodify; print(moodify.__file__)"
python -m moodify.release_cli --help
ffmpeg -version
ffprobe -version
python -c "import basic_pitch; print('basic_pitch available')"
python -c "import music21; print('music21 available')"
```

Interpret honestly:

- Python 3.10–3.12, Moodify Core 1.0.0-rc.1, FFmpeg and FFprobe support the expected full runtime.
- Basic Pitch and music21 are optional.
- Missing optional dependencies do not fail the shell release.
- A missing required external component blocks only the dependent functional stage; record `BLOCKED_EXTERNAL_RUNTIME` rather than inventing success.

Do not print API keys, tokens, environment-variable values, or private configuration.

## 6. Install the Setup build

Ensure no old Moodify Studio process is running. If another version is installed, record it before making any change.

Launch interactively:

```powershell
Start-Process -FilePath "E:\moodify-release-ci-37131909433\Moodify_Studio_1.0.0-rc.1_Setup_x64.exe"
```

The normal installer UI must be used. Do not substitute a silent install because the installer interface itself is part of acceptance.

Verify with screenshots or observable evidence:

1. the installer opens;
2. Windows may show unsigned or Unknown publisher, as documented;
3. the installer identifies the product as Moodify Studio;
4. installation directory selection is available;
5. installation completes without error;
6. Start Menu entry exists;
7. desktop shortcut exists if selected;
8. uninstall entry exists;
9. installed executable exists and is non-zero.

If DeepSeek cannot click the native installer UI, ask the human to complete only those clicks, then continue verifying the resulting state. Do not claim a pass from process launch alone.

## 7. Installed launch and visual check

Launch the installed application using its Start Menu entry or resolved installed executable.

Verify:

- one main window opens;
- title/product identity is Moodify Studio;
- Moodify icon renders;
- interface is not blank or visibly corrupted;
- renderer loads without an immediate crash;
- no missing-file dialog appears;
- the process remains alive long enough for interaction;
- closing the window exits normally.

Collect relevant application logs and one screenshot of the main window. Redact private information.

## 8. Choose authorized real audio

Ask the human owner to select one non-sensitive audio file for this acceptance. Do not crawl unrelated personal directories looking for music.

Before use, record only:

- redacted filename or test identifier;
- extension;
- byte size;
- SHA-256;
- duration, sample rate, bit depth when available;
- channel count.

Do not copy the audio into Git or upload it.

## 9. Functional production-flow check

Open the authorized audio in the installed Studio and test in order.

### 9.1 Detect

- Run Detect.
- Confirm the operation completes or produces an explicit failure state.
- Locate the real Core report/evidence path.
- Confirm the UI is not showing invented measurements.

### 9.2 Diagnose

- Run Diagnose.
- Confirm issues map to actual Core report evidence.
- If `issues: []`, confirm the UI says only that current rules found no technical issue, not that the song has no problem.
- Confirm `preserve` remains human judgment rather than an invented default.

### 9.3 Quick separation

- Run quick separation.
- Confirm actual output/stem artifacts or an explicit dependency failure.
- Confirm the UI preserves the `PREVIEW_NOT_MASTERING_GRADE` boundary.
- Do not describe this as production-grade neural separation.

### 9.4 Deeper stages when available

If Basic Pitch, music21, and the required external runtime are available, continue:

```text
Separate → MIDI → Plan → Finish
```

Verify the canonical gates:

- Plan is locked until stems and MIDI both exist;
- MusicXML alone cannot substitute for MIDI;
- deep Finish requires a written plan artifact;
- quick stereo finish requires explicit human opt-in;
- quick finish does not unlock Plan;
- mode labels remain `深度完成` or `快速（仅立体声）`.

Do not bypass a gate to force completion.

## 10. Human listening checkpoint

When input and output audio can be played, ask the human owner to confirm:

```text
1. Input playback is audible and free of obvious transport glitches.
2. Preview/separation playback is audible.
3. A/B switching corresponds to the expected files.
4. There is no obvious channel swap, truncation, silence, severe clipping, or speed error.
5. Whether the result is acceptable for RC review.
```

Record the human response exactly as one of:

```text
HUMAN_LISTENING_PASS
HUMAN_LISTENING_FAIL
HUMAN_LISTENING_INCONCLUSIVE
HUMAN_LISTENING_NOT_PERFORMED
```

Do not convert automated loudness or waveform measurements into `HUMAN_LISTENING_PASS`.

## 11. Restart persistence

1. Close Moodify Studio normally.
2. Confirm the process exits.
3. Reopen the installed application.
4. Confirm it remains launchable and the main interface renders.
5. Record whether recent case/session state behaves as designed; do not call missing persistence a bug unless the current product contract requires it.

## 12. Portable build

Close the installed application, then launch:

```powershell
Start-Process -FilePath "E:\moodify-release-ci-37131909433\Moodify_Studio_1.0.0-rc.1_Portable_x64.exe"
```

Verify:

- the portable EXE launches without using the installed shortcut;
- main window and icon render;
- the same authorized audio can be opened;
- Detect runs when the external runtime is available;
- no packaged runtime file is reported missing;
- closing exits normally.

Record any behavioral difference between installed and portable builds.

## 13. Uninstall

After closing both builds:

1. locate the registered Moodify Studio uninstaller;
2. use the normal Windows uninstall UI;
3. confirm uninstall completion;
4. confirm installed executable and shortcuts are removed;
5. confirm the portable EXE remains independent;
6. do not delete user audio, Core evidence, Python environments, or unrelated Moodify workspaces;
7. distinguish retained user data from failed uninstall residue.

If DeepSeek cannot operate the native uninstall UI, ask the human to perform the clicks and then verify the filesystem and registry result.

## 14. Evidence package

Keep all evidence in the timestamped acceptance directory outside Git:

```text
environment.txt
artifact_integrity.txt
manifest_copy.json
runtime_inventory.txt
installer.md
installed_launch.md
functional_flow.md
listening_confirmation.md
portable.md
uninstall.md
screenshots/
logs/
```

Redact:

- usernames and unnecessary personal paths;
- API keys and tokens;
- private audio names and metadata;
- unrelated application or desktop content.

## 15. Result classification

Use exactly one technical result:

```text
PASS_LOCAL_ACCEPTANCE
PASS_SHELL_ONLY_EXTERNAL_RUNTIME_BLOCKED
FAIL_ARTIFACT_INTEGRITY
FAIL_INSTALLER
FAIL_INSTALLED_LAUNCH
FAIL_FUNCTIONAL_PIPELINE
FAIL_PORTABLE_LAUNCH
FAIL_UNINSTALL
BLOCKED_EXTERNAL_RUNTIME
BLOCKED_UI_INTERACTION
```

`PASS_LOCAL_ACCEPTANCE` requires:

- artifact integrity pass;
- installer pass;
- installed launch pass;
- Detect and Diagnose pass;
- quick separation pass or an explicitly accepted external-runtime boundary;
- restart pass;
- portable launch pass;
- uninstall pass;
- an explicit human listening status.

## 16. Required final report

Return one Markdown report containing:

```text
EXECUTIVE RESULT
ARTIFACT INTEGRITY
LOCAL ENVIRONMENT
INSTALLER
INSTALLED LAUNCH
REAL AUDIO IDENTITY
DETECT
DIAGNOSE
QUICK SEPARATION
OPTIONAL DEEP FLOW
HUMAN LISTENING STATUS
RESTART
PORTABLE
UNINSTALL
EVIDENCE DIRECTORY
FAILURES / BLOCKERS
RECOMMENDATION
```

The recommendation must be exactly one of:

```text
READY_FOR_PR_REVIEW
NOT_READY — FIX_REQUIRED
INCONCLUSIVE — HUMAN_ACTION_REQUIRED
```

For any failure, include the exact action, error, log/screenshot path, classification, and smallest recommended next step.

## 17. Release gate remains closed

Completing this task does not authorize merge or release.

Do not create `desktop-v1.0.0-rc.1` until the human owner confirms:

```text
PR #36 merged
PR #37 merged
PR #38 merged
manual Windows launch/listening check passed
```

DeepSeek supplies execution evidence. The human owner retains listening, merge, and release authority.
