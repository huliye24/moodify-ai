# protocol/

The rules layer — what a valid job, artifact, and claim look like, and how conformance is
checked.

```text
protocol/
├── specs/         normative specifications
├── schemas/       machine-readable schemas
├── conformance/   tests that decide whether an implementation conforms
└── mips/          Moodify Improvement Proposals
```

## What lives here

**The Moodify Sound Protocol.** A declarative sound job that AI systems, agents, CLIs, apps,
and third-party software can all submit to the same Core.

Current normative specification:
[`../docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md`](../docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md)
(superseded in part by
[`_0_2.md`](../docs/protocol/MOODIFY_SOUND_PROTOCOL_0_2.md)).

The specification text stays in `docs/protocol/` where it has always lived, so existing
links keep working. This directory is the **structural** home of the protocol layer:
schemas, conformance, and proposals.

Minimal job shape:

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
moodify protocol process job.json
```

A `processed_review_required` status means the execution path completed. **It does not mean
the audio passed professional validation.** Human listening and release authority are not
delegated to the protocol — `Generated is not finished.`

## MIPs

Changes to the protocol, a schema, a Core behavior contract, governance, the evidence
format, or public compatibility require a Moodify Improvement Proposal.

- [`mips/MIP-0000-template.md`](mips/MIP-0000-template.md) — how to write one
- [`mips/MIP-0001-moodify-network-governance.md`](mips/MIP-0001-moodify-network-governance.md) — the governance proposal

Lifecycle: `DRAFT → DISCUSSION → EXPERIMENTAL → EVIDENCE → ACCEPTED → IMPLEMENTED → RELEASED`.
Ordinary bug fixes do not need a MIP.

## A note on this directory's history

Before 2026-10-03 this path held the **MOOD Protocol** — an unrelated Web3 line (EVM/BSC
mainnet BEP-20 token, node registry, reputation, contribution). It was moved out of the
mainline on that date and now lives on disk as `mood-web3-protocol/`, untracked. See
[`../docs/ARCHIVE_INDEX.md`](../docs/ARCHIVE_INDEX.md).

The two are not the same thing, and the collision is worth knowing about: a directory named
`protocol/` that contained a different protocol was a substantial source of confusion. This
is why the current contents are stated explicitly above.

## Governance

Roles, powers, and the decision process are in [`../GOVERNANCE.md`](../GOVERNANCE.md) and
[`../docs/governance/NETWORK.md`](../docs/governance/NETWORK.md).
