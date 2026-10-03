# Moodify Cloud Node

**Node:** `moodify-global-engine` — Los Angeles, `103.144.246.242` (host `yisu-6a7bcb73aac20`)
**Role:** Integration / Relay node
**Established:** 2026-10-03
**Task:** `MOODIFY_CLOUD_NODE_SETUP_001`

> **Local is where Moodify is heard. Cloud is where Moodify is verified.**

---

## 1. Purpose

A stable, always-on place to verify that what landed on `main` actually works — not a
development machine, not an AI training box, and not the product itself.

```text
Local Windows / macOS
        │  develop / listen / UI / device test
        ↓
      GitHub
        │  push / PR / main
        ↓
Moodify Cloud Node
        ├── integration tests
        ├── Core verification
        ├── audio pipeline smoke test
        ├── artifacts
        └── future relay service
```

---

## 2. Node role

| Role | Status |
|---|---|
| **A — Integration Node** | **Enabled.** Every 6 hours, plus manual runs. |
| **B — Audio Pipeline Test Node** | **Enabled** for the steps this node can actually run (see §8). |
| **C — Staging API Node** | **Reserved.** `/opt/moodify/staging/` exists; port `127.0.0.1:8765` reserved. Nothing listens on it. |
| **D — Future Relay Node** | **Reserved only.** `/opt/moodify/staging/relay/` is an empty placeholder. No relay logic. |

---

## 3. This machine is shared with production

**This is the critical fact about this node, and the setup task document did not assume it.**

The same server already runs, as `moodify` / `root`:

```text
moodify-api.service          Moodify Ear FastAPI        127.0.0.1:8000
moodify-worker.service       Ear unattended worker
moodify-music.service        Music Platform             127.0.0.1:3100
moodify-music-bff.service    Music Public BFF (LA)      127.0.0.1:8100
cloudflared-moodify.service  Cloudflare Tunnel
nginx                        six production domains, Certbot SSL
```

and, belonging to a **different project**:

```text
/opt/duoweilai     duoweilai webhook + gunicorn 8090
/opt/crestwave     crestwave
/opt/mood-research audiolla
/opt/mood-node
```

Everything the cloud node adds is therefore **additive and isolated**:

- `/opt/moodify/` is a **release-based deployment** (`releases/<timestamp>/` + a `current`
  symlink that `moodify-api` and `moodify-worker` use as their `WorkingDirectory`).
  It is **root-owned** and is **never** touched by this node's tooling.
- The cloud node's directories are **new siblings** under `/opt/moodify/`, owned by the
  existing `moodify` user. **There is no recursive `chown` anywhere.**
- The engineering venv is `/opt/moodify/runtime/venv` — separate from the production
  `/opt/moodify/venv`.

---

## 4. Directory layout

```text
/opt/moodify/
├── releases/            ← production deployments (root-owned, untouched)
├── current -> releases/20260816T080724Z
├── venv/                ← production venv (untouched)
├── music*/ music-bff/   ← production services (untouched)
│
├── repo/                ← git clone of huliye24/moodify-ai, branch main   (moodify)
├── runtime/venv/        ← engineering venv, Core installed editable       (moodify)
├── artifacts/           ← integration and health outputs                  (moodify)
│   ├── integration/<commit-sha>/{summary.json,summary.txt,logs/,smoke/}
│   └── health/latest.txt
├── cache/               ← reserved
├── logs/                ← health.log and long-form logs                   (moodify)
├── scripts/             ← the four operator scripts                       (moodify)
├── staging/             ← reserved; staging/relay/ is an empty placeholder
└── backups/             ← reserved
```

All new paths are owned `moodify:moodify`. The production tree keeps its original
ownership and was verified unchanged after setup.

---

## 5. Installed dependencies

The setup document asked for a package list; **most of it was already present**. Installed
during this task:

```text
unzip
sqlite3
```

Already present and used as-is (versions at setup time):

```text
git      2.34.1          python3   3.10.12
ffmpeg   4.4.2           node      v20.19.4   (/usr/local/bin)
nginx    installed       npm       10.8.2
jq, curl, rsync, htop, ufw
```

**Node was not installed.** v20.19.4 already satisfies the "Node 20 LTS" requirement, and a
second `/opt/node22` is in use by `moodify-music.service` — installing NodeSource's Node 20
risked disturbing a running service for no gain. The setup document's "do not install
multiple Node versions" cannot be satisfied retroactively; it is recorded as a known
limitation rather than papered over.

**nginx was not installed.** It is already serving production sites; see §7.

Engineering venv: `/opt/moodify/runtime/venv`

```text
pip       26.2.1
moodify   1.0.0-rc.1   (editable, from /opt/moodify/repo/moodify-core-package)
ruff      0.15.15      PINNED to match .github/workflows/*.yml
pytest    9.1.1
```

