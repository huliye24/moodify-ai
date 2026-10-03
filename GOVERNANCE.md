# GOVERNANCE

How Moodify decides things.

> **Fork the code. Join the process.**
> 代码可以复制，过程需要参与。

Moodify does not try to stop anyone from forking it. It tries to be the place where the
next version gets made. What is protected here is *continuity* — standards, review quality,
release trust, history, and network density — not the secrecy of the source.

---

## 1. What Moodify Network is

**Moodify Network is the open collaboration network around the Moodify Protocol, Core,
Evidence, and the contribution process.**

It is not:

- a synonym for an in-house engineering team;
- a DAO, and not a return to Web3;
- a token, airdrop, treasury, or wallet scheme — see §9.

It is three things held together:

```text
                    Moodify Network
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
     Protocol            Core            Evidence
      规则层             能力层             经验层
        │                 │                 │
       MIP            DSP / Audio          Cases
     Schemas            Processing         A/B
    Contracts           Playback           Review
   Conformance        Verification        Benchmarks
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                    Contribution
                          │
                          ▼
                    Real-world use → Feedback → next cycle
```

**Protocol** is the rules — what a valid job, artifact, and claim look like, and how
conformance is checked. **Core** is the capability — the single home of audio
intelligence. **Evidence** is the experience — what we tried, what happened, and why we
believe what we believe. The loop that turns these into a next version is in
[`NETWORK.md`](docs/governance/NETWORK.md).

## 2. Roles

Five layers, deliberately small. Do not invent permanent departments.

```text
Moodify Project
├── Project Stewards
├── Core Maintainers
├── Working Groups      WG-AUDIO · WG-PROTOCOL · WG-STUDIO · WG-EVIDENCE · WG-RESEARCH
├── Contributors
└── Review Network      mix/mastering engineers, producers, musicians, listeners, researchers
```

Plus **AI Agents**, which hold execution rights and no product sovereignty (§8).

## 3. Project Stewards

The Stewards own the continuity of the project. Their job is not to write the most code.
It is to keep the river flowing in the right direction.

Stewards decide:

- the mission and the Canon;
- brand and trademark;
- release signing;
- security response;
- appointing and removing Maintainers;
- major product-boundary questions;
- final publication of protocol versions.

Stewards do **not** monopolize code contributions, technical ideas, research, plugins, or
implementations. Steward ships the direction; Stewards do not need to carry every drop of
water.

If a legal entity is needed (brand, signing, infrastructure hosting), the founding company
may hold it. The distinction between **the Company** and **the Open Project** is
deliberate and must not be collapsed: the Company is a participant in the project, not the
project itself.

## 4. Core Maintainers

Maintainers are the repository's technical custodians. They may:

- review and merge pull requests;
- manage releases and CI;
- approve implementation-level RFCs;
- manage module ownership.

Maintainers may **not** unilaterally change:

- what Moodify *is*;
- core product boundaries;
- whether human listening judgment is replaced by machines;
- the fundamental governance principles of the Protocol.

Those require a MIP plus Steward approval — see §6.

## 5. Contributors and the Review Network

Anyone may become a Contributor. Contribution is not only code:

```text
CODE · PROTOCOL · CASE · REVIEW · BENCHMARK · DATASET
DOCUMENTATION · RESEARCH · BUG · PLUGIN · INTEGRATION
```

A professional mix engineer submitting twenty high-quality A/B judgments may be worth more
than two thousand lines of code. **Do not measure contribution in commits.**

The **Review Network** is what makes this a sound project rather than a generic open-source
repository. Mix and mastering engineers, producers, musicians, listeners, and researchers
need not write any code. They submit A/B preferences, processing failures, artifact
reports, perceptual judgments, reference-track observations, edge cases, and device
playback differences.

That accumulated judgment is the professional experience layer, and it is the asset the
project is actually building.

## 6. Moodify Improvement Proposals (MIP)

A MIP is required to change:

```text
the protocol · a schema · a core behavior contract
governance · the evidence format · public compatibility
```

Ordinary bug fixes do not need a MIP.

Lifecycle:

```text
DRAFT → DISCUSSION → EXPERIMENTAL → EVIDENCE → ACCEPTED → IMPLEMENTED → RELEASED
```

Also terminal: `REJECTED`, `WITHDRAWN`, `SUPERSEDED`.

