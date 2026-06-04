# MHP-046: Next Cycle Entry — MHP-047→052 Plan Generation

**Status**: proposed  
**Direction**: 6-Step Plan Cycle — N1 (Next Entry)  
**Depends on**: MHP-043 (V1 results), MHP-044 (V2 results)  
**Protocol**: 泫榛 6-Step Plan Protocol — Plan = 2E + 2V + 1S + 1N

## Context

The 6-Step Plan Protocol says: **N must lower the next round's startup cost.** The worst thing a project can do is finish a cycle and leave no entry point — forcing the next developer to reverse-engineer the state from 17 files and 38+ tests.

MHP-046 reads the **real results** from MHP-043 (API tests) and MHP-044 (contract tests) to determine what the next cycle should address. It does not guess. It reads test output, identifies actual failures and gaps, and generates MHP-047→052 from evidence.

## Goal

Read V1 and V2 test results. Identify what actually failed, what's missing, and what's most important. Generate the next 6-plan cycle (MHP-047→052) as concrete plan files. Update the project roadmap.

## Non-Goals

- Do not generate plans that ignore test results
- Do not plan features that have no failing test or clear gap
- Do not skip the evidence-gathering step
- Do not generate plans without acceptance criteria

## Process

### Step 1: Read Evidence

```bash
python3 -m pytest moodify_runtime/tests/test_api_*.py -v --tb=short 2>&1 | tail -80
python3 -m pytest moodify_runtime/tests/test_api_contract.py -v --tb=short 2>&1 | tail -40
```

Capture:
- Total API tests: N (target ≥40)
- Passed: P
- Failed: F
- Skipped: S
- Contract tests: N (target ≥15)
- Specific failure messages

### Step 2: Classify Gaps

Categorize every failure or uncovered area:

| Category | Example |
|----------|---------|
| Missing test | Endpoint has no test at all |
| Broken contract | API returns shape JS doesn't expect |
| Missing feature | Endpoint is still a stub |
| Error handling | Endpoint crashes on bad input instead of returning 4xx |
| Performance | Test suite takes >5s (indicates real processing leaking into unit tests) |

### Step 3: Prioritize

Rank by:
1. **Blocking** — prevents the Console UI from working
2. **Data integrity** — could corrupt job/delivery/craft records
3. **Coverage** — critical path untested
4. **Polish** — edge cases, error messages, docs

### Step 4: Generate 6 Plans

Apply the 6-Step Plan formula to the evidence:

```text
MHP-047 (E1): Address the highest-priority execution gap
MHP-048 (E2): Address the second execution gap, forming continuity with E1
MHP-049 (V1): Validate E1/E2 with focused tests
MHP-050 (V2): Validate stability, scale, or edge cases
MHP-051 (S1):  Document what was learned, update configs/specs
MHP-052 (N1): Generate MHP-053→058 from V1/V2 results
```

### Step 5: Write Plan Files

Write 6 plan files to `docs/plan/MHP-047_*.md` through `docs/plan/MHP-052_*.md`. Each must follow the MHP plan format (Status, Direction, Context, Goal, Non-Goals, Requirements, Acceptance Criteria, Test Plan, Done Means).

### Step 6: Update Roadmap

Update `docs/PROJECT_ROADMAP.md` (create if missing) with:
- Completed: MHP-031→040 (v0.1.0-alpha cycle 1)
- Completed: MHP-041→046 (v0.1.0-alpha cycle 2)
- Next: MHP-047→052 (v0.1.0-alpha cycle 3)

## Acceptance Criteria

- V1 test output read and analyzed
- V2 test output read and analyzed
- Gap classification complete (at least 3 categories identified)
- 6 plan files written (MHP-047 through MHP-052)
- Each plan has: Status, Context, Goal, Non-Goals, Requirements, Acceptance Criteria, Test Plan, Done Means
- PROJECT_ROADMAP.md created or updated
- Plan files are concrete and executable (not vague aspirations)

## Done Means

The next developer (or Claude session) can open `docs/plan/MHP-047_*.md` and start working immediately, with no context-reconstruction cost. The cycle continues without breaking flow.

> 真正好的计划不是任务列表，而是一个能继续生长的工程闭环。
