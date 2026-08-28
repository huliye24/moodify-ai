# Environment Template
## Names Only — Do Not Store Secrets Here

Codex must derive exact names from the repository where possible.

The following is a conceptual staging model.

```env
# Public chain configuration
NEXT_PUBLIC_CHAIN_ID=56
NEXT_PUBLIC_MOOD_TOKEN_ADDRESS=0x1BB3115D43E397f7bb586F090831B02cA639e73E
NEXT_PUBLIC_BSC_EXPLORER_BASE_URL=https://bscscan.com

# Public staging state
NEXT_PUBLIC_DEPLOYMENT_ENV=staging
NEXT_PUBLIC_AIRDROP_CLAIMS_ENABLED=false

# RPC
# Prefer a server-side/private binding if the chosen endpoint contains credentials.
BSC_RPC_URL=<configured-in-cloudflare>
```

If the repository already uses different variable names, preserve repository conventions.

---

## Distributor

For Package 009:

```env
NEXT_PUBLIC_DISTRIBUTOR_ADDRESS=
NEXT_PUBLIC_AIRDROP_CLAIMS_ENABLED=false
```

Do not invent a distributor address.

---

## Cloudflare Bindings

Repository inspection indicates Web infrastructure may use bindings such as:

```text
DB
MEDIA
```

Codex must verify actual runtime use before creating staging resources.

Never reuse production bindings by assumption.

---

## Rules

- public values may be exposed intentionally;
- secrets must use Cloudflare secret storage or equivalent;
- no `.env` containing secrets may be committed;
- no private key is required for Package 009;
- no deployer wallet secret is required for Package 009.
