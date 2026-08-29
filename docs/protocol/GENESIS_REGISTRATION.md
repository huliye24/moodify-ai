# Moodify Protocol — Genesis Registration (G-002)

Status: **Implemented in `apps/web`**
Owner: Moodify Protocol
Applies to: `chainId = 56` (BNB Smart Chain mainnet)
Canonical config: `apps/web/lib/genesis-config.ts`
Implementation package: `web 3.0/Moodify_Protocol_Genesis_002/`

## 1. Purpose

`/genesis` is a wallet-signed registration flow that issues a **Genesis Participant number** to a verified wallet holder. It is a single-purpose identity-only operation:

- It does **not** mint tokens.
- It does **not** allocate MOOD.
- It does **not** invoke any contract, send any transaction, or sign any on-chain message.
- It does **not** require gas.

The signature is an EIP-191 `personal_sign` over a deterministic human-readable message. The wallet UI shows the text verbatim — the user is never asked to approve a transfer they didn't read.

> Public framing: *"Every voice deserves to be heard."* Genesis is the protocol's invitation to be counted, not a financial product.

## 2. Authority model

| Question | Authority |
| --- | --- |
| Which chain is supported? | `GENESIS_CONFIG.chainId` (`lib/genesis-config.ts`) — currently 56 |
| Which message text is canonical? | `lib/genesis-message.ts` — `buildGenesisMessage(fields)` |
| Which signature scheme? | EIP-191 `personal_sign` only |
| Which status / score / allocation values are valid? | None. The server never accepts them. |
| Which runtime signs? | The user's wallet, in response to an explicit click. The server never signs. |

Bumping the message wording requires bumping `GENESIS_CONFIG.signatureVersion`. Bumping the chain requires a new config value and a new migration copy — never an in-place edit.

## 3. The canonical signed message

```text
Moodify Protocol Genesis Registration

Wallet: <checksum address>
Chain ID: 56
Nonce: <server-issued hex>
Issued At: <ISO-8601>
Expires At: <ISO-8601>
Signature Version: <v>
Terms Version: <v>
Domain: <app.moodify.example>

I am registering this wallet as a Moodify Genesis Participant.
This signature does not authorize any token transfer or transaction.
```

Properties:

- **Whitespace and ordering are part of the contract** — do not reorder fields.
- The same `buildGenesisMessage(fields)` runs on the client (preview) and on the server (verification), producing byte-identical text.
- The signed digest is `keccak256("\x19Ethereum Signed Message:\n" + len + body)` per EIP-191.
- The `Chain ID`, `Signature Version`, `Terms Version`, and `Domain` lines are filled from the server-side constants; the client cannot change them.

## 4. Nonce model

Nonces are **server-generated**, **single-use**, and **time-limited**.

| Property | Value |
| --- | --- |
| Length | `GENESIS_CONFIG.nonceByteLength` bytes (16 bytes by default → 32 hex chars) |
| Source | `crypto.getRandomValues()` (CSPRNG) |
| Storage | `genesis_nonces.nonce_hash = sha256(nonce)` (we never store the raw nonce) |
| TTL | `GENESIS_CONFIG.nonceTtlSeconds` (default 600 s = 10 min) |
| Single use | `nonce.used_at` is set inside the same registration transaction |
| Lookup key | `(nonce_hash, wallet_address_normalized)` |

The client never generates, replays, or modifies a nonce. The client only echoes the one it received back to the server.

## 5. Participant numbering

Participant numbers are **monotonically increasing integers, allocated by the server**.

| Property | Authority |
| --- | --- |
| What is the next number? | `MAX(participant_number) + 1` inside the same transaction |
| Who computes it? | The server. The client may suggest `0` only to indicate "no claim". The server ignores any client-supplied number. |
| Race safety | The `participant_number` column has a DB UNIQUE index. If two concurrent allocations collide on the same number, the loser retries with a fresh value. |
| Idempotency | If the same wallet re-registers, the server returns the existing record (HTTP 200, `participant_number` unchanged). |
| Number formatting | `String(n).padStart(4, "0")` for display — `#0001`, `#0002`, etc. |

There is **no off-chain, off-identity way** to influence a participant number. Status, score, and allocation are not part of this version.

## 6. Endpoints

