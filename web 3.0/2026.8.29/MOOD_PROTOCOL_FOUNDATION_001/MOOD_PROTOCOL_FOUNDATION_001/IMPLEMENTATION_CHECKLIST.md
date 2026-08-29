# MPF-001 Implementation Checklist

Use this checklist during implementation. It is intentionally ordered from discovery to freeze.

## A. Baseline

- [ ] Record base branch SHA.
- [ ] Create isolated work branch.
- [ ] Read repository authority/canon files.
- [ ] Run current relevant tests before edits.
- [ ] Record existing failures separately; do not attribute them to MPF-001.

## B. Discover facts

- [ ] Search repository for MOOD chain/token constants.
- [ ] Search all environment templates.
- [ ] Search Web3 provider/client code.
- [ ] Search claim/distribution code.
- [ ] Search deploy artifacts and contract scripts.
- [ ] Search launch/runbook docs.
- [ ] Search tests/fixtures for hidden duplicate constants.
- [ ] Verify public-chain facts read-only where possible.

## C. Build canonical source

- [ ] Add `protocol/mainnet.schema.json`.
- [ ] Add `protocol/mainnet.json`.
- [ ] Fill only evidence-backed values.
- [ ] Use `null` / decision flags for unknown values in draft.
- [ ] Store atomic supply as a decimal string.
- [ ] Store only public addresses.

## D. Reconcile consumers

- [ ] Inventory every duplicated identity value.
- [ ] Choose direct read or thin generated adapter.
- [ ] Preserve testnet/dev isolation.
- [ ] Keep transport overrides separate from identity facts.
- [ ] Remove or label conflicting production constants.
- [ ] Avoid broad refactors.

## E. Evidence docs

- [ ] Add `docs/protocol/MAINNET.md`.
- [ ] Add `docs/protocol/ADDRESSES.md`.
- [ ] Add `docs/protocol/MAINNET_EVIDENCE.md`.
- [ ] Ensure docs point back to canonical JSON.

## F. Validation

- [ ] Add validator.
- [ ] Test invalid EVM address case if EVM.
- [ ] Test invalid Solana address case if Solana.
- [ ] Test bad decimals.
- [ ] Test floating/non-integer supply rejection.
- [ ] Test duplicate RPC rejection.
- [ ] Test locked-with-placeholder rejection.
- [ ] Test draft allowed with unresolved facts.

## G. Lock

- [ ] Resolve all human-decision fields before lock.
- [ ] Set locked timestamp.
- [ ] Record source commit.
- [ ] Validate.
- [ ] Generate lock file.
- [ ] Revalidate.
- [ ] Run tests/build.

## H. Final audit

- [ ] `git diff` has no secrets.
- [ ] no chain write was performed.
- [ ] no new dependency is required for the validator if avoidable.
- [ ] no unrelated UI/audio/product changes.
- [ ] final report follows Acceptance Gate format.
