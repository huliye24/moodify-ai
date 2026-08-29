# Moodify Music authenticated media upload E2E — 2026-08-13

Environment: `https://rongjinwenchuan.xyz`

## Verified path

1. An anonymous `PUT /api/v1/music/media` request was rejected with HTTP 503
   because invite-beta account capabilities were unavailable.
2. A valid invite-beta session uploaded a 44-byte WAV fixture through the LA
   BFF.
3. The BFF validated the declared media type and WAV signature, streamed the
   body to temporary storage, calculated SHA-256, and atomically promoted it
   into the authenticated user's namespace.
4. The public media origin returned HTTP 206 for a byte-range request with
   `Content-Type: audio/wav` and `Content-Range: bytes 0-15/44`.
5. The fixture and its empty per-upload directory were removed after the
   verification. No track, version, passport, or catalogue row was created by
   this test.

## Namespace and authority

The verified storage shape was:

```text
beta/<server-session-user-id>/<server-generated-upload-id>/<safe-filename>
```

The user identity and upload ID were selected by the server. Client-supplied
identity headers were not authoritative.

## Failure and recovery behavior

- Requests without an authenticated beta session fail before media bytes are
  accepted.
- Unsupported MIME types, invalid file signatures, empty uploads, and files
  larger than 100 MiB are rejected.
- Incomplete uploads remain temporary and are removed on failure; successful
  uploads use an atomic rename.
- The deployed nginx route disables request buffering and applies a 100 MiB
  body limit and extended upstream timeouts.
- The test fixture was disposable; production catalogue media and the five
  imported Cadeau10 songs were not modified.
