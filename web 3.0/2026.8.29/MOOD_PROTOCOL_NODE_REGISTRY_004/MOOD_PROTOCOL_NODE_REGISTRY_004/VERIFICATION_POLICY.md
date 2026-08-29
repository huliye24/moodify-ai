# Node Verification Policy

## Goal

Verify that a node/operator controls or can reliably answer for the registered resource.

Verification does not prove legal ownership.

## Verification methods

### HTTP challenge

Registry generates a public nonce.

Node serves it under a defined path such as:

```text
/.well-known/mood-node-challenge
```

Verifier checks exact challenge response.

### Public-key challenge

Node generates its own public verification key.

Registry stores only the public key.

A challenge can be signed by the node key.

Private key never enters repository or registry.

### Repository proof

Useful for developer nodes.

A public repository artifact may bind:
- protocol node ID
- contributor protocol ID
- verification nonce

### Manual evidence

Allowed only with:
- reviewer ID
- timestamp
- evidence
- reason
- policy version

## Verification status

```text
pending
verified
partially_verified
rejected
expired
```

## Capability-level verification

Node verification does NOT verify every capability.

Example:

```text
node endpoint = verified
GPU model = declared only
```

Keep those states separate.

## Expiry

Verification may have validity windows where appropriate.

Do not invent production expiry periods without policy authority.
