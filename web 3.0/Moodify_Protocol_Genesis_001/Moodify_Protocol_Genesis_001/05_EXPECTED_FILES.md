# Expected File Map

The exact file paths depend on the existing Moodify repository. Codex must adapt to current conventions.

A likely target shape is:

```text
<active-web-app>/
├── src/
│   ├── config/
│   │   └── mood-token.ts
│   ├── app/
│   │   └── token/
│   │       └── page.tsx
│   └── components/
│       └── ...
├── tests/
│   └── ...
└── ...

docs/
└── protocol/
    └── MOOD_TOKEN.md
```

Do not force this exact tree if the repository uses:
- Pages Router;
- route groups;
- monorepo app packages;
- shared config packages;
- another established testing layout.

## Forbidden anti-patterns

Do not create:

```text
moodify-token-demo/
new-web3-app/
crypto-dashboard/
mood-protocol-v2/
```

Do not duplicate:
- wallet providers;
- design systems;
- environment loaders;
- config systems;
- routing roots.
