# Guardrails and Rollback

## Asset safety

This package is deliberately designed so that Codex never needs custody of assets.

Codex must not:
- request a seed phrase;
- request a private key;
- insert secrets into `.env`;
- sign a transaction;
- approve token spending;
- transfer MOOD;
- add/remove liquidity;
- deploy contracts.

## Git safety

Before editing:

```bash
git status --short
git branch --show-current
git rev-parse --short HEAD
```

Preserve unrelated user modifications.

Prefer one focused commit when the user asks Codex to commit.

Suggested commit:

```text
feat(web): add official MOOD token foundation
```

## Rollback

All changes in this package must be reversible with normal Git rollback.

No irreversible external actions are allowed.

## Data safety

No destructive DB migration is required for Package 001.

If implementation unexpectedly requires a destructive migration:
**STOP** and report it instead of applying it.
