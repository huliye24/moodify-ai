# ECHAIN-MOODIFY-CRAFT-22-012

## Title

Moodify 22-Process Craft System

## Status

IMPLEMENTED ON MAINLINE — status reconciliation pending

## Strategic Intent

Upgrade Moodify from a small preset processor into an industrial craft system with 22 controlled processing operations. The goal is not to add random effects; the goal is to create a disciplined process chain that can improve audio quality, preserve intent, support tidal-cycle iteration, and leave measurable evidence after every operation.

This E-chain must run on Tencent Cloud under `/home/ubuntu/moodify-mainline`.

## Why This Matters

Current processing craft feels too thin. The Acoustic CT reports show that scanning is already useful, but the treatment layer needs more expressive and more controllable operations. Moodify should behave less like a one-click consumer enhancer and more like an internal studio operating system: scan, diagnose, choose craft, process, rescan, compare, remember.

## Cloud Runtime Requirement

```bash
ssh ubuntu@43.156.175.4
cd /home/ubuntu/moodify-mainline
source .venv/bin/activate
```

All implementation and tests must pass on this cloud machine.

## Proposed 22 Craft Operations

The executor may refine names after reading the current code, but the final system must expose 22 distinct craft operations.

| # | Craft Operation | Purpose |
|---|---|---|
| 1 | Input normalize | Prepare safe internal level without destroying dynamics |
| 2 | Silence trim | Remove leading/trailing silence for stable analysis |
| 3 | DC offset repair | Remove low-level waveform bias |
| 4 | Sub-bass discipline | Control excessive <60 Hz energy |
| 5 | Bass body shaping | Improve 60-150 Hz weight |
| 6 | Low-mid de-mud | Reduce 150-350 Hz cloudiness |
| 7 | Mid presence lift | Improve intelligibility around 700-2000 Hz |
| 8 | Harshness guard | Reduce painful upper-mid energy |
| 9 | Air recovery | Restore controlled high-frequency openness |
| 10 | Sibilance guard | Control sharp vocal consonants |
| 11 | Transient soften | Smooth spikes without flattening the track |
| 12 | Transient restore | Recover attack when processing dulls the sound |
| 13 | Micro-dynamics lift | Add perceived life at low intensity |
| 14 | Macro-dynamics guard | Avoid over-compression and pumping |
| 15 | Stereo width control | Adjust width with mono safety |
| 16 | Center focus | Improve vocal/lead stability |
| 17 | Noise floor polish | Reduce low-level hiss/rumble where safe |
| 18 | Room/reverb cleanup | Reduce smeared ambience when detected |
| 19 | Warmth injection | Add controlled warmth without mud |
| 20 | Clarity polish | Add final articulation and separation |
| 21 | Loudness landing | Land target loudness without clipping |
| 22 | Final safety limiter | Prevent overs and generate delivery-safe output |

## Deliverables

- `moodify_runtime/craft_processes.py`
- `moodify_runtime/craft_chain.py`
- `moodify_runtime/craft_selector.py`
- `moodify_runtime/craft_policy.py`
- `moodify_runtime/tests/test_craft_22_processes.py`
- `moodify_runtime/tests/test_craft_chain.py`
- Updated CLI/API hooks
- Updated craft memory writeback
- Documentation under `docs/runbook/MOODIFY_22_PROCESS_CRAFT_SYSTEM.md`

## E-Chain Map

This E-chain contains 54 MHP nodes, grouped into three NEMs.

| Range | NEM | Purpose |
|---|---|---|
| MHP-683 to MHP-700 | NEM-CRAFT-TAXONOMY | Define and register the 22 craft operations |
| MHP-701 to MHP-718 | NEM-CRAFT-CHAIN-ENGINE | Execute safe, measurable craft chains |
| MHP-719 to MHP-736 | NEM-CRAFT-INTELLIGENCE | Select craft from CT/MRS/tidal evidence and write back learning |

## NEM-CRAFT-TAXONOMY: MHP-683 to MHP-700

| MHP | Task | Acceptance Gate |
|---|---|---|
| 683 | Audit existing processing presets | List current operations and gaps |
| 684 | Define craft operation schema | Each operation has id, name, params, risk, metrics |
| 685 | Define 22 operation registry | Registry returns exactly 22 active operations |
| 686 | Add input normalize operation | Unit test covers level target and clipping safety |
| 687 | Add silence trim operation | Unit test covers trim boundaries |
| 688 | Add DC offset repair operation | Unit test verifies reduced DC bias |
| 689 | Add sub/bass operations | Sub and bass shaping are separate operations |
| 690 | Add low-mid/mid operations | De-mud and presence controls are separate |
| 691 | Add harshness/air/sibilance operations | High-band controls are distinct and bounded |
| 692 | Add transient operations | Soften and restore can be selected independently |
| 693 | Add dynamics operations | Micro and macro dynamics policies are separate |
| 694 | Add stereo/center operations | Mono safety is tested |
| 695 | Add noise/room operations | Operations are conservative and reversible by config |
| 696 | Add warmth/clarity operations | Tonal polish does not bypass safety gates |
| 697 | Add loudness/limiter operations | True peak and clipping gates exist |
| 698 | Add parameter validation | Invalid params fail fast |
| 699 | Add operation docs | Every operation has intent, risk, and metrics |
| 700 | Close taxonomy NEM | Registry and docs pass tests |

## NEM-CRAFT-CHAIN-ENGINE: MHP-701 to MHP-718

| MHP | Task | Acceptance Gate |
|---|---|---|
| 701 | Implement `CraftChain` model | Chain stores ordered operations and metadata |
| 702 | Implement chain executor | Runs selected operations on an audio artifact |
| 703 | Add dry-run planner | Shows operation order without processing |
| 704 | Add per-step metrics | Each step records before/after measurements |
| 705 | Add per-step artifact policy | Optional intermediate artifacts are controlled |
| 706 | Add safety rollback policy | Failed step preserves previous valid artifact |
| 707 | Add clipping/peak gate | Chain fails or repairs unsafe output |
| 708 | Add loudness gate | Chain records LUFS/RMS policy result if available |
| 709 | Add spectral gate | CT metrics can compare before/after |
| 710 | Add runtime budget policy | Long chains can be bounded on cloud |
| 711 | Add deterministic seed/config | Same input/config produces stable chain output |
| 712 | Add preset-to-chain adapter | Existing presets map to craft chains |
| 713 | Add chain manifest | JSON records operations, params, metrics, artifacts |
| 714 | Add CLI `craft plan` | Prints planned 22-process subset |
| 715 | Add CLI `craft run` | Runs chain on sample audio |
| 716 | Add CLI `craft inspect` | Reads manifest and summarizes result |
| 717 | Add tests for chain engine | Unit/integration tests pass |
| 718 | Close chain engine NEM | Cloud sample chain produces artifact + manifest |

## NEM-CRAFT-INTELLIGENCE: MHP-719 to MHP-736

| MHP | Task | Acceptance Gate |
|---|---|---|
| 719 | Define craft selection input | CT, MRS, preset, operator notes accepted |
| 720 | Implement rule-based selector v1 | Selector chooses operations from diagnosis |
| 721 | Add risk-aware operation limits | Dangerous combinations are blocked or warned |
| 722 | Add tidal-cycle compatibility | Tidal loop can request craft plan, not just preset |
| 723 | Add Acoustic CT feedback hook | CT deltas influence next craft plan |
| 724 | Add MRS feedback hook | Human/listening score can influence selector |
| 725 | Add craft memory writeback | Success/failure of operations is stored |
| 726 | Add adoption states | proposed, accepted, rejected, retired |
| 727 | Add operator override reason | Overrides must be recorded in manifest |
| 728 | Add 22-process coverage report | Reports which operations are used across runs |
| 729 | Add before/after PDF hook | Chain can trigger PDF comparison report |
| 730 | Add batch experiment runner | Runs controlled craft variants on cloud |
| 731 | Add benchmark fixtures | Small fixtures keep tests fast |
| 732 | Add regression tests | Existing presets still work |
| 733 | Add integration with delivery records | Delivery references craft chain manifest |
| 734 | Add runbook | Cloud execution, examples, troubleshooting |
| 735 | Record PoEW evidence | Commands, outputs, metrics, commit hash |
| 736 | Close E-chain | 22 operations, chain engine, selector, tests complete |

## Required Test Commands

```bash
cd /home/ubuntu/moodify-mainline
source .venv/bin/activate
python3 -m pytest moodify_runtime/tests/test_craft_22_processes.py -v
python3 -m pytest moodify_runtime/tests/test_craft_chain.py -v
python3 -m moodify_runtime.cli craft plan --help
python3 -m moodify_runtime.cli craft run --help
```

## Definition of Done

- Moodify exposes exactly 22 documented craft operations.
- Operators and other AI agents can plan, run, inspect, and compare craft chains.
- Each processing result has a manifest with operation order, parameters, metrics, and safety gates.
- Tidal Cycle can use craft chains as a system-level module.
- Acoustic CT PDF reports can show the processing chain and before/after effects.
