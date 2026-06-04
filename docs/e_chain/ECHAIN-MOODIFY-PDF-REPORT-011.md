# ECHAIN-MOODIFY-PDF-REPORT-011

## Title

Moodify Cloud PDF Report Module

## Status

PLANNED

## Strategic Intent

Build a first-class PDF reporting module inside Moodify so every acoustic scan and every processed result can produce a branded, stable, cloud-generated report. This module must run on Tencent Cloud under `/home/ubuntu/moodify-mainline`; it must not depend on local Windows-only tools.

The report should feel like an industrial acoustic CT output: clear enough for internal operators to judge the effect quickly, structured enough for later automation, and branded enough to become a reusable Moodify artifact.

## Current Evidence

Local samples downloaded from cloud:

- `E:\moodify\data\outpot\CT_1088FCB0.pdf`
- `E:\moodify\data\outpot\CT_9936FC1D.pdf`
- `E:\moodify\data\outpot\OKAY_OKAY_COMPARISON.pdf`

Observed quality:

- The dark CT-style visual language is directionally correct.
- The spectrogram pages already look like real diagnostic output.
- The Moodify logo appears, but the white logo block is visually heavy and needs a clear standard.
- Footer text is too faint in several pages.
- Frequency balance pages are readable but too sparse; they need diagnostic annotation.
- Before/after comparison is useful, but scales and deltas must be standardized so changes are trustworthy.
- The PDF output exists, but the project still needs a reusable `moodify_runtime` PDF module and cloud dependency checks.

## Cloud Runtime Requirement

Primary execution environment:

```bash
ssh ubuntu@43.156.175.4
cd /home/ubuntu/moodify-mainline
source .venv/bin/activate
```

Required principle:

- All PDF creation, QA, and tests must pass on Tencent Cloud.
- If PDF dependencies are missing, add them to the project dependency path used by cloud runtime.
- Do not rely on manually installed Windows packages.

## Canonical Brand Asset

Expected cloud path:

```text
assets/brand/moodify_logo_symbol_original_white_canvas_1254.png
```

If absent, the executor must add or upload the asset before closing this E-chain.

Report logo rules:

- Logo must appear in the header of every report page.
- Logo size must be fixed by template, not manually tuned per figure.
- Header must preserve clear space around the logo.
- The logo must never overlap plot titles, axes, legends, or footer.

## Deliverables

- `moodify_runtime/pdf_report.py`
- `moodify_runtime/pdf_templates.py`
- `moodify_runtime/pdf_assets.py`
- `moodify_runtime/pdf_qa.py`
- CLI entry points for rendering single and comparison reports
- Tests under `moodify_runtime/tests/`
- Example generated PDFs under `outputs/demo_single/ct_scan/`
- Runbook under `docs/runbook/MOODIFY_PDF_REPORT_MODULE.md`

## E-Chain Map

This E-chain contains 54 MHP nodes, grouped into three NEMs.

| Range | NEM | Purpose |
|---|---|---|
| MHP-629 to MHP-646 | NEM-PDF-FOUNDATION | Cloud dependency, data contract, template foundation |
| MHP-647 to MHP-664 | NEM-PDF-ACOUSTIC-CT | Acoustic CT pages, comparison pages, diagnostic layer |
| MHP-665 to MHP-682 | NEM-PDF-OPS-QA | CLI/API integration, QA, regression, runbook |

## NEM-PDF-FOUNDATION: MHP-629 to MHP-646

| MHP | Task | Acceptance Gate |
|---|---|---|
| 629 | Probe cloud PDF/rendering dependencies | Script reports available/missing libs without crashing |
| 630 | Choose supported PDF stack | Decision doc explains ReportLab/PyMuPDF/matplotlib path |
| 631 | Add dependency spec | Fresh cloud venv can install and import required modules |
| 632 | Define `PdfReportConfig` | Includes page size, theme, brand asset, footer, output dir |
| 633 | Define `PdfReportManifest` | JSON manifest links source audio, processed audio, plots, PDF |
| 634 | Implement brand asset resolver | Missing logo gives clear error and fallback behavior |
| 635 | Implement page template contract | Header, body, footer regions are stable |
| 636 | Implement dark industrial theme | Colors/typography match Acoustic CT visual direction |
| 637 | Implement figure export helper | Matplotlib figures export consistently for PDF embedding |
| 638 | Implement PDF writer skeleton | Can create a one-page branded PDF on cloud |
| 639 | Add metadata block | PDF contains report id, preset, source, timestamp |
| 640 | Add output path policy | Reports land in deterministic output directories |
| 641 | Add manifest writer | Every PDF has sibling `.manifest.json` |
| 642 | Add basic unit tests | Config, asset, manifest, writer tests pass |
| 643 | Add cloud smoke command | One command renders sample report on Tencent Cloud |
| 644 | Add failure diagnostics | Missing dependency/logo/audio errors are actionable |
| 645 | Add golden sample fixture | Small fixture avoids large audio in tests |
| 646 | Close foundation NEM | All MHP-629 to 645 gates pass in cloud |

