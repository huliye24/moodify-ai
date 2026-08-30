# MOOD BSC / Flap Go-No-Go Review - 2026-09-01

**Review state:** `NO-GO / GATES OPEN`
**Reviewed:** 2026-08-30
**Action taken:** read-only review; no wallet connected, no metadata submitted, no contract deployed, no funds moved

## Verified platform facts

- `flap.sh/board` currently exposes BSC as the selected chain and offers non-tax and tax token creation.
- The visible non-tax creation form requests image, name, symbol, description, quote asset, optional creator purchase, protection period, and public links.
- The form reports an approximate deployment cost of `0.001 BNB`, allows an optional creator purchase up to 20M tokens, and exposes a configurable protection period.
- Flap documentation describes non-tax tokens and tax choices of 1%, 3%, 5%, or 10%.
- Flap documentation lists BNB Chain mainnet Portal `0xe2cE6ab80874Fa9Fa2aAE65D277Dd6B8e65C9De0` as v5.8.6 at review time, plus implementation/vault addresses. These values must be reverified immediately before any transaction.
- Flap documentation links CertiK and BlockSec audit reports. An audit of platform code does not audit MOOD's parameters, launch entity, key custody, disclosures, treasury, or operational behavior.
- BSC mainnet Chain ID is `56`; BSC testnet Chain ID is `97`.

## Current blockers

| Gate | State | Evidence needed |
|---|---|---|
| Applicable jurisdiction and launch entity | `BLOCKED` | Qualified legal opinion and named responsible entity/person |
| MOOD Genesis network prerequisites | `FAIL` | Persistent Passport/Contribution/Proof/Agent/Node state and runtime evidence |
| Token purpose and holder rights | `UNRESOLVED` | Frozen utility, exclusions, disclosures, and accounting treatment |
| Name/symbol/supply/curve/quote asset | `UNRESOLVED` | Signed parameter manifest |
| Tax vs non-tax | `UNRESOLVED` | Economic rationale, recipient/vault, accounting and legal review |
| Contract/admin/upgrade/pause/mint authority | `UNVERIFIED` | On-chain inspection and authority matrix for the selected Flap version |
| Deployer and treasury custody | `BLOCKED` | Multisig/key-custody/recovery policy and approved signers |
| Testnet rehearsal | `NOT_RUN` | Transaction simulation, event verification, explorer record and incident drill |
| Mainnet funding and transaction | `NOT_AUTHORIZED` | Exact amount plus action-time human approval |
| Public CA announcement | `NOT_AUTHORIZED` | Successful verified deployment plus signed release record |

## Regulatory boundary

The current operator location and target audience must be resolved before proceeding. Chinese authorities' 2017 announcement characterizes token issuance financing as unauthorized public financing, and the 2021 multi-agency notice states that token issuance financing and related virtual-currency business activities are illegal financial activities and that overseas exchanges serving mainland residents are also within the prohibition described by the notice.

This repository cannot convert a technical ability to deploy on BSC into a legal authorization. A platform form, disclaimer, foreign entity, or offshore domain is not accepted as a substitute for qualified advice on the actual people, entity, promotion, users, funds, and jurisdictions involved.

## September 1 decision

The default decision is:

```text
NO-GO
```

September 1 may be used to publish the Scope Freeze, project state, risk boundary, and a transparent no-launch decision. It must not be used to manufacture urgency around a wallet signature.

If every gate becomes satisfied, the final wallet connection, signature, contract creation, initial purchase, liquidity action, or financial transaction still requires explicit action-time human approval.

## Sources reviewed

- https://flap.sh/board
- https://flap.sh/create?lang=zh
- https://docs.flap.sh/flap
- https://docs.flap.sh/flap/audit-reports
- https://docs.flap.sh/flap/developers/deployed-contract-addresses
- https://docs.bnbchain.org/bnb-smart-chain/developers/json_rpc/json-rpc-endpoint/
- https://www.csrc.gov.cn/csrc/c100028/c1001463/content.shtml
- https://www.pbc.gov.cn/tiaofasi/144941/3581332/4348658/index.html

