# Capacity & Scaling Contract

## Current Stage

Target:

`1 Golden Song → 3 songs → 10 songs`

## Per-node Contract

### [Node]

- max concurrent jobs:
- supported expected song duration:
- RAM safe floor:
- swap warning:
- disk scratch budget:
- CPU warning:
- temp cleanup owner:
- external API assumptions:
- evidence:
- unknowns:

## Scale-up Triggers

Do not scale merely because resources exist.

Examples of valid triggers:

- repeated memory pressure
- sustained queue delay
- repeated processing timeout
- verified external API bottleneck
- disk/scratch contention
- inability to complete 3-song pilot safely

## Unknown Rule

If no measured evidence exists:

`CAPACITY_UNKNOWN — MEASURE_IN_P07/P08`
