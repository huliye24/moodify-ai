# MFY-CR-P08 — UNRESOLVED

Only items affecting the P09 Listening Environment are listed (per §11 of the
final response template).

1. **Real authorized corpus / human review evidence**: P07 blocker persists —
   the 10-track real corpus needs human-provided authorized material; blind
   listening and hardware validation remain PENDING (skipped per user
   instruction). P08's product semantics are exercised on synthetic fixtures
   only; end-to-end evidence on real tracks is pending the corpus.
2. **Worker deployment / routing**: reconstruction worker runs locally; LA
   product-node deployment, systemd unit, and node routing follow the
   cloud-fabric pattern but are not part of this package. No IPs/secrets in
   code (env-configured).
3. **Multiuser auth**: `single_user` is the default auth mode (dev boundary).
   BFF session integration and a real identity layer are P09 scope; until
   then, deployments MUST set `MOODIFY_AUTH_MODE=owner` +
   `MOODIFY_AUDIO_TOKEN_SECRET` behind the BFF.
4. **AAC/M4A decode coverage**: supported via ffmpeg; long-form m4a edge cases
   (chapters, weird codecs inside m4a) not exhaustively tested.
5. **peak memory**: Windows build reports tracemalloc-based peak (0.0 when
   not tracing); RSS-level accounting needs a POSIX/Linux deploy for the LA
   node.
6. **MEDIUM objective -> HUMAN_REQUIRED frequency**: on real music, MEDIUM
   findings will route a share of jobs to HUMAN_REQUIRED; the operator CLI
   review flow is the v0.1 admin path (no consumer review UI — P09/P11 scope).
7. **P04 evidence coupling**: `plan_from_findings` gained an
   `include_low_confidence=False` production mode (LOW findings never
   authorise candidates; ED-02 NOISE_REDUCTION is unsupported in v0.1). The
   golden experiment keeps the default behavior; P04's own generator remains
   the objective authority.
