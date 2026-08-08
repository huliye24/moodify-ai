# DeepSeek handoff contract

## Preconditions

Do not send a task until human annotations exist and Codex has produced
`audit_summary.json`, `baseline_results.json`, and `pilot_summary.json`.
Absence of evidence must result in `inconclusive`.

Generate the bounded package:

```powershell
pwrm prepare-deepseek --evidence-dir runs\pilot\evidence --out-dir runs\pilot\deepseek
```

This creates:

- `tasks.jsonl`: four atomic, independently retryable tasks;
- `prompt.md`: role and reasoning boundaries;
- `expected_output_schema.json`: machine-checkable response contract.

Run it with the repository's existing worker transport:

```powershell
python E:\moodify\scripts\deepseek_worker_client.py `
  --input runs\pilot\deepseek\tasks.jsonl `
  --prompt runs\pilot\deepseek\prompt.md `
  --schema runs\pilot\deepseek\expected_output_schema.json `
  --output-dir runs\pilot\deepseek\results
```

Set the API credentials using the transport's documented environment variables;
never place secrets in this package or a JSONL task.

## DeepSeek is allowed to

- summarize supplied numeric evidence;
- detect missing fields or contradictory gate results;
- return one bounded decision and next action per task.

## DeepSeek is prohibited from

- redefining “power”, changing thresholds, or inventing labels;
- claiming access to audio, source code, or records not included in the task;
- treating predictive accuracy as causal proof;
- merging train and test tracks;
- issuing a final scientific conclusion without Human/Judge review.

The Judge must inspect rejected outputs, anomalies, provenance, and at least a
sample of raw listening records before accepting any recommendation.
