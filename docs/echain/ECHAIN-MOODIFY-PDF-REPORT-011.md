# ECHAIN-MOODIFY-PDF-REPORT-011: Moodify Cloud PDF Report Module E-Chain 54

## 1. Chain Metadata

- **E-Chain ID**: ECHAIN-MOODIFY-PDF-REPORT-011
- **Owner**: Raphael Davad
- **Project**: Moodify
- **Status**: PLANNED
- **Start Date**: 2026-06-04
- **Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18
- **Parent**: ECHAIN-MOODIFY-TIDAL-OPERATIONS-010
- **Target Gate**: SEALED

## 2. Phase Transition Target

```text
manual/demo PDF generation -> reusable moodify_runtime PDF report module
```

Build a first-class PDF reporting module inside Moodify so every acoustic scan and every processed result can produce a branded, stable, cloud-generated report. This module must run on Tencent Cloud under `/home/ubuntu/moodify-mainline`; it must not depend on local Windows-only tools.

## 3. Product Concept

- **Single Scan PDF**: branded Acoustic CT diagnostic report with spectrogram, frequency balance, waveform dynamics, summary/diagnosis page.
- **Comparison PDF**: before/after paired visual plates with delta charts, processing chain section, and audio identity block.
- **Reusable Module**: `moodify_runtime/pdf_report.py` as the canonical PDF generation entry point, callable from CLI, API, and other modules.

## Brand Asset Requirement

All PDF reports must include the Moodify brand symbol. Use this canonical asset path:

```text
assets/brand/moodify_logo_symbol_original_white_canvas_1254.png
```

The logo must appear in the header of every report page with fixed template sizing, clear space preserved, never overlapping plot titles/axes/legends/footer.

## 4. Three-NEM Structure

| NEM | Role | MHP Range | Purpose | Gate |
|-----|------|-----------|---------|------|
| NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe NEM | MHP-629 to MHP-646 | Cloud dependency probe, PDF stack selection, data contracts, template foundation, brand assets, dark theme, figure export, PDF writer skeleton, smoke. | Gate 1: ADOPT / HOLD / DROP |
| NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build NEM | MHP-647 to MHP-664 | Acoustic CT pages, comparison pages, diagnostic layer, before/after deltas, processing chain section, identity block, quality score, report bundle integration. | Gate 2: ADOPT / HOLD / ROLLBACK |
| NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System NEM | MHP-665 to MHP-682 | CLI/API integration, QA checks, regression tests, artifact cleanup, runbook, operator handoff, PoEW evidence, seal. | Gate 3: SEALED / EXTEND / REWORK |

## 5. Full MHP Index

