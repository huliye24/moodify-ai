# Protocol Identity Model

## Goal

Provide a stable protocol identity without creating a centralized identity provider.

## Primary identity

A public wallet may be the primary identity if that matches repository authority.

Example:

```json
{
  "type": "wallet",
  "namespace": "eip155:<chainId>",
  "id": "0x..."
}
```

Never store a private key.

## Protocol ID

Recommended canonical derivation:

```text
protocolId =
"mood:contributor:" +
sha256(
  canonical(namespace + ":" + normalizedPublicIdentity)
)
```

The exact derivation must be tested and versioned.

## Linked identities

Example:

```json
{
  "type": "github",
  "id": "public-handle",
  "verification": {
    "status": "verified",
    "method": "signed_public_message_or_repository_proof",
    "evidenceId": "..."
  }
}
```

## Rules

- display name is not identity;
- matching avatar is not identity;
- same email must not be used unless explicit policy allows it;
- same nickname is not proof;
- identity merge is reversible only through new records, not hidden rewriting.

## Lost wallet / identity migration

Do not solve custody recovery in MPF-003.

Provide a future migration hook:

```text
old protocol identity
   ↓
verified migration evidence
   ↓
new linked identity
```

but do not implement privileged account takeover.
