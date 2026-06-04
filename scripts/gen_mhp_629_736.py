#!/usr/bin/env python3
"""Generate MHP-629 to MHP-736 plan files for PDF-REPORT-011 and CRAFT-22-012.

Protocol: NEM-18 = 3 × Plan-6 = 2E+2V+1S+1N per Plan-6
E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18
"""

from pathlib import Path

PLAN_DIR = Path("/home/ubuntu/moodify-mainline/docs/plan")

# ═══════════════════════════════════════════════════════════
# Data definition
# ═══════════════════════════════════════════════════════════


def make_mhp_seal_section(num, echain, nem):
    """Return the Seal Protocol section for a new MHP."""
    seal_id = f"SEAL-MOODIFY-MHP{num:03d}"
    aep_id = f"AEP-MOODIFY-MHP{num:03d}"
    return f"""
## Seal Protocol (AEP Industrial Seal v0.1)

> ⚠️ **Pending** — this MHP has not been executed yet.
> Do NOT mark INDUSTRIAL_DONE until all six evidence layers are complete.

```yaml
# ── Identity ──
seal_id: {seal_id}
aep_id: {aep_id}
nem_id: {nem}
e_chain_id: {echain}
project: Moodify
version: v0.1
created_at: pending
executor: pending
reviewer: pending

# ── Status ──
seal_status: PLANNED
function_complete: false

# ── PoEW Reference ──
poew_id: pending
poew_file: pending
poew_hash: pending
execution_timestamp: pending
execution_duration_s: pending
environment: pending

# ── Gate Reference ──
gate_id: pending
gate_file: pending
gate_result: pending
must_pass_total: 0
must_pass_passed: 0
must_stop_triggered: false

# ── Evidence Bundle (6 layers) ──
functional_evidence: []
execution_evidence: []
quality_evidence: []
integrity_evidence: []
risk_evidence: []
downstream_evidence: []

# ── Test Summary ──
tests_total: 0
tests_passed: 0
tests_failed: 0
tests_skipped: 0
success_rate: 0.0
critical_failures: 0

# ── Artifact Summary ──
artifacts: []

# ── Risk Summary ──
risks: []

# ── Downstream ──
downstream_dependency_note: pending
reopen_criteria: []

# ── Decision ──
seal_decision:
  decision: PLANNED
  decision_reason: MHP not yet executed
  approved_by: pending
  approved_at: pending
  next_status: FUNCTION_COMPLETE
```
"""


def make_mhp(num, title, direction, depends, context, goal, expected_output,
             exec_notes, accept_criteria, echain="", nem=""):
    """Return a single MHP markdown string (AEP Seal Protocol v0.1 compliant)."""
    seal = make_mhp_seal_section(num, echain, nem)
    return f"""# MHP-{num}: {title}

**Status**: planned
⚠️ **工业封口**: 未完成
**Direction**: {direction}
**Depends on**: MHP-{depends}
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Context

{context}

## Goal

{goal}

## Expected Output

`{expected_output}`

## Execution Notes

{chr(10).join('- ' + n for n in exec_notes)}

## Acceptance Criteria

{chr(10).join('- ' + a for a in accept_criteria)}
{seal}"""


def title_to_slug(title):
    """Convert title to snake_case slug."""
    return title.lower().replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")


# ═══════════════════════════════════════════════════════════
# PDF-REPORT-011
# ═══════════════════════════════════════════════════════════

PDF_CONTEXT = (
    "Moodify acoustic scans and processed results should produce branded, "
    "stable, cloud-generated PDF reports. The existing demo PDFs show the "
    "right visual direction but were generated ad-hoc. The project needs a "
    "reusable moodify_runtime PDF module that can generate single-scan "
    "diagnostic reports and before/after comparison reports on Tencent Cloud "
    "without depending on Windows-only tools."
)

PDF_PROBE_EXEC = [
    "Probe cloud dependencies before committing to a PDF stack.",
    "Validate that the chosen stack works on Tencent Cloud with matplotlib Agg backend.",
    "Every template decision must be testable with a one-page smoke PDF.",
    "Record dependency gaps, fallback behavior, and cloud-specific constraints.",
]

PDF_BUILD_EXEC = [
    "Build Acoustic CT PDF pages using the dark industrial theme and brand templates.",
    "Ensure before/after comparisons use shared axis scales for trustworthy deltas.",
    "Every new page type must have a corresponding unit test or smoke render.",
    "Preserve compatibility with existing acoustic_ct.py plate generators.",
]

PDF_SYSTEM_EXEC = [
    "CLI commands must be callable from cloud: python3 -m moodify_runtime.cli pdf-report ...",
    "QA checks must verify non-empty pages, logo presence, footer readability, and structural validity.",
    "Regression tests must pass with python3 -m pytest moodify_runtime/tests/ -v.",
    "The runbook must enable DeepSeek/Claude operators to run the module without PDF knowledge gaps.",
]

PDF_ACCEPT = [
    "The expected output exists or a HOLD reason is documented.",
    "The PDF module gains a reusable function, template, config, or QA check.",
    "Failures are recorded as reusable engineering memory.",
    "The next MHP can start without reconstructing context.",
]

