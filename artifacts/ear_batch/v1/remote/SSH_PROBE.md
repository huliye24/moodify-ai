# Remote Linux Probe

No configured SSH target was usable during the read-only preflight:

- `aliyun-moodify`: host answered, but non-interactive authentication failed.
- `nemt-cloud`: connection refused.

No remote file, service, package, or credential was changed. Deployment requires
one reachable Linux SSH alias with key-based authentication. The host must allow
Codex CLI installation/authentication and a user-level systemd service.
