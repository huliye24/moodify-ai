# Package Manifest

Package: `MOOD_PROTOCOL_NODE_REGISTRY_004`

Purpose:

> Build a verifiable directory of independent resources that can participate in MOOD Protocol.

## Files

- START_HERE.md
- CODEX_TASK.md
- ARCHITECTURE.md
- NODE_MODEL.md
- CAPABILITY_MODEL.md
- NODE_STATE_MACHINE.md
- VERIFICATION_POLICY.md
- HEALTH_AND_HEARTBEAT.md
- DISCOVERY_API.md
- PRIVACY_AND_LOCATION.md
- SECURITY_BOUNDARY.md
- TEST_PLAN.md
- ACCEPTANCE_GATE.md
- IMPLEMENTATION_CHECKLIST.md
- ROLLBACK.md
- EVIDENCE_TEMPLATE.md
- schema/node.schema.json
- schema/capability-manifest.schema.json
- schema/heartbeat.schema.json
- schema/registry-snapshot.schema.json
- config/node-policy.draft.json
- config/health-policy.draft.json
- fixtures/compute-node.example.json
- fixtures/compute-capability.example.json
- SHA256SUMS.txt

## Explicit exclusions

- task marketplace
- automatic workload scheduler
- job execution protocol
- remote shell
- SSH management
- cloud provisioning
- GPU metering/payment
- MOOD staking
- node reward formula
- treasury
- governance
- contract deployment

## Success condition

At the end of MPF-004, MOOD should be able to represent:

```text
Tokyo      Developer Node
Singapore  Compute Node
Hangzhou   Data Node
Los Angeles Storage Node
Europe     Validation Node
```

as independent, verifiable registry entries without requiring MOOD to own those resources.
