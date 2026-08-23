# Contributing to Moodify

Thanks for helping improve Moodify. The repository contains canonical product
surfaces, internal auditory-intelligence research, and experimental modules.
Read [AGENTS.md](AGENTS.md) and the linked Canon documents before changing
behavior, data authority, or product language.

## Workflow

```text
Fork
  ↓
Create branch
  ↓
Commit focused change
  ↓
Pull request
  ↓
Review and CI
```

1. Fork the repository and create a branch from the intended base branch.
2. Keep one pull request focused on one problem or capability boundary.
3. Add or update tests for observable behavior.
4. Run the local quality checks before opening the pull request.
5. Describe measurements, evidence, verification, failure behavior, and any
   user-visible or Canon implications in the pull request.

## Commit Messages

Use concise, imperative messages with a scope when useful:

```text
api: add bounded intelligence evaluation facade
mrs: validate normalized feature contract
docs: clarify API deployment boundary
```

Do not claim model quality, production deployment, or listening improvements
without supporting evidence.

## Code and Test Standards

- Target Python 3.10+ and use type annotations for new public interfaces.
- Follow Ruff linting and formatting conventions configured in
  `moodify-core-package/pyproject.toml`.
- Add deterministic tests; generate small synthetic audio where possible.
- Do not commit secrets, private audio, unauthorized datasets, or large output
  artifacts.
- Keep experimental work clearly labeled and separate from canonical behavior.

Run before requesting review:

```bash
cd moodify-core-package
python -m ruff check src tests ../tests
python -m pytest -q tests ../tests
```

## Review Expectations

Reviewers check architecture boundaries, test evidence, security and data
handling, compatibility, and whether a machine decision remains within its
authorized scope. Changes to Canon-controlled identity, authority, or data
boundaries require `CANON_CHANGE = YES` and the required change record.
