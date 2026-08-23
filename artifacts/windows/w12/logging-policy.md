# Logging Policy

INFO/WARN/ERROR structured console markers cover startup, shutdown, version, window, native invocation, recovery and update failures. Local telemetry is allowlisted, redacted, opt-out and never uploaded. Support export is manual and safety-scanned. Tokens, credentials, URLs and media paths are prohibited.

Durable rotating production logs and explicit migration error records are not implemented: `LOGGING = PARTIAL`.
