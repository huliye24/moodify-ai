# MIP-0001 — Moodify Network Governance

```yaml
mip: 0001
title: Moodify Network Governance
author: 荣景文川 (huliye24)
status: DRAFT
type: Governance
created: 2026-10-03
requires: none
supersedes: none
```

> **Status note.** The structure described here was established on 2026-10-03 under an
> explicit human instruction (the MOODIFY_NETWORK_RESTRUCTURE_001 task), which is the
> highest authority in `docs/canon/AUTHORITY_ORDER.md`. This MIP is the formal ratification
> of that structure. It is deliberately left at `DRAFT` rather than self-declaring
> `ACCEPTED`: a governance process that exempts its own founding document from its own
> stages would not be worth adopting. Ratification by the Steward moves it forward through
> the normal lifecycle.

---

## Abstract

Defines what Moodify Network is, the roles within it, how decisions are made, and how the
project is meant to keep producing future versions after its code is freely forkable.

This proposal does not change any audio behavior. It changes who may decide what.

## Motivation

Moodify's repository carried the accumulated structure of several abandoned product lines:
multiple competing Core implementations, four competing "product identities", parallel
platform scaffolds, and a Web3 token line. An agent or a new contributor could not answer
"what is Moodify?" from the tree in any reasonable time. Three separate prior reduction
plans had been written and none executed.

The deeper problem was not clutter. It was that the project had **no stated process for
deciding what to keep**. Without one, every future feature accumulates the same way, and
forking the repository would produce a copy with the same problem.

Moodify's premise is that its durable asset is not the code — anyone may fork that — but the
process that keeps generating the next version:

```text
Moodify Moat ≠ Code
Moodify Moat = Process × History × Network
```

A stated governance process is the minimum required to make that true.

## Specification

### 1. Definition

**Moodify Network is the open collaboration network around the Moodify Protocol, Core,
Evidence, and the contribution process.** It is not a team alias, not a DAO, and not a
return to Web3.

### 2. Roles

```text
Project Stewards → Core Maintainers → Working Groups → Contributors → Review Network
```

Plus AI Agents, which hold execution rights and no product sovereignty.

Powers and limits are specified in [`GOVERNANCE.md`](../../GOVERNANCE.md) §3–§8.

### 3. Decision rule

Moodify decides by **proposal + experiment + evidence** — not by volume, seniority, or
authority:

```text
Problem → Proposal → Experiment → Process → A/B → Evidence
       → Human Review → Merge → Release → Real-world use → Feedback → Next Proposal
```

### 4. MIP process

Changes to the protocol, a schema, a Core behavior contract, governance, the evidence
format, or public compatibility require a MIP. Ordinary bug fixes do not.

```text
DRAFT → DISCUSSION → EXPERIMENTAL → EVIDENCE → ACCEPTED → IMPLEMENTED → RELEASED
```

Terminal states: `REJECTED`, `WITHDRAWN`, `SUPERSEDED`.

A proposal cannot reach `ACCEPTED` without a populated Evidence section. Negative and
inconclusive results are valid evidence and must be recorded rather than suppressed.

### 5. Human authority and agent limits

**AI is an executor of capability, not the authority of product direction.** Agents may
implement, refactor, test, benchmark, assemble evidence, and implement MIPs. Agents may not
decide what sounds better, the commercial direction, core identity, or whether human
listening judgment is replaced. Conflicts that are product-philosophy questions must be
recorded as `HUMAN_DECISION_REQUIRED`.

This restates `AGENTS.md`, which remains authoritative and is not modified by this MIP.

### 6. No token governance

```text
NO TOKEN · NO DAO · NO AIRDROP · NO TREASURY GOVERNANCE
```

Contribution, review, evidence, release, and governance come first. Any economic mechanism
is a later question requiring its own MIP.

### 7. Repository consequences

- One canonical Core; one canonical `moodify` console entry point; one owner per capability.
- Dependency direction is one-way: `protocol/contracts → core → CLI/apps`.
- Structural regressions are prevented by `scripts/check_repo_structure.py` in CI, not by
  convention alone.

## Rationale

**Why not a DAO or token?** A governance mechanism adopted before a working discipline
substitutes process for substance. The project's actual bottleneck is evidence quality and
review capacity, not incentive alignment.

**Why not keep the Web3 line inside this mainline?** It is a different project with a
different subject matter (a deployed BEP-20 token) and a different audience. It was moved
out, not deleted — see [`docs/ARCHIVE_INDEX.md`](../../docs/ARCHIVE_INDEX.md).

**Why Working Groups instead of departments?** Permanent departments calcify. A Working
Group forms around a problem and dissolves when it is solved.

**Why is the Review Network a first-class role?** Moodify is a sound project. A mix engineer
contributing twenty documented A/B judgments may advance it more than a large patch.
Measuring contribution in commits would systematically undervalue the most important
contributors.

