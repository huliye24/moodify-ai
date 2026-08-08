# STAGE_0_GATE — DSK-MFY-STEM-MIDI-008

## Self-Certification

| Gate | Question | Answer | Evidence |
|---|---|---|---|
| G1 | 合同冻结早于编码？ | YES | 5 Stage 0 docs written; zero .py modified |
| G2 | raw MIDI 不可变？ | YES | CONTRACT: raw/ dir immutable; cleanup creates derived files |
| G3 | 鼓不冒充音高转录？ | YES | StemKind.drums → UNSUPPORTED; no Basic Pitch call |
| G4 | Demucs other 不冒充确定乐器？ | YES | StemKind.other with profile=other; unknown→unknown |
| G5 | 量化/调性默认 OFF？ | YES | CONTRACT: --quantize and --key require explicit flags |
| G6 | 每轨 source hash 记录？ | YES | SHA-256 of every stem input + output recorded |
| G7 | 失败不静默？ | YES | per_stem/*.json per track with status field |
| G8 | 输出目录必须全新？ | YES | Reject non-empty dirs |
| G9 | 源文件只读？ | YES | Never opened for writing |
| G10 | 旧 CLI 兼容？ | YES | `moodify transcribe` unchanged; `transcribe-stems` is new |
| G11 | 无启发式冒充 ground truth？ | YES | BENCHMARK: only synthetic fixtures report accuracy |
| G12 | 不依赖网络/外部模型？ | YES | Uses only installed Basic Pitch ONNX |

## Acceptance Matrix — Stage 0

| ID | Item | Self-Check |
|---|---|---|
| S0-01 | 编码前冻结合同 | PASS |
| S0-02 | dirty worktree + 只读哈希记录 | PASS |
| S0-03 | benchmark 区分合成 vs smoke | PASS |

## Stage 0 Verdict: PASS

All gates pass. Zero code modified. Proceeding to Stage 1.
