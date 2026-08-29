# CloudPreparation Contract (Blocked Contract Draft)

No live model was persisted or exposed. The minimum future normalized model is:

```text
CloudPreparation { id, track_id, status, created_at, updated_at, error_code?, prepared_source? }
status = NOT_REQUESTED | QUEUED | PREPARING | READY | FAILED | CANCELLED | UNKNOWN
```

READY is authorized only after a playable prepared source resolves. Internal Analyze/Stem/Judge/Intervene/Verify states must map to the small public state set server-side or in a narrow adapter; they must never appear in consumer UI.
