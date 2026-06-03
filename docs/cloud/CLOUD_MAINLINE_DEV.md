# Moodify Cloud Mainline Development

Generated: 2026-06-03 UTC

## Directories

- `/home/ubuntu/moodify-o3is`: preserved experimental workspace with the existing dirty tree.
- `/home/ubuntu/moodify-mainline`: clean git worktree for mainline development.
- `/home/ubuntu/moodify-admin/snapshots`: out-of-repo git status/diff snapshots for audit and recovery.

## Current Mainline Focus

The mainline task package is tracked under:

- `docs/experiments/????`

The first development priority is MT-001 Runtime cloud execution stability, then MT-002 MRS scoring.

## Git Rule

Generated outputs, logs, local runtime data, and SSH/Tencent Cloud key material stay out of git. Mainline task documents are explicitly allowed into git because they are development source material.

## Session Rule

Start remote work from the clean worktree:

```bash
cd /home/ubuntu/moodify-mainline
tmux new -s mainline-dev
```

Keep long-running experiments in separate tmux sessions and write logs under ignored runtime/output paths.

## Environment

System packages installed on the Tencent Cloud host:

- `ffmpeg`
- `python3-venv`
- `build-essential`
- `pkg-config`

Project virtual environment:

```bash
cd /home/ubuntu/moodify-mainline
source .venv/bin/activate
```

Installed Python surface:

- editable `moodify-core-package[dev]`
- `pytest`
- `ruff`

Verified on 2026-06-03 UTC:

```text
ffmpeg 6.1.1
Python 3.12.3
pytest: 109 passed, 8 warnings
```

## Useful Checks

```bash
cd /home/ubuntu/moodify-mainline
.venv/bin/moodify --help
.venv/bin/python -m pytest moodify-core-package/tests -q
.venv/bin/ruff check moodify-core-package/src/moodify moodify_runtime
```

## MT-001 Runtime Smoke

Run the first mainline gate from the clean worktree:

```bash
cd /home/ubuntu/moodify-mainline
bash scripts/mt001_smoke_run.sh
```

Expected gate result: 3 baseline audio files x 3 presets = 9 successful tasks, followed by report, craft memory, failure analysis, and next-plan output.

MT-001 Gate 1 evidence: `docs/cloud/MT001_GATE1_EVIDENCE.md`
