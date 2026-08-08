# DSK-MFY-CLI-NATIVE-REFACTOR-015 HANDOFF

**Status:** READY_FOR_CODEX_REVIEW
**Worker:** DeepSeek | **Date:** 2026-08-01 | **HEAD:** df3a8a3

## Stages

| Stage | Status |
|---|---|
| Stage 0 审计 (capability + dependency + risk) | PASS |
| Stage 1 合同 (architecture + schema + error catalog) | PASS |
| Stage 2 骨架 (domain/app/ports/adapters/cli_v2) | PASS |
| Stage 3 纵向闭环 (8 CLI v2 commands) | PASS |
| Stage 4 兼容层 (capability declaration) | PASS |
| Stage 5 验证 + HANDOFF | PASS |

## CLI v2 — 8 Commands

```powershell
py -3.11 -m moodify.cli_v2 version          # JSON product identity
py -3.11 -m moodify.cli_v2 capabilities     # 10 capability declarations
py -3.11 -m moodify.cli_v2 project init DIR # CanonicalProject.create
py -3.11 -m moodify.cli_v2 project inspect DIR  # Read project.json
py -3.11 -m moodify.cli_v2 asset import DIR AUDIO  # SHA-256 + reference mode
py -3.11 -m moodify.cli_v2 plan create DIR --dry-run  # Plan before apply
py -3.11 -m moodify.cli_v2 run execute DIR  # NOT_IMPLEMENTED (needs 014)
py -3.11 -m moodify.cli_v2 run verify DIR   # NOT_IMPLEMENTED
```

## Architecture: domain/app/ports/adapters/cli_v2

- `domain/project.py` — CanonicalProject, AssetRef, Decision, Plan, Run, Evidence, Revision
- `cli_v2/main.py` — JSON-first, stderr for errors, stable exit codes
- No CLI/subprocess/GUI in domain layer (P0-03)
- Source read-only with SHA-256 (P0-04)

## JSON Contract

Every response: `{"schema_version":"1.0.0","command":"...","status":"..."}`
Errors on stderr, non-zero exit. No mixed output.

## Capability Honesty

- cli_daw_reaper: NOT_IMPLEMENTED
- run.execute: NOT_IMPLEMENTED (requires 014 Codex acceptance)
- score: experimental

## Old CLI

17 existing commands unchanged. No deletion.

## HANDOFF Path

`E:\moodify\docs\tasks\deepseek\DSK-MFY-CLI-NATIVE-REFACTOR-015\HANDOFF.md`

Worker stops. Final judgment belongs to Codex.
