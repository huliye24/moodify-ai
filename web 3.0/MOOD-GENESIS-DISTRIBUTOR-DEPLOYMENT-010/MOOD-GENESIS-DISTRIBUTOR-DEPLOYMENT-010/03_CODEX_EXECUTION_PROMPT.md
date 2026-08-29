# Codex Execution Prompt

Read every file in this package before acting.

## Known inputs

- Repo: `huliye24/moodify-ai`
- Chain: BNB Smart Chain Mainnet
- Chain ID: `56`
- MOOD: `0x1BB3115D43E397f7bb586F090831B02cA639e73E`
- Contract: `MoodGenesisDistributor`
- Staging: `test.crestwavecoin.com`

## Mission

Deploy and fund the Genesis Distributor through explicit human-controlled signatures, verify it, configure its public address in staging, and keep claims disabled.

## Mandatory order

1. Confirm Package 009.
2. Audit real distributor source and tests.
3. Freeze source/artifact.
4. Freeze Package 004 snapshot.
5. Generate Merkle root twice.
6. Simulate/estimate deployment.
7. **STOP FOR HUMAN APPROVAL.**
8. After the human supplies the public deployment tx hash, verify deployment.
9. Attempt BscScan source verification.
10. Compute exact funding requirement.
11. **STOP FOR HUMAN APPROVAL.**
12. After the human supplies the public funding tx hash, verify funding.
13. Configure distributor address on staging.
14. Keep claims disabled.
15. Write final report.

## Forbidden

- Never request or accept a seed phrase/private key.
- Never sign on behalf of the human.
- Never deploy on an ambiguous snapshot/root.
- Never fund an unverified address.
- Never enable `claim`.
- Never modify liquidity or token ownership.
- Never merge to `main` without human approval.
- Never repoint `crestwavecoin.com`.

## Final chat response

Return only:

1. Package 009 prerequisite status
2. Distributor source commit
3. Snapshot hash
4. Participant count
5. Total allocation
6. Merkle root
7. Deployment tx hash
8. Distributor address
9. BscScan verification
10. Funding tx hash
11. Distributor MOOD balance
12. Claims enabled? `NO`
13. P0/P1 blockers
14. Final report path

Do not begin Package 011.
