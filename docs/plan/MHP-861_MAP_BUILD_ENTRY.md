# MHP-861: MAP Build Entry

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6C: Handoff / S5
**Depends on**: MHP-857, MHP-858, MHP-859, MHP-860
**Protocol**: AWJ Stack + E-Chain 54

## Context

Probe NEM-045 is complete (6A ADOPT, 6B ADOPT, 6C contracts defined). This MHP defines the Build NEM-046 entry — the first Build MHP, the full scope, and the execution order.

## Build NEM-046: Full Scope (18 MHPs)

### Build Plan-6A: Data Model Block (MHP-863 → MHP-868)

| MHP | Type | Title | Contracts From |
|-----|------|-------|---------------|
| 863 | E | Implement MAP Data Model | MHP-852 (Feature Vector), MHP-853 (Problem Vector) |
| 864 | E | Implement Scan Result Contract | MHP-851 (Scan Gap) |
| 865 | V | Implement Feature Vector Contract | MHP-852 (Feature Weights) |
| 866 | V | Implement Diagnosis Vector Contract | MHP-853 (Problem Taxonomy) |
| 867 | S | MAP Core Tests | MHP-859 (Command Gate L1/L2) |
| 868 | N | Close Data Model Block | All above |

### Build Plan-6B: Validation Block (MHP-869 → MHP-874)

| MHP | Type | Title | Contracts From |
|-----|------|-------|---------------|
| 869 | E | MRS Engine Adapter Hook | MHP-854 (MRS Boundary) |
| 870 | E | Damage Loss Gate | MHP-854 (MRS Adapter), MHP-853 (Taxonomy) |
| 871 | V | Risk Flag Taxonomy | MHP-853 (Problems → risks) |
| 872 | V | Pass Policy Threshold Config | MHP-854 (Boundary), MHP-860 (Diff Risk) |
| 873 | S | Validation Matrix Tests | MHP-859 (Command Gate L3-L5) |
| 874 | N | Close Validation Block | All above |

### Build Plan-6C: Delivery Block (MHP-875 → MHP-880)

| MHP | Type | Title | Contracts From |
|-----|------|-------|---------------|
| 875 | E | Delivery Manifest Writer | MHP-855 (Inventory) |
| 876 | E | Reproducibility Metadata Hook | MHP-855 (Metadata Schema) |
| 877 | V | JSON/PDF Report Contract | MHP-846 (Interface Contract), MHP-848 (Schema Probe) |
| 878 | V | CLI/API MAP Contract | MHP-846 (CLI Contract), MHP-859 (Command Gate) |
| 879 | S | Build Gate Report | MHP-858 (Judge Schema), MHP-860 (Diff Risk) |
| 880 | N | Close Build NEM | All above |

## Execution Order

```text
1. MHP-863 (Data Model)     ← prerequisite for everything
2. MHP-864 (Scan Contract)  ← parallel with 865
3. MHP-865 (Feature Vector) ← parallel with 864
4. MHP-866 (Diagnosis Vector)
5. MHP-867 (Core Tests)
6. MHP-868 (Close 6A)       ← gate before validation block

7. MHP-869 (MRS Adapter)    ← prerequisite for 870-872
8. MHP-870 (Damage Loss)
9. MHP-871 (Risk Flags)
10. MHP-872 (Pass Policy)
11. MHP-873 (Validation Tests)
12. MHP-874 (Close 6B)      ← gate before delivery block

13. MHP-875 (Manifest)      ← parallel with 876
14. MHP-876 (Metadata)      ← parallel with 875
15. MHP-877 (Report Contract)
16. MHP-878 (CLI/API Contract)
17. MHP-879 (Build Gate Report)
18. MHP-880 (Close Build NEM)
```

## Worker Task Budget

| Block | MHPs | Est. Worker Tasks | Est. Time |
|-------|------|------------------|-----------|
| Data Model (6A) | 6 | ~14 | 1 session |
| Validation (6B) | 6 | ~10 | 1 session |
| Delivery (6C) | 6 | ~12 | 1 session |
| **Total** | **18** | **~36** | **3 sessions** |

## AWJ Rules for Build NEM

1. **Architect** approves all dataclass changes in `v01_types.py`.
2. **Worker** implements bounded MHPs using the JSONL task contract (MHP-857).
3. **Judge** validates every Worker AEP against the 6-gate schema (MHP-858).
4. Command gate (MHP-859): L1-L2 must pass for every PR; L3-L5 for block gates.
5. Diff risk gate (MHP-860): low-risk auto-accept; medium → Architect review; high → reject.
6. No Worker AEP may modify `mrs_engine.py`, `operator_api.py`, `supervisor.py`, or `scheduler.py`.

## First Build Action

**MHP-863**: Implement MAP Data Model — add `FeatureVector`, `ProblemVector`, `ProblemEntry` dataclasses to `v01_types.py`, with `to_dict()` serialization.

## Acceptance Criteria

- [x] Build NEM scope is defined with 18 MHPs across 3 blocks.
- [x] Execution order is defined with parallelism notes.
- [x] Worker task budget estimated at ~36 tasks.
- [x] AWJ rules for Build NEM are explicit.
- [x] First Build MHP (863) is identified.
- [x] All 5 Probe 6B briefs have corresponding Build MHPs.
