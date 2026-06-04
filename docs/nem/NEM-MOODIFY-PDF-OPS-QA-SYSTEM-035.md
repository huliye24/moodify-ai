# NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035: PDF Ops and QA System

## 1. Node Metadata

- **NEM ID**: NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035
- **Role**: System NEM
- **Owner**: Raphael Davad
- **Project**: Moodify
- **Status**: PLANNED
- **Protocol**: NEM-18 inside E-Chain 54
- **Parent Chain**: ECHAIN-MOODIFY-PDF-REPORT-011

## 2. Node Purpose

Add CLI/API integration for PDF report rendering, QA checks, regression tests, artifact cleanup policy, runbook, operator handoff, PoEW evidence, and seal the E-chain.

## 3. MHP Plan

| Step | Type | MHP | Plan-6 | Task | Status |
|------|------|-----|--------|------|--------|
| P1 | E | 665 | System Plan-6A: CLI and API | Add CLI pdf-report render-single | planned |
| P2 | E | 666 | System Plan-6A: CLI and API | Add CLI pdf-report render-comparison | planned |
| P3 | V | 667 | System Plan-6A: CLI and API | Add CLI pdf-report inspect | planned |
| P4 | V | 668 | System Plan-6A: CLI and API | Add API Endpoint for Report Generation | planned |
| P5 | S | 669 | System Plan-6A: CLI and API | Add Job Runner Hook | planned |
| P6 | N | 670 | System Plan-6A: CLI and API | CLI/API Integration Smoke | planned |
| P7 | E | 671 | System Plan-6B: QA and Validation | Add Delivery Record Hook | planned |
| P8 | E | 672 | System Plan-6B: QA and Validation | Add Craft Memory Hook | planned |
| P9 | V | 673 | System Plan-6B: QA and Validation | Add PDF QA Checks | planned |
| P10 | V | 674 | System Plan-6B: QA and Validation | Add Text Extraction Smoke | planned |
| P11 | S | 675 | System Plan-6B: QA and Validation | Add Image Render Smoke | planned |
| P12 | N | 676 | System Plan-6B: QA and Validation | QA Validation Report | planned |
| P13 | E | 677 | System Plan-6C: Seal and Next Entry | Add Comparison Scale QA | planned |
| P14 | E | 678 | System Plan-6C: Seal and Next Entry | Add Artifact Cleanup Policy | planned |
| P15 | V | 679 | System Plan-6C: Seal and Next Entry | Add Runbook | planned |
| P16 | V | 680 | System Plan-6C: Seal and Next Entry | Add Operator Handoff Note | planned |
| P17 | S | 681 | System Plan-6C: Seal and Next Entry | Add Regression Test Suite | planned |
| P18 | N | 682 | System Plan-6C: Seal and Next Entry | Close E-Chain | planned |

## 4. Gate Criteria

- CLI commands `pdf-report render-single`, `render-comparison`, `inspect` work on cloud.
- API endpoint can request report generation.
- PDF QA checks pass (non-empty pages, logo presence, footer readability).
- Text extraction and image render smoke pass.
- Comparison scale QA verifies shared axis policy.
- Artifact cleanup policy is documented and applied.
- Runbook, operator handoff, regression tests, and PoEW evidence are complete.
- E-Chain is SEALED.
