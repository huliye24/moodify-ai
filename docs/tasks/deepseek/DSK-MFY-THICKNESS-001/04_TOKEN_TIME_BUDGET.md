# Token and Time Budget

## Estimation Basis

The directly relevant baseline documents and Worker code contain approximately 69.6 KB across 1,280 lines. The implementation scope also includes Treatment aggregation, craft evidence, runtime, workspace recovery, tests, and generated evidence. Token counts are planning estimates, not API billing guarantees; expect ±30% variance due to prompt repetition, Chinese/English tokenization, retries, and code diffs.

## DeepSeek Audit Run

There are 18 independent calls. The current client repeats the system prompt for each call and limits each output to 512 tokens.

| Component | Estimated tokens |
|---|---:|
| Repeated system prompt | 23,000–32,000 input |
| 18 task payloads | 12,000–20,000 input |
| Retry/format overhead | 5,000–12,000 input |
| 18 outputs | 5,000–9,216 output |
| **Audit subtotal** | **45,000–73,000 aggregate** |

Expected sequential API wall time: **25–70 minutes**, assuming no rate-limit incident. Manual/Codex evidence triage: **60–90 minutes**.

## Complete Implementation Budget

The audit is not the implementation. A no-shortcut implementation includes repository inspection, patches, negative tests, reruns, evidence generation, compatibility checks, and documentation.

| Phase | Agent tokens | Human-supervised time |
|---|---:|---:|
| Audit and triage | 55k–95k | 2–3 h |
| Treatment truth/generator hardening | 60k–110k | 4–6 h |
| Evidence contract and write-back gate | 80k–140k | 5–8 h |
| Failure, repeatability, recovery tests | 100k–180k | 7–10 h |
| Compatibility, ledgers, final verification | 60k–110k | 4–7 h |
| **Total** | **355k–635k aggregate** | **22–34 h** |

At four hours per day, the honest plan is **6–9 working days**. Faster completion is possible only if the audit proves several items already satisfy the gates; those items must still receive `EVIDENCED_NO_CHANGE` evidence. API latency and full-suite runtime are machine time and may overlap human review, but are not removed from the log.

## Reserve Policy

- Hold a 20% token and time reserve for failed tests, malformed model output, and recovery verification.
- Do not spend the reserve on new features.
- If the upper bound is reached, stop at a clean gate and report remaining items as incomplete; do not silently reduce test scope.

