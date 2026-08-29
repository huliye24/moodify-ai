# Security Model
## Genesis Registration

### Threats in scope

1. Signature replay
2. Nonce reuse
3. Expired signature replay
4. Client-side participant spoofing
5. Duplicate wallet registration
6. Wrong-chain registration
7. Address casing inconsistencies
8. Race conditions during concurrent registration
9. CSRF where relevant to chosen API model
10. Abuse/rate spikes
11. Sensitive signature logging
12. Malicious or misleading signature text

### Required controls

#### Nonce
- generated server-side;
- cryptographically random;
- single use;
- short TTL, recommended 5–15 minutes;
- invalidated after successful registration;
- never accept arbitrary client nonce.

#### Signature
- recover signer server-side;
- compare normalized recovered signer to requested wallet;
- sign message only, never typed data authorizing transfers unless intentionally using SIWE-compatible typed structure;
- text must explicitly say the signature does not authorize token transfer.

#### Address handling
Use a canonical EVM address library.

Store:
- normalized/checksum display address;
- optional lowercase indexed address for uniqueness.

Never compare addresses with naive case-sensitive string equality.

#### DB concurrency
The database must enforce uniqueness for:
- participant wallet;
- participant number;
- nonce identifier if persisted as unique.

Application checks alone are insufficient.

#### Rate limiting
Use existing infrastructure if available.

At minimum rate-limit:
- nonce creation;
- register attempts.

Do not block legitimate users with fragile IP-only assumptions if deployment environment makes client IP unreliable.

#### Logging
Never log:
- seed phrases;
- private keys;
- full sensitive auth secrets.

Avoid logging raw signatures unless necessary for debugging; if retained temporarily, document why and how long.

#### Secrets
No new blockchain private key is required.

If a server signing key is introduced unnecessarily:
**reject that design**.

### Stop conditions

Codex must stop and report instead of proceeding if:
- the only available wallet library requires unsafe permissions;
- production secrets are required but unavailable;
- an existing auth flow conflicts with this registration model;
- D1 schema changes would be destructive;
- participant number cannot be made race-safe using existing DB capabilities.
