# MPF-001 Security Boundary

The foundation task deals only with **public protocol facts**.

## Allowed

- public contract/mint address;
- public treasury address;
- public genesis pool address;
- public RPC URL intended for browsers;
- public explorer URL;
- chain ID / cluster;
- token metadata;
- read-only RPC calls;
- public explorer/API reads;
- source verification reads;
- local hashing and validation.

## Forbidden

- private key;
- seed phrase / mnemonic;
- keystore password;
- exchange/API trading secret;
- cloud access key;
- wallet session export;
- signing service credential;
- deployer secret;
- sending a transaction;
- signing a transaction;
- token mint/burn/transfer;
- liquidity add/remove;
- token approval;
- contract ownership transfer;
- contract upgrade;
- changing admin roles.

## Secret handling rule

If a command or tool requests a private key or seed phrase in order to "verify" a fact, do not proceed. Public mainnet facts must be verifiable without custody secrets.

## Address ambiguity

A public address found in code is not automatically canonical. It must have contextual evidence identifying its role and environment.

Examples:

- a testnet token address is not mainnet;
- a deployer address is not automatically treasury;
- a personal wallet is not automatically genesis pool;
- an old token mint is not automatically the current MOOD token;
- a liquidity-pool address is not the token contract/mint.

When unclear, use `HUMAN_DECISION_REQUIRED`.
