# AUDIT B — Protocol and Gate Consistency Review

**Task**: DSK-MFY-DAY2-CLOSURE-003  
**Date**: 2026-07-31  
**Status**: COMPLETE — 1 P2, 1 P3 found

## B1. Blind Scoring Semantics Without A/B Identity

**Assessment**: PASS (minor P3 note)

`LISTENING_PROTOCOL_V0.1.md` Section 6 defines 7 dimensions, each scored 1-5 with clear semantic anchors:
- 1 = 明显更差 (significantly worse)
- 2 = 略差 (slightly worse)
- 3 = 持平/不可辨 (tied/indistinguishable)
- 4 = 明显更好 (significantly better)
- 5 = 显著改善 (dramatically better)

The SCORECARD.md asks: "分数（1—5）" without restating anchors.

**P3**: SCORECARD.md does not restate the 1-5 anchor definitions. A scorer reading only the scorecard (without the protocol) might not know whether 1 or 5 means "better." The protocol anchors exist but are not physically co-located with the scoring form. Minimal fix: add a one-line anchor reminder on the scorecard.

## B2. "1-5" Reference Direction

**Assessment**: PASS

The protocol explicitly defines higher = better (4 = "明显更好", 5 = "显著改善"). The scoring is relative: "B相对于A" — comparing the two presented versions without knowing which is processed. The forced preference question "A / B / NO_PREFERENCE" is unambiguous regardless of A/B identity.

The semantics are clear: score each dimension for the B version relative to A (or equivalently, compare the two and assign the better one a higher score).

## B3. Mapping File Isolation from Scoring Materials

**Assessment**: PASS

Physical structure:
```
blind/
  _mapping/          ← mapping (separate from scoring)
    round-01.json
  round-01/          ← scoring materials
    A.wav
    B.wav
    SCORECARD.md
```

SCORECARD.md instructs: "评分提交后，才由记录人读取相邻 `_mapping` 目录中的映射" (only read mapping after score submission).

The mapping is in a parent-sibling directory, not inside `round-01/`. A scorer opening only `round-01/` would not see `_mapping/`. However, `_mapping/` is visible at the same directory depth level. If the scorer navigates up one level in the file explorer, they would see it.

**No P0/P1**: The physical separation exists. A determined scorer could find and read the mapping, but this is a procedural/trust control, not a cryptographic one. The protocol does not claim the mapping is cryptographically hidden.

## B4. Loudness Match 0.2 dB Threshold Consistency

**Assessment**: PASS

`LISTENING_PROTOCOL_V0.1.md` Section 3.3: "匹配后目标差异不超过 `0.2 dB`; 超过则标记 `LOUDNESS_MISMATCH`"

`TRIAL_PREFLIGHT_REPORT.md` Section 5: "FFmpeg `volumedetect` 复核：Before `-15.4 dB`、After Matched `-15.2 dB`，显示精度下差异为 0.2 dB，未超过协议门限"

The protocol says "不超过 0.2 dB" (not exceeding). The measurement shows 0.2 dB — this is exactly at the boundary. "不超过" (does not exceed) is ambiguous at the boundary: ≤ or <? 

