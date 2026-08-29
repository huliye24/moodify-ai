# Cache Layout

`.moodify/cache/<source_sha256>/nodes/<node_key>/`

Each entry contains `manifest.json`, `payload.json`, and optional compressed
`arrays.npz`. NumPy loading uses `allow_pickle=False`. Manifests record schema,
node/source versions, dependency hashes, content hash and size.
