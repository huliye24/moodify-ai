# Task Specification
## Genesis Registration

### 1. Mission

Add a production-quality Genesis registration flow to the existing Moodify web application.

The flow must:

1. explain what Genesis participation means;
2. connect an EVM wallet;
3. require BNB Smart Chain;
4. obtain a one-time nonce from the server;
5. sign a structured human-readable message;
6. verify the signature server-side;
7. prevent replay and duplicate registration;
8. create a Genesis Participant record;
9. assign a monotonic public participant number;
10. show a success state.

### 2. Required public route

Create:

`/genesis`

The page should fit the current Moodify visual system and should not look like a generic crypto launchpad.

Required sections:

#### Genesis introduction
Explain:
- Moodify Protocol Genesis is the early participation registry;
- registration does not guarantee financial value;
- registration does not require a token purchase;
- a wallet signature proves wallet ownership only.

#### Wallet connection
Support the existing wallet stack if already present.

Preferred behavior:
- MetaMask / injected EVM wallets;
- WalletConnect only if already used in the repo;
- do not introduce a large wallet dependency if unnecessary.

#### Network state
Required chain:
- BNB Smart Chain
- chainId `56`

If wrong network:
- show clear state;
- offer network switch only through standard wallet APIs;
- never auto-submit a transaction.

#### Registration
The user requests a nonce from Moodify backend, signs the registration message, and submits signature + message payload for server verification.

#### Success state
Show:
- `Genesis Participant #XXXX`
- wallet address
- registration timestamp
- status: `registered`
- copy Participant ID
- view wallet on BscScan

### 3. Signature message

The signed message must be human-readable and include enough context to prevent ambiguous signatures.

Required semantic fields:

- protocol/domain: Moodify
- action: Genesis Registration
- wallet address
- chain ID
- nonce
- issued-at timestamp
- expiration timestamp
- terms/version identifier
- request origin/domain if safely available

Recommended message shape:

```text
Moodify Protocol Genesis Registration

Wallet: 0x...
Chain ID: 56
Nonce: ...
Issued At: ...
Expires At: ...
Terms Version: genesis-v1
Domain: <official Moodify domain>

I am registering this wallet as a Moodify Genesis Participant.
This signature does not authorize any token transfer or transaction.
```

Use SIWE/EIP-4361 if the repository already supports it or if adopting it is clean and justified. Otherwise implement a minimal equivalent with strict server-side verification.

Do not invent a custom signing format if a secure existing implementation is already present.

### 4. Registration invariants

- one wallet address can have at most one active Genesis Participant record;
- one nonce can be used at most once;
- nonce expires;
- expired nonce cannot be verified;
- signature must recover the exact submitted wallet address;
- normalized address handling must be deterministic;
- wrong chain must be rejected;
- terms version must be recorded;
- participant number must not be derived from array length in a race-prone way;
- repeated submissions must be idempotent where sensible.

### 5. API surface

Adapt route style to the existing project.

Likely semantic endpoints:

```text
POST /api/genesis/nonce
POST /api/genesis/register
GET  /api/genesis/me?address=...
```

Equivalent server actions are acceptable if consistent with the repository.

#### `POST /api/genesis/nonce`

Input:
- wallet address
- chainId

Output:
- nonce
- issuedAt
- expiresAt
- termsVersion
- message fields required for signing

Server responsibilities:
- validate address;
- validate chain;
- create cryptographically secure nonce;
- persist hash/value safely;
- set short expiration;
- invalidate stale nonce strategy.

#### `POST /api/genesis/register`

Input:
- address
- chainId
- nonce/message payload
- signature

Server responsibilities:
- validate schema;
- load valid unused nonce;
- rebuild or validate canonical message;
- verify signature;
- transactionally mark nonce used;
- prevent duplicate participant;
- create participant;
- return participant data.

Never trust client-provided participant number, registration status, score, allocation or claim status.

### 6. UI states

Implement explicit states:

- idle
- wallet disconnected
- connecting
- wrong network
- ready to sign
- nonce loading
- signature requested
- verifying
- already registered
- registered successfully
- rejected / invalid signature
- expired nonce
- server unavailable

No spinner-only dead states.

### 7. Accessibility

- keyboard-accessible controls;
- readable wallet addresses;
- clear status text;
- focus handling for errors;
- do not rely only on color for success/error;
- responsive on mobile.

### 8. Analytics/privacy

Do not add invasive wallet analytics.

If the project already has analytics:
- record only product-level events;
- do not expose signatures;
- do not log private information.

Suggested events:
- genesis_view
- wallet_connected
- genesis_signature_requested
- genesis_registered
- genesis_registration_failed

### 9. Documentation

Create:

`docs/protocol/GENESIS_REGISTRATION.md`

Document:
- purpose;
- registration flow;
- signature semantics;
- nonce model;
- DB model;
- participant numbering;
- privacy/security boundaries;
- future relationship to allocation and airdrop.

### 10. Explicit non-goals

Do not implement:
- token transfer;
- claim smart contract;
- Merkle tree;
- reward allocation;
- contribution tasks;
- referrals;
- trading incentives;
- NFT minting;
- paid registration;
- social-follow gating;
- Sybil-resistance scoring beyond basic duplicate wallet prevention.