# ── Probe NEM: PDF-FOUNDATION (629-646) ──

pdf_probe_plan6a = [
    (629, "P1 (Execution)", "Probe Plan-6A: Foundation Boundary",
     "Probe Cloud PDF Rendering Dependencies",
     "Complete `Probe Cloud PDF Rendering Dependencies` as a state-converting AEP for selecting a supported cloud PDF stack. Probe all available rendering libraries and document what works on Tencent Cloud."),
    (630, "P2 (Execution)", "Probe Plan-6A: Foundation Boundary",
     "Choose Supported PDF Stack",
     "Complete `Choose Supported PDF Stack` as a state-converting AEP for establishing the canonical PDF rendering path. Select matplotlib.backends.backend_pdf + PdfPages and document the decision."),
    (631, "P3 (Validation)", "Probe Plan-6A: Foundation Boundary",
     "Add Dependency Spec",
     "Complete `Add Dependency Spec` as a state-converting AEP for verifying that a fresh cloud venv can install and import all required PDF modules without manual intervention."),
    (632, "P4 (Validation)", "Probe Plan-6A: Foundation Boundary",
     "Define PdfReportConfig",
     "Complete `Define PdfReportConfig` as a state-converting AEP for creating a validated config dataclass with page size, theme, brand asset, footer, and output directory fields."),
    (633, "P5 (Systemization)", "Probe Plan-6A: Foundation Boundary",
     "Define PdfReportManifest",
     "Complete `Define PdfReportManifest` as a state-converting AEP for defining the JSON manifest contract that links source audio, processed audio, plots, PDF path, and metadata."),
    (634, "P6 (Next Entry)", "Probe Plan-6A: Foundation Boundary",
     "PDF Foundation Probe Backlog",
     "Complete `PDF Foundation Probe Backlog` as a state-converting AEP for recording probe findings and opening the template foundation Plan-6B with clear entry points."),
]

pdf_probe_plan6b = [
    (635, "P7 (Execution)", "Probe Plan-6B: Template Foundation",
     "Implement Brand Asset Resolver",
     "Complete `Implement Brand Asset Resolver` as a state-converting AEP for resolving the canonical logo path, providing fallback behavior, and surfacing actionable errors when the logo is missing."),
    (636, "P8 (Execution)", "Probe Plan-6B: Template Foundation",
     "Implement Page Template Contract",
     "Complete `Implement Page Template Contract` as a state-converting AEP for establishing stable header/body/footer regions with fixed logo placement that never overlaps plot content."),
    (637, "P9 (Validation)", "Probe Plan-6B: Template Foundation",
     "Implement Dark Industrial Theme",
     "Complete `Implement Dark Industrial Theme` as a state-converting AEP for validating that the dark industrial color palette, typography, and risk-band colors render correctly on cloud."),
    (638, "P10 (Validation)", "Probe Plan-6B: Template Foundation",
     "Implement Figure Export Helper",
     "Complete `Implement Figure Export Helper` as a state-converting AEP for validating that matplotlib figures export consistently to PNG and PDF with the correct background color and DPI."),
    (639, "P11 (Systemization)", "Probe Plan-6B: Template Foundation",
     "Implement PDF Writer Skeleton",
     "Complete `Implement PDF Writer Skeleton` as a state-converting AEP for creating a multi-page PDF writer that can produce a one-page branded PDF with logo, header, and footer on cloud."),
    (640, "P12 (Next Entry)", "Probe Plan-6B: Template Foundation",
     "PDF Foundation Tech Probe Report",
     "Complete `PDF Foundation Tech Probe Report` as a state-converting AEP for synthesizing template probe results and opening the Foundation Gate Plan-6C."),
]

pdf_probe_plan6c = [
    (641, "P13 (Execution)", "Probe Plan-6C: Foundation Gate",
     "Add Metadata Block",
     "Complete `Add Metadata Block` as a state-converting AEP for embedding report id, preset, source audio path, and timestamp into every generated PDF cover page."),
    (642, "P14 (Execution)", "Probe Plan-6C: Foundation Gate",
     "Add Output Path Policy",
     "Complete `Add Output Path Policy` as a state-converting AEP for ensuring reports land in deterministic output directories with operator-friendly, conflict-free filenames."),
    (643, "P15 (Validation)", "Probe Plan-6C: Foundation Gate",
     "Add Manifest Writer",
     "Complete `Add Manifest Writer` as a state-converting AEP for validating that every PDF has a sibling .manifest.json with full generation metadata."),
    (644, "P16 (Validation)", "Probe Plan-6C: Foundation Gate",
     "Add Basic Unit Tests",
     "Complete `Add Basic Unit Tests` as a state-converting AEP for validating config, asset resolution, manifest serialization, and writer skeleton with pytest."),
    (645, "P17 (Systemization)", "Probe Plan-6C: Foundation Gate",
     "Add Cloud Smoke Command",
     "Complete `Add Cloud Smoke Command` as a state-converting AEP for generating a one-page branded PDF on Tencent Cloud and recording the result as foundation NEM evidence."),
    (646, "P18 (Next Entry)", "Probe Plan-6C: Foundation Gate",
     "Close Foundation NEM",
     "Complete `Close Foundation NEM` as a state-converting AEP for sealing the probe phase, recording PoEW evidence, and opening the Acoustic CT Build NEM entry."),
]

