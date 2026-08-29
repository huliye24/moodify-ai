# Node Model

## Node is not a server

A node is a protocol-level resource identity.

Depending on type, a node may represent:

- one machine
- one service
- one data provider
- one storage service
- one validation service
- one developer endpoint
- one gateway

Do not force all node classes into server semantics.

## Required fields

```text
nodeId
operatorProtocolId
nodeType
displayName
region
endpoint
capabilityManifestId
verification
health
lifecycleStatus
registeredAt
updatedAt
recordFingerprint
```

## Node types

### developer

Human/developer contribution interface.

Endpoint may be null.

### compute

CPU/GPU/inference/processing resource.

### data

Data or metadata resource provider.

### storage

Object/blob/archive resource.

### validation

Independent verification / benchmark resource.

### gateway

Public connectivity or protocol gateway.

## Immutability

Identity fields should be immutable after registration:

- nodeId
- operatorProtocolId
- original nodeType

Infrastructure details can evolve via versioned updates.

If operator changes, use explicit migration/transfer policy in a future task. Do not silently rewrite ownership/operator identity.

## Node record fingerprint

Fingerprint normalized public record content.

Exclude ephemeral health observations from the immutable identity fingerprint if the chosen design uses separate health records.

Document exactly what is included.
