# Offline / Retry Policy

Because the preparation path is disabled, offline/network failures cannot damage local playback, Library, Playlist or Queue. Existing public catalogue calls retain their bounded BffClient behavior.

Future preparation retries: timeout, connection reset, 429 and temporary 5xx only; maximum three attempts with exponential/stepped delay and jitter, using the same server idempotency key. Invalid source, unsupported format, 401/403 and malformed request are non-retryable until user/auth correction. No infinite polling/retry and no simulated server cancellation.