All endpoints return JSON. All endpoints reject any request whose `chainId` is not the canonical BSC mainnet.

### `POST /api/genesis/nonce`

Request:

```json
{ "address": "0x...", "chainId": 56 }
```

Response:

```json
{
  "nonce": "0x...",
  "issuedAt": "2026-08-26T13:30:00.000Z",
  "expiresAt": "2026-08-26T13:40:00.000Z",
  "termsVersion": "1",
  "signatureVersion": "1",
  "chainId": 56,
  "domain": "app.moodify.example",
  "message": "<canonical text>"
}
```

Errors:

| HTTP | code | when |
| --- | --- | --- |
| 400 | `ADDRESS_INVALID` | malformed address |
| 400 | `CHAIN_UNSUPPORTED` | chainId ≠ 56 |
| 500 | `INTERNAL` | unexpected |

### `POST /api/genesis/register`

Request:

```json
{
  "address": "0x...",
  "chainId": 56,
  "nonce": "0x...",
  "signature": "0xRRRR...SSSS...VV"
}
```

Response (200):

```json
{
  "participant": {
    "id": "uuid",
    "participantNumber": 1,
    "address": "0x...checksum",
    "joinedAt": "2026-08-26T13:31:00.000Z",
    "status": "registered",
    "signatureVersion": "1",
    "termsVersion": "1"
  }
}
```

Errors:

| HTTP | code | when |
| --- | --- | --- |
| 400 | `ADDRESS_INVALID` | malformed address |
| 400 | `CHAIN_UNSUPPORTED` | chainId ≠ 56 |
| 400 | `NONCE_INVALID` | wrong hex format |
| 400 | `NONCE_UNKNOWN` | nonce not issued (or wrong wallet) |
| 400 | `NONCE_EXPIRED` | ttl elapsed |
| 400 | `NONCE_WALLET_MISMATCH` | nonce issued to a different wallet |
| 409 | `NONCE_USED` | nonce already consumed |
| 400 | `SIGNATURE_INVALID` | malformed or unverifiable |
| 400 | `SIGNER_MISMATCH` | signature was valid but signed by a different address |
| 409 | `WALLET_ALREADY_REGISTERED` | defensive (should not occur because lookup-then-insert is idempotent) |
| 500 | `INTERNAL` | unexpected |

### `GET /api/genesis/me?address=0x...`

Returns `{ participant: <Participant> | null }`. Used by the client to detect a previously-registered wallet and jump straight to the success card.

## 7. UI state machine (`/genesis`)

States declared in `app/genesis/page.tsx`:

| State | Trigger | Resolves by |
| --- | --- | --- |
| `idle` | No wallet detected | `connectWallet` |
| `wallet-disconnected` | Wallet present, not connected | `connectWallet` |
| `connecting` | User clicked connect | wallet response |
| `wrong-network` | Chain ≠ 56 | `switchToBsc` |
| `ready-to-sign` | Chain = 56, no nonce yet | `requestChallenge` |
| `nonce-loading` | Nonce requested | wallet sign prompt |
| `signature-requested` | Wallet sign prompt open | wallet response |
| `verifying` | Signature returned, server verifying | server response |
| `registered` | First-time success | — (final) |
| `already-registered` | Wallet was previously registered | — (final) |
| `rejected` | User rejected sign | — (final, retryable) |
| `expired` | Nonce expired | — (final, retryable) |
| `server-error` | Other server error | — (final, retryable) |

The page never auto-signs and never auto-submits. Every transition requires user action.

## 8. What is **never** done

- The page never calls `eth_sendTransaction`, `eth_signTypedData*`, `approve`, `setApprovalForAll`, or any contract method.
- The server never requests, stores, transmits, or displays private keys or seed phrases.
- The server never accepts client-supplied `participantNumber`, `status`, `contributionScore`, or `allocation`.
- The server never accepts a client-supplied nonce; the nonce is always `crypto.getRandomValues`-generated.
- No data is logged that includes the raw signature bytes.
- The page never asks the user to pay gas; there is no chain interaction.

## 9. Verification

The implementation is enforced by the test suite `tests/genesis-registration.test.mjs`. Every claim in this document has a named test. The complete suite — `node --test tests/*.test.mjs` — currently runs 73 tests, all passing.
