# MOOD Mainnet Integration 009
## Crestwave Public Staging

**Package ID:** `MOOD-MAINNET-INTEGRATION-009`  
**Execution target:** Moodify main repository  
**Primary repo:** `huliye24/moodify-ai`  
**Deployment target:** Cloudflare  
**Staging domain:** `test.crestwavecoin.com`  
**Official chain:** BNB Smart Chain Mainnet  
**Chain ID:** `56`  
**Official MOOD contract:** `0x1BB3115D43E397f7bb586F090831B02cA639e73E`  
**Mode:** Public staging / read-only mainnet  
**CANON_CHANGE:** `NO`  
**Asset movement:** `FORBIDDEN`  
**Distributor deployment:** `FORBIDDEN`

---

## Mission

Take the already-built local Moodify Web3 system and move it into the first public staging environment without moving any real MOOD and without deploying the Genesis Distributor.

This package is specifically intended to close the gap identified by the Web3 completion audit:

- local Web3 implementation exists;
- MOOD token already exists on BSC mainnet;
- public Web3 deployment is not yet established;
- live RPC reads are incomplete;
- `mood-chain.ts` / equivalent chain layer still contains placeholder behavior;
- Distributor deployment must wait until read-only mainnet integration is proven.

The desired first public state is:

```text
Local Web3
   ↓
Git staging branch
   ↓
Cloudflare Worker
   ↓
test.crestwavecoin.com
   ↓
BSC Mainnet RPC
   ↓
MOOD contract
0x1BB3115D43E397f7bb586F090831B02cA639e73E
```

The staging deployment must prove that the web app can read real on-chain state from BSC mainnet.

It must not move funds, deploy contracts, create claims, fund a distributor, or use a project private key.

---

## Success Condition

A public visitor can open:

`https://test.crestwavecoin.com`

and the application can, from BSC mainnet:

1. identify the MOOD token contract;
2. show BSC network status;
3. read `totalSupply`;
4. connect a user wallet;
5. detect wrong network;
6. read the connected wallet's MOOD balance;
7. link to BscScan;
8. fail safely if RPC is unavailable;
9. clearly mark all write/claim actions as unavailable in this stage.

Read `01_TASK_SPEC.md` first.
