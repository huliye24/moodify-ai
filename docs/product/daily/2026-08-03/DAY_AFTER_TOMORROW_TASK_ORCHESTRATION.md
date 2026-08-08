# Moodify后日任务编排｜2026-08-03

## 第一新增主任务

`DSK-MFY-IDENTITY-CORE-010｜作品身份守恒核心 v0.1`

010不是继续扩展工具链，而是把One-Point原则落实为可执行核心。原周计划的
W05周结论保留，并在010封口后用于判断ADOPT/HOLD/REWORK；没有额外时间时，
其他增量任务显式顺延。

## 严格依赖

```text
008 Audio-to-MIDI HANDOFF
  -> 009 Score Engine HANDOFF
    -> 010 Identity Core
```

009未形成可读HANDOFF时，010保持HOLD/PENDING。不得让009和010并行修改
Bridge/Core接口，也不得以日期到达为由绕过依赖。

## 时间盒（6小时上限）

1. **Gate A｜30分钟：** 检查009状态、dirty边界、测试与接口稳定性。
2. **Stage 0｜75分钟：** 冻结身份守恒、证据对齐、Owner主权和可证伪合同。
3. **Stage 1｜105分钟：** 实现四态IdentityConservationReport。
4. **Stage 2｜105分钟：** 实现盲听包、Owner decision、NOT_PROMOTED Craft观察。
5. **Stage 3｜75分钟：** fixture、双运行、失败矩阵、全量回归和HANDOFF。
6. **Codex验收｜剩余窗口：** 按矩阵独立给出ACCEPT/REWORK/HOLD。

## 当日完成定义

最低完成：Stage 0合同PASS，能明确什么是身份证据、什么不能自动判断。  
目标完成：Source/Candidate产生可审计四态报告，Owner可显式决定，Craft只
形成未晋级观察。  
禁止宣称：已经理解作品、已经优于制作人、已经形成商业护城河。

DeepSeek入口：

```text
E:\moodify\docs\tasks\deepseek\DSK-MFY-IDENTITY-CORE-010\01_DEEPSEEK_EXECUTION_COMMAND.txt
```

## 第二新增任务｜010之后严格串行

`DSK-MFY-DECISION-INTELLIGENCE-011｜制作决策智能训练地基 v0.1`

011把010产生的身份守恒、Owner决定和Craft观察组织为未来可训练的
DecisionEpisode。它不直接训练生产模型，只建立只读数据builder、防泄漏
split、CPU离线baseline、dataset card和模型晋级协议。

依赖链更新为：

```text
008 -> 009 -> 010 -> 011
```

011只有在010形成可验收HANDOFF后才能启动。由于010本身已有6小时上限，
011在8月3日属于**排队任务**：有独立追加窗口才执行；否则保留在8月3日队列
并顺延实际实施日期，不与010并行、不压缩010验收、不制造同日虚假完成。

011 DeepSeek入口：

```text
E:\moodify\docs\tasks\deepseek\DSK-MFY-DECISION-INTELLIGENCE-011\01_DEEPSEEK_EXECUTION_COMMAND.txt
```