# ── Build NEM: PDF-ACOUSTIC-CT (647-664) ──

pdf_build_plan6a = [
    (647, "B1 (Execution)", "Build Plan-6A: Acoustic CT Pages",
     "Implement Spectrogram Report Page",
     "Complete `Implement Spectrogram Report Page` as a state-converting AEP for building a spectrogram page that uses the dark template, risk-band overlays, and the brand header."),
    (648, "B2 (Execution)", "Build Plan-6A: Acoustic CT Pages",
     "Implement Frequency Balance Page",
     "Complete `Implement Frequency Balance Page` as a state-converting AEP for building a frequency balance page with standardized axes, band labels, and documented risk-band colors."),
    (649, "B3 (Validation)", "Build Plan-6A: Acoustic CT Pages",
     "Implement Waveform Dynamics Page",
     "Complete `Implement Waveform Dynamics Page` as a state-converting AEP for validating that waveform and RMS panels render without overlap and with correct time-axis scaling."),
    (650, "B4 (Validation)", "Build Plan-6A: Acoustic CT Pages",
     "Implement Summary Diagnosis Page",
     "Complete `Implement Summary Diagnosis Page` as a state-converting AEP for validating that human-readable findings, gate results, and audio identity appear correctly."),
    (651, "B5 (Systemization)", "Build Plan-6A: Acoustic CT Pages",
     "Add Risk-Band Visual Grammar",
     "Complete `Add Risk-Band Visual Grammar` as a state-converting AEP for documenting the sub-bass, low-mid, harshness, sibilance, and safe-band color mapping as a reusable visual standard."),
    (652, "B6 (Next Entry)", "Build Plan-6A: Acoustic CT Pages",
     "Acoustic CT Pages Tests",
     "Complete `Acoustic CT Pages Tests` as a state-converting AEP for opening the comparison layer Plan-6B with passing page-builder tests."),
]

pdf_build_plan6b = [
    (653, "B7 (Execution)", "Build Plan-6B: Comparison Layer",
     "Add Diagnostic Callouts",
     "Complete `Add Diagnostic Callouts` as a state-converting AEP for building annotation callouts that mark top risks and improvements on spectrogram and frequency balance pages."),
    (654, "B8 (Execution)", "Build Plan-6B: Comparison Layer",
     "Add Before/After Comparison Layout",
     "Complete `Add Before/After Comparison Layout` as a state-converting AEP for building side-by-side before/after pages with shared axis scales for trustworthy comparison."),
    (655, "B9 (Validation)", "Build Plan-6B: Comparison Layer",
     "Add Delta Chart Page",
     "Complete `Add Delta Chart Page` as a state-converting AEP for validating that delta charts correctly show energy, risk, loudness, and MRS changes between before and after scans."),
    (656, "B10 (Validation)", "Build Plan-6B: Comparison Layer",
     "Add Processing Chain Section",
     "Complete `Add Processing Chain Section` as a state-converting AEP for validating that the processing chain section lists operations, parameters, and overrides in the correct order."),
    (657, "B11 (Systemization)", "Build Plan-6B: Comparison Layer",
     "Add Audio Identity Block",
     "Complete `Add Audio Identity Block` as a state-converting AEP for standardizing the audio identity block to show input id, output id, duration, sample rate, and channel count."),
    (658, "B12 (Next Entry)", "Build Plan-6B: Comparison Layer",
     "Comparison Layer Tests",
     "Complete `Comparison Layer Tests` as a state-converting AEP for opening the product integration Plan-6C with passing comparison-layer tests."),
]

pdf_build_plan6c = [
    (659, "B13 (Execution)", "Build Plan-6C: Product Integration",
     "Add CT Quality Score",
     "Complete `Add CT Quality Score` as a state-converting AEP for implementing a scan completeness score based on pages, plates, MRS data, and defect flags."),
    (660, "B14 (Execution)", "Build Plan-6C: Product Integration",
     "Add PDF Filename Policy",
     "Complete `Add PDF Filename Policy` as a state-converting AEP for implementing deterministic, operator-friendly PDF filenames that include sample id, preset, and report type."),
    (661, "B15 (Validation)", "Build Plan-6C: Product Integration",
     "Add Report Bundle Integration",
     "Complete `Add Report Bundle Integration` as a state-converting AEP for validating that PDF reports are linked into the existing operator report bundle system."),
    (662, "B16 (Validation)", "Build Plan-6C: Product Integration",
     "Add Example Single Report",
     "Complete `Add Example Single Report` as a state-converting AEP for validating that cloud produces one polished single-scan Acoustic CT PDF with all plates and a quality score."),
    (663, "B17 (Systemization)", "Build Plan-6C: Product Integration",
     "Add Example Comparison Report",
     "Complete `Add Example Comparison Report` as a state-converting AEP for generating a polished before/after comparison PDF as system-level evidence of the CT build NEM."),
    (664, "B18 (Next Entry)", "Build Plan-6C: Product Integration",
     "Close CT NEM",
     "Complete `Close CT NEM` as a state-converting AEP for closing the build NEM and opening the Ops-QA System NEM entry."),
]

