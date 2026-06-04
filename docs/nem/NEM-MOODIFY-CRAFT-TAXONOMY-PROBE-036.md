# NEM-MOODIFY-CRAFT-TAXONOMY-PROBE-036: Craft 22 Taxonomy Probe

## 1. Node Metadata

- **NEM ID**: NEM-MOODIFY-CRAFT-TAXONOMY-PROBE-036
- **Role**: Probe NEM
- **Owner**: Raphael Davad
- **Project**: Moodify
- **Status**: IN PROGRESS
- **Protocol**: NEM-18 inside E-Chain 54
- **Parent Chain**: ECHAIN-MOODIFY-CRAFT-22-012

## 2. Node Purpose

Define and register the 22 craft operations with schemas, parameters, risk levels, and unit tests. Each operation must have documented intent, risk, and metrics.

## 3. MHP Plan

| Step | Type | MHP | Plan-6 | Task | Status |
|------|------|-----|--------|------|--------|
| P1 | E | 683 | Probe Plan-6A: Taxonomy Boundary | Audit Existing Processing Presets | in_progress |
| P2 | E | 684 | Probe Plan-6A: Taxonomy Boundary | Define Craft Operation Schema | in_progress |
| P3 | V | 685 | Probe Plan-6A: Taxonomy Boundary | Define 22 Operation Registry | in_progress |
| P4 | V | 686 | Probe Plan-6A: Taxonomy Boundary | Add Input Normalize Operation | in_progress |
| P5 | S | 687 | Probe Plan-6A: Taxonomy Boundary | Add Silence Trim Operation | in_progress |
| P6 | N | 688 | Probe Plan-6A: Taxonomy Boundary | Craft Taxonomy Probe Backlog | planned |
| P7 | E | 689 | Probe Plan-6B: Operation Build | Add Sub-Bass and Bass Operations | planned |
| P8 | E | 690 | Probe Plan-6B: Operation Build | Add Low-Mid and Mid Operations | planned |
| P9 | V | 691 | Probe Plan-6B: Operation Build | Add Harshness/Air/Sibilance Operations | planned |
| P10 | V | 692 | Probe Plan-6B: Operation Build | Add Transient Operations | planned |
| P11 | S | 693 | Probe Plan-6B: Operation Build | Add Dynamics Operations | planned |
| P12 | N | 694 | Probe Plan-6B: Operation Build | Operation Build Report | planned |
| P13 | E | 695 | Probe Plan-6C: Taxonomy Gate | Add Stereo/Center Operations | planned |
| P14 | E | 696 | Probe Plan-6C: Taxonomy Gate | Add Noise/Room Operations | planned |
| P15 | V | 697 | Probe Plan-6C: Taxonomy Gate | Add Warmth/Clarity Operations | planned |
| P16 | V | 698 | Probe Plan-6C: Taxonomy Gate | Add Loudness/Limiter Operations | planned |
| P17 | S | 699 | Probe Plan-6C: Taxonomy Gate | Add Operation Docs and Parameter Validation | planned |
| P18 | N | 700 | Probe Plan-6C: Taxonomy Gate | Close Taxonomy NEM | planned |

## 4. Gate Criteria

- All 22 operations registered with id, name, params, risk level, and metrics.
- Each operation has parameter validation (invalid params fail fast).
- Unit tests cover each operation.
- Registry returns exactly 22 active operations.
