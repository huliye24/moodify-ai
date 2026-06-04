# MHP-045: Alpha Documentation & Module Map

**Status**: proposed  
**Direction**: 6-Step Plan Cycle — S1 (Systemization)  
**Depends on**: MHP-042, MHP-043, MHP-044 (captures their results)  
**Protocol**: 泫榛 6-Step Plan Protocol — Plan = 2E + 2V + 1S + 1N

## Context

MHP-031 through MHP-044 added significant code. The module count grew from ~8 to 17 Python files. New subsystems (studio, scheduler, calibration, operator API) were added. Without updated documentation, the next developer (or Claude in a fresh session) must read 17 files to understand the system.

The 6-Step Plan Protocol says: **S must leave assets.** Documentation is the most durable asset a codebase can have. Without it, the system has memory loss.

Current documentation state:
- `README.md` — good for v0.1.0-alpha.3, partially outdated
- `docs/ARCHITECTURE.md` — exists but predates MHP-031
- `docs/GLOSSARY.md` — exists
- `CHANGELOG.md` — last updated at initial commit
- No module dependency graph
- No API route reference (outside of code)
- No data model reference

## Goal

Update all project documentation to reflect the current state after MHP-044. Create a module dependency map. Write the CHANGELOG for MHP-031→040.

## Non-Goals

- Do not write tutorial-style documentation (not the right phase)
- Do not generate API docs from docstrings (use the existing route table)
- Do not rewrite historical docs — update, don't replace

## Engineering Requirements

### 1. ARCHITECTURE.md Update

Current structure is outdated. Required new sections:

```markdown
# Moodify Architecture — v0.1.0-alpha.4

## Module Map (17 modules)

[diagram showing dependencies]

## Data Flow

Sample → Registry → Queue → Runner → Manifest → Operator Job → Detail → Gate → Report → Delivery → Craft

## Subsystem Map

| Subsystem | Modules | MHP |
|-----------|---------|-----|
| Runtime Core | registry, queue, runner, metrics, report | pre-031 |
| Operator Console | operator_console, operator_api, operator_console.html | 031-035 |
| Studio Back Office | studio | 036 |
| Craft Library | craft_memory | 037 |
| Cloud Scheduler | scheduler | 038 |
| MRS Calibration | mrs_calibration | 039 |

## API Route Table

[25+ endpoints organized by subsystem]

## Storage Layout

data/moodify_runtime/
├── operator_jobs.jsonl
├── operator_job_details/
├── operator_deliveries.jsonl
├── studio/
│   ├── clients.jsonl
│   ├── projects.jsonl
│   ├── orders.jsonl
│   └── staff_notes.jsonl
├── scheduler/
│   ├── requests.jsonl
│   ├── leases.jsonl
│   ├── runs.jsonl
│   └── costs.jsonl
├── calibration/
│   ├── sample_sets.jsonl
│   ├── reviews.jsonl
│   ├── audits.jsonl
│   └── thresholds.jsonl
└── craft_memory/
    └── craft_records.jsonl
```

### 2. CHANGELOG.md Update

Add entries for MHP-031 through MHP-040. Each entry should have:
- MHP number and title
- Files changed/added
- Key decisions made
- Test count

### 3. Module Dependency Graph

Generate a text-based dependency graph showing which modules import from which. This helps new developers understand the layering:

```text
cli.py
├── config.py
├── operator_console.py
│   ├── config.py
│   ├── utils.py
│   ├── registry.py
│   ├── queue.py
│   └── runner.py
├── studio.py
│   ├── config.py
│   └── utils.py
├── scheduler.py
├── craft_memory.py
├── mrs_calibration.py
└── (legacy) report, runner, queue, registry

operator_api.py
├── config.py
├── operator_console.py
├── craft_memory.py
└── (FastAPI)
```

### 4. README Update

- Update version to v0.1.0-alpha.4
- Update test count (38 → ~80 after MHP-043/044)
- Add "Studio OS Alpha" section
- Update "Next Milestones" to point to MHP-046 (next cycle)

### 5. `.gitignore` Update

Ensure new data directories are covered:
```gitignore
data/moodify_runtime/studio/
data/moodify_runtime/scheduler/
data/moodify_runtime/calibration/
```

## Acceptance Criteria

- ARCHITECTURE.md updated with module map and data flow
- CHANGELOG.md has entries for MHP-031→040
- Module dependency graph is correct (verify with `grep -r "from \." moodify_runtime/`)
- README version and test count are current
- .gitignore covers new data directories
- Existing 38+ tests still pass

## Test Plan

```bash
# Verify no broken imports
python3 -c "import moodify_runtime; print('all imports ok')"

# Verify .gitignore coverage
git check-ignore data/moodify_runtime/studio/clients.jsonl
```

## Done Means

A new developer can read ARCHITECTURE.md and understand the system without reading 17 source files. The project has memory.