# ── System NEM: PDF-OPS-QA (665-682) ──

pdf_system_plan6a = [
    (665, "S1 (Execution)", "System Plan-6A: CLI and API",
     "Add CLI pdf-report render-single",
     "Complete `Add CLI pdf-report render-single` as a state-converting AEP for adding the CLI command that renders a single-scan Acoustic CT PDF from a WAV file path."),
    (666, "S2 (Execution)", "System Plan-6A: CLI and API",
     "Add CLI pdf-report render-comparison",
     "Complete `Add CLI pdf-report render-comparison` as a state-converting AEP for adding the CLI command that renders a before/after comparison PDF from two WAV files."),
    (667, "S3 (Validation)", "System Plan-6A: CLI and API",
     "Add CLI pdf-report inspect",
     "Complete `Add CLI pdf-report inspect` as a state-converting AEP for validating that the inspect command prints pages, manifest, asset status, and QA results."),
    (668, "S4 (Validation)", "System Plan-6A: CLI and API",
     "Add API Endpoint for Report Generation",
     "Complete `Add API Endpoint for Report Generation` as a state-converting AEP for validating that the operator API can request PDF report generation and receive the manifest."),
    (669, "S5 (Systemization)", "System Plan-6A: CLI and API",
     "Add Job Runner Hook",
     "Complete `Add Job Runner Hook` as a state-converting AEP for standardizing the hook that lets processing jobs request PDF output automatically on completion."),
    (670, "S6 (Next Entry)", "System Plan-6A: CLI and API",
     "CLI/API Integration Smoke",
     "Complete `CLI/API Integration Smoke` as a state-converting AEP for opening the QA and Validation Plan-6B with passing integration smoke results."),
]

pdf_system_plan6b = [
    (671, "S7 (Execution)", "System Plan-6B: QA and Validation",
     "Add Delivery Record Hook",
     "Complete `Add Delivery Record Hook` as a state-converting AEP for linking PDF report artifacts to delivery records so delivered jobs reference their CT reports."),
    (672, "S8 (Execution)", "System Plan-6B: QA and Validation",
     "Add Craft Memory Hook",
     "Complete `Add Craft Memory Hook` as a state-converting AEP for storing the report manifest path in craft memory writeback so craft records link to their PDF evidence."),
    (673, "S9 (Validation)", "System Plan-6B: QA and Validation",
     "Add PDF QA Checks",
     "Complete `Add PDF QA Checks` as a state-converting AEP for validating non-empty pages, logo presence, footer readability, and structural PDF validity."),
    (674, "S10 (Validation)", "System Plan-6B: QA and Validation",
     "Add Text Extraction Smoke",
     "Complete `Add Text Extraction Smoke` as a state-converting AEP for validating that PDF reports contain extractable text markers or provide equivalent metadata via the manifest."),
    (675, "S11 (Systemization)", "System Plan-6B: QA and Validation",
     "Add Image Render Smoke",
     "Complete `Add Image Render Smoke` as a state-converting AEP for validating that the first page of every generated PDF can be structurally verified as a valid PDF."),
    (676, "S12 (Next Entry)", "System Plan-6B: QA and Validation",
     "QA Validation Report",
     "Complete `QA Validation Report` as a state-converting AEP for synthesizing QA results and opening the Seal and Next Entry Plan-6C."),
]

pdf_system_plan6c = [
    (677, "S13 (Execution)", "System Plan-6C: Seal and Next Entry",
     "Add Comparison Scale QA",
     "Complete `Add Comparison Scale QA` as a state-converting AEP for verifying that before/after comparison pages use identical axis scales for trustworthy delta interpretation."),
    (678, "S14 (Execution)", "System Plan-6C: Seal and Next Entry",
     "Add Artifact Cleanup Policy",
     "Complete `Add Artifact Cleanup Policy` as a state-converting AEP for implementing a policy that places temp images under the output directory and cleans up after PDF generation."),
    (679, "S15 (Validation)", "System Plan-6C: Seal and Next Entry",
     "Add Runbook",
     "Complete `Add Runbook` as a state-converting AEP for validating that the runbook documents cloud commands, dependencies, examples, and troubleshooting steps."),
    (680, "S16 (Validation)", "System Plan-6C: Seal and Next Entry",
     "Add Operator Handoff Note",
     "Complete `Add Operator Handoff Note` as a state-converting AEP for validating that a DeepSeek or Claude operator can run the PDF module without prior PDF library knowledge."),
    (681, "S17 (Systemization)", "System Plan-6C: Seal and Next Entry",
     "Add Regression Test Suite",
     "Complete `Add Regression Test Suite` as a state-converting AEP for ensuring all PDF module tests pass with python3 -m pytest moodify_runtime/tests/ -v on cloud."),
    (682, "S18 (Next Entry)", "System Plan-6C: Seal and Next Entry",
     "Close E-Chain",
     "Complete `Close E-Chain` as a state-converting AEP for sealing ECHAIN-MOODIFY-PDF-REPORT-011, recording PoEW evidence, and generating next E-chain candidates."),
]


# ═══════════════════════════════════════════════════════════
# CRAFT-22-012
# ═══════════════════════════════════════════════════════════

