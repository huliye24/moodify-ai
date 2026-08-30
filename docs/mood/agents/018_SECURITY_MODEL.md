# MOOD AGENTS 018 — Security Model

**Authority:** MOOD-AGENTS-018 TASK.md Phase P

## What is NEVER exposed

- API keys (`sk-…`, `sk_test_…`, etc.).
- System prompts.
- Secret endpoints (admin URLs, internal RPCs).
- Wallet private keys / signer paths.
- Hidden chain-of-thought.

The public serializer (`publicBySlug`, `publicList`) strips:
- `operatorResidentId` (raw)
- `operatorOrganizationId` (raw)
- `healthSummary` (operator-internal)

INV-018-08 is enforced by serialization AND by field absence in the typed
record (the registry has no `apiKey`, `secretKey`, `signer`, or `privateKey`
properties at all).

## INV-018-12: Agent has no funds-operation authority

The registry class has **no methods** named with `transfer`, `mint`, `claim`,
`approve`, `sign`, `treasury`, `settle`, `payout`, `withdraw`. (Reflection-tested
in tests/agents-invariants.test.mjs.)

## Defense in depth

- Banned API-key patterns are absent from the type.
- Public serializers do not echo operator-internal fields.
- Status display requires heartbeat.
- Operator authorization gates lifecycle mutations.