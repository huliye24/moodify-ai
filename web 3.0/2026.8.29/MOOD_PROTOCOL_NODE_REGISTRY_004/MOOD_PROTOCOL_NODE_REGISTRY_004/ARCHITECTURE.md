# Architecture — Node Registry

## Position in the rough-build architecture

```text
                 MOOD PROTOCOL

        Mainnet Facts / Identity / Proof
                    │
                    ▼
             ┌──────────────┐
             │ Node Registry│
             └──────────────┘
                    │
        ┌───────────┼────────────┐
        ▼           ▼            ▼
    Identity    Capabilities    Health
        │           │            │
        └───────────┼────────────┘
                    ▼
             Resource Directory
                    │
                    ▼
            Registry Snapshot
                    │
           future package boundary
                    ▼
          Scheduler / Marketplace
```

## Important distinction

Node Registry answers:

> What resources claim to exist and what has been verified?

It does NOT answer:

> Which node should execute this job?
> How much should the node be paid?
> How much MOOD must be staked?

Those are future layers.

## Recommended domain boundaries

```text
domain/
  Node
  OperatorIdentity
  Region
  CapabilityManifest
  VerificationEvidence
  HeartbeatObservation
  RegistrySnapshot

services/
  NodeIdFactory
  NodeValidator
  LifecycleStateMachine
  CapabilityValidator
  VerificationService
  HealthEvaluator
  RegistrySnapshotBuilder

ports/
  NodeRepository
  CapabilityRepository
  HeartbeatRepository

adapters/
  FilesystemRegistry
  optional existing DB adapter
```