| MHP | Type | NEM | Plan-6 | Title |
|-----|------|-----|--------|-------|
| 629 | E | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6A: Foundation Boundary | Probe Cloud PDF Rendering Dependencies |
| 630 | E | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6A: Foundation Boundary | Choose Supported PDF Stack |
| 631 | V | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6A: Foundation Boundary | Add Dependency Spec |
| 632 | V | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6A: Foundation Boundary | Define PdfReportConfig |
| 633 | S | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6A: Foundation Boundary | Define PdfReportManifest |
| 634 | N | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6A: Foundation Boundary | PDF Foundation Probe Backlog |
| 635 | E | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6B: Template Foundation | Implement Brand Asset Resolver |
| 636 | E | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6B: Template Foundation | Implement Page Template Contract |
| 637 | V | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6B: Template Foundation | Implement Dark Industrial Theme |
| 638 | V | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6B: Template Foundation | Implement Figure Export Helper |
| 639 | S | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6B: Template Foundation | Implement PDF Writer Skeleton |
| 640 | N | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6B: Template Foundation | PDF Foundation Tech Probe Report |
| 641 | E | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6C: Foundation Gate | Add Metadata Block |
| 642 | E | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6C: Foundation Gate | Add Output Path Policy |
| 643 | V | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6C: Foundation Gate | Add Manifest Writer |
| 644 | V | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6C: Foundation Gate | Add Basic Unit Tests |
| 645 | S | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6C: Foundation Gate | Add Cloud Smoke Command |
| 646 | N | NEM-MOODIFY-PDF-FOUNDATION-PROBE-033 | Probe Plan-6C: Foundation Gate | Close Foundation NEM |
| 647 | E | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6A: Acoustic CT Pages | Implement Spectrogram Report Page |
| 648 | E | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6A: Acoustic CT Pages | Implement Frequency Balance Page |
| 649 | V | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6A: Acoustic CT Pages | Implement Waveform Dynamics Page |
| 650 | V | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6A: Acoustic CT Pages | Implement Summary Diagnosis Page |
| 651 | S | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6A: Acoustic CT Pages | Add Risk-Band Visual Grammar |
| 652 | N | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6A: Acoustic CT Pages | Acoustic CT Pages Tests |
| 653 | E | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6B: Comparison Layer | Add Diagnostic Callouts |
| 654 | E | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6B: Comparison Layer | Add Before/After Comparison Layout |
| 655 | V | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6B: Comparison Layer | Add Delta Chart Page |
| 656 | V | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6B: Comparison Layer | Add Processing Chain Section |
| 657 | S | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6B: Comparison Layer | Add Audio Identity Block |
| 658 | N | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6B: Comparison Layer | Comparison Layer Tests |
| 659 | E | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6C: Product Integration | Add CT Quality Score |
| 660 | E | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6C: Product Integration | Add PDF Filename Policy |
| 661 | V | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6C: Product Integration | Add Report Bundle Integration |
| 662 | V | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6C: Product Integration | Add Example Single Report |
| 663 | S | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6C: Product Integration | Add Example Comparison Report |
| 664 | N | NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034 | Build Plan-6C: Product Integration | Close CT NEM |
| 665 | E | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6A: CLI and API | Add CLI pdf-report render-single |
| 666 | E | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6A: CLI and API | Add CLI pdf-report render-comparison |
| 667 | V | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6A: CLI and API | Add CLI pdf-report inspect |
| 668 | V | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6A: CLI and API | Add API Endpoint for Report Generation |
| 669 | S | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6A: CLI and API | Add Job Runner Hook |
| 670 | N | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6A: CLI and API | CLI/API Integration Smoke |
| 671 | E | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6B: QA and Validation | Add Delivery Record Hook |
| 672 | E | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6B: QA and Validation | Add Craft Memory Hook |
| 673 | V | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6B: QA and Validation | Add PDF QA Checks |
| 674 | V | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6B: QA and Validation | Add Text Extraction Smoke |
| 675 | S | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6B: QA and Validation | Add Image Render Smoke |
| 676 | N | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6B: QA and Validation | QA Validation Report |
| 677 | E | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6C: Seal and Next Entry | Add Comparison Scale QA |
| 678 | E | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6C: Seal and Next Entry | Add Artifact Cleanup Policy |
| 679 | V | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6C: Seal and Next Entry | Add Runbook |
| 680 | V | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6C: Seal and Next Entry | Add Operator Handoff Note |
| 681 | S | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6C: Seal and Next Entry | Add Regression Test Suite |
| 682 | N | NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035 | System Plan-6C: Seal and Next Entry | Close E-Chain |

## 6. Deliverables

- `moodify_runtime/pdf_report.py`
- `moodify_runtime/pdf_templates.py`
- `moodify_runtime/pdf_assets.py`
- `moodify_runtime/pdf_qa.py`
- CLI entry points for rendering single and comparison reports
- Tests under `moodify_runtime/tests/`
- Example generated PDFs under `outputs/demo_single/ct_scan/`
- Runbook under `docs/runbook/MOODIFY_PDF_REPORT_MODULE.md`

## 7. Definition of Done

- PDF module is reusable inside `moodify_runtime`.
- Cloud can generate branded single and before/after Acoustic CT PDFs.
- Reports include logo, manifest, diagnostic summary, and stable visual scales.
- Existing demo PDFs are improved or regenerated through the new module.
- No PDF generation step depends on the local Windows machine.