CRAFT_CONTEXT = (
    "Moodify should evolve from a small preset processor into an industrial "
    "craft system with 22 controlled processing operations. Current processing "
    "feels too thin: the Acoustic CT reports show that scanning is already "
    "useful, but the treatment layer needs more expressive and more controllable "
    "operations. Moodify should behave less like a one-click consumer enhancer "
    "and more like an internal studio operating system: scan, diagnose, choose "
    "craft, process, rescan, compare, remember."
)

CRAFT_PROBE_EXEC = [
    "Audit existing processing presets and identify gaps before designing new operations.",
    "Every craft operation must have an id, name, params schema, risk level, and metrics produced.",
    "Parameter validation must fail fast: invalid params are rejected before any audio processing.",
    "The registry must return exactly 22 active operations when queried.",
]

CRAFT_BUILD_EXEC = [
    "The chain executor must run selected operations in order on an audio artifact.",
    "Per-step metrics must record before/after measurements for every operation.",
    "Safety rollback must preserve the previous valid artifact when a step fails.",
    "CLI commands craft plan, craft run, and craft inspect must work on cloud.",
]

CRAFT_SYSTEM_EXEC = [
    "The craft selector must accept CT findings, MRS scores, genre, and preset hints as input.",
    "Risk-aware operation limits must block or warn about dangerous combinations.",
    "Craft memory writeback must store success/failure data and adoption states.",
    "The runbook must enable operators to plan, run, inspect, and compare craft chains.",
]

CRAFT_ACCEPT = [
    "The expected output exists or a HOLD reason is documented.",
    "The craft system gains a clearer operation, chain, selector, or memory capability.",
    "Failures are recorded as reusable craft memory evidence.",
    "The next MHP can start without reconstructing context.",
]

# ── Probe NEM: CRAFT-TAXONOMY (683-700) ──

craft_probe_plan6a = [
    (683, "P1 (Execution)", "Probe Plan-6A: Taxonomy Boundary",
     "Audit Existing Processing Presets",
     "Complete `Audit Existing Processing Presets` as a state-converting AEP for listing all current processing operations and identifying gaps against the target 22-operation taxonomy."),
    (684, "P2 (Execution)", "Probe Plan-6A: Taxonomy Boundary",
     "Define Craft Operation Schema",
     "Complete `Define Craft Operation Schema` as a state-converting AEP for defining the canonical operation schema with id, name, category, params, risk level, and metrics fields."),
    (685, "P3 (Validation)", "Probe Plan-6A: Taxonomy Boundary",
     "Define 22 Operation Registry",
     "Complete `Define 22 Operation Registry` as a state-converting AEP for validating that the registry data structure correctly stores and returns exactly 22 operations."),
    (686, "P4 (Validation)", "Probe Plan-6A: Taxonomy Boundary",
     "Add Input Normalize Operation",
     "Complete `Add Input Normalize Operation` as a state-converting AEP for validating the first PREPARE operation with unit tests covering level target and clipping safety."),
    (687, "P5 (Systemization)", "Probe Plan-6A: Taxonomy Boundary",
     "Add Silence Trim Operation",
     "Complete `Add Silence Trim Operation` as a state-converting AEP for documenting the silence trim operation with threshold, min-silence, and fade parameters."),
    (688, "P6 (Next Entry)", "Probe Plan-6A: Taxonomy Boundary",
     "Craft Taxonomy Probe Backlog",
     "Complete `Craft Taxonomy Probe Backlog` as a state-converting AEP for recording probe findings and opening the Operation Build Plan-6B."),
]

craft_probe_plan6b = [
    (689, "P7 (Execution)", "Probe Plan-6B: Operation Build",
     "Add Sub-Bass and Bass Operations",
     "Complete `Add Sub-Bass and Bass Operations` as a state-converting AEP for implementing sub_bass_discipline and bass_body_shaping as distinct, independently testable operations."),
    (690, "P8 (Execution)", "Probe Plan-6B: Operation Build",
     "Add Low-Mid and Mid Operations",
     "Complete `Add Low-Mid and Mid Operations` as a state-converting AEP for implementing low_mid_de_mud and mid_presence_lift as separate CORRECTIVE and ENHANCE operations."),
    (691, "P9 (Validation)", "Probe Plan-6B: Operation Build",
     "Add Harshness/Air/Sibilance Operations",
     "Complete `Add Harshness/Air/Sibilance Operations` as a state-converting AEP for validating that high-band controls are distinct, bounded, and independently selectable."),
    (692, "P10 (Validation)", "Probe Plan-6B: Operation Build",
     "Add Transient Operations",
     "Complete `Add Transient Operations` as a state-converting AEP for validating that transient_soften and transient_restore can be selected independently and produce measurable delta."),
    (693, "P11 (Systemization)", "Probe Plan-6B: Operation Build",
     "Add Dynamics Operations",
     "Complete `Add Dynamics Operations` as a state-converting AEP for standardizing micro_dynamics_lift and macro_dynamics_guard as separate DYNAMICS category operations."),
    (694, "P12 (Next Entry)", "Probe Plan-6B: Operation Build",
     "Operation Build Report",
     "Complete `Operation Build Report` as a state-converting AEP for synthesizing the build results and opening the Taxonomy Gate Plan-6C."),
]

