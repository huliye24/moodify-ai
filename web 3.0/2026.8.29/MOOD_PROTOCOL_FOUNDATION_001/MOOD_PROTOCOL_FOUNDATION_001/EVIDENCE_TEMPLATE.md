# MAINNET_EVIDENCE Template

Use this template for `docs/protocol/MAINNET_EVIDENCE.md`.

## Snapshot

- Evidence date:
- Repository:
- Base commit:
- Work commit:
- Canonical config SHA-256:
- Launch status: draft / locked

## Fact table

| Fact | Canonical value | Evidence source | Verification method | Status |
|---|---|---|---|---|
| Chain family | | | | |
| Network | | | | |
| Chain ID / cluster | | | | |
| Token contract / mint | | | | |
| Name | MOOD / verified name | | | |
| Symbol | MOOD | | | |
| Decimals | | | | |
| Total supply atomic | | | | |
| Treasury | | | | |
| Genesis pool | | | | |
| Explorer | | | | |
| Source verification | | | | |

Allowed status values:

```text
VERIFIED
REPOSITORY_ONLY
PUBLIC_CHAIN_ONLY
CONFLICT
HUMAN_DECISION_REQUIRED
NOT_APPLICABLE
```

## Conflicts

For every conflict:

```text
ID:
Fact:
Candidate A:
Source A:
Candidate B:
Source B:
Higher authority available?:
Resolution:
Human decision required?:
```

## Read-only commands

Record commands/API requests used to verify facts. Redact API keys. Never paste private keys, auth headers, cookies or wallet secrets.

## Conclusion

```text
MAINNET_LOCKED = TRUE | FALSE
Reason:
```
