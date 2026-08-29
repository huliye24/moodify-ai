# Track Identity

Local Track IDs use `local_` plus the first 128 bits of SHA-256 over the normalized absolute source locator. Windows normalization resolves the path, normalizes separators, and applies locale-stable lower casing. Metadata and temporary UI/player state never participate in identity.

Consequences:

- Same normalized path is idempotent and returns `ALREADY_EXISTS`.
- Case/slash variants resolve to the same Track.
- Same filename in different directories can coexist.
- Same content copied to another path becomes another Track. W02 intentionally avoids a heavy content-hash pipeline.
- Moving a file preserves the existing Track as `UNAVAILABLE`; W02 does not silently manufacture a new locator or delete identity.
- `source_kind` and `source_ref` keep future Cloud sources separate without changing Player identity semantics.

Contract fields: `id`, `source_kind`, `source_ref`, `title`, `artist`, `album`, `duration_ms`, `format`, `availability`, `created_at`, `updated_at`.
