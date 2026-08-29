# Execution Plan

## Gate 0 — Preflight

- read Package 009 final report;
- confirm 009 exit condition;
- run `git status`;
- record branch and HEAD;
- locate Distributor source/tests/deployment scripts;
- locate Package 004 snapshot tooling;
- locate candidate canonical snapshot;
- scan for secrets;
- confirm BSC RPC read access.

## Gate A — Contract Freeze

Run tests, inspect constructor/config, replay/double-claim protection, root/admin functionality, compiler settings, then freeze commit/artifact.

## Gate B — Snapshot Freeze

Generate canonical snapshot, hash it, count participants, total allocation, generate root twice, compare results, and produce a human-review table.

## Gate C — Dry Run

Build, simulate, estimate BNB gas, inspect constructor arguments, and prepare an unsigned deployment payload. Do not broadcast.

## Gate D — Human Signature #1

Pause. Human reviews exact chain, deployer, artifact, MOOD address, root, participant count, allocation total and gas estimate, then signs outside Codex custody.

## Gate E — Post-Deploy Verification

Confirm tx receipt, distributor address, code, MOOD reference, Merkle root, owner/admin state and BscScan verification.

## Gate F — Funding Plan

Calculate exact required MOOD funding and present the human funding card.

## Gate G — Human Signature #2

Human signs the MOOD transfer. Codex does not control signer.

## Gate H — Funding Verification

Confirm receipt and distributor `balanceOf`.

## Gate I — Staging Integration

Configure real distributor address in staging. Keep claim disabled.

## Gate J — Freeze

Record all hashes, txs, addresses, deployment version and final report. Do not start Package 011.
