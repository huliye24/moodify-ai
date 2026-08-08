# Moodify 验证集素材权利门禁｜VSR-001

**创建日期：2026-07-30**  
**用途：Moodify Phase 1内部声音验证**  
**当前状态：PASS**  
**处理状态：允许在本文件第1节限定范围内启动内部验证**

## 1. 请求确认的使用范围

本次确认仅授权以下有限用途：

- 在荣景文川与Moodify内部进行技术测试；
- 执行诊断、DSP处理、MRS和技术质量门；
- 生成响度匹配的Before/After候选；
- 由内部人员进行盲听评价；
- 保存指标、日志、Treatment Record和内部报告；
- 不对外发布、不公开传播、不商业发行；
- 不转授权第三方；
- 不将音频上传到新的外部服务；
- 不用于训练公开模型或建立可对外下载的数据集。

任何超出上述范围的使用必须重新取得确认。

## 2. 候选素材

| ID | 类型 | 绝对路径 | 当前状态 |
|---|---|---|---|
| VS-001 | AI vocal | `E:\moodify\local_audio_assets\mhp026\source\01_ai_vocal\mhp026_01_ai_vocal__pour_le_moi_pas_encore_ecrit.wav` | READY |
| VS-002 | Dense mix | `E:\moodify\local_audio_assets\mhp026\source\06_dense_mix\mhp026_06_dense_mix__neural_poison.mp3` | READY |
| VS-003 | Thin demo | `E:\moodify\local_audio_assets\mhp026\source\07_thin_demo\mhp026_07_thin_demo__jian_zhong_weiguang.mp3` | READY |
| VS-004 | Rock | `E:\moodify\local_audio_assets\mhp026\source\03_rock\mhp026_03_rock__black_therapy.mp3` | READY |
| VS-005 | Ambient | `E:\moodify\local_audio_assets\mhp026\source\04_ambient\mhp026_04_ambient__echoes_in_the_neon_labyrinth.mp3` | READY |

## 3. 人工确认声明

确认人需要确认以下事实：

1. 荣景文川或确认人有权将上述5个文件用于本文件第1节所述的内部验证；
2. 内部处理和盲听不会违反素材来源平台、创作者或第三方的使用条件；
3. 素材中不存在未经许可而不得进行内部处理的人声、采样或录音；
4. 如果某一文件不能确认，应单独标记为`BLOCKED`，不能用整体确认掩盖单项不确定性；
5. 本次确认不等于授权公开发布、商业发行、模型训练或外部上传。

## 4. 可接受的确认结果

### 全部允许

```text
我确认 VS-001 至 VS-005 可以按照 VSR-001 第1节的范围用于荣景文川与Moodify内部验证。
```

### 部分允许

```text
允许：VS-___、VS-___
禁止：VS-___、VS-___
不确定：VS-___
```

### 全部禁止

```text
VS-001 至 VS-005 均不允许用于本轮内部验证。
```

## 5. 确认记录

| 字段 | 当前值 |
|---|---|
| 确认人 | 用户（当前 Codex 任务中的授权确认人） |
| 确认时间 | 2026-07-31 08:45:00 +08:00（Asia/Shanghai） |
| 确认范围 | VSR-001 第1节；VS-001 至 VS-005 |
| 排除文件 | 无 |
| 备注 | 用户明确回复“确认，开始” |
| 门禁结论 | PASS |

## 6. 后续状态转换

```text
PENDING
  -> 人工逐项确认
  -> READY / BLOCKED
  -> READY数量 >= 5：冻结验证集v0.1
  -> READY数量 < 5：只从已确认素材池补充，不从不明目录临时抽取
```

只有门禁结论更新为`PASS`后，才可以建立验证集Manifest并开始Preflight。
