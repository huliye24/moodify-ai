# External Comprehension Experiment Workspace

**Date:** 2026-08-19
**Package:** 06 - External Comprehension Validation
**Location:** `docs/public-form/validation/`

---

## Directory Structure

```
docs/public-form/validation/
├── README.md                    # This file — workspace overview
├── protocol/
│   ├── 00_SESSION_PROTOCOL.md   # How to run a comprehension session
│   ├── 01_SILENT_TEST.md        # Silent comprehension test procedure
│   ├── 02_LISTENING_TEST.md     # Listening proof validation
│   └── 03_INVESTOR_TEST.md      # Investor commercial clarity test
├── sessions/
│   ├── .gitkeep                 # Placeholder for session records
│   ├── TEMPLATE.json            # New session template
│   └── README.md                # Session naming & storage rules
├── reports/
│   ├── .gitkeep                 # Placeholder for wave reports
│   ├── WAVE_REPORT_TEMPLATE.md  # Wave summary report template
│   └── README.md                # Report naming convention
├── schemas/
│   ├── response_schema.json     # Response data schema (from P06 package)
│   ├── session_schema.json      # Session metadata schema
│   ├── classifier_rules.json    # Identity classification rules
│   └── wave_report_schema.json  # Wave aggregation schema
├── lab/
│   ├── comprehension_lab.html   # Local testing interface (or reference)
│   └── lab_instructions.md      # How to use the lab
└── privacy/
    └── PRIVACY_PROTOCOL.md      # Data handling & privacy rules
```

---

## Usage

### Running a Session

1. Create session from `sessions/TEMPLATE.json`
2. Follow appropriate protocol (`protocol/01_*.md` or `02_*.md` or `03_*.md`)
3. Record responses in `sessions/` using `response_schema.json`
4. Classify using `schemas/classifier_rules.json`
5. After 3-5 sessions, generate wave report from `reports/WAVE_REPORT_TEMPLATE.md`

### Privacy Rules

- **No personal identifiers** in committed files (use PARTICIPANT-XX)
- **No contact info** unless explicitly permitted
- **Verbatim responses** required — no paraphrasing without marking
- **Audio recordings** only with explicit consent; store separately, don't commit
- **Investor sessions** anonymized by default (INVESTOR-XX)

---

## What Goes Here vs. What Doesn't

### ✅ Store here
- Anonymized response data (JSON)
- Aggregated wave reports (Markdown)
- Protocol documents
- Classification schemas
- Lab HTML/tooling

### ❌ Don't store here
- Real names / contact info
- Audio recordings (reference external secure location)
- Unconsented photos/video
- Internal strategy notes (use `experiments/` or internal docs)
- Non-anonymized investor feedback

---

## Integration with Package System

This workspace consumes outputs from:
- **Package 05** — `FINAL_PUBLIC_FORM_REPORT.md` (what we're validating)
- **Package 04** — Player surface (what users interact with)
- **Package 03** — Company Home surface
- **Package 02** — Product Home surface
- **Package 01** — Brand constitution (correctness benchmark)

This workspace produces inputs for:
- **Package 07** — Value Capture (commercial intent validation)
- **Package 08** — Capital Optionality (investor clarity evidence)
- **Future iterations** — Product/messaging changes based on findings
