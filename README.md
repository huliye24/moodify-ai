<p align="center"><img src="brand/assets/moodify-horizontal.png" alt="Moodify" width="100%"></p>

# Moodify

**An open protocol and reference implementation for evolving audio intelligence.**

> **Generated is not finished.**
> 生成，不等于完成。
>
> **Fork the code. Join the process.**
> 代码可以复制，过程需要参与。

[![Test](https://github.com/huliye24/moodify-ai/actions/workflows/test.yml/badge.svg)](https://github.com/huliye24/moodify-ai/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/License-GPL%20v3-blue)](LICENSE)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.10-3776AB?logo=python&logoColor=white)](moodify-core-package/pyproject.toml)

---

## Five layers, one product

```text
Moodify = Core + Protocol + Studio + App + Network
```

Not five products — five layers of one product, each with a single responsibility.

| Layer | Responsibility | Lives in |
|---|---|---|
| **Core** | Audio analysis, processing, verification, playback capability | [`moodify-core-package/`](moodify-core-package) |
| **Protocol** | Stable contracts between Core, Studio, App, agents and future integrations | [`protocol/`](protocol/README.md) + [`docs/protocol/`](docs/protocol/) |
| **Studio** | Creator-side desktop workspace: create, process, review, finish, publish | [`moodify-desktop/`](moodify-desktop) |
| **App** | **Personal music node**: receive, store, play — sharing comes later | Listener-side clients |
| **Network** | Connect personal music nodes and creators | **not implemented** — see below |

**One Core, many interfaces.** An interface must never keep its own copy of a sound
algorithm, and no capability has two owners.

### The first product loop

```text
Studio → Publish to My Library → Phone → Play
```

> *I finish a song on my computer, press Publish to My Library, and the song appears on my
> phone so I can immediately listen to it.*

That single loop, working reliably, is already a valid product. Social features grow from it
later — not the other way around. **None of it is built yet**; see the status table below.

### Two different things called "Network"

This is a real term collision, so it is stated plainly:

- **Moodify Network (product layer)** — connecting personal music nodes. **Not implemented.**
  In V1 it means exactly two nodes: your desktop and your own phone.
- **Moodify Network (collaboration)** — the open process around the Protocol, Core and
  Evidence: fork, experiment, produce evidence, open a MIP, and the result can re-enter the
  canonical project. This one is real and documented in [`GOVERNANCE.md`](GOVERNANCE.md).

### Product strategy

```text
stability > novelty · completion > ambition
working loop > architecture purity · maintainability > technical fashion
```

Mature, public, common technology first: `existing > standard library > mature OSS >
commodity service > custom > experimental`. The burden of proof is on custom and
experimental. See [`docs/canon/TECHNOLOGY_PRINCIPLES.md`](docs/canon/TECHNOLOGY_PRINCIPLES.md)
and [`docs/canon/PRODUCT_DEFINITION_V3.md`](docs/canon/PRODUCT_DEFINITION_V3.md).

---

## Clone

For normal development, use a shallow clone:

```bash
git clone --depth 1 https://github.com/huliye24/moodify-ai.git
cd moodify-ai
```

The active source tree is lightweight; the project has a comparatively large
historical object store. Most contributors do not need the entire history to build,
test, and open a pull request.

A shallow clone supports the normal loop — edit, commit, push, PR, tests, and both
repository guards — but `git log` shows only the current commit.

If you need more history, note that `--deepen` is **not** a gradual cost here: `main`
contains 31 merge commits, so a small deepen pulls whole merged branch histories with
it (measured: `--deepen=5` took a 27 MB clone to 70 MB; `--deepen=25` to 240 MB).
Prefer a predictable complete fetch:

```bash
git fetch --unshallow
```

Background and measurements:
[`docs/repository/REPOSITORY_SIZE_AUDIT.md`](docs/repository/REPOSITORY_SIZE_AUDIT.md).

---

## Quick start

Two interfaces share the Core. **CLI** is the Creator side — the action is `PROCESS`.
**App** is the Listener side — the action is `PLAY`.

```bash
python -m pip install -e moodify-core-package
```

Save this as `job.json`, with the audio beside it at `audio/source.wav`. Relative paths in a
job resolve against the job file's own directory.

```json
{
  "protocol": "moodify.sound/0.1",
  "source": "audio/source.wav",
  "preset": "clean_master",
  "output_dir": "outputs"
}
```

```bash
moodify protocol validate job.json
moodify protocol process  job.json
```

The CLI writes JSON to stdout (errors to stderr as JSON, exit code 2). The result carries
the output WAV path, input and output SHA-256, the parameters actually applied, and
diagnostics, with status `processed_review_required`.

> **`processed_review_required` means the execution path completed. It does not mean the
> audio is finished.** Human listening and release authority are not delegated to the
> protocol. That is the whole point of *Generated is not finished.*

Presets: `clean_master`, `warm_vocal`, `wide_space`. Human workbench:
[`moodify-desktop/`](moodify-desktop).

## What is verified, and what is not

This project separates what has been demonstrated from what is aspirational, and says which
is which.

**Demonstrated.** The protocol validate/process path runs end to end through the Core and
returns hash-verified artifacts. The measurement, diagnosis, and controlled-intervention
capabilities are implemented and tested in Core. Private deployment works from `pip`.

**Not demonstrated.** Automated perceptual validation. A complete
Import → Analyze → Diagnose → Plan → Process → Verify → Export finishing session. An
editable Mix Graph. Cloud production carrying real listening traffic.

**Not built at all** — the entire first product loop above. There is no publish action, no
track package, no LAN transfer or pairing, no Android receive, and no local library. A
repository-wide search finds no `publish to my library`, `lan sync`, `pairing token`, or
`local transfer` implementation. The same applies to identity, accounts, device
registration, and every Network feature.

**Unresolved.** Cloud runtime state is unverified — the database check was blocked and the
record says so rather than guessing. See
[`docs/REPOSITORY_STATUS.md`](docs/REPOSITORY_STATUS.md) and
[`docs/evidence/README.md`](docs/evidence/README.md).

Never promote a capability to canonical because a document claims it. Evidence is authority
tier 4 ([`docs/canon/AUTHORITY_ORDER.md`](docs/canon/AUTHORITY_ORDER.md)).

## Repository layout

```text
moodify-ai/
├── moodify-core-package/   # Core: the audio intelligence (679 files)
├── protocol/               # Protocol layer: specs, schemas, conformance, MIPs
├── moodify-desktop/        # Studio — the Creator-side workbench
├── apps/                   # Listener-side clients (Android, ear-workbench)
├── docs/
│   ├── canon/              # Authority: identity, boundaries, authority order
│   ├── protocol/           # Sound Protocol specifications
│   ├── evidence/           # Verified runtime evidence (authority tier 4)
│   ├── governance/         # Network process + engineering constraints
│   └── restructure/        # The 2026-10-03 restructure record
├── ops/                    # Deployment, node operation, web origin
├── security/               # Data policy, privacy, threat model
├── schemas/canonical/      # Generated Core contracts
└── tests/                  # Root-level integration tests
```

Supporting: `moodify-music-package/` (music domain API), `moodify_runtime/` (commerce),
`examples/`, `benchmark/`, `research/`, `scripts/`, `brand/`.

## Governance in one paragraph

Stewards hold mission, Canon, brand, signing, and security response. Maintainers review and
merge. Working Groups form around problems and dissolve. Anyone may contribute — and
contribution is not counted in commits: twenty documented A/B judgments from a mastering
engineer may be worth more than a large patch. Protocol, schema, contract, governance, and
compatibility changes require a **MIP**, and a proposal cannot be accepted without evidence.

AI agents write code, run benchmarks, and implement MIPs. They do not decide what sounds
better, where the project goes commercially, or whether human listening judgment is
replaced. **Agents have execution rights, not product sovereignty.**

**No token. No DAO. No airdrop. No treasury governance.** Contribution, review, evidence,
release, and governance come first.

## Contributing

Read [`AGENTS.md`](AGENTS.md) (repository authority), [`GOVERNANCE.md`](GOVERNANCE.md), and
[`CONTRIBUTING.md`](CONTRIBUTING.md). Before changing behavior, data authority, or product
language, read [`docs/canon/`](docs/canon/).

```bash
cd moodify-core-package
python -m ruff check src tests ../tests
python -m pytest -q tests ../tests
```

Want to propose a change to the protocol? Start with
[`protocol/mips/MIP-0000-template.md`](protocol/mips/MIP-0000-template.md).

## License

**GNU GPL v3.0 only.** See [LICENSE](LICENSE). Copyright 荣景文川 2024–2026.

---

**Moodify — every voice deserves to be heard.**
每一种声音，都值得被世界听见。
