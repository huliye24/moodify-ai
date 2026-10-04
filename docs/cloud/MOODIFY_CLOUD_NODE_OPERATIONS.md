# Moodify Cloud Node — Operations

Day-to-day commands for `moodify-global-engine` (`103.144.246.242`).
Background and design: [`MOODIFY_CLOUD_NODE.md`](MOODIFY_CLOUD_NODE.md).

> **This machine also runs production.** Nothing below touches `moodify-api`,
> `moodify-worker`, `moodify-music`, `moodify-music-bff`, `cloudflared-moodify`, nginx,
> or `/opt/moodify/releases`. If a command you are about to run is not in this document,
> stop and check what else uses it.

---

## Check status

```bash
# one-screen health report
cat /opt/moodify/artifacts/health/latest.txt

# regenerate it now
/opt/moodify/scripts/health_report.sh

# is the node scheduled?
systemctl status moodify-integration.timer
systemctl list-timers moodify-integration.timer

# what did the last run do?
systemctl status moodify-integration.service
```

`health.latest.txt` carries: hostname, OS, kernel, CPU, RAM, disk, current commit and whether
it is in sync with `origin/main`, last run / last PASS / last FAIL, consecutive failure count,
nginx state, timer state, and any thresholds breached.

---

## Run integration manually

```bash
# full run: pull origin/main, verify, write artifacts
sudo systemctl start moodify-integration.service

# watch it (runs ~4-5 minutes)
journalctl -u moodify-integration.service -f
```

Read the result afterwards:

```bash
cat /opt/moodify/artifacts/integration/$(git -C /opt/moodify/repo rev-parse HEAD)/summary.txt
```

Useful extra: `systemctl reset-failed moodify-integration.service` before re-running if the
previous run failed — otherwise `status` keeps showing the old failure.

### Run only the checks, without pulling

```bash
sudo -u moodify /opt/moodify/scripts/run_integration.sh
```

### Run only the audio smoke test

```bash
sudo -u moodify MOODIFY_REPO=/opt/moodify/repo MOODIFY_VENV=/opt/moodify/runtime/venv \
  /opt/moodify/scripts/smoke_pipeline.sh /tmp/smoke-manual
```

The smoke test clears its output directory before every run, so it is safe to repeat.

---

## View logs

```bash
# the service
journalctl -u moodify-integration.service -n 200
journalctl -u moodify-integration.service --since "24 hours ago"

# one step of the last run
D=/opt/moodify/artifacts/integration/$(git -C /opt/moodify/repo rev-parse HEAD)
cat $D/logs/03-core-tests.log
ls $D/logs/                     # 01-structure-guard … 08-pipeline-smoke

# threshold warnings only
cat /opt/moodify/logs/health.log
```

`journalctl` is the log store. There is no Loki, no Elasticsearch, no Grafana — and none is
wanted on a 4-core box that also runs production.

---

## Update the repo (without running checks)

```bash
sudo -u moodify /opt/moodify/scripts/update_repo.sh
```

It does `git fetch` → `checkout main` → `reset --hard origin/main`, then cleans **only**
explicitly-listed generated directories.

> **Never run `git clean -fdx` in `/opt/moodify/repo`.** The tree can hold locally-produced
> evidence that has not been classified, and an unrestricted clean destroys it. Adding a path
> to `CLEAN_PATHS` in `update_repo.sh` is a deliberate act, not a convenience.

---

## Check disk, memory, and load

```bash
df -h /                       # the node warns above 80%
free -h                       # warns above 90%
uptime                        # load vs 4 cores
du -sh /opt/moodify/artifacts /opt/moodify/logs
du -sh /opt/moodify/repo      # ~312 MB, mostly .git
```

---

## Clean up artifacts

```bash
sudo -u moodify /opt/moodify/scripts/cleanup_artifacts.sh
```

Retention: successful runs 7 days, failed runs 14 days, latest success and latest failure
always kept. It **only** touches `/opt/moodify/artifacts` and `/opt/moodify/logs`, refuses any
other path, and computes age with `stat` rather than `find -mtime -exec` (see the setup
report for why).

---

## Restart nginx (only if you must)

```bash
sudo nginx -t                          # ALWAYS validate first
sudo systemctl reload nginx            # reload, not restart — keeps connections

# only if reload is not enough
sudo systemctl restart nginx
```

nginx serves six production domains. **Do not add a `default_server` directive and do not
edit `sites-available/default`.** If you need a new endpoint, add a name-based vhost.

Creating the cloud node did not modify nginx. Changing it now is a production change.

---

## Rollback configuration

Backups are taken before any system config edit:

```bash
ls -la /etc/systemd/system/moodify-integration.service*
ls -la /etc/nginx/sites-available/

# restore a unit
sudo cp /etc/systemd/system/moodify-integration.service.bak.<timestamp> \
        /etc/systemd/system/moodify-integration.service
sudo systemctl daemon-reload
```

### Disable the schedule without deleting anything

```bash
sudo systemctl disable --now moodify-integration.timer
```

The scripts, venv, repo and artifacts all stay; nothing is lost. Re-enable with
`sudo systemctl enable --now moodify-integration.timer`.

### Full rollback of the cloud node

Everything the node added lives in paths that production does not use:

```bash
sudo systemctl disable --now moodify-integration.timer
sudo rm -f /etc/systemd/system/moodify-integration.{service,timer}
sudo systemctl daemon-reload
sudo rm -rf /opt/moodify/{repo,runtime,artifacts,cache,logs,scripts,staging,backups}
```

**Verify before you delete** that `releases/`, `current`, `venv/`, `music*/`, `music-bff/`
are not in that list — they belong to production and must never be removed.

---

## Change the schedule

Edit `/etc/systemd/system/moodify-integration.timer` (back it up first), then:

```bash
sudo systemctl daemon-reload
sudo systemctl restart moodify-integration.timer
```

Cadence is intentionally not every few minutes: polling GitHub frequently costs more than it
finds, and this box has other work to do.

---

## Secrets

Reserved directory: `/opt/moodify/runtime/env/` (`chmod 600`).

**Never commit secrets**, and never place them in `/opt/moodify/repo` — that tree is
hard-reset on every run. The current setup needs no secrets at all.

---

## Escalation

If integration fails three runs in a row, `health_report.sh` writes a warning to
`/opt/moodify/logs/health.log`. There is **no alerting service** — by design. Read the
warning, read the run's `logs/`, and fix the cause.

If the failure is a step whose file simply has not merged yet, it will show as `SKIP`, not
`FAIL`. A `FAIL` means something real.