**Alternative considered: permissive contributions with Steward veto.** Rejected — a veto
model still accumulates unreviewed work and produces exactly the clutter this proposal
exists to prevent.

## Backwards compatibility

- **No protocol change.** No schema, job, or artifact changes.
- **No code change.** This MIP is documentation plus a structural guard.
- **Breaking for one thing only:** the repository no longer accepts a second public product
  identity, a second Core, or a second `moodify` console entry point. Contributions that
  assume otherwise must be re-proposed.
- **Rollback:** revert the governance commits. Recorded in
  [`docs/restructure/CLEANUP_MANIFEST.md`](../../docs/restructure/CLEANUP_MANIFEST.md), with
  the full pre-change tree at tag `pre-network-restructure-2026-10-03`.

## Evidence

This MIP's evidence is the repository state before and after the 2026-10-03 restructure.

| What was measured | How | Result | Artifact |
|---|---|---|---|
| Baseline tracked files | `git ls-files` at `c11bc7f5` | 2760 | [`docs/restructure/BEFORE_TREE.txt`](../../docs/restructure/BEFORE_TREE.txt) |
| Duplicate `moodify` console entry points | `git grep 'moodify = '` across `*.toml` | **2** conflicting declarations (`moodify-core-package`, `demo`) | [`CLEANUP_MANIFEST.md`](../../docs/restructure/CLEANUP_MANIFEST.md) |
| Duplicate schema definitions | schema census | `contribution.schema.json`, `evidence.schema.json`, `reputation-evidence.schema.json` — **4 copies each**, two live copies differing in `$schema` (draft-07 vs 2020-12) while sharing one `$id` | idem |
| Competing public product identities | dir census | `moodify-qa`, `moodify-qa-desktop`, `moodify-pulse`, `products/{qa,master,rating,supply}` | idem |
| Test baseline before removal | `pytest -q tests ../tests` | **1197 passed, 5 skipped, 0 failed** | this document |
| Test result after Phase 1 | `pytest -m v01` | **265 passed, 5 skipped** | this document |
| `ruff` before and after | `ruff check src tests ../tests` | clean → clean | this document |

**Reproducibility.** Every removal is reversible:

```bash
git checkout pre-network-restructure-2026-10-03 -- <path>
```

**Negative result, recorded.** The 2026-10-03 restructure did **not** resolve several items,
and they remain open rather than being quietly closed by this proposal: which of the two
Android clients is current; the deployment path for the web surface after it left the
mainline; the disposition of the MOOD Protocol layer embedded in Core; the future of
`moodify_runtime/`; and a 4.0 GB git history that materially undercuts the
public-collaboration goal. All six are listed in
[`RESTRUCTURE_REPORT.md`](../../docs/restructure/RESTRUCTURE_REPORT.md). A governance
proposal that claimed to have settled them would be its own first counterexample.

## Human review

The governance change itself requires Steward ratification — this MIP is the request.

The Review Network is explicitly created as the channel for perceptual judgment that
machines may not supply. No clause in this MIP permits an automated gate to replace human
listening authority over finished audio.

## Reference implementation

- [`GOVERNANCE.md`](../../GOVERNANCE.md) — roles, powers, limits, conflict resolution
- [`MAINTAINERS.md`](../../MAINTAINERS.md) — current holders (mostly vacant, stated honestly)
- [`docs/governance/NETWORK.md`](../../docs/governance/NETWORK.md) — the process loop
- [`docs/governance/constraints/`](../../docs/governance/constraints/CONSTRAINT_REGISTRY.md) — ME-001…ME-003
- `scripts/check_repo_structure.py` — the structural guard enforcing §7

## Test plan

```bash
# structural guard (added in Phase 7 of the restructure)
python scripts/check_repo_structure.py

# exactly one 'moodify' console entry point
git grep -n 'moodify = ' -- '*.toml' '*.cfg'

# the pre-change tree is recoverable
git rev-parse pre-network-restructure-2026-10-03
```

## Security and privacy considerations

No new attack surface. This MIP adds no runtime code. It does assign security response to
the Stewards and forbids credentials, private audio, and personal data in evidence
artifacts — see [`GOVERNANCE.md §10`](../../GOVERNANCE.md) and `security/`.

## Unresolved questions

1. When, and whether, additional Stewards should be appointed.
2. Whether the Working Groups should have named initial members or remain open until they
   self-organize.
3. Whether a Contributor License Agreement or DCO is needed. `CONTRIBUTING.md` currently
   requires neither.
4. How the Review Network's judgments are versioned and attributed as evidence — the
   evidence format for perceptual data is not yet specified.
5. Whether the Evidence layer warrants a schema of its own, or stays a documented
   convention plus `docs/evidence/` structure.

## Copyright

GPL-3.0-only, matching this repository.
