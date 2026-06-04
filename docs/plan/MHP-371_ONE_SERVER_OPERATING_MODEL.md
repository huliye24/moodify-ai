# MHP-371: One-Server Operating Model

**Status**: planned
**Direction**: ECHAIN-MOODIFY-VELOCITY-006 / NEM-MOODIFY-VELOCITY-PROBE-018 / Probe Plan-6C: Automation Gate / P13 (Execution)
**Depends on**: MHP-370
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Context

Moodify now uses one cloud server as its main engineering work layer. Hardware is fixed for this chain. The acceleration target is therefore to raise `K`, `S`, `P`, `A`, and `Tu`, while reducing `F`.

## Goal

Complete `One-Server Operating Model` as a state-converting AEP for engineering velocity. The output should make future cloud work faster, less interrupt-driven, and easier for humans or agents to resume.

## Expected Output

`docs/spec/one_server_operating_model.md`

## Execution Notes

- Do not require hardware upgrades or extra servers.
- Prefer command-driven, reproducible, cloud-native workflows.
- Reduce manual intervention, context rebuild, handoff ambiguity, or rework.
- Preserve compatibility with existing E-Chain/NEM/MHP docs and runtime code.

## Acceptance Criteria

- The expected output exists and is linked from the relevant NEM or gate package.
- The task improves at least one X-AEVF factor or reduces one named friction term.
- Failures are recorded as reusable engineering material.
- The next MHP can start without reconstructing context.
