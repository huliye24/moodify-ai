# Runtime State Machine Spec — MHP-126

**E-Chain**: ECHAIN-MOODIFY-RUNTIME-001

## States

| State | Description | Terminal? |
|-------|-------------|-----------|
| pending | Task waiting in queue | No |
| claimed | Task assigned to a runner | No |
| running | Task subprocess executing | No |
| done | Task completed successfully | Yes |
| failed | Task failed after all retries | Yes |
| abandoned | Runner died mid-task | No (recyclable) |

## Valid Transitions

```
pending  → claimed, abandoned
claimed  → running, abandoned
running  → done, failed
failed   → pending (retry)
abandoned → pending (recycle)
```

## Abandoned Detection

Tasks with status `claimed` or `running` and `status_updated_at` older than 30 minutes are considered abandoned. The `resume_queue()` function finds and recycles them.
