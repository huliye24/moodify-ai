# Authentication and Rate Limits

## Public reads

Public protocol facts may be unauthenticated.

Use rate limiting to prevent abuse.

## Restricted actions

Any write action must use the repository's existing authentication system if present.

Do not invent:
- hard-coded admin passwords
- shared production API keys committed to Git
- wallet-private-key authentication

## Roles

If existing project roles exist, reuse them.

Potential conceptual roles:

```text
public
contributor
node_operator
reviewer
protocol_admin
```

Do not create these as production authority unless repository policy approves them.

## Rate limits

At minimum distinguish:

- cheap public reads
- expensive filtered reads
- write attempts
- verification probes

Do not let a public caller trigger unbounded expensive queries.

## Abuse response

Return standardized `RATE_LIMITED`.

Do not expose internal rate-limit implementation details.