## NEM-PDF-ACOUSTIC-CT: MHP-647 to MHP-664

| MHP | Task | Acceptance Gate |
|---|---|---|
| 647 | Implement spectrogram report page | Page resembles current CT visual but uses template |
| 648 | Implement frequency balance page | Uses standardized axes and band labels |
| 649 | Implement waveform dynamics page | Waveform and RMS panels fit without overlap |
| 650 | Implement summary/diagnosis page | Human-readable findings and gate result appear |
| 651 | Add risk-band visual grammar | Sub-bass/low-mid/etc. bands have documented colors |
| 652 | Add diagnostic callouts | Top risks and improvements are annotated on pages |
| 653 | Add before/after comparison layout | Same metric scales for before and after |
| 654 | Add delta chart page | Shows change in energy, risk, loudness, MRS if available |
| 655 | Add processing chain section | Lists preset, process passes, parameters, overrides |
| 656 | Add audio identity block | Shows input id, output id, duration, sample rate |
| 657 | Add CT quality score | Report includes scan completeness and visual QA status |
| 658 | Add PDF filename policy | Names are deterministic and operator-friendly |
| 659 | Add report bundle integration | PDF is included in existing report bundle system |
| 660 | Add example single report | Cloud produces one polished single CT report |
| 661 | Add example comparison report | Cloud produces one polished before/after PDF |
| 662 | Add visual regression snapshots | First pages can be rasterized or image-checked in tests |
| 663 | Add tests for CT builders | Unit tests cover page generation and manifests |
| 664 | Close CT NEM | Single and comparison PDFs pass cloud smoke QA |

## NEM-PDF-OPS-QA: MHP-665 to MHP-682

| MHP | Task | Acceptance Gate |
|---|---|---|
| 665 | Add CLI `pdf-report render-single` | Command renders PDF from audio/result paths |
| 666 | Add CLI `pdf-report render-comparison` | Command renders before/after PDF |
| 667 | Add CLI `pdf-report inspect` | Command prints pages, manifest, asset status |
| 668 | Add API endpoint if operator API exists | Endpoint can request report generation |
| 669 | Add job runner hook | Processing jobs can request PDF output automatically |
| 670 | Add delivery record hook | Delivery records link PDF artifacts |
| 671 | Add craft memory hook | Craft writeback stores report manifest path |
| 672 | Add PDF QA checks | Checks non-empty pages, logo presence, footer readability |
| 673 | Add text extraction smoke | Title/report id are extractable or manifest-backed |
| 674 | Add image/render smoke | First page can be rendered in CI/cloud |
| 675 | Add comparison scale QA | Before/after pages verify shared axis policy |
| 676 | Add artifact cleanup policy | Large temp images are cleaned or placed under output dir |
| 677 | Add runbook | Cloud commands, dependencies, examples, troubleshooting |
| 678 | Add operator handoff note | DeepSeek/Claude can run module without PDF knowledge gaps |
| 679 | Add regression test suite | Tests pass with `python3 -m pytest moodify_runtime/tests/ -v` |
| 680 | Generate final sample PDFs | Fresh cloud outputs replace or accompany demo samples |
| 681 | Record PoEW evidence | Commit hash, commands, outputs, screenshots/manifests |
| 682 | Close E-chain | All 54 gates complete and cloud smoke reports exist |

## Required Test Commands

```bash
cd /home/ubuntu/moodify-mainline
source .venv/bin/activate
python3 -m pytest moodify_runtime/tests/ -v
python3 -m moodify_runtime.cli pdf-report render-single --help
python3 -m moodify_runtime.cli pdf-report render-comparison --help
```

## Definition of Done

- PDF module is reusable inside `moodify_runtime`.
- Cloud can generate branded single and before/after Acoustic CT PDFs.
- Reports include logo, manifest, diagnostic summary, and stable visual scales.
- Existing demo PDFs are improved or regenerated through the new module.
- No PDF generation step depends on the local Windows machine.

