# MFY-ALIYUN-DATA-NODE-001 — Operations Log (2026-08-10)

## Deployment

- Uploaded current branch `moodify-core-package` (src + pyproject + deploy + scripts) to `/opt/moodify/moodify-core-package` (no git on server; packaged tar).
- venv: `/opt/moodify/.venv` (Python 3.14.4), `pip install -e .`
- systemd unit: `/etc/systemd/system/moodify-data-worker.service` (from `deploy/systemd/`), `User=moodify`, restart-on-failure, MemoryHigh=1500M
- swap: 2 GiB `/swapfile` via `ensure_swap_2g.sh` (no swap existed), `vm.swappiness=10`
- dirs: `/var/lib/moodify/{inbox,data_factory}`, owned by `moodify`
- environment: `MOODIFY_NODE_*` defaults per `node.env.example`

## First-run issues

1. `ModuleNotFoundError: matplotlib` — the comparison contact-sheet path
   (`moodify.auditory.comparison.build_delta_spectrograms`) imports matplotlib,
   which is an optional dev dependency not installed by `pip install -e .`.
   Fixed on server: `pip install matplotlib`. Job retried via
   `moodify-node retry <job_id>`; the partial case from the failed attempt
   remains on disk as failure evidence (`case_be0b530c...`, 12 MB).
   NOTE for next deploy: install `moodify[dev]` or document matplotlib as a
   runtime requirement of the scan/comparison path.

## Verification

- `moodify-node init` → creates queue db at `/var/lib/moodify/node.sqlite3`
- `moodify-node enqueue <file>` → QUEUED
- `systemctl enable --now moodify-data-worker.service` → active
- worker processed queue serially: QUEUED 2 → SUCCEEDED 2 (both 45s owned tracks)
- restart test: `systemctl restart moodify-data-worker.service` — queue state
  and SUCCEEDED records retained (SQLite persistence)
- no OOM kills observed; swap usage peaked at 76 MiB

## Current queue

```text
QUEUED: 0  RUNNING: 0  SUCCEEDED: 3  FAILED: 0
```

## Operator commands (runbook)

```bash
sudo -u moodify /opt/moodify/.venv/bin/moodify-node status
sudo -u moodify /opt/moodify/.venv/bin/moodify-node jobs --status FAILED
sudo -u moodify /opt/moodify/.venv/bin/moodify-node retry <job_id>
sudo -u moodify /opt/moodify/.venv/bin/moodify-node recover
journalctl -u moodify-data-worker.service -f
```

Backup targets: `/var/lib/moodify/node.sqlite3` + `/var/lib/moodify/data_factory/cases/`.