Moodify does not decide by who is loudest. It decides by **proposal + experiment +
evidence**. Templates and the process live in [`protocol/mips/`](protocol/mips/); the
first substantive proposal is
[`MIP-0001`](protocol/mips/MIP-0001-moodify-network-governance.md).

## 7. Release authority

- The **Protocol** version is published by Stewards, following an accepted MIP.
- **Core** releases are cut by Maintainers.
- A release must state what was verified and what was not. Never write an unverified
  capability as if it were running — see `docs/canon/AUTHORITY_ORDER.md` and
  `docs/REPOSITORY_STATUS.md`.
- Human listening and release authority over *finished audio* is not delegated to any
  automated gate. `Generated is not finished.`

## 8. Human authority and AI agent limits

**AI is an executor of capability, not the authority of product direction.**
（AI 拥有能力执行权，人类保留产品定义权。）

This restates and is governed by `AGENTS.md`, which remains the authoritative text.

**AI agents may:** implement, refactor, test, implement CLI and schemas, work on
performance, fix bugs, sync documentation, search parameters, maintain CI, and execute
migrations — including writing code, running benchmarks, generating tests, scanning for
regressions, assembling evidence, and implementing MIPs.

**AI agents may not decide:** what counts as better-sounding, which commercial direction
the project takes, whether core product identity changes, or whether human final listening
judgment is replaced.

> **An agent has execution rights. It does not have product sovereignty.**
> （Agent 有执行权，没有最终产品主权。）

Where instructions conflict and the answer is a product-philosophy question, an agent must
write `HUMAN_DECISION_REQUIRED` rather than adjudicating it.

## 9. No token governance

Explicitly, at this stage:

```text
NO TOKEN · NO DAO · NO AIRDROP · NO TREASURY GOVERNANCE
```

None of these is a precondition for Moodify Network existing. Build contribution, review,
evidence, release, and governance first. Only then is it worth asking whether any other
economic mechanism is warranted.

**Note on the repository's history.** This repository previously carried an active MOOD
Protocol line — an EVM/BSC mainnet BEP-20 token with a deployed contract and DEX trading.
On 2026-10-03 that line was moved out of this mainline and is kept on disk but untracked;
it is documented in [`docs/ARCHIVE_INDEX.md`](docs/ARCHIVE_INDEX.md). Its existence is
recorded here so that history is not silently rewritten, and the "no token governance"
rule above applies to **Moodify Network** — which is a different thing from the MOOD token
line.

## 10. Security

- Report vulnerabilities privately to the Stewards; do not open a public issue first.
- The Stewards own security response and coordinated disclosure.
- Never commit secrets, private audio, or personal data. `security/` holds the data policy,
  privacy, security model, and threat model.
- Evidence artifacts must not contain credentials, keys, or private recordings.

## 11. Conflict resolution

1. **Prefer evidence over opinion.** A disagreement about a measurable fact is settled by
   measurement, not by seniority.
2. **Prefer the lower-authority change.** If two designs both work, take the one that
   changes less Canon.
3. **Escalate product-philosophy conflicts to the Stewards.** Technical conflicts go to the
   relevant Maintainers; if unresolved, to a Working Group; if still unresolved, to the
   Stewards.
4. **Record the decision.** A resolution that is not written down did not happen. Canon-level
   changes are logged in `docs/canon/CANON_CHANGELOG.md`.
5. **Do not hide counterexamples.** When evidence contradicts a constraint, record the
   conflict and request revision — do not suppress the evidence to preserve the principle.
   (This is `ME-002`; see [`docs/governance/constraints/`](docs/governance/constraints/).)

## 12. Amending this document

Changes to this file are governance changes and require a MIP, not a pull request alone.

---

## See also

- [`MAINTAINERS.md`](MAINTAINERS.md) — who currently holds each role
- [`docs/governance/NETWORK.md`](docs/governance/NETWORK.md) — the process loop in detail
- [`docs/governance/constraints/`](docs/governance/constraints/CONSTRAINT_REGISTRY.md) — ME-001…ME-003 engineering constraints
- [`AGENTS.md`](AGENTS.md) — repository authority and agent rules
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to submit work
- [`docs/canon/AUTHORITY_ORDER.md`](docs/canon/AUTHORITY_ORDER.md) — which document wins
