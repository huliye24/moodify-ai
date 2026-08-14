# Remote Linux Execution

This layer keeps planning and source preparation local, then runs the same
file-backed ledger on an always-on Linux host. It is an operations worker, not
a Moodify product state machine.

## Architecture

```text
Windows workspace -> scoped immutable snapshot -> SSH host
                                                   -> Codex CLI worker
                                                   -> task ledger/evidence
                                                   -> systemd --user restart
                                                   -> result archive -> Windows
```

## One-time remote requirements

- Linux with OpenSSH, Bash, Python 3.10+, Git, `tar`, `flock`, and systemd user services.
- Codex CLI installed and available in the remote login shell.
- Authentication completed once with `codex login --device-auth` under the
  same Linux user that owns the service.

Never commit or copy `~/.codex/auth.json` into the repository or deployment
archives. This private-host design uses ChatGPT-managed cached CLI auth so an
API key is not inherited by repository commands. For public CI or multi-tenant
runners, use the official Codex GitHub Action or another isolated credential
proxy instead of this private-host service.

## Deploy from Windows

```powershell
powershell -ExecutionPolicy Bypass -File ops/ear_batch/remote/Deploy-EarBatchRemote.ps1 `
  -HostAlias your-ssh-alias
```

The deployment command is intentionally stopped by failed SSH preflight. It
does not guess passwords, bypass host identity, install packages, or overwrite
an existing remote run unless `-ReplaceRun` is explicitly supplied.

## Start on Linux

```bash
cd ~/moodify-ear-remote/repo
bash ops/ear_batch/remote/install_user_service.sh ~/moodify-ear-remote
systemctl --user start moodify-ear-batch.service
systemctl --user status moodify-ear-batch.service
journalctl --user -u moodify-ear-batch.service -f
```

To survive logout, an administrator may enable lingering once:

```bash
sudo loginctl enable-linger "$USER"
```

That administrative action is not performed automatically.

## Recover results

```powershell
powershell -ExecutionPolicy Bypass -File ops/ear_batch/remote/Collect-EarBatchRemote.ps1 `
  -HostAlias your-ssh-alias
```

Collection downloads a timestamped result archive and verifies its SHA-256
digest before extraction.

The snapshot intentionally excludes private audio, unrelated generated
artifacts, installers, legacy worktrees, and Git internal refs. The remote host
creates a local baseline commit after extraction so Codex can review diffs. The
deployment report records the originating local commit.