**P2**: The protocol uses "不超过 0.2 dB" which is ambiguous at the exact boundary value. If interpreted as strictly-less-than, 0.2 dB would fail. If interpreted as less-than-or-equal, 0.2 dB passes. The measured value of exactly 0.2 dB (at FFmpeg's reported precision) sits on this boundary. Recommend: clarify as "≤ 0.2 dB" or "< 0.2 dB" in protocol, and document the specific interpretation used.

## B5. FFmpeg Single-Decimal Precision Sufficiency

**Assessment**: PASS with note

FFmpeg `volumedetect` reports `mean_volume` and `max_volume` in dB with one decimal place. The protocol threshold is 0.2 dB (one decimal). The measurement resolution matches the threshold precision, but:

- A true difference of 0.199 dB would display as 0.2 dB (rounding up)
- A true difference of 0.201 dB would also display as 0.2 dB (rounding down)
- The rounding error band is ±0.05 dB around the displayed value

At the boundary value of exactly 0.2 dB, this creates a ±0.05 dB uncertainty band. The protocol does not account for this measurement precision limitation.

**P2 note**: This is a known limitation of the tooling. The protocol should either: (a) accept that 0.2 dB at FFmpeg precision is a pass, (b) use a tool with higher precision (e.g., ITU-R BS.1770 loudness meter with 0.01 dB resolution), or (c) set the threshold at 0.3 dB to provide a margin above the quantization floor.

## B6. Technical Hard Failure Consistency Across Documents

**Assessment**: PASS

`dynamic_damage` and `passed=false` consistently reported:
- `validation_report.json`: `passed: false`, `risk_flags: ["dynamic_damage"]`
- `TRIAL_PREFLIGHT_REPORT.md`: "技术门判定 `FAIL`" and "MRS proxy 虽然上升，但不能推翻硬失败"
- `DAILY_GATE_REPORT.md`: "技术门判定 `FAIL`，主要风险为动态范围减少 7.61 dB"
- `treatment_record.json`: `human_feedback.status: "pending"` (not silently marked as passed)

No document attempts to override the hard failure with the MRS increase. The protocol rule "MRS 上升不能覆盖 dynamic_damage 硬失败" is consistently enforced.

## B7. "DAY 2 PASS" Meaning Clarity

**Assessment**: PASS

`DAILY_GATE_REPORT.md` Section 2 explicitly states:
"技术门判定 `FAIL`，主要风险为动态范围减少 7.61 dB；该失败已如实保留，不影响"协议可执行"这一日目标成立。"

And in the orchestration:
"DAY 2 PASS 只允许表示验证集与协议闭环成立，不能表示声音结果通过"

The DAY 2 PASS claim is about process completeness (validation set frozen, protocol defined, trial executed), NOT about audio quality. The technical failure is acknowledged and preserved. The distinction is clear in all four relevant documents.

## B8. Human Scoring "PENDING" Consistency

**Assessment**: PASS

`human_feedback.status: "pending"` appears consistently:
- `treatment_record.json`: `"status": "pending"`
- `TRIAL_PREFLIGHT_REPORT.md`: "人工听感尚未填写"
- `DAILY_GATE_REPORT.md`: Table shows human scoring not yet completed
- `SCORECARD.md`: All fields empty (blank template)

No document implies scores have been filled or that pending means anything other than "awaiting human input."

## B9. Identity Leak and Pre-Unblinding Risk

**Assessment**: PASS (P3 observations)

Risk vectors examined:
1. **File timestamps**: Source WAV timestamp `Jun 1 16:14`; `after_matched.wav` timestamp `Jul 31 08:52`. A.wav inherits the source timestamp, B.wav inherits the after_matched timestamp. A scorer examining file metadata could distinguish them by date. **(P3)**
2. **File sizes**: A.wav = 34,429,612 bytes, B.wav = 34,294,484 bytes. The size difference is 135,128 bytes (~0.4%). Detectable but not visually obvious without explicit comparison. **(P3)**
3. **Path leakage**: No preset name, parameter values, or before/after labels appear in round-01/ filenames. **(PASS)**
4. **Silent post-scoring modification**: Scorecard is a Markdown file. After submission, it could theoretically be modified with no audit trail. The protocol says "评分提交后不得改分，只能追加复核记录" but provides no technical enforcement (e.g., hash commitment, append-only log, or write-once storage). **(P2)**

**Summary**: Low risk of accidental unblinding; moderate risk that a curious scorer could identify A/B by examining file metadata. The protocol relies on procedural trust, not cryptographic blinding.

## B10. Score Recording Immutability and Unblinding Append Protocol

**Assessment**: P2

`LISTENING_PROTOCOL_V0.1.md` Section 4:
"揭盲必须发生在该轮评分提交之后，评分提交后不得改分，只能追加复核记录。"

`SCORECARD.md`:
"评分完成后只允许追加揭盲结果，不修改原始评分。"

These are clear procedural rules, but:
- The scorecard is a plain Markdown file with no versioning, hash, or append-only mechanism
- No timestamp or integrity record is generated at score-submission time
- The mapping directory is readable at any time; no technical barrier prevents pre-unblinding
- No Git commit, hash chain, or digital signature anchors the "submitted" state

**P2**: The protocol correctly describes the desired behavior but provides no technical enforcement. A subsequent editor could modify both scores and mapping without detection. For a production validation system, recommend: (a) hash the scorecard at submission time and record the hash in a separate tamper-evident location, (b) use append-only formats (e.g., JSONL with sequence numbers), or (c) commit the submitted scorecard to git as a signed snapshot before unblinding.

## Batch B Summary

| Check | Result | Issues |
|---|---|---|
| B1 Blind semantics | PASS | P3: anchors not on scorecard |
| B2 1-5 direction | PASS | |
| B3 Mapping isolation | PASS | |
| B4 0.2 dB consistency | PASS | P2: boundary ambiguity |
| B5 FFmpeg precision | PASS | P2: ±0.05 dB uncertainty |
| B6 Hard failure consistency | PASS | |
| B7 DAY 2 PASS meaning | PASS | |
| B8 Human PENDING | PASS | |
| B9 Identity leak | PASS | P3: file timestamps, P2: no tamper detection |
| B10 Score immutability | PASS | P2: no technical enforcement |

**P2 issues (4)**: B4 (0.2 dB boundary), B5 (FFmpeg precision), B9 (tamper detection), B10 (score immutability)  
**P3 issues (2)**: B1 (anchor reminder), B9 (file timestamps)

**Batch B Conclusion: PASS with noted concerns. No P0 or P1 issues. Protocol is internally consistent and executable; identified concerns are about measurement precision, boundary definitions, and lack of technical tamper-proofing — none prevent the protocol from functioning as designed for an internal validation round.**