craft_probe_plan6c = [
    (695, "P13 (Execution)", "Probe Plan-6C: Taxonomy Gate",
     "Add Stereo/Center Operations",
     "Complete `Add Stereo/Center Operations` as a state-converting AEP for implementing stereo_width_control with mono safety and center_focus with crossover control."),
    (696, "P14 (Execution)", "Probe Plan-6C: Taxonomy Gate",
     "Add Noise/Room Operations",
     "Complete `Add Noise/Room Operations` as a state-converting AEP for implementing noise_floor_polish and room_reverb_cleanup as conservative, reversible-by-config operations."),
    (697, "P15 (Validation)", "Probe Plan-6C: Taxonomy Gate",
     "Add Warmth/Clarity Operations",
     "Complete `Add Warmth/Clarity Operations` as a state-converting AEP for validating that warmth_injection and clarity_polish do not bypass safety gates."),
    (698, "P16 (Validation)", "Probe Plan-6C: Taxonomy Gate",
     "Add Loudness/Limiter Operations",
     "Complete `Add Loudness/Limiter Operations` as a state-converting AEP for validating that loudness_landing and final_safety_limiter have true peak and clipping gates."),
    (699, "P17 (Systemization)", "Probe Plan-6C: Taxonomy Gate",
     "Add Operation Docs and Parameter Validation",
     "Complete `Add Operation Docs and Parameter Validation` as a state-converting AEP for ensuring every operation has documented intent, risk, metrics, and fast-fail parameter validation."),
    (700, "P18 (Next Entry)", "Probe Plan-6C: Taxonomy Gate",
     "Close Taxonomy NEM",
     "Complete `Close Taxonomy NEM` as a state-converting AEP for sealing the taxonomy probe, recording PoEW evidence, and opening the Chain Engine Build NEM entry."),
]

# ── Build NEM: CRAFT-CHAIN (701-718) ──

craft_build_plan6a = [
    (701, "B1 (Execution)", "Build Plan-6A: Chain Core",
     "Implement CraftChain Model",
     "Complete `Implement CraftChain Model` as a state-converting AEP for building the ChainStep and ChainPlan dataclasses that store ordered operations and metadata."),
    (702, "B2 (Execution)", "Build Plan-6A: Chain Core",
     "Implement Chain Executor",
     "Complete `Implement Chain Executor` as a state-converting AEP for building the CraftChainExecutor that runs selected operations on an audio artifact in order."),
    (703, "B3 (Validation)", "Build Plan-6A: Chain Core",
     "Add Dry-Run Planner",
     "Complete `Add Dry-Run Planner` as a state-converting AEP for validating that the planner shows operation order, risk level, and estimated step count without processing audio."),
    (704, "B4 (Validation)", "Build Plan-6A: Chain Core",
     "Add Per-Step Metrics",
     "Complete `Add Per-Step Metrics` as a state-converting AEP for validating that each chain step records before/after measurements in the OpResult."),
    (705, "B5 (Systemization)", "Build Plan-6A: Chain Core",
     "Add Per-Step Artifact Policy",
     "Complete `Add Per-Step Artifact Policy` as a state-converting AEP for standardizing whether intermediate WAV artifacts are kept or cleaned up after chain execution."),
    (706, "B6 (Next Entry)", "Build Plan-6A: Chain Core",
     "Chain Core Tests",
     "Complete `Chain Core Tests` as a state-converting AEP for opening the Safety and Integration Plan-6B with passing chain-core unit tests."),
]

craft_build_plan6b = [
    (707, "B7 (Execution)", "Build Plan-6B: Safety and Integration",
     "Add Safety Rollback Policy",
     "Complete `Add Safety Rollback Policy` as a state-converting AEP for implementing the rule that a failed step preserves the previous valid artifact and does not corrupt the chain."),
    (708, "B8 (Execution)", "Build Plan-6B: Safety and Integration",
     "Add Clipping/Peak Gate",
     "Complete `Add Clipping/Peak Gate` as a state-converting AEP for implementing a gate that fails or repairs the chain when output exceeds the true-peak ceiling."),
    (709, "B9 (Validation)", "Build Plan-6B: Safety and Integration",
     "Add Loudness Gate",
     "Complete `Add Loudness Gate` as a state-converting AEP for validating that the chain records LUFS/RMS policy results when loudness_landing is active."),
    (710, "B10 (Validation)", "Build Plan-6B: Safety and Integration",
     "Add Spectral Gate",
     "Complete `Add Spectral Gate` as a state-converting AEP for validating that CT metrics can compare before/after spectral energy across frequency bands."),
    (711, "B11 (Systemization)", "Build Plan-6B: Safety and Integration",
     "Add Runtime Budget Policy",
     "Complete `Add Runtime Budget Policy` as a state-converting AEP for standardizing that long chains can be bounded by a max_chain_time_s parameter on cloud."),
    (712, "B12 (Next Entry)", "Build Plan-6B: Safety and Integration",
     "Safety Integration Tests",
     "Complete `Safety Integration Tests` as a state-converting AEP for opening the CLI and Product Plan-6C with passing safety integration tests."),
]

