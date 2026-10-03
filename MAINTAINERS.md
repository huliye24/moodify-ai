# Maintainers

Who currently holds which role. Roles and their powers are defined in
[`GOVERNANCE.md`](GOVERNANCE.md).

**This file is deliberately short and truthful.** Moodify does not invent a community it
does not have. Most roles below are open, and that is stated plainly rather than filled
with names that would not answer a pull request.

*Last updated: 2026-10-03*

---

## Project Stewards

Owns mission, Canon, brand, release signing, security response, Maintainer appointments,
major product boundaries, and final protocol publication.

| Steward | Contact | Since |
|---|---|---|
| 荣景文川 (`huliye24`) | GitHub [@huliye24](https://github.com/huliye24) | project founding |

Sole Steward at present. Stewardship is expected to widen as the Network develops; see
[`GOVERNANCE.md §12`](GOVERNANCE.md).

## Core Maintainers

Review and merge PRs, manage releases and CI, approve implementation-level RFCs.

| Maintainer | Scope |
|---|---|
| 荣景文川 (`huliye24`) | all areas, currently |

**Open.** Additional Core Maintainers are wanted — particularly for the areas below.

## Protocol Maintainers

Own `protocol/` — specs, schemas, conformance, and the MIP process.

| Maintainer | Scope |
|---|---|
| *vacant* | — |

Until this is filled, protocol changes route through the Steward.

## Studio Maintainers

Own `moodify-desktop/` and the Creator-side workflow.

| Maintainer | Scope |
|---|---|
| *vacant* | — |

## Evidence Maintainers

Own `docs/evidence/`, A/B and listening review, benchmarks, and evaluation protocol.

| Maintainer | Scope |
|---|---|
| *vacant* | — |

## Working Groups

Open groups that form around a problem for a period of time — not permanent departments.

| Group | Concern | Status |
|---|---|---|
| WG-AUDIO | sound analysis, DSP, processing | open |
| WG-PROTOCOL | protocol, schemas, conformance | open |
| WG-STUDIO | CLI, desktop, workflow, UX | open |
| WG-EVIDENCE | A/B, benchmark, listening review, evaluation | open |
| WG-RESEARCH | new methods, papers, experiments | open |

## Review Network

Mix and mastering engineers, producers, musicians, listeners, and researchers who
contribute perceptual judgments rather than code. This is the layer that makes Moodify a
sound project instead of a generic repository.

| Member | Domain |
|---|---|
| *open* | — |

**This is the role with the lowest barrier and the highest current value to the project.**
Twenty well-documented A/B judgments are worth more here than a large code contribution —
see [`GOVERNANCE.md §5`](GOVERNANCE.md).

## AI agents

Agents contribute code, tests, benchmarks, evidence assembly, and reviews. They hold
**execution rights and no product sovereignty** — see [`GOVERNANCE.md §8`](GOVERNANCE.md)
and [`AGENTS.md`](AGENTS.md).

| Agent | Role | Notes |
|---|---|---|
| AI coding agents | execution | Commits authored by agents are attributed in git history under `Cursor Assistant` and similar identities. Agent authorship does not convey Maintainer status or decision rights. |

## Module ownership

Code ownership follows the dependency direction enforced by
[`AGENTS.md`](AGENTS.md): `protocol / contracts → core → CLI / apps`. A capability has
exactly one canonical owner; no interface keeps a private copy of a sound algorithm.

| Module | Path | Owner |
|---|---|---|
| Core | `moodify-core-package/` | Core Maintainers |
| Protocol | `protocol/` | Protocol Maintainers |
| Studio | `moodify-desktop/` | Studio Maintainers |
| Evidence | `docs/evidence/` | Evidence Maintainers |

Unassigned modules fall to the Core Maintainers.

---

## How to become a Maintainer

There is no formal ladder, and no commit-count threshold — `GOVERNANCE.md §5` explicitly
rejects measuring contribution in commits. In practice, Maintainers are Contributors who
have shown sustained, careful judgment in a specific area, including the willingness to
say "the evidence does not support this".

If you want a role, open an issue describing the area you want to own and what you have
already contributed to it. Stewards appoint Maintainers.
