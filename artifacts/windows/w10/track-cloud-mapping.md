# Track ↔ Cloud Mapping

Future mapping must be `LibraryTrack.id -> zero/one active CloudPreparation -> optional prepared source`; it cannot create a second Track. A source revision must be content-derived (server SHA-256 or another verified revision), not filename-only. The current stable local Track ID is path-derived and alone is insufficient to prove unchanged bytes for cloud result reuse.

No mapping was created in W10 because no preparation ID/source-revision contract is live.
