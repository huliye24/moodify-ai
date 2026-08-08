# Moodify 真实音频验证集 v0.1｜候选冻结记录

**日期：2026-07-31**  
**状态：FROZEN / READY｜VSR-001 已通过**  
**用途：仅限荣景文川与 Moodify 内部声音验证**  
**禁止事项：对外发布、商业发行、外部上传、模型训练、覆盖或修改源文件**

## 1. 冻结规则

以下 5 个文件的身份、路径、校验值和验证问题已经冻结。权利门禁通过前，它们只是候选验证集，不得启动 DSP、生成衍生音频或开展试听；VSR-001 全部通过后，状态可直接转换为 `FROZEN/READY`。任何文件被判定为 `BLOCKED` 时，只能从已确认权利的候选池补位并提升验证集版本号。

## 2. 验证集清单

| ID | 类型/曲风 | 时长 | 格式 | 采样率/声道 | 主要声音问题 | 本轮目标 | 权利状态 |
|---|---|---:|---|---|---|---|---|
| VS-001 | AI vocal | 179.320 s | WAV/PCM 16-bit | 48 kHz/2 | 人声塑料感、主体稳定性、清晰度 | 降低塑料感和刺激感，同时保留人声主体 | READY |
| VS-002 | Dense mix | 219.960 s | MP3 | 48 kHz/2 | 层级拥挤、动态受压、主体分离不足 | 改善层次与清晰度，不造成削薄或泵动 | READY |
| VS-003 | Thin demo | 113.520 s | MP3 | 48 kHz/2 | 厚度不足、频谱空洞、过处理风险 | 增加稳定厚度，不以过暗或低频膨胀换取丰满 | READY |
| VS-004 | Rock | 306.560 s | MP3 | 48 kHz/2 | 瞬态、动态保留、高频刺激 | 控制刺激感，同时保留鼓和吉他的冲击力 | READY |
| VS-005 | Ambient | 269.520 s | MP3 | 48 kHz/2 | 空间宽度、尾音、单声道兼容 | 保留纵深和尾音，避免相位不稳与空间坍缩 | READY |

## 3. 源文件身份

| ID | 源文件 | 字节数 | SHA-256 |
|---|---|---:|---|
| VS-001 | `E:\moodify\local_audio_assets\mhp026\source\01_ai_vocal\mhp026_01_ai_vocal__pour_le_moi_pas_encore_ecrit.wav` | 34,429,612 | `27BEA8E034F737D2B96C63A48B20859DAE36A3AC1D1DB567992BFA46B59B0D27` |
| VS-002 | `E:\moodify\local_audio_assets\mhp026\source\06_dense_mix\mhp026_06_dense_mix__neural_poison.mp3` | 4,991,948 | `68D1E9A5AE1A6D8515D16C3D1699D0F0AFFA15B35BB233A24425C674D388F7F5` |
| VS-003 | `E:\moodify\local_audio_assets\mhp026\source\07_thin_demo\mhp026_07_thin_demo__jian_zhong_weiguang.mp3` | 2,508,563 | `C13F80127B00B61376F058D25B3E1804BC54A212A5156DC394BC29E21683ED31` |
| VS-004 | `E:\moodify\local_audio_assets\mhp026\source\03_rock\mhp026_03_rock__black_therapy.mp3` | 6,646,380 | `C14B884C873D16EEE67FDD53D65FADDF6F9DD73E92EAFB258808488680E7910D` |
| VS-005 | `E:\moodify\local_audio_assets\mhp026\source\04_ambient\mhp026_04_ambient__echoes_in_the_neon_labyrinth.mp3` | 5,865,189 | `BAF9DBB783CF7C275EE788A59E61869B5FA7DCF912C5C8A2EC55173B5D1A852A` |

## 4. 可复现检查

元数据由本机 `ffprobe` 只读取得；文件身份使用 SHA-256。运行前必须重新校验哈希，任一不一致即停止并记录为 `SOURCE_CHANGED`。源文件永远只读，所有结果写入新的日期化运行目录。

## 5. 状态转换

- 当前：`FROZEN / READY`；
- VSR-001 五项全部确认：转为 `FROZEN / READY`，版本仍为 v0.1；
- 少于五项确认：保持阻塞，补位后发布 v0.2，不静默替换；
- 任何源文件哈希变化：保持阻塞，重新登记版本。
