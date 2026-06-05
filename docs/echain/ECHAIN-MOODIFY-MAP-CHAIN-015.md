# ECHAIN-MOODIFY-MAP-CHAIN-015: MAP-Chain Industrial Processing Protocol

## 1. Chain Metadata

- **E-Chain ID**: ECHAIN-MOODIFY-MAP-CHAIN-015
- **Project**: Moodify
- **Status**: SEALED ✅ — E-Chain 015 closed 2026-06-05. 54 MHPs, 60 tests, 3 NEMs complete.
- **Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18
- **Control Mode**: AWJ Stack
- **Parent**: ECHAIN-MOODIFY-ACOUSTIC-CT-007, ECHAIN-MOODIFY-PDF-REPORT-011, ECHAIN-MOODIFY-CRAFT-22-012
- **Target Gate**: SEALED

## 2. Phase Transition Target

```text
one-click audio processing -> S-A-D-P-V-R-G industrial delivery chain
```

Moodify must stop treating a processed WAV as the product. The product is the MAP-Chain delivery package:

```text
Y = G o R o V o P_theta o D o A o S(X0)
```

The first mainline alignment is already started in `moodify-core-package/src/moodify/v01_pipeline.py`: v01 now records scan, before/after metrics, validation, JSON/PDF reports, and delivery artifacts. This E-chain turns that local improvement into a stable engineering protocol.

## 3. MAP-Chain Current Gap Map

| MAP Layer | Current State | Required Upgrade | AWJ Owner |
| --- | --- | --- | --- |
| S Scan | File readability, basic spectrum/dynamics, before chart | formal scan object with loudness, transient, space, texture, reality fields | Worker + Judge |
| A Analyze | raw metric object reused as analysis | feature vector `b,w,c,p,d,s,t,r` and task/genre weights | Worker candidate, Architect contract |
| D Diagnose | issue strings and preset suggestions | problem vector, severity, priority, diagnosis loss | Architect + Worker |
| P Process | 3 v01 presets, `auto` selector | diagnosis-aware craft selector, 22-operation adapter, safe limits | Architect + Worker |
| V Validate | quality gate and `mrs_proxy_v01` | calibrated MRS before/after, damage loss, risk matrix, pass policy | Judge-heavy |
| R Report | compact JSON/PDF delivery report | reusable MAP report schema, CT plates, customer/operator sections | Worker + Judge |
| G Generate | delivery paths in JSON | reproducible package with metadata, logs, manifest, environment | Worker + Judge |

## 4. Three-NEM Structure

| NEM | Role | MHP Range | Purpose | Gate |
| --- | --- | --- | --- | --- |
| NEM-MOODIFY-MAP-PROBE-045 | Probe NEM | MHP-845 to MHP-862 | Audit the current v01/runtime/report/craft/MRS surfaces against MAP, define contracts, choose what is mainline vs future work. | Gate 1: ADOPT / HOLD / DROP |
| NEM-MOODIFY-MAP-BUILD-046 | Build NEM | MHP-863 to MHP-880 | Implement MAP report schema, feature/problem vectors, calibrated validation adapter, delivery manifest, CLI/API contract. | Gate 2: ADOPT / HOLD / ROLLBACK |
| NEM-MOODIFY-MAP-SYSTEM-047 | System NEM | MHP-881 to MHP-898 | Add AWJ worker packs, Judge gates, operator runbook, regression evidence, and seal MAP v0.1. | Gate 3: SEALED / EXTEND / REWORK |

## 5. Full MHP Index

