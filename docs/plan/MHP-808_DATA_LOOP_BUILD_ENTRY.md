# MHP-808: Data Loop Build Entry

**Status**: done
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-BUILD-043 / Probe Plan-6C: Feasibility Gate / P6 (Next Entry)
**Depends on**: MHP-807
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Create the entry point for Build NEM-043 after Probe NEM-042 ADOPT decision.

## Build NEM-043 Scope

Build NEM-043 transforms the Probe prototype into production-ready collectors, recommenders, and loop runners.

### Build Plan-6A: Data Collectors (MHP-809 → MHP-814)

Transform per-loop extraction from script logic into formal collector modules:

| MHP | Type | Title |
|-----|------|-------|
| 809 | E | Define NightMetricRecord Schema |
| 810 | E | Implement Summary Collector |
| 811 | V | Implement Tidal Event Collector |
| 812 | V | Implement Queue Collector |
| 813 | S | Collector Unit Tests |
| 814 | N | Collector Build Report |

### Build Plan-6B: Recommendation Engine (MHP-815 → MHP-820)

Replace simulated DeepSeek outputs with real API calls + rule-based fallback:

| MHP | Type | Title |
|-----|------|-------|
| 815 | E | Implement Score Disagreement Recommender |
| 816 | E | Implement Penalty-Driven Preset Recommender |
| 817 | V | Implement Runtime Reliability Recommender |
| 818 | V | Implement Operator Next-MHP Writer |
| 819 | S | Recommendation Engine Tests |
| 820 | N | Recommendation Gate Report |

### Build Plan-6C: Loop Runner (MHP-821 → MHP-826)

Wire collectors + recommenders into a CLI-callable loop runner:

| MHP | Type | Title |
|-----|------|-------|
| 821 | E | Add Data Loop CLI |
| 822 | E | Add Data Loop Report Writer |
| 823 | V | Add Craft Memory Writeback Hook |
| 824 | V | Add MRS Calibration Proposal Hook |
| 825 | S | Data Loop Integration Smoke |
| 826 | N | Data Loop System Entry |

## Prerequisites for Build NEM

- [x] Probe NEM-042 ADOPT decision
- [x] Worker protocol validated
- [x] Per-loop extraction working
- [x] Schema stable
- [ ] DeepSeek API key configured (for real calls)
- [ ] Multi-night data available (for statistical significance)

## First Build Action

MHP-809: Define NightMetricRecord Schema — formalize the JSON schema for the nightly metric snapshot as a reusable collector input contract.

## Acceptance Criteria

- Build NEM scope is defined with 18 MHPs. ✅
- Each Build Plan-6 has a clear goal. ✅
- Prerequisites for Build are listed. ✅
- First Build MHP is identified. ✅ → MHP-809
