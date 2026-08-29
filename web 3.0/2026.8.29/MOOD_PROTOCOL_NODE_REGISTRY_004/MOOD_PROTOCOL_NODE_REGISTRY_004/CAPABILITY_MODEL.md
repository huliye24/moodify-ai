# Capability Model

## Principle

Capability has two layers:

```text
Declaration
    ↓
Verification
```

Self-declaration is useful but must never render as verified truth.

## Manifest

Recommended shape:

```json
{
  "schemaVersion": "1.0.0",
  "manifestId": "mood:capability:...",
  "nodeId": "mood:node:...",
  "nodeType": "compute",
  "protocolVersions": ["0.1"],
  "capabilities": [
    {
      "key": "compute.cpu.arch",
      "value": "x86_64",
      "visibility": "public",
      "verificationStatus": "declared",
      "evidenceIds": []
    }
  ],
  "createdAt": "...",
  "fingerprint": "sha256:..."
}
```

## Capacity privacy

Prefer capacity classes instead of exact sensitive infrastructure details when appropriate.

Example:

```text
memoryClass = "8-16GB"
storageClass = "100-500GB"
```

rather than exposing operationally sensitive exact values.

## Data nodes

Data manifests should indicate:

- category
- provenance availability
- access mode
- license class
- public/private/restricted status

Do not put raw private datasets into the registry.

## Capability vocabulary

Use a registry or documented namespace.

Examples:

```text
compute.cpu.arch
compute.cpu.capacity_class
compute.gpu.model
compute.runtime.python
compute.runtime.container
storage.protocol.s3
storage.capacity_class
data.audio
data.metadata
validation.audio_quality
gateway.http
```

Avoid free-form capability names becoming authority.
