# Human Signature Gates

## Gate #1 — Deployment

Human must verify:

- BSC mainnet / chain ID 56;
- deployer public address;
- official MOOD contract;
- exact Merkle root;
- participant count;
- total allocation;
- contract artifact/commit;
- constructor inputs;
- gas estimate.

Codex may prepare the transaction but must not sign it.

## Gate #2 — Funding

Human must verify:

- source public address;
- distributor address;
- MOOD token contract;
- exact amount;
- current distributor balance;
- expected post-transfer balance.

Codex may prepare but must not sign.

## Never request

- seed phrase;
- raw private key;
- recovery words;
- keystore password in chat.

Use only an already-established human-controlled signer such as browser wallet, hardware wallet, multisig, or local wallet under direct human control.
