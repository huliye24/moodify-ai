# MFY-CR-P06 — Final Response

## 1. Result

```text
STATUS = P06_COMPLETE_WITH_BLOCKERS (listening is a human step, not a technical failure)
BRANCH = codex/moodify-classic-reconstruction-001
HEAD   = ef21e523 (implementation) + a41547bd (evidence)
GOLDEN_STATUS = PENDING_LISTENING (kit ready; machine portion complete)
```

完整 golden 链路已实现并在自有曲目上跑通。盲听是人类的步骤——机器侧全部
完成且诚实标注为 PENDING。

## 2. Source

```text
SOURCE_ALIAS = CAD10-05_VIEILLIR ("Vieillir et devenir nouveau avec toi")
SOURCE_SHA256 = aa1542c00866efa8e438cfcaf6b40b2325abe2285e5896e8751151459700e9e5
DURATION = 182.16 s | FORMAT = WAV 48k/24-bit/stereo
ERA_HINT = owned cadeau10 album, HF-limited character
RIGHTS_STATUS = OWNED
```

## 3. Diagnostic

```text
ED-01 = POSSIBLE_TECHNICAL_LIMITATION (LOW)  cutoff ~14.1k, rolloff ~9.3k
ED-02 = INSUFFICIENT_EVIDENCE (LOW)          floor -29 dBFS, no quiet windows
ED-03 = NOT_APPLICABLE
ED-04 = NOT_APPLICABLE (corr 0.71)
ED-05 = NOT_APPLICABLE
ED-06 = NOT_SUPPORTED_IN_V0_1
```

## 4. Candidates

```text
SOURCE = immutable reference
A = Minimal:        comp bypass, reverb 0, +0.5 dB @10k        — gates PASS
B = Balanced:       +1.5 dB @10k, presence +0.8 dB @3k        — gates PASS
C = Upper Boundary: +3.0 dB @10k, presence +1.5, low +1.0      — gates PASS
```

硬门全部通过（无新削波 / 时长保留 / 声道保留 / 有限样本 / 响度预算内）。
候选改动为外科手术级：LUFS +0.03..+0.93，LRA +0.0..+0.55，centroid +38..+253 Hz。

## 5. Identity Guard

```text
A = PASS   B = PASS   C = PASS   (IG-03 NOT_MEASURABLE as designed)
```

无 REJECT、无 HUMAN_REQUIRED。早前 REJECT 来自链的常开压缩器——被 guard
正确拦截，objective 随后显式旁路（记录为决策，非静默调参）。

## 6. Technical Ranking

```text
TECHNICAL_TOP = C (PASS, auto-approvable)
SOURCE_RANK = 4 (always eligible)
```

## 7. Blind Listening

```text
ROUND_1_TOP = PENDING_HUMAN
ROUND_2_TOP = PENDING_HUMAN
PAIRWISE_SOURCE_VS_WINNER = PENDING_HUMAN
NOTICEABLE / PREFERRED / IDENTITY_SAFE / REPEATABLE = PENDING_HUMAN
```

盲听工具包已就绪：`moodify-core-package/golden_run_out/listening/X1-X4.wav`
（level-matched 到 -13.94 LUFS，映射隐藏，评分前不可查看）。

## 8. Hardware Observation

```text
CHAIN_A = PENDING (consumer)
CHAIN_B = PENDING (reference)
SAME_WINNER_ACROSS_CHAINS / ARTIFACTS / BENEFIT = PENDING
```

协议已建立；canonical master 保持 hardware-neutral（零设备代码）。

## 9. Golden Decision

```text
PENDING_LISTENING
```

机器侧全部满足（gates PASS、identity PASS、technical top C、候选可感知差异
大概率存在——centroid +253 Hz）。但按 Golden 规则，NOTICEABLE + PREFERRED +
IDENTITY_SAFE + REPEATABLE 必须由盲听判定，不能由机器宣称。这是诚实边界，
不是失败。

## 10. What We Learned

1. 链的常开 Compressor 对动态录音（LRA 12.7）是破坏性的——Identity Guard
   正确拦截，证明 guard 有真实价值。
2. 链的默认 20% 湿混响给输出加 +4.2 LU——objective 必须显式关掉。
3. ED-02 在此源上是诚实的 INSUFFICIENT——无静区的噪声无法判读，BYPASS 是
   正确结果。
4. 带宽 objective 只能增亮现存内容（centroid +253 Hz），不能恢复 14k 以上
   缺失频谱——这是 v0.1 的边界。
5. C 的 centroid 增量（+253 Hz）贴着 IG-01 代理预算（300 Hz）——校准重点。
6. 候选的响度/动态/立体声几乎不动——重建是"决策导向"，不是"preset 导向"。
7. 盲听是硬门槛——没有它，golden 不能宣称。
8. 整条链（scan→diagnose→plan→render→gate→guard→rank→blind kit）已可重复
   运行，具备多曲目验证基础。

## 11. Tests

```text
pipeline = 12 passed (objective/gates/blind/record/integration)
blind_tooling = 4 passed (label hiding, level match, mapping, no leak)
p03_p04_p05_regression = included and green
full_python = 851 passed / 5 skipped / 0 failed
ruff = all checks passed
diff_check = clean
```

## 12. Recommendation

```text
READY_FOR_P07_RECONSTRUCTION_DATA_FACTORY
(盲听完成后按结果更新 golden_status；技术侧无阻塞)
```
