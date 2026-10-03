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

## Three things, one system

### Protocol — the rules

A declarative **sound job**: a JSON document naming a source, a preset, and an output
location. AI systems, agents, CLIs, apps, and third-party software all submit the same job
to the same Core and get back a machine-readable record of what happened.

→ [`docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md`](docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md) ·
[`protocol/`](protocol/README.md) · [proposals](protocol/mips/)

### Core — the capability

The single home of the audio intelligence: analysis, DSP, processing, playback,
verification, contracts. **One Core, many interfaces.** An interface must never keep its own
copy of a sound algorithm — and no capability has two owners.

→ [`moodify-core-package/`](moodify-core-package) · contracts in
[`schemas/canonical/`](schemas)

### Network — the process

The open collaboration around the Protocol, Core, and Evidence. Forking is an entry point,
not an exit: run an experiment, produce evidence, open a MIP, and the result can re-enter
the canonical project.

```text
Problem → Proposal → Experiment → Process → A/B → Evidence
       → Human Review → Merge → Release → Real-world use → Feedback → ↻
```

→ [`GOVERNANCE.md`](GOVERNANCE.md) · [`docs/governance/NETWORK.md`](docs/governance/NETWORK.md) ·
[`CONTRIBUTING.md`](CONTRIBUTING.md)

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
