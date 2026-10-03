# Cloud Node Setup — 2026-10-03

**Task:** `MOODIFY_CLOUD_NODE_SETUP_001`
**Node:** `moodify-global-engine` · `103.144.246.242` · host `yisu-6a7bcb73aac20`
**Result:** integration node operational — `status: PASS`, `consecutive failures: 0`

---

## 1. Server facts

```text
OS        Ubuntu 22.04.2 LTS
Kernel    5.15.0-69-generic
CPU       4 cores       (load 1.06 at setup time)
RAM       7.9 GB        (2.0 GB used, 26%)
Disk      98 GB         (52 GB used, 54%, ~45 GB free)
Uptime    7 weeks 3 days
```

---

## 2. The document and the server disagreed — four times

The task document was written assuming a dedicated, largely empty engineering box.
**This server is running production.** Five Moodify services, nginx serving six domains, and
a **different project** (`duoweilai`) are all live on it.

Four instructions would have been wrong to follow as written:

| Document | Reality | Action taken |
|---|---|---|
| §4 "Create `/opt/moodify/`", owner `moodify:moodify` | It exists: **7.1 GB, root-owned**, a release-based deployment (`releases/` + `current` symlink) that `moodify-api` and `moodify-worker` use as `WorkingDirectory` | Created the new directories as **siblings**; chowned **only the new ones**. **No recursive chown.** Verified afterwards that `current`, `releases`, `venv` are still root-owned. |
| §4 "Create user `moodify`" | Already exists (uid 998) | Used it. Nothing created. |
| §5 "Install nginx" | Already installed, serving six production domains with Certbot SSL | Not installed. **nginx untouched.** |
| §6 "Install Node 20 LTS; do not install multiple Node versions" | **v20.19.4 already present**, plus `/opt/node22` used by `moodify-music.service` | Not installed. Installing would have risked a running service. Left as a recorded limitation. |
| §16 "`ufw` allow … enable" | Already active with correct rules (22/80/443, plus 8181 limited to `172.16.0.0/12`) | Not modified. |

Splitting the ownership change into "new directories only" was the single most important
decision here: a literal `chown -R moodify:moodify /opt/moodify` would have changed ownership
of a live deployment.

---

## 3. Installed

Packages (only genuinely missing ones):

```text
unzip   sqlite3
```

Already present, used as-is: `git 2.34.1`, `ffmpeg 4.4.2`, `python3 3.10.12`,
`node v20.19.4`, `npm 10.8.2`, `jq`, `curl`, `rsync`, `htop`, `ufw`, `nginx`.

Engineering venv `/opt/moodify/runtime/venv`:

```text
pip 26.2.1 · moodify 1.0.0-rc.1 (editable) · ruff 0.15.15 (pinned) · pytest 9.1.1
```

Repo clone: `/opt/moodify/repo`, branch `main`, 1549 tracked files, `.git` **312 MB**.

> The local working copy of this repository has a 4.0 GB `.git`. The clone is 312 MB because
> most of that size is **unpushed local branches and dangling objects**, not published
> history. The earlier concern about a costly public clone was overstated — worth knowing
> before anyone considers a history rewrite.

---

## 4. Created

```text
/opt/moodify/{repo,runtime,artifacts,cache,logs,scripts,staging,backups}   moodify:moodify
/opt/moodify/staging/relay/            ← reserved placeholder, no code
/opt/moodify/artifacts/{integration,health}/
/opt/moodify/scripts/{update_repo,run_integration,smoke_pipeline,cleanup_artifacts,health_report}.sh
```

Services:

```text
moodify-integration.service   enabled, Type=oneshot, User=moodify
moodify-integration.timer     enabled, every 6h (OnBootSec=15min + OnUnitActiveSec=6h)
```

---

## 5. Integration result

Two runs are recorded, because the first was against a commit that predated a merge.

### First run — `3723448` (PR #35 still unmerged)

```text
PASS  01-structure-guard        PASS  04-studio-contracts      PASS  07-protocol-tests
PASS  02-ruff                   SKIP  05-studio-pipeline       PASS  08-pipeline-smoke
PASS  03-core-tests             PASS  06-v02-studio-chain
```

`05-studio-pipeline` skipped because that file existed only in an unmerged PR. **A check whose
file has not merged is a `SKIP`, never a `FAIL`** — inventing alarms CI cannot see is how a
verifier loses credibility.

### Second run — `01edc902` (current `origin/main`, PR #35 merged)

```json
{
  "schema": "moodify.cloud.integration/0.1",
  "commit_sha": "01edc902d72c15010dd86390dc0511fc03fb6323",
  "started_at": "2026-10-03T13:53:47Z",
  "ended_at":   "2026-10-03T13:58:09Z",
  "duration_s": 262,
  "status": "PASS",
  "failed_step": null,
  "host": "moodify-global-engine"
}
```

**All eight steps passed — no skips:**