craft_build_plan6c = [
    (713, "B13 (Execution)", "Build Plan-6C: CLI and Product",
     "Add Deterministic Seed/Config",
     "Complete `Add Deterministic Seed/Config` as a state-converting AEP for ensuring that the same input and config produce stable, deterministic chain output."),
    (714, "B14 (Execution)", "Build Plan-6C: CLI and Product",
     "Add Preset-to-Chain Adapter",
     "Complete `Add Preset-to-Chain Adapter` as a state-converting AEP for mapping existing presets (clean_master, warm_vocal, wide_space, safe_air) to craft chains."),
    (715, "B15 (Validation)", "Build Plan-6C: CLI and Product",
     "Add Chain Manifest",
     "Complete `Add Chain Manifest` as a state-converting AEP for validating that the JSON manifest records operations, params, metrics, and artifact paths correctly."),
    (716, "B16 (Validation)", "Build Plan-6C: CLI and Product",
     "Add CLI craft plan/run/inspect",
     "Complete `Add CLI craft plan/run/inspect` as a state-converting AEP for validating that all three CLI commands work on cloud with real audio."),
    (717, "B17 (Systemization)", "Build Plan-6C: CLI and Product",
     "Add Tests for Chain Engine",
     "Complete `Add Tests for Chain Engine` as a state-converting AEP for ensuring unit and integration tests pass with python3 -m pytest on cloud."),
    (718, "B18 (Next Entry)", "Build Plan-6C: CLI and Product",
     "Close Chain Engine NEM",
     "Complete `Close Chain Engine NEM` as a state-converting AEP for closing the build NEM and opening the Craft Intelligence System NEM entry."),
]

# ── System NEM: CRAFT-INTELLIGENCE (719-736) ──

craft_system_plan6a = [
    (719, "S1 (Execution)", "System Plan-6A: Selector Core",
     "Define Craft Selection Input",
     "Complete `Define Craft Selection Input` as a state-converting AEP for defining the CraftSelectionInput dataclass that accepts CT, MRS, preset, operator notes, and genre."),
    (720, "S2 (Execution)", "System Plan-6A: Selector Core",
     "Implement Rule-Based Selector v1",
     "Complete `Implement Rule-Based Selector v1` as a state-converting AEP for implementing the selector that chooses operations from CT diagnosis, genre recommendations, and preset hints."),
    (721, "S3 (Validation)", "System Plan-6A: Selector Core",
     "Add Risk-Aware Operation Limits",
     "Complete `Add Risk-Aware Operation Limits` as a state-converting AEP for validating that dangerous operation combinations are blocked or warned with clear messages."),
    (722, "S4 (Validation)", "System Plan-6A: Selector Core",
     "Add Tidal-Cycle Compatibility",
     "Complete `Add Tidal-Cycle Compatibility` as a state-converting AEP for validating that the tidal loop can request a craft plan with speed/quality/experiment priority modes."),
    (723, "S5 (Systemization)", "System Plan-6A: Selector Core",
     "Add Acoustic CT Feedback Hook",
     "Complete `Add Acoustic CT Feedback Hook` as a state-converting AEP for standardizing the hook that lets CT deltas influence the next craft plan selection."),
    (724, "S6 (Next Entry)", "System Plan-6A: Selector Core",
     "Selector Core Tests",
     "Complete `Selector Core Tests` as a state-converting AEP for opening the Feedback and Memory Plan-6B with passing selector tests."),
]

craft_system_plan6b = [
    (725, "S7 (Execution)", "System Plan-6B: Feedback and Memory",
     "Add MRS Feedback Hook",
     "Complete `Add MRS Feedback Hook` as a state-converting AEP for implementing the hook that lets human/listening MRS scores influence the craft selector."),
    (726, "S8 (Execution)", "System Plan-6B: Feedback and Memory",
     "Add Craft Memory Writeback",
     "Complete `Add Craft Memory Writeback` as a state-converting AEP for implementing the writeback that stores operation success/failure data in craft memory records."),
    (727, "S9 (Validation)", "System Plan-6B: Feedback and Memory",
     "Add Adoption States",
     "Complete `Add Adoption States` as a state-converting AEP for validating that operations track proposed, candidate, accepted, rejected, and retired adoption states."),
    (728, "S10 (Validation)", "System Plan-6B: Feedback and Memory",
     "Add Operator Override Reason",
     "Complete `Add Operator Override Reason` as a state-converting AEP for validating that operator overrides are recorded with a reason in the chain manifest."),
    (729, "S11 (Systemization)", "System Plan-6B: Feedback and Memory",
     "Add 22-Process Coverage Report",
     "Complete `Add 22-Process Coverage Report` as a state-converting AEP for standardizing the coverage report that shows which operations are used across all runs."),
    (730, "S12 (Next Entry)", "System Plan-6B: Feedback and Memory",
     "Feedback Integration Tests",
     "Complete `Feedback Integration Tests` as a state-converting AEP for opening the Seal and Next Entry Plan-6C with passing feedback integration tests."),
]

