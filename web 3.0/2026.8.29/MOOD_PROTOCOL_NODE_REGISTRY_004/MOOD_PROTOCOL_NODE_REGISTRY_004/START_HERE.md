# MPF-004 — MOOD Protocol Node Registry

## Mission

Build the first auditable **Node Registry** for MOOD Protocol.

MPF-001 establishes protocol facts.
MPF-002 establishes contribution evidence.
MPF-003 establishes contributor identity and reputation.
MPF-004 establishes the network's resource map.

The registry must answer:

> Which independent nodes exist, who operates them, what resources do they claim to provide, where are they logically located, what can they do, and are they currently verifiably available?

## Core flow

```text
Operator / Protocol Identity
          ↓
     Node Registration
          ↓
    Capability Manifest
          ↓
   Verification / Challenge
          ↓
      Node Registry
          ↓
  Heartbeat / Health State
          ↓
      Network Resource Map
```

## What MPF-004 is NOT

It is NOT:

- a GPU marketplace
- a token reward system
- an automatic job scheduler
- a remote shell
- a cloud control plane
- a staking system
- a payment rail
- a DAO
- a contract deployment task

Those belong to later packages.

## Read order

1. `START_HERE.md`
2. `CODEX_TASK.md`
3. `ARCHITECTURE.md`
4. `NODE_MODEL.md`
5. `CAPABILITY_MODEL.md`
6. `NODE_STATE_MACHINE.md`
7. `VERIFICATION_POLICY.md`
8. `HEALTH_AND_HEARTBEAT.md`
9. `DISCOVERY_API.md`
10. `PRIVACY_AND_LOCATION.md`
11. `SECURITY_BOUNDARY.md`
12. `TEST_PLAN.md`
13. `ACCEPTANCE_GATE.md`
14. `IMPLEMENTATION_CHECKLIST.md`
15. `ROLLBACK.md`

Then inspect repository authority, current MPF-001/002/003 implementations, current cloud/node code, and existing service discovery patterns.

## Non-negotiable principle

**Registry is declaration + verification, not ownership.**

A node can belong to anyone.

MOOD Protocol records its public identity and capabilities without taking custody of the machine.

## Expected completion output

Codex must return:

- branch
- base commit
- final commit
- changed files
- tests
- sample node IDs
- sample capability manifest
- sample active/degraded/offline transitions
- unresolved human decisions
- `NO_REMOTE_CODE_EXECUTION_ADDED`
- `NO_CHAIN_WRITE_PERFORMED`
- `NO_TOKEN_ECONOMICS_ADDED`