```text
PASS 01-structure-guard    PASS 04-studio-contracts    PASS 07-protocol-tests
PASS 02-ruff               PASS 05-studio-pipeline     PASS 08-pipeline-smoke
PASS 03-core-tests         PASS 06-v02-studio-chain
```

Underlying counts from that run:

```text
03-core-tests       1196 passed, 6 skipped   (242.5s)
05-studio-pipeline    33 passed, 0 failed
```

`05` became a real assertion run the moment its file reached `main`, which is the behaviour
the SKIP rule was designed to produce.

Health report confirms: `commit 01edc902 (in sync with origin/main)`, `last FAIL: none`,
`consecutive failures: 0`, `nginx: active`, `timer: active`, `WARNINGS: none`.

> The node's `moodify-api`, `moodify-worker`, `moodify-music`, `moodify-music-bff`,
> `cloudflared-moodify` and `nginx` services were checked at every step of both runs and
> stayed `active` throughout.

---

## 6. Failures found and fixed during setup

Five real defects, all in the node's own tooling. Recorded because two of them were silent.

**1. False `FAIL` from a newer ruff.** The venv resolved `ruff>=0.6.0` to **0.16.10** and
reported **857 errors** on a tree CI passes with **0.15.15**. A verification node that
invents failures CI cannot see is worse than none. **Fixed by pinning `ruff==0.15.15`.**

**2. `$S` unbound variable aborted `run_integration.sh` before the summary was written.**
The script referenced `$S/smoke_pipeline.sh`, but the heredoc that generated it was
quote-delimited, so `$S` was never expanded — and `set -u` killed the script at step 7.
Result: no `summary.json` at all, indistinguishable from a run that never happened.
**Fixed:** literal path, plus a `trap write_summary EXIT` so a summary is written however the
script exits.

**3. `spawn python ENOENT`.** The server has `python3` but no `python`. The desktop shell
defaults to `python`. **Fixed** by exporting `MOODIFY_PYTHON` (the shell's own documented
override) in the unit and the script.

**4. The smoke test was not idempotent.** It cleared `case/` but not `out/` and `stems/`, so
the *second* run of an unchanged commit failed with Core's `refusing to overwrite existing
output`. The first run passed only because the directory was new — a flake that would have
looked exactly like a real regression. **Fixed** by clearing the whole output area.

**5. `find … -exec` silently deleted nothing.** *The most interesting one.*

```text
find: Failed to restore initial working directory: /root: Permission denied
```

`sudo -u moodify` inherits the caller's cwd (`/root` under a root shell). GNU `find` must
`chdir` back to its initial working directory to run `-exec`; it cannot, so it **exits 1 and
deletes nothing**. `2>/dev/null || true` hid it completely.

This affected **`cleanup_artifacts.sh` too** — a retention policy that would have silently
never run, with disk filling up mysteriously months later. **Fixed** by replacing
`find -exec` with explicit glob loops and `stat`-based age, and by adding a defensive
`cd /opt/moodify` to every script so an unreadable inherited cwd cannot break anything again.

Verified after the fix: smoke test run **three consecutive times into the same directory —
all three PASS**.

---

## 7. Manual decisions (human-approved)

1. **No public `GET /health`.** The document's §15 asked nginx to serve it. Port 80 already has
   a `default_server` and six production vhosts; every route to adding it either edits
   production nginx config or needs a new domain. **Decision: local-only health report** at
   `/opt/moodify/artifacts/health/latest.txt`. nginx untouched.
2. **Enable the 6-hour timer** (rather than manual-only), as the document specified.

---

## 8. Verification performed

```bash
git --version         2.34.1          node --version    v20.19.4
python3 --version     3.10.12         npm --version     10.8.2
ffmpeg -version       4.4.2           nginx -t          ok
systemctl status nginx                active
systemctl status moodify-integration.timer   active
```

Production services checked before and after every step — all five stayed `active`
throughout, and `/opt/moodify/{current,releases,venv}` kept their original ownership.

`summary.json`, `summary.txt` and per-step logs all exist; the recorded commit SHA matches
`origin/main`; no secret appears in the repository.

---

## 9. Not done, and why

- **Basic Pitch / music21 not installed** → MIDI and score stages are `SKIPPED`. If they
  cannot share the engineering venv without a NumPy conflict they need an isolated venv —
  never a downgrade of the main environment.
- **Staging service** — directory and port `127.0.0.1:8765` reserved; nothing bound.
- **Relay** — placeholder directory only. No code, no ports, no configuration.
- **No alerting, no monitoring stack, no Docker, no database** — per the task document.
- **Artifact retention untested against real age** — no artifact is old enough to expire yet.

---

## 10. What the node does and does not prove

It proves a commit can be pulled, its engineering checks run, and an audio chain executed with
a recorded PASS/FAIL and artifacts.

It does **not** prove the product's GUI works, nor audio quality — there is no window and no
listening here. Local is where Moodify is heard. Cloud is where it is verified.