> **`ruff` is pinned deliberately.** The venv initially resolved `ruff>=0.6.0` to 0.16.10,
> which reported **857 lint errors** on the same tree CI passes with 0.15.15. A verification
> node that reports failures CI cannot see is worse than no node: it manufactures noise and
> destroys trust in the signal. The pin is the fix.

---

## 6. Services

```text
/etc/systemd/system/moodify-integration.service   Type=oneshot, User=moodify
/etc/systemd/system/moodify-integration.timer      every 6h (OnBootSec=15min + OnUnitActiveSec=6h)
```

The service runs, in order:

```text
1. /opt/moodify/scripts/update_repo.sh      fetch + hard-reset to origin/main
2. /opt/moodify/scripts/run_integration.sh  the checks; records PASS/FAIL
3. /opt/moodify/scripts/health_report.sh    ExecStopPost — runs even on failure
```

`ExecStopPost` is deliberate: the health report matters most when verification fails.

Scheduling is **relative to boot** (`OnBootSec` + `OnUnitActiveSec`) with a 120 s randomized
delay, so it does not stampede at a fixed wall-clock minute and spreads naturally across
machines. `Persistent=true` catches a run missed while the machine was down.

Resource discipline — the node must never compete with production:

```text
Nice=10        CPUWeight=20        IOWeight=20        TimeoutStartSec=5400
```

---

## 7. Ports and exposure

```text
public : 22 (SSH) · 80 · 443      ← unchanged, already correct
local  : 8000 8100 3100 8090 (production services, loopback only)
reserved: 127.0.0.1:8765           ← staging; NOT bound, NOT exposed
```

**No new public surface was added.** `ufw` was already active with correct rules
(`22`, `80/443`, plus `8181` restricted to `172.16.0.0/12`); it was **not modified**.

**nginx was not touched.** It serves `rongjingmusic.com`, `play.rongjingmusic.com`,
`rongjingwenchuan.com`, `rongjinwenchuan.xyz`, `crestwavecoin.com`, `postyouth.club` and
`duoweilai`, and `/etc/nginx/sites-available/default` holds the port-80 `default_server`.

The setup document's §15 asked for a public `GET /health`. **It was declined by human
decision**, because every way of adding it either touches production nginx config or needs a
new domain. Health is reported **locally** at `/opt/moodify/artifacts/health/latest.txt`
instead. If external probing is wanted later, add a name-based vhost — never a
`default_server` change.

---

## 8. What the smoke test actually runs

`scripts/smoke_pipeline.sh` uses only a **tracked baseline file** from the repository
(`moodify-core-package/tests/baseline/test_audio/piano.wav`). No private audio, no downloads,
no models, no cloud inference.

```text
ANALYZE    moodify analyze            → case bundle          PASS
DIAGNOSE   moodify protocol process   → Core diagnosis       PASS
SEPARATE   dsp_separate.py            → stems + manifest     PASS
STRUCTURE  MIDI (Basic Pitch)         → SKIPPED: not installed
STRUCTURE  score (music21)            → SKIPPED: not installed
CONTEXT    pipeline.js                → SKIPPED until it lands on main
```

Skipped steps are recorded **as skipped with the reason**. An unrun step must never read as
a pass. A step whose file has not merged yet is a skip, not a failure — reporting it as
FAIL would raise alarms CI cannot see.

The chain is small on purpose. Its job is engineering continuity, not audio judgement.

---

## 9. Security boundary

```text
SSH          unchanged; key-based access confirmed working before any change
root login   unchanged
ufw          unchanged (already correct)
nginx        unchanged
secrets      no secrets in the repo; /opt/moodify/runtime/env/ reserved, chmod 600
repo         server never force-pushes, never edits main, never becomes source authority
```

The server is a **verifier**, not a publisher. It only checks out and reports.

---

## 10. Known limitations

1. **Shared with production and a third-party project.** Resource headroom is comfortable
   today (4 cores, load ~1; RAM 26%; disk 54%), but this is not a dedicated box.
2. **Two Node installations exist** (`/usr/local/bin/node` v20.19.4 and `/opt/node22`).
   Not introduced here; not resolvable without touching a running service.
3. **Node 20 is not managed by NodeSource**, so it will not receive Node 20 patch releases
   through apt.
4. **Basic Pitch and music21 are not installed**, so MIDI/score stages are skipped. If they
   cannot share the engineering venv without a NumPy conflict, they belong in their own
   isolated venv — per the task document, never by downgrading the main environment.
5. **Artifact retention has not yet been exercised** — no artifact is old enough to expire.
   The logic avoids `find -exec` (see the setup report); it is untested against real age.
