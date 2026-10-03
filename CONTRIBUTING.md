# Contributing to Moodify

Thanks for helping improve Moodify.

Moodify is an open collaboration network around the Moodify Protocol, Core, and Evidence.
Anyone may contribute, and **contribution is not counted in commits** — a documented A/B
judgment from a mastering engineer can be worth more than a large patch. See
[`GOVERNANCE.md`](GOVERNANCE.md).

Before changing behavior, data authority, or product language, read
[`AGENTS.md`](AGENTS.md) and the linked Canon documents.

## Ways to contribute

```text
CODE · PROTOCOL · CASE · REVIEW · BENCHMARK · DATASET
DOCUMENTATION · RESEARCH · BUG · PLUGIN · INTEGRATION
```

You do not need to write code. The **Review Network** — mix and mastering engineers,
producers, musicians, listeners, researchers — contributes perceptual judgments, artifact
reports, reference-track observations, device playback differences, and edge cases. That
accumulates into the project's professional experience layer, and it is what makes this a
sound project rather than a generic repository. See
[`docs/governance/NETWORK.md`](docs/governance/NETWORK.md).

## Workflow

```text
Fork → Branch → Focused commit → Pull request → Review and CI
```

1. Fork the repository and create a branch from the intended base branch.
2. Keep one pull request focused on one problem or capability boundary.
3. Add or update tests for observable behavior.
4. Run the local quality checks below.
5. In the pull request, describe measurements, evidence, verification, failure behavior,
   and any user-visible or Canon implications.

## Proposing a change to the protocol

A change to the protocol, a schema, a Core behavior contract, governance, the evidence
format, or public compatibility requires a **MIP** — a pull request alone is not enough.

```text
DRAFT → DISCUSSION → EXPERIMENTAL → EVIDENCE → ACCEPTED → IMPLEMENTED → RELEASED
```

Start from [`protocol/mips/MIP-0000-template.md`](protocol/mips/MIP-0000-template.md).
A proposal cannot reach `ACCEPTED` without a populated Evidence section. Negative and
inconclusive results are valid evidence and must be recorded, not suppressed.

Ordinary bug fixes do not need a MIP.

## Commit messages

Concise and imperative, with a scope when useful:

```text
api: add bounded intelligence evaluation facade
mrs: validate normalized feature contract
docs: clarify API deployment boundary
```

Do not claim model quality, production deployment, or listening improvements without
supporting evidence.

## Code and test standards

- Target Python 3.10+; type-annotate new public interfaces.
- Follow the Ruff configuration in `moodify-core-package/pyproject.toml`.
- Add deterministic tests; prefer small synthetic audio.
- Do not commit secrets, private audio, unauthorized datasets, or large output artifacts.
- Keep experimental work clearly labeled and separate from canonical behavior.

Run before requesting review:

```bash
cd moodify-core-package
python -m ruff check src tests ../tests
python -m pytest -q tests ../tests
```

### Adding files — check `.gitignore` first

This repository ignores broad patterns (`*.png`, `*.html`, `*.wav`, `*.json` subsets) with a
long list of `!` exceptions, and it has silently swallowed new files four times. **Before
adding any non-`.py` file:**

```bash
git check-ignore -v <path>
```

If it is ignored and should not be, add a narrow `!` exception rather than widening a
pattern.

## Ownership

A capability has exactly one canonical owner, and the dependency direction is one-way:

```text
protocol / contracts → core → CLI / apps
```

An interface must never keep its own copy of a sound algorithm, and a duplicate schema
definition is a defect. See [`protocol/schemas/README.md`](protocol/schemas/README.md) for
the schema owner map and the concrete harm it prevents.

Module owners are listed in [`MAINTAINERS.md`](MAINTAINERS.md). Working Groups
(WG-AUDIO, WG-PROTOCOL, WG-STUDIO, WG-EVIDENCE, WG-RESEARCH) form around problems and
dissolve when they are solved — see [`GOVERNANCE.md §2`](GOVERNANCE.md).

## Security

**Report vulnerabilities privately to the Stewards.** Do not open a public issue first.
Stewards own security response and coordinated disclosure — see
[`GOVERNANCE.md §10`](GOVERNANCE.md).

Never commit credentials, private audio, or personal data. Evidence artifacts must not
contain keys, tokens, or private recordings. The data policy, privacy statement, security
model, and threat model live in [`security/`](security).

## AI agents

Agents are welcome as contributors and must follow [`AGENTS.md`](AGENTS.md). An agent may
implement, refactor, test, benchmark, assemble evidence, and implement a MIP. An agent may
not decide what sounds better, the commercial direction, core identity, or whether human
listening judgment is replaced.

> **Agents have execution rights, not product sovereignty.**

Where a change raises a product-philosophy question, write `HUMAN_DECISION_REQUIRED` instead
of deciding it.

## Review expectations

Reviewers check architecture boundaries, test evidence, security and data handling,
compatibility, and whether a machine decision remains within its authorized scope. Changes
to Canon-controlled identity, authority, or data boundaries require `CANON_CHANGE = YES`
and a record in [`docs/canon/CANON_CHANGELOG.md`](docs/canon/CANON_CHANGELOG.md).