| MHP | Type | NEM | Plan | Title |
| --- | --- | --- | --- | --- |
| 845 | E | MAP-PROBE-045 | Probe 6A | MAP-Chain Current State Audit |
| 846 | E | MAP-PROBE-045 | Probe 6A | MAP Interface Contract |
| 847 | V | MAP-PROBE-045 | Probe 6A | v01 Seven-Stage Alignment Smoke |
| 848 | V | MAP-PROBE-045 | Probe 6A | MAP Report Schema Probe |
| 849 | S | MAP-PROBE-045 | Probe 6A | AWJ Scope and Forbidden Files Policy |
| 850 | N | MAP-PROBE-045 | Probe 6A | Probe Gate 1 Evidence Package |
| 851 | E | MAP-PROBE-045 | Probe 6B | Scan Vector Gap Brief |
| 852 | E | MAP-PROBE-045 | Probe 6B | Feature Vector Weighting Brief |
| 853 | V | MAP-PROBE-045 | Probe 6B | Diagnosis Problem Taxonomy Probe |
| 854 | V | MAP-PROBE-045 | Probe 6B | MRS Proxy Replacement Boundary |
| 855 | S | MAP-PROBE-045 | Probe 6B | Delivery Package Inventory |
| 856 | N | MAP-PROBE-045 | Probe 6B | Probe Decision |
| 857 | E | MAP-PROBE-045 | Probe 6C | Worker Task JSONL Shape |
| 858 | E | MAP-PROBE-045 | Probe 6C | Judge Result Schema Shape |
| 859 | V | MAP-PROBE-045 | Probe 6C | Command Gate Smoke Plan |
| 860 | V | MAP-PROBE-045 | Probe 6C | Diff Risk Gate Plan |
| 861 | S | MAP-PROBE-045 | Probe 6C | MAP Build Entry |
| 862 | N | MAP-PROBE-045 | Probe 6C | Close Probe NEM |
| 863 | E | MAP-BUILD-046 | Build 6A | Implement MAP Data Model |
| 864 | E | MAP-BUILD-046 | Build 6A | Implement Scan Result Contract |
| 865 | V | MAP-BUILD-046 | Build 6A | Implement Feature Vector Contract |
| 866 | V | MAP-BUILD-046 | Build 6A | Implement Diagnosis Vector Contract |
| 867 | S | MAP-BUILD-046 | Build 6A | MAP Core Tests |
| 868 | N | MAP-BUILD-046 | Build 6A | Close Data Model Block |
| 869 | E | MAP-BUILD-046 | Build 6B | MRS Engine Adapter Hook |
| 870 | E | MAP-BUILD-046 | Build 6B | Damage Loss Gate |
| 871 | V | MAP-BUILD-046 | Build 6B | Risk Flag Taxonomy |
| 872 | V | MAP-BUILD-046 | Build 6B | Pass Policy Threshold Config |
| 873 | S | MAP-BUILD-046 | Build 6B | Validation Matrix Tests |
| 874 | N | MAP-BUILD-046 | Build 6B | Close Validation Block |
| 875 | E | MAP-BUILD-046 | Build 6C | Delivery Manifest Writer |
| 876 | E | MAP-BUILD-046 | Build 6C | Reproducibility Metadata Hook |
| 877 | V | MAP-BUILD-046 | Build 6C | JSON/PDF Report Contract |
| 878 | V | MAP-BUILD-046 | Build 6C | CLI/API MAP Contract |
| 879 | S | MAP-BUILD-046 | Build 6C | Build Gate Report |
| 880 | N | MAP-BUILD-046 | Build 6C | Close Build NEM |
| 881 | E | MAP-SYSTEM-047 | System 6A | AWJ Worker Pack Generator |
| 882 | E | MAP-SYSTEM-047 | System 6A | Judge Schema Checker |
| 883 | V | MAP-SYSTEM-047 | System 6A | Judge Output Checker |
| 884 | V | MAP-SYSTEM-047 | System 6A | Judge Command Checker |
| 885 | S | MAP-SYSTEM-047 | System 6A | AWJ Integration Smoke |
| 886 | N | MAP-SYSTEM-047 | System 6A | Close AWJ Gate Block |
| 887 | E | MAP-SYSTEM-047 | System 6B | Operator MAP Runbook |
| 888 | E | MAP-SYSTEM-047 | System 6B | Customer Report Redaction Policy |
| 889 | V | MAP-SYSTEM-047 | System 6B | MAP Regression Evidence Pack |
| 890 | V | MAP-SYSTEM-047 | System 6B | Delivery Artifact QA |
| 891 | S | MAP-SYSTEM-047 | System 6B | Product Acceptance Smoke |
| 892 | N | MAP-SYSTEM-047 | System 6B | Close Product Block |
| 893 | E | MAP-SYSTEM-047 | System 6C | MAP Manifest Version |
| 894 | E | MAP-SYSTEM-047 | System 6C | Ownership Map |
| 895 | V | MAP-SYSTEM-047 | System 6C | AI Agent MAP Handoff Pack |
| 896 | V | MAP-SYSTEM-047 | System 6C | Next MAP Candidates |
| 897 | S | MAP-SYSTEM-047 | System 6C | Gate 3 Seal Decision |
| 898 | N | MAP-SYSTEM-047 | System 6C | Close E-Chain |

## 6. AWJ Control Policy

### Architect Layer

- Owns MAP formulas, layer boundaries, schemas, threshold policy, merge decisions.
- Must approve changes touching `v01_pipeline.py`, MRS scoring semantics, delivery package contract, or public API shape.
- Defines each Worker task with allowed files, expected outputs, proof requirements, and merge policy.

### Worker Layer

- Can implement bounded AEPs in scan/report/manifest/test surfaces.
- Can draft JSON schemas, markdown runbooks, local tests, and non-core helper modules.
- Must not change the meaning of MRS, remove quality gates, or expand scope beyond the task spec.

### Judge Layer

Required gates for every MAP AEP:

```text
G_schema * G_scope * G_runtime * G_test * G_evidence * G_arch = 1
```

Minimum checks:

- schema fields exist and parse;
- modified files stay inside allowed scope;
- target CLI/API command exits 0;
- specified tests pass;
- generated WAV/JSON/PDF/charts exist;
- diff risk is low or Architect-reviewed;
- Codex semantic review accepts the result.

## 7. Immediate Mainline Upgrade Already Applied

The first local upgrade aligns v01 with MAP naming:

```text
S_scan -> A_analyze -> D_diagnose -> P_process -> V_validate -> R_report -> G_generate
```

It adds:

- `auto` preset selection from diagnosis suggestions;
- before/after metrics and charts;
- `validation_result` with `mrs_proxy_v01`, damage loss, risk flags, and pass status;
- JSON report with MAP layer fields;
- PDF report and delivery bundle paths.

This is not the final MAP system. It is the v0.1 bridge that makes the future E-chain executable.

## 8. Definition of Done

- v01 and runtime surfaces expose the same MAP layer vocabulary.
- MAP report JSON has stable schema and backwards-compatible API exposure.
- MRS proxy is replaced or explicitly wrapped by a calibrated MRS adapter.
- Delivery package includes audio, PDF, charts, JSON metrics, metadata, logs, and reproducibility fields.
- AWJ Judge can reject malformed, unscoped, untested, or low-evidence Worker output.
- Gate 3 evidence shows at least one real-audio MAP run with WAV/JSON/PDF/charts and passing tests.

