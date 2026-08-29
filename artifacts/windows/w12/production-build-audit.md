# Production Build Audit

`npm run build` now maps to the real Forge package operation. `npm run make` completed without a dev server and generated an ASAR-packaged x64 application plus Squirrel installer in `out-w12`. Renderer CSP permits only the declared production host; production DevTools remain closed; sandbox, context isolation and web security are enabled.

No source maps were emitted in packaged resources and no embedded credential pattern was identified. The configured public BFF URL is not a claim that W10 preparation exists. Clean-machine runtime independence remains unverified and is a Beta blocker.
