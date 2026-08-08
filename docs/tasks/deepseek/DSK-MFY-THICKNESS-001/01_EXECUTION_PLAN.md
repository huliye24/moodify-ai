# Execution Plan and Checkpoints

## Ordered Queue

1. Validate all JSON and JSONL files locally.
2. Run the Worker in dry-run mode and archive the result.
3. Run the 18 live DeepSeek calls sequentially.
4. Validate each response against `expected_output_schema.json`.
5. Reject any response that invents a file, test result, right, metric, or repository fact.
6. Merge duplicate findings without losing their original task IDs.
7. Rank accepted work by `P0`, `P1`, then `P2`; safety, data integrity, and recovery precede presentation.
8. Implement one bounded batch at a time.
9. Run targeted tests after each patch.
10. Run the full relevant suite after the batch.
11. Repeat determinism/recovery checks.
12. Update logs and ledgers before moving the batch to `IMPLEMENTED_AND_VERIFIED`.

## Implementation Batches

### Batch 1 — Data truth and generator integrity

- Reproduce the Treatment summary mismatch from the source directory.
- Determine whether the summary is stale, the generator is defective, or both.
- Fix generator defects only when reproduced by a failing test.
- Regenerate derived summaries from the 27 real records.
- Record the three missing records as missing; never synthesize their measurements or feedback.

### Batch 2 — Evidence contract

- Define a per-run evidence bundle with run ID, source identity, rights state, configuration hash, environment, step evidence, results, errors, approval state, and artifact hashes.
- Add validation tests for required fields and invalid transitions.
- Ensure failed or unapproved runs cannot enter the Craft Library.

### Batch 3 — Failure, determinism, and recovery

- Add tests for malformed inputs, missing paths, write failures, interruption, retry, duplicate execution, partial outputs, and stale state.
- Verify identical inputs and configuration produce equivalent decisions and traceable outputs.
- Verify retry is idempotent or explicitly versioned.

### Batch 4 — Compatibility and inheritance

- Test loading historical workspace and manifest fixtures.
- Document migration or explicit refusal for unsupported schema versions.
- Seed/update the Failure Ledger, Standard Evolution Ledger, Craft Evidence Ledger, and Product History.

## Gate Sequence

| Gate | Question | Pass evidence |
|---|---|---|
| G0 | Is the input authorized and frozen? | baseline + rights state |
| G1 | Is the finding grounded? | repository citation or reproducible command |
| G2 | Is the implementation correct? | targeted tests and diff review |
| G3 | Does failure remain controlled? | negative tests and artifact inspection |
| G4 | Is rerun/recovery stable? | repeated-run comparison |
| G5 | Can the next maintainer inherit it? | updated log and ledger |

## Stop Conditions

Stop the affected task, preserve evidence, and mark it `HUMAN_BLOCKED` or `REWORK` when:

- rights metadata is absent or ambiguous;
- a test failure cannot be explained;
- a patch changes product direction or public contracts beyond the task;
- generated evidence conflicts with source files;
- repeat runs disagree without a documented nondeterminism policy;
- rollback/recovery cannot be demonstrated for a state-changing operation.

