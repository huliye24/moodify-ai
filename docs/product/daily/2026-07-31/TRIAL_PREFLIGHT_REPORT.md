# VS-001 单样本试跑前检查

**日期：2026-07-31**  
**样本：VS-001｜AI vocal**  
**结论：TRIAL COMPLETED / TECHNICAL GATE FAIL / HUMAN SCORE PENDING**

## 1. 已完成的只读检查

| 检查项 | 结果 |
|---|---|
| 文件存在且可读 | PASS |
| 容器/编码 | WAV / PCM signed 16-bit little-endian |
| 采样率/声道 | 48,000 Hz / 2 channels |
| 时长 | 179.320 s |
| 文件大小 | 34,429,612 bytes |
| SHA-256 | `27BEA8E034F737D2B96C63A48B20859DAE36A3AC1D1DB567992BFA46B59B0D27` |
| 源文件修改 | 未修改 |

检查工具：`ffprobe`、PowerShell `Get-FileHash`。这些步骤只解析文件头并读取文件内容计算校验值，不产生音频副本或处理结果。

## 2. 权利门禁解除

用户于 2026-07-31 08:45:00 +08:00 明确确认 VS-001 至 VS-005 可在 VSR-001 第1节范围内用于内部验证。VSR-001 已转为 `PASS`，本报告原有的处理阻塞随之解除。

## 3. 正式试跑

| 项目 | 结果 |
|---|---|
| 样本/预设 | VS-001 / `warm_vocal` |
| 处理输出 | `outputs/daily_runs/20260731_vs001_trial/process` |
| Inspector输出 | `outputs/daily_runs/20260731_vs001_trial/inspector` |
| Treatment Record | `outputs/daily_runs/20260731_vs001_trial/treatment_record.json` |
| 输出时长/格式 | 179.320 s / 48 kHz stereo PCM16 WAV |
| 输出 SHA-256 | `475778A3CC97499E088C0736C4AB9496813EBA3D7C1D20D6139449BB74ECA0CC` |
| 响度匹配副本 SHA-256 | `014E2AE8A3130A20919D3893FC75C096F31D18FD5FC6DFB9551D8C8C7EB6EE95` |

处理、Inspector与Treatment Record命令均返回成功，证据链完整。源文件哈希复核一致，未被修改。

## 4. 技术门禁结果

| 指标 | Before | After | Delta |
|---|---:|---:|---:|
| Peak | -3.88 dB | -0.18 dB | +3.70 dB |
| RMS | -15.72 dB | -9.83 dB | +5.89 dB |
| Crest factor | 3.91 | 3.04 | -0.87 |
| Dynamic range | 24.06 dB | 16.45 dB | **-7.61 dB** |
| Presence | -16.4 dB | -14.7 dB | +1.7 dB |
| Air | -16.8 dB | -15.7 dB | +1.1 dB |
| MRS proxy | 1106.69 | 1131.51 | +24.82 |

`validation_report.json` 判定 `passed=false`，风险标志为 `dynamic_damage`，原因是动态范围减少超过 4 dB。MRS proxy 虽然上升，但不能推翻硬失败。

## 5. 响度匹配与盲听包

- Inspector 对 After 施加 `-5.89 dB` 固定增益生成 `after_matched.wav`；
- 初次 FFmpeg `volumedetect` 只显示一位小数，不作为边界判定的最终证据；
- 使用 `pyloudnorm` 按 BS.1770 集成响度复核：Before `-13.303462 LUFS`、After Matched `-13.257675 LUFS`，绝对差 `0.045787 LU`，明确满足 `|Δ loudness| ≤ 0.20 dB`；
- 随机种子：`20260731|VS-001|warm_vocal|round-01`；
- 种子 SHA-256：`4696473a4c066e8b08da5bedf2dd6e743c154251ff2a240dfbbc383d5a8d6194`；
- 确定性规则：首字节为偶数时 A=Before；本轮首字节 70，因此 A=Before、B=After Matched；
- 盲听文件位于 `outputs/daily_runs/20260731_vs001_trial/blind/round-01`；
- 人工听感尚未填写，不能作主观偏好结论。

## 6. 协议歧义检查结果

旧评分卡固定暴露 `before → after_matched` 顺序，不满足真正盲听。新协议已改为随机 A/B 标签、平衡身份和评分后揭盲。另外，旧卡把温暖度与空间感作为所有曲目的通用主维度；v0.1 改为通用技术维度加每曲 `target_fit`，避免用不适合曲目的目标误判。
