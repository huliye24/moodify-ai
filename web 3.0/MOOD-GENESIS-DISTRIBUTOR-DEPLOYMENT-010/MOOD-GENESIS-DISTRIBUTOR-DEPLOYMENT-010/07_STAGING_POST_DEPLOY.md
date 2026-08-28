# Staging Post-Deployment Integration

Target:

`test.crestwavecoin.com`

Allowed public information:

- distributor address;
- BscScan link;
- Merkle root;
- distributor MOOD balance;
- deployment tx;
- funding state.

Equivalent config must remain:

```env
NEXT_PUBLIC_DISTRIBUTOR_ADDRESS=<real deployed address>
NEXT_PUBLIC_AIRDROP_CLAIMS_ENABLED=false
```

Use repository-native variable names if different.

The staging UI may read distributor state, but must not send a claim transaction.

Do not repoint `crestwavecoin.com`.
