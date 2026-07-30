# Moodify Local Git Checkpoint Protocol

**Applies to:** DSK-MFY-AUX-HARDENING-002  
**Purpose:** survive power loss, network loss, terminal interruption, context loss, and worker restart without mixing unrelated work or losing engineering evidence.

## 1. Git Is the Engineering Save System

A checkpoint is a local, recoverable engineering state. It is not a release, acceptance decision, or remote publication.

The recovery chain is:

```text
Codex baseline checkpoint
    -> DeepSeek batch work-in-progress checkpoint
    -> DeepSeek tested batch checkpoint
    -> Codex independent acceptance checkpoint
```

Each checkpoint must answer: what state was saved, what evidence existed at that moment, and from which commit work should resume.

## 2. Safety Constraint for the Current Repository

The repository already contains many tracked modifications and untracked files. Some overlap the hardening task. Therefore DeepSeek must not create the initial baseline and must not begin edits until Codex records it in `BASELINE_CHECKPOINT.md`.

The baseline is necessary to distinguish inherited work from this task's changes. It also prevents broad staging from capturing audio, installers, outputs, temporary files, IDE state, or unrelated projects.

## 3. Forbidden Git Operations

Do not use:

- `git add .`
- `git add -A`
- wildcard or directory-wide staging without an audited file list
- `git commit -a`
- `git stash`
- `git reset` in any mode
- `git clean`
- checkout/restore commands that discard content
- amend, rebase, merge, branch switching, tags, push, or any remote operation

Do not stage private audio, generated audio, installers, output directories, temporary directories, IDE metadata, credentials, environment files, or files outside the declared task.

## 4. Permitted Checkpoints

### CP0 — Baseline

Created by Codex before DeepSeek edits. Records the exact commit, branch, working-tree inventory, inclusion policy, exclusions, and recovery notes in `BASELINE_CHECKPOINT.md`.

### CP1 — Batch Work in Progress

Create after a coherent invariant and its tests exist, or before a risky multi-file change. It may be red only when the commit message and engineering log explicitly say why.

Commit form:

```text
checkpoint(dsk-aux-002): batch-a wip — proposal isolation
```

### CP2 — Batch Gate

Create only after the batch's focused gate has run. The engineering log must already contain the command, exit code, counts, warnings, and limitations.

Commit form:

```text
checkpoint(dsk-aux-002): batch-a gate — PASS
```

Use `REWORK` or `HOLD` instead of `PASS` when applicable. A commit is saved state, not proof of success.

### CP3 — Worker Handoff

Create after `ENGINEERING_LOG.md` and `HANDOFF.md` accurately describe the final worker state.

```text
checkpoint(dsk-aux-002): worker handoff
```

Codex independently reviews this checkpoint and may later create a separate acceptance checkpoint.

## 5. Exact-Path Staging Procedure

Before every commit:

1. Run `git status --short`.
2. Create an explicit list of task files intended for the checkpoint.
3. Inspect each file's diff or full content when new.
4. Stage each file by its exact literal path.
5. Run `git diff --cached --check`.
6. Run `git diff --cached --name-status` and compare it with the intended list.
7. If any unrelated file is staged, stop and ask Codex; do not unstage it using destructive or broad commands without review.
8. Commit locally with the required task-prefixed message.
9. Record the resulting commit hash in `ENGINEERING_LOG.md`.

If a task file already contained pre-task changes, the baseline record governs attribution. Never claim the whole file as newly authored by DeepSeek.

## 6. Resume Procedure After Interruption

On every restart:

1. Read the task orchestration, this protocol, `BASELINE_CHECKPOINT.md`, `ENGINEERING_LOG.md`, and `HANDOFF.md`.
2. Run `git branch --show-current`, `git rev-parse --short HEAD`, `git status --short`, and task-prefixed `git log`.
3. Identify the latest valid CP0/CP1/CP2/CP3 checkpoint.
4. Compare the working tree with that checkpoint; preserve newer uncommitted work.
5. Rerun the smallest test that proves the last recorded invariant.
6. Continue from the first incomplete logged action, not from memory.

If repository state contradicts the log, stop with `HOLD: CHECKPOINT STATE DIVERGED` and report exact evidence. Do not guess, reset, or overwrite.

## 7. Recovery Guarantee and Limit

Local commits protect against process, context, and ordinary power interruption once disk state has been flushed. They do not protect against total disk loss. Remote backup is deliberately outside this task because it requires an authorized repository and data-classification decision.
