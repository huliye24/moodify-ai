# Task Specification
## Security & Public Launch

### 1. Mission

Audit and harden the entire Moodify Protocol Genesis v1 system from Package 001 through Package 007.

The package must result in a release candidate that can be reviewed by a human operator before production deployment/public promotion.

### 2. Audit scope

#### A. Token identity
Review:
- official token config;
- contract address consistency;
- chain ID;
- decimals;
- supply;
- explorer/trade links;
- no stale placeholder values;
- no duplicate hard-coded addresses.

Official MOOD:

- Network: BNB Smart Chain
- Chain ID: 56
- Contract:
  `0x1BB3115D43E397f7bb586F090831B02cA639e73E`
- Decimals: 18
- Total Supply: 33,000,000 MOOD

#### B. Wallet registration
Review:
- nonce generation;
- nonce entropy;
- nonce expiry;
- single use;
- signature replay resistance;
- domain binding;
- chain binding;
- terms/version binding;
- address normalization;
- duplicate registration;
- concurrent registration;
- signature error handling;
- logging/privacy.

#### C. Admin
Review:
- authentication;
- server-side authorization;
- privilege escalation;
- IDOR;
- CSRF where applicable;
- session handling;
- admin event audit integrity;
- internal notes privacy;
- allocation controls;
- concurrent update safety.

#### D. Distribution Engine
Review:
- exact arithmetic;
- deterministic ordering;
- wallet uniqueness;
- participant uniqueness;
- status inclusion rule;
- pool ceiling;
- snapshot reproducibility;
- dataset fingerprint;
- Merkle leaf encoding;
- proof verification;
- artifact overwrite rules;
- checksum generation;
- artifact privacy.

#### E. Merkle Airdrop Contract
Review:
- Package 004 compatibility;
- immutable root;
- token address;
- SafeERC20;
- claim uniqueness;
- wrong wallet/amount/proof behavior;
- insufficient balance behavior;
- deadline/recovery policy;
- owner privileges;
- reentrancy assumptions;
- event correctness;
- gas considerations;
- BSC compatibility;
- no hidden mint/admin drain;
- no proxy/upgradability unless explicitly approved.

#### F. Airdrop frontend
Review:
- distributor config;
- chain enforcement;
- proof lookup;
- wrong-wallet behavior;
- stale proof behavior;
- receipt confirmation;
- already-claimed state;
- wallet rejection;
- insufficient gas;
- RPC failure;
- no token approval request;
- no misleading "claim success" before chain confirmation.

#### G. Contribution Network
Review:
- task visibility;
- submission authorization;
- self-review prevention;
- status transitions;
- duplicate submission controls;
- reward exactness;
- reputation append-only source;
- reward append-only source;
- Genesis allocation separation;
- privacy;
- anti-spam;
- no trade-to-earn mechanics.

#### H. Transparency & Treasury
Review:
- no fabricated metrics;
- source labeling;
- stale/unavailable state;
- no incorrect circulating supply;
- treasury labels human-approved only;
- read-only RPC architecture;
- no signer/write client;
- privacy of public API;
- accounting reconciliation.

### 3. Security tooling

Use available project-compatible tooling.

Preferred:

#### Solidity
- Foundry
- forge test
- fuzz tests
- invariant tests
- forge coverage
- Slither
- gas snapshot/report

#### TypeScript/Web
- lint
- typecheck
- unit tests
- integration tests
- production build
- dependency audit where appropriate
- route/API authorization tests

#### Database
- migration dry-run
- schema integrity tests
- uniqueness/constraint tests
- concurrency tests where practical

Do not add heavy tooling solely to satisfy a checklist if it does not fit repository architecture. Document unavailable tools.

### 4. Threat model

Create:

`docs/security/GENESIS_THREAT_MODEL.md`

Threat actors should include:

- unauthenticated internet user;
- malicious Genesis participant;
- compromised browser;
- malicious wallet extension/site clone;
- replay attacker;
- admin account attacker;
- malicious/buggy contributor;
- malicious API caller;
- erroneous operator;
- compromised RPC/explorer;
- smart-contract attacker;
- accidental configuration mismatch.

Assets to protect:

- MOOD treasury;
- distributor funds;
- participant allocation correctness;
- Merkle root integrity;
- admin authority;
- participant wallet ownership proofs;
- internal notes;
- protocol reputation/reward records;
- public transparency accuracy.

### 5. Security findings model

Create severity levels:

```text
CRITICAL
HIGH
MEDIUM
LOW
INFO
```

Each finding:

```text
id
severity
component
title
description
impact
evidence
reproduction
recommended_fix
status
owner
```

Critical/High issues must block release.

### 6. Release gates

Release candidate cannot pass if any of these remain:

- CRITICAL security issue;
- HIGH security issue without explicit human risk acceptance;
- contract tests failing;
- replay protection broken;
- admin auth bypass;
- Merkle proof mismatch;
- allocation total mismatch;
- private data exposed;
- production private key in repo;
- production distributor config points to unverified address;
- treasury transfer action exposed through UI unexpectedly;
- public site fabricates token metrics;
- build fails due to task-related issue.

### 7. Dependency/security review

Review package dependencies.

Look for:
- abandoned wallet libraries;
- known vulnerable packages;
- duplicate Web3 stacks;
- unnecessary wallet permissions;
- accidental server/client secret leakage;
- permissive CORS;
- unsafe JSON parsing;
- arbitrary RPC forwarding;
- dangerous eval/dynamic code.

Do not mass-upgrade dependencies unless needed. Prefer minimal risk-reducing changes.

### 8. Secret scanning

Search repository for:

- private keys;
- seed phrases;
- API secrets;
- wallet mnemonics;
- BSC RPC keys;
- admin passwords;
- Cloudflare tokens;
- `.env` files committed accidentally.

Use safe secret scanning patterns/tools.

Never print secrets in the final report. Redact them.

If a real secret is found:
- stop exposure;
- report location/type safely;
- recommend immediate rotation;
- do not continue using it.

### 9. Environment separation

Audit:

- local;
- preview/staging;
- production.

Ensure:
- mainnet distributor address cannot accidentally be replaced by test address;
- chain ID mismatch fails closed;
- production build cannot silently use mock Genesis data;
- test private keys never ship to client;
- local fixtures clearly marked.

### 10. CSP / web security

Where architecture supports it, review:

- Content Security Policy;
- frame-ancestors;
- referrer policy;
- clickjacking;
- external link rel;
- XSS;
- user evidence rendering;
- markdown sanitization;
- open redirect;
- unsafe URL schemes.

Particular attention:
- contribution evidence URLs;
- admin notes;
- task descriptions;
- wallet-provided content.

### 11. Rate limiting and abuse

Review protections for:

- nonce endpoint;
- registration endpoint;
- contribution submission;
- admin mutations;
- public proof endpoint;
- transparency endpoint.

Do not add fragile IP-only bans where unsuitable.

### 12. Data retention/privacy

Create:

`docs/security/GENESIS_PRIVACY_REVIEW.md`

Review storage of:
- wallet addresses;
- signatures;
- nonces;
- evidence URLs;
- admin notes;
- contribution text;
- participant display names;
- analytics.

Minimize retained data.

Document:
- public data;
- private data;
- retention;
- deletion policy where applicable;
- immutable protocol records that cannot be removed.

### 13. Operational runbook

Create:

`docs/protocol/GENESIS_LAUNCH_RUNBOOK.md`

It must cover:

#### Pre-launch
- database backup/export;
- approved snapshot;
- approved Merkle root;
- contract bytecode/tests;
- wallet/admin checks;
- website build;
- environment config;
- BscScan verification plan;
- treasury/funding plan.

#### Deployment
Human-signature checkpoints:
- deploy contract;
- verify contract;
- fund distributor;
- publish frontend config;
- smoke claim.

#### Post-launch
Monitor:
- claim failures;
- admin auth;
- RPC errors;
- reward/export consistency;
- site availability;
- distributor balance;
- suspicious repeated submissions.

### 14. Incident response

Create:

`docs/security/GENESIS_INCIDENT_RESPONSE.md`

Scenarios:

- wrong Merkle root deployed;
- distributor underfunded;
- frontend config wrong;
- claim contract vulnerability;
- admin credential compromise;
- DB allocation corruption;
- leaked private key;
- malicious contribution spam;
- RPC outage;
- BscScan metadata mismatch;
- treasury wallet compromise.

For each:
- detect;
- contain;
- communicate;
- recover;
- preserve evidence;
- postmortem.

Do not invent capabilities the contract does not have.

### 15. Release candidate report

Create:

`docs/releases/GENESIS_V1_RC.md`

Include:
- package completion status 001–007;
- security findings summary;
- unresolved issues;
- tests;
- deployment status;
- production actions still human-only;
- known limitations;
- launch decision: GO / NO-GO / CONDITIONAL GO.

### 16. Public launch UI review

Review navigation/access to:

- `/token`
- `/genesis`
- `/airdrop`
- `/contribute`
- `/transparency`

Ensure:
- coherent naming;
- no dead links;
- no dev copy;
- no conflicting contract address;
- no speculative claims;
- mobile/desktop usable;
- empty-state behavior safe.

### 17. Final cleanup

Remove:
- test buttons;
- debug panels;
- console secret logs;
- mock production data;
- placeholder addresses;
- stale TODOs that can create dangerous ambiguity.

Do not perform broad unrelated refactors.

### 18. Explicit non-goals

Do not:
- redesign Moodify brand;
- change tokenomics;
- change MOOD contract;
- create staking;
- create DAO governance;
- move treasury;
- add liquidity;
- run marketing bots;
- fabricate on-chain activity;
- auto-launch mainnet.