6. **`temporal-texture` is a pre-existing chronic CI failure** and is not run here.

---

## 11. Future relay role

Reserved, not implemented:

```text
Studio ──HTTPS──▶ Cloud Relay ──HTTPS──▶ Moodify App
```

A future relay might provide temporary object delivery, metadata sync, device authorization
and notifications. **None of it exists.** `/opt/moodify/staging/relay/` is an empty directory
and a note; no code, no ports, no configuration.

---

## 12. Reference card — copy these, do not guess

Everything in this section was read off the running node, not written from memory.

### 12.1 Last verified commit

```text
commit   : 01edc902d72c15010dd86390dc0511fc03fb6323   (= origin/main at the time)
status   : PASS          duration: 262s          failed: none
ran      : 2026-10-03T13:53:47Z → 13:58:09Z
artifacts: /opt/moodify/artifacts/integration/01edc902d72c15010dd86390dc0511fc03fb6323
```

All eight steps passed, including `05-studio-pipeline` — which reads `SKIP` on any commit
that does not yet contain that file, and becomes a real result once it is merged.

```text
PASS 01-structure-guard    PASS 04-studio-contracts    PASS 07-protocol-tests
PASS 02-ruff               PASS 05-studio-pipeline     PASS 08-pipeline-smoke
PASS 03-core-tests         PASS 06-v02-studio-chain
```

Underlying numbers from that run: `03-core-tests` = **1196 passed, 6 skipped**;
`05-studio-pipeline` = **33 passed, 0 failed**.

### 12.2 systemd units

```text
/etc/systemd/system/moodify-integration.service     Type=oneshot, User=moodify
/etc/systemd/system/moodify-integration.timer       enabled
```

### 12.3 Scripts

```text
/opt/moodify/scripts/update_repo.sh          fetch + reset --hard origin/main
/opt/moodify/scripts/run_integration.sh      8 checks; writes PASS/FAIL + summary
/opt/moodify/scripts/smoke_pipeline.sh       audio smoke chain
/opt/moodify/scripts/cleanup_artifacts.sh    retention (the ONLY deleter)
/opt/moodify/scripts/health_report.sh        writes artifacts/health/latest.txt
```

### 12.4 Commands

```bash
# THE one command to trigger a full verification (pulls latest main first)
sudo systemctl start moodify-integration.service

# latest result
cat /opt/moodify/artifacts/integration/$(sudo -u moodify git -C /opt/moodify/repo rev-parse HEAD)/summary.txt

# latest logs (live, or the last N lines)
journalctl -u moodify-integration.service -f
journalctl -u moodify-integration.service -n 200

# one step's log
D=/opt/moodify/artifacts/integration/$(sudo -u moodify git -C /opt/moodify/repo rev-parse HEAD)
cat $D/logs/03-core-tests.log

# health report
cat /opt/moodify/artifacts/health/latest.txt

# re-run after a failure (otherwise status shows the stale failure)
sudo systemctl reset-failed moodify-integration.service
```

### 12.5 Paths, and what may be deleted

```text
MAY be deleted by cleanup_artifacts.sh (and nothing else):
  /opt/moodify/artifacts/**      (integration runs, health reports)
  /opt/moodify/logs/**           (*.log)

Written but never auto-deleted:
  /opt/moodify/artifacts/health/latest.txt    (overwritten each run)

Reserved, empty, no code:
  /opt/moodify/staging/          /opt/moodify/staging/relay/
  /opt/moodify/cache/            /opt/moodify/backups/

The verifier's own working area:
  /opt/moodify/repo/             git clone, hard-reset every run
  /opt/moodify/runtime/venv/     engineering venv
```

`cleanup_artifacts.sh` **refuses** any base path other than `/opt/moodify/artifacts` and
`/opt/moodify/logs` — a mis-set variable fails loudly instead of deleting somewhere else.

Current footprint: artifacts 33 MB · logs 4 KB · repo 407 MB · runtime 646 MB (~1.1 GB).

### 12.6 Git update policy

```text
branch      : main only
update      : git fetch origin --prune
              git checkout main
              git reset --hard origin/main
clean       : ONLY paths listed in CLEAN_PATHS in update_repo.sh
              NEVER `git clean -fdx` over the whole tree
```

**The cloud worktree is not a development tree.** Manual edits to `/opt/moodify/repo` are
forbidden — they are destroyed by the next `reset --hard`, and if they somehow survive they
make every subsequent verification a statement about modified code rather than about `main`.

### 12.7 GitHub permission boundary — read-only, enforced

```text
fetch       : allowed
push        : DISABLED BY CONFIGURATION
```

```text
origin  https://github.com/huliye24/moodify-ai.git (fetch)
origin  DISABLED_BY_POLICY_read_only_verifier      (push)
```