craft_system_plan6c = [
    (731, "S13 (Execution)", "System Plan-6C: Seal and Next Entry",
     "Add Before/After PDF Hook",
     "Complete `Add Before/After PDF Hook` as a state-converting AEP for implementing the hook that lets a craft chain trigger a PDF comparison report on completion."),
    (732, "S14 (Execution)", "System Plan-6C: Seal and Next Entry",
     "Add Batch Experiment Runner",
     "Complete `Add Batch Experiment Runner` as a state-converting AEP for implementing a runner that executes controlled craft variants on cloud for comparison."),
    (733, "S15 (Validation)", "System Plan-6C: Seal and Next Entry",
     "Add Benchmark Fixtures",
     "Complete `Add Benchmark Fixtures` as a state-converting AEP for validating that small benchmark fixtures keep craft chain tests fast and deterministic."),
    (734, "S16 (Validation)", "System Plan-6C: Seal and Next Entry",
     "Add Regression Tests",
     "Complete `Add Regression Tests` as a state-converting AEP for validating that existing presets still work and produce the expected chain output after craft system changes."),
    (735, "S17 (Systemization)", "System Plan-6C: Seal and Next Entry",
     "Record PoEW Evidence",
     "Complete `Record PoEW Evidence` as a state-converting AEP for recording commit hash, commands, outputs, metrics, and screenshots as proof of engineering work."),
    (736, "S18 (Next Entry)", "System Plan-6C: Seal and Next Entry",
     "Close E-Chain",
     "Complete `Close E-Chain` as a state-converting AEP for sealing ECHAIN-MOODIFY-CRAFT-22-012, recording final PoEW evidence, and generating next E-chain candidates."),
]


# ═══════════════════════════════════════════════════════════
# Generator
# ═══════════════════════════════════════════════════════════

def generate_all():
    """Generate all 108 MHP files (629-736)."""
    PLAN_DIR.mkdir(parents=True, exist_ok=True)

    configs = [
        # (echain, nem, nem_type, plan6a, plan6b, plan6c, context, exec_notes, accept)
        ("ECHAIN-MOODIFY-PDF-REPORT-011", "NEM-MOODIFY-PDF-FOUNDATION-PROBE-033", "Probe",
         pdf_probe_plan6a, pdf_probe_plan6b, pdf_probe_plan6c,
         PDF_CONTEXT, PDF_PROBE_EXEC, PDF_ACCEPT),

        ("ECHAIN-MOODIFY-PDF-REPORT-011", "NEM-MOODIFY-PDF-ACOUSTIC-CT-BUILD-034", "Build",
         pdf_build_plan6a, pdf_build_plan6b, pdf_build_plan6c,
         PDF_CONTEXT, PDF_BUILD_EXEC, PDF_ACCEPT),

        ("ECHAIN-MOODIFY-PDF-REPORT-011", "NEM-MOODIFY-PDF-OPS-QA-SYSTEM-035", "System",
         pdf_system_plan6a, pdf_system_plan6b, pdf_system_plan6c,
         PDF_CONTEXT, PDF_SYSTEM_EXEC, PDF_ACCEPT),

        ("ECHAIN-MOODIFY-CRAFT-22-012", "NEM-MOODIFY-CRAFT-TAXONOMY-PROBE-036", "Probe",
         craft_probe_plan6a, craft_probe_plan6b, craft_probe_plan6c,
         CRAFT_CONTEXT, CRAFT_PROBE_EXEC, CRAFT_ACCEPT),

        ("ECHAIN-MOODIFY-CRAFT-22-012", "NEM-MOODIFY-CRAFT-CHAIN-BUILD-037", "Build",
         craft_build_plan6a, craft_build_plan6b, craft_build_plan6c,
         CRAFT_CONTEXT, CRAFT_BUILD_EXEC, CRAFT_ACCEPT),

        ("ECHAIN-MOODIFY-CRAFT-22-012", "NEM-MOODIFY-CRAFT-INTELLIGENCE-SYSTEM-038", "System",
         craft_system_plan6a, craft_system_plan6b, craft_system_plan6c,
         CRAFT_CONTEXT, CRAFT_SYSTEM_EXEC, CRAFT_ACCEPT),
    ]

    count = 0
    for echain, nem, nem_type, plan6a, plan6b, plan6c, context, exec_notes, accept in configs:
        for plan_group in [plan6a, plan6b, plan6c]:
            for num, step_id, phase_name, title, goal in plan_group:
                depends = num - 1
                direction = f"{echain} / {nem} / {phase_name} / {step_id}"
                slug = title_to_slug(title)
                echain_slug = echain.lower()
                expected = f"reports/{echain_slug}/mhp_{num}_{slug}.md"

                content = make_mhp(
                    num=num, title=title, direction=direction,
                    depends=depends, context=context, goal=goal,
                    expected_output=expected,
                    exec_notes=exec_notes,
                    accept_criteria=accept,
                    echain=echain,
                    nem=nem,
                )

                filename = f"MHP-{num:03d}_{title.upper().replace(' ', '_').replace('/', '_')}.md"
                filepath = PLAN_DIR / filename
                filepath.write_text(content, encoding="utf-8")
                count += 1

    print(f"Generated {count} MHP files in {PLAN_DIR}")


if __name__ == "__main__":
    generate_all()
