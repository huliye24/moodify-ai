# MFY-MIG-001 Baseline

- Recorded: 2026-08-08 (Asia/Shanghai)
- Starting branch: `main` (remote canonical baseline)
- Starting commit: `fa88b0b9c41df5a57a3683712a7df4e2341d8ca5`
- Implementation branch: `codex/mfy-mig-001-canonical-contracts`
- PR #16: merged as `028ccf10b71819816f75d95d9dfc9d508f3632db`
- PR #17: merged as `fa88b0b9c41df5a57a3683712a7df4e2341d8ca5`
- README identity: `The Ear of AI` present
- Architecture documents: present
- PR #15 extraction artifacts: present

## Tests before implementation

- `python -m pytest -q`: **109 passed**, 7 existing matplotlib layout warnings.
- `python -m ruff check src/moodify tests`: **23 pre-existing violations** in
  legacy test files (primarily unused imports and multi-import lines).
- Working tree: clean isolated worktree based on `origin/main`.

The historical Ruff violations are recorded as baseline and are outside this
contract migration's scope. New and changed Python files must pass Ruff.
