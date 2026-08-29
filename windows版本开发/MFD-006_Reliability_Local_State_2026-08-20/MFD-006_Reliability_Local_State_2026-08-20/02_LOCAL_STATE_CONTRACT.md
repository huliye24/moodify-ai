# Moodify Desktop — Local State Contract v0.1

## 1. Principle

Local state exists to improve continuity.

It is not product business authority.

---

## 2. Durable State

Recommended initial shape:

```ts
type LocalStateV1 = {
  schemaVersion: 1;

  playback: {
    lastTrackId: string | null;
    positionMs: number;
    volume: number;
  };

  window: {
    width: number;
    height: number;
    x?: number;
    y?: number;
    maximized?: boolean;
  };

  app: {
    lastSuccessfulVersion?: string;
  };
};
```

Adjust to actual implementation.

---

## 3. Must Not Persist Here

```text
session token
refresh token
signed media URL
Authorization header
service key
OSS key
database credential
raw PlaybackManifest
full private library dump
```

---

## 4. Validation

Every read must validate:

- schema
- type
- bounds

Examples:

```text
volume: 0..1
positionMs: >= 0
width/height: reasonable range
track id: known product id format if available
```

---

## 5. Migration

```text
v1 → v2
```

must be explicit.

If migration impossible:

```text
backup optional
→ reset safe defaults
```

Do not silently reinterpret fields.
