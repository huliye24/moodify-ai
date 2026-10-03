# GIT SAFETY

012 is an extraction task in a repository with possible concurrent work.

## Never

```bash
git reset --hard
git clean -fd
git push --force
git push --force-with-lease
git merge codex/mood-mainnet-integration-009
```

## Use

- isolated worktree
- isolated branch
- explicit source SHA recording
- file-by-file or commit-by-commit review
- minimal cherry-picks only when a commit is cleanly scoped

If a source commit mixes:
- Android
- Electron
- Token launch
- Contribution
- Wallet

do not cherry-pick blindly.

Prefer manual extraction or targeted patch.

## Source provenance

Every extracted module should be traceable to:

```text
source branch
source SHA
source path
adaptations made
```

Record this in `012_EXTRACTION_MANIFEST.md`.
