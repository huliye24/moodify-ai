# Moodify Network

What the Network is, and the loop that makes it worth joining.

Companion documents: [`GOVERNANCE.md`](../../GOVERNANCE.md) (roles and powers),
[`MAINTAINERS.md`](../../MAINTAINERS.md) (who holds them),
[`constraints/`](constraints/CONSTRAINT_REGISTRY.md) (engineering constraints ME-001…ME-003).

---

## The premise

Moodify does not treat "nobody can see our code" as a moat.

```text
Moodify Moat ≠ Code
Moodify Moat = Process × History × Network
```

Anyone can fork a version of Moodify — and is welcome to. What is hard to fork is the
process that keeps producing the *next* version: the accumulated cases, A/B judgments,
parameter experience, failure records, benchmarks, contributors, agents, and professional
engineering judgment.

> **A competitor can copy a version. Moodify Network intends to own the ability to produce
> the next one.**

This is why the repository is public, and why the governance spends its effort on
continuity — standards, review quality, release trust, history, and network density —
rather than on restricting access.

## The loop

```text
Problem
  ↓
Proposal        (MIP — see protocol/mips/)
  ↓
Experiment
  ↓
Process
  ↓
A/B
  ↓
Evidence        (docs/evidence/)
  ↓
Human Review
  ↓
Merge
  ↓
Release
  ↓
Real-world use
  ↓
Feedback
  ↓
Next Proposal
```

Moodify decides by **proposal + experiment + evidence**, not by who argues hardest or who
holds the most authority. A change that cannot point at evidence has not finished the loop.

## Forking is an entry point, not an exit

```text
Fork → Experiment → Evidence → MIP / PR → Review → Canonical Moodify
```

You do not need permission to fork, and you do not need to be a Maintainer to run an
experiment. You need evidence, a proposal, and review for the result to re-enter the
canonical project.

What the Network protects is therefore not the code but:

```text
continuity · standards · review quality · release trust · history · network density
```

## The three layers

| Layer | Directory | Holds | Changed by |
|---|---|---|---|
| **Protocol** — 规则层 | `protocol/` | Specs, schemas, conformance, MIPs | MIP + Steward approval |
| **Core** — 能力层 | `moodify-core-package/` | Analysis, DSP, processing, playback, verification, contracts | Maintainer review |
| **Evidence** — 经验层 | `docs/evidence/` | Cases, A/B results, benchmarks, decisions, run captures | Evidence review |

The dependency direction is one-way and enforced:

```text
Protocol / Contracts
        ↓
       Core
        ↓
 ┌──────┴──────┐
 CLI          Apps
```

An interface must never hold its own copy of a sound algorithm. A capability has exactly
one canonical owner. (See `AGENTS.md`, "One Core, Multiple Interfaces".)

## The Evidence layer

Every accepted change that affects sound should be traceable to:

```text
source hash · core version · protocol version · parameters · processing graph
before metrics · after metrics · A/B result · human review
agent version · timestamp · reproducibility info
```

This is not a secret database. It exists so that **Moodify can answer why it became what it
is** — as opposed to "because someone thought it sounded better".

The lowest acceptable answer to "why this change?" is a measurement. The next is a
measurement plus a judgment. The best is a measurement, a judgment, and a reproduction
command.

### Evidence discipline

Where evidence is insufficient, the record says so. The repository's W01-P00 evidence index
is the model: it registers every claim with a source, a timestamp, and a confidence level,
and it explicitly records what could **not** be verified — a blocked database check, a
medium-confidence finding that could not be reproduced.

Never manufacture certainty. `AGENTS.md` requires the same of machine judgment: an
out-of-scope or uncertain case must produce `HUMAN_REQUIRED` or `INCONCLUSIVE`, never
invented confidence.

## Professional judgment is a first-class contribution

Moodify is a sound project, so the Network needs people who listen, not only people who
compile:

```text
Mix Engineer · Mastering Engineer · Producer · Musician · Listener · Researcher
```

They contribute A/B preferences, processing failures, artifact reports, perceptual
judgments, reference-track observations, edge cases, and device playback differences. Their
output accumulates into the professional experience layer.

This is why [`GOVERNANCE.md §5`](../../GOVERNANCE.md) refuses to measure contribution in
commits: one engineer's twenty careful A/B judgments can outweigh a large patch.

## AI agents in the loop

Agents are contributors with execution rights. They may write code, run benchmarks,
generate tests, scan for regressions, assemble evidence, build reports, and implement MIPs.

They may not decide what sounds better, where the project should go commercially, whether
the core identity changes, or whether human listening judgment is replaced.

> **Agents have execution authority. Humans retain product sovereignty.**

## Why not token governance

```text
NO TOKEN · NO DAO · NO AIRDROP · NO TREASURY GOVERNANCE
```

None of these is required for the Network to exist, and adopting them before the process
works would substitute a mechanism for a discipline. Contribution, review, evidence,
release, and governance come first; economic mechanisms are a later question and a MIP.

For the record, so that history is not silently erased: this repository previously carried
an active MOOD Protocol line with a deployed BEP-20 token. It was moved out of this
mainline on 2026-10-03 — see [`docs/ARCHIVE_INDEX.md`](../ARCHIVE_INDEX.md). That line is
not Moodify Network, and the rule above governs the Network.

## What success looks like

A first-time visitor understands within a minute what Moodify is, where the protocol lives,
where the Core lives, how to run it, how to contribute, and how to propose a MIP.

A year from now, someone can ask "why is this threshold what it is?" and get an answer that
cites a case, a measurement, and a review — not a person's recollection.
