# W12 Handoff

```text
W11_STATUS = PARTIAL
W12_GATE = PASS
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
HUMAN_OVERRIDE = NON_CLOUD_SETTINGS AUTHORIZED
```

W11 core Settings schema/authority is stable. Partial reflects deliberately hidden Cloud, cache relocation and startup registration—not a false implementation. W10 remains BLOCKED and W12 must preserve that claim.

- app/build: package `0.1.0-alpha.4`; Forge + Vite + Squirrel; current `npm run build` script reality must be audited.
- installer: Squirrel configured; file association and login startup registration require installer implementation/test.
- migration: LocalState v6, Settings v1, Recovery v1; preserve LKG/backups and all durable data.
- data: Electron userData `/moodify/local-state.json`; original audio external/in-place.
- cache: none owned at runtime; do not invent cleanup that touches durable data.
- diagnostics: existing local telemetry/support bundle/logging and renderer/main crash seams.
- output devices: verify enumerate/setSinkId/hotplug on packaged Windows hardware.
- signing/update: existing seams require release truth audit.
