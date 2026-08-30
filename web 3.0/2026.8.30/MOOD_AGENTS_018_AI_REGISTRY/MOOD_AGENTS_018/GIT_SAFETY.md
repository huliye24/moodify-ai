# GIT SAFETY

018 may inspect AI / worker code spread across the repository.

Never:

```bash
git reset --hard
git clean -fd
git push --force
```

Do not move or rename existing production workers just to fit the Agent model.

Prefer:
- registry adapters
- metadata
- wrappers
- documentation

before invasive worker refactors.

Never copy secrets from environment files into registry data.
