# Security Regression

PASS by code audit: sandbox/context isolation/web security enabled; node integration disabled; narrow typed IPC; audio argv requires absolute supported paths; no shell concatenation; no generic execution IPC; updater disabled; renderer CSP restricted; no client/admin secret found; original media excluded from uninstall.

Installer is Authenticode `NotSigned`, file-association lifecycle is absent, durable-log privacy is not applicable because no durable logger exists. `SECURITY = PASS_WITH_LIMITATIONS`; unsigned distribution requires explicit acceptance.

`npm audit --omit=dev` reports 0 production vulnerabilities. The complete development toolchain reports 31 findings (including 2 critical), so Forge/Vite dependencies require a separately controlled upgrade before a trusted release build environment is declared clean; they are not runtime production dependencies in the packaged ASAR.