There are no stored credentials for the `moodify` user (no `.git-credentials`, no `.netrc`,
no credential helper), so the node could not authenticate even before this. The push URL is
disabled anyway, so an accidental `git push` **fails immediately with a clear message**
instead of depending on a credential being absent:

```text
fatal: 'DISABLED_BY_POLICY_read_only_verifier' does not appear to be a git repository
```

The node **verifies**. It never publishes, merges, tags, or writes to GitHub.

### 12.8 Pinned baseline

Machine differences, not code differences, are the usual cause of "CI passes but the node
fails". Compare against this table first:

| Tool | Version | Notes |
|---|---|---|
| Python | **3.10.12** | both system and venv |
| ruff | **0.15.15** | **pinned to match `.github/workflows/*.yml`** |
| pytest | 9.1.1 | |
| Node | **v20.19.4** | `/usr/local/bin/node`; a second `/opt/node22` exists (not this node's) |
| npm | 10.8.2 | |
| FFmpeg | **4.4.2** | `4.4.2-0ubuntu0.22.04.1` |
| git | 2.34.1 | |
| moodify | 1.0.0-rc.1 | editable, from `/opt/moodify/repo/moodify-core-package` |

The ruff pin is load-bearing: unpinned, the venv resolved 0.16.10 and reported **857 errors**
on a tree CI passes with 0.15.15.

### 12.9 Resource envelope

```text
systemd      Nice=10   CPUWeight=20   IOWeight=20   TimeoutStartSec=5400 (90 min)
schedule     OnBootSec=15min + OnUnitActiveSec=6h + RandomizedDelaySec=120 + Persistent
retention    successful runs 7 days · failed runs 14 days
             latest PASS and latest FAIL always kept
concurrency  1 (systemd runs one instance; a second start is queued, not parallel)
logs         14 days
```

Thresholds that raise a warning in `logs/health.log`: disk > 80%, RAM > 90%, three
consecutive integration failures. **No alerting service** — by design.

A hung check is bounded by `TimeoutStartSec=5400`, so it cannot block the next scheduled run.

### 12.10 Production forbidden zones — never modify

The Cloud Verification Agent must **never** write to, restart, reconfigure, or delete:

```text
SERVICES (production, Moodify)
  moodify-api.service          moodify-worker.service
  moodify-music.service        moodify-music-bff.service
  cloudflared-moodify.service   nginx.service

SERVICES (other project — not ours at all)
  duoweilai.service  duoweilai-webhook.service

DIRECTORIES (production, root-owned)
  /opt/moodify/releases/       /opt/moodify/current -> releases/…
  /opt/moodify/venv/           /opt/moodify/music/     /opt/moodify/music-bff/
  /opt/moodify/music-media/    /opt/moodify/music-build-*/
  /opt/moodify/capabilities/   /opt/moodify/moodify-core-package/
  /opt/duoweilai/   /opt/crestwave/   /opt/mood-research/   /opt/mood-node/

CONFIG
  /etc/nginx/**  (six production vhosts + default_server + Certbot SSL)
  /etc/moodify/*.env  (production secrets)
  ufw rules
  SSH configuration
```

**Never run a recursive `chown` over `/opt/moodify`.** Production assets are root-owned;
the verifier's own directories are `moodify`-owned. The split is deliberate — a
`chown -R moodify:moodify /opt/moodify` would break the running deployment.

**Never add a `default_server` directive to nginx** and never edit
`sites-available/default`. A new endpoint, if one is ever needed, is a name-based vhost.

### 12.11 One-line summary for task documents

> Cloud node `moodify-global-engine` (103.144.246.242) verifies `origin/main` read-only.
> Trigger: `sudo systemctl start moodify-integration.service`. Units:
> `moodify-integration.{service,timer}`. Scripts: `/opt/moodify/scripts/*.sh`.
> Artifacts: `/opt/moodify/artifacts/integration/<sha>/`. Health:
> `/opt/moodify/artifacts/health/latest.txt`. Retention 7/14 days via
> `cleanup_artifacts.sh` only. **Never touch `/opt/moodify/{releases,current,venv,music*}`,
> nginx, ufw, or the production services.** No push access, by configuration.

---

## 13. Related documents

- [`MOODIFY_CLOUD_NODE_OPERATIONS.md`](MOODIFY_CLOUD_NODE_OPERATIONS.md) — day-to-day commands
- [`../reports/CLOUD_NODE_SETUP_2026-10-03.md`](../reports/CLOUD_NODE_SETUP_2026-10-03.md) — setup record, including where the task document and the server disagreed
- [`../canon/TECHNOLOGY_PRINCIPLES.md`](../canon/TECHNOLOGY_PRINCIPLES.md) — why this is built from boring parts
