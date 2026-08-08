# DSK-MFY-LYRICS-INTENT-007｜歌词意图证据层

**日期：** 2026-08-01  
**执行 Worker：** DeepSeek  
**独立验收与最终收尾：** Codex / 授权用户  
**执行方式：** 三阶段严格串行；每阶段先形成可验收闭环，再进入下一阶段

## 1. 核心命题

延续 One-Point 原则：

> **让这首音乐成为它自己。**

歌词可以帮助 Moodify 理解作品“在指向什么”，但不能成为新的控制
中心：

> **声音呈现作品的身体，歌词显露作品的指向；Moodify 倾听两者，但不替作者解释作品。**

本任务新增的是可选的 **Lyrics Intent Evidence（歌词意图证据）**，不是
自动审美、心理诊断、文本生成、翻译服务或歌词驱动的处理指令。

## 2. 不可改变的边界

1. 创作者声明与 human_owner 的判断权高于任何歌词推断。
2. 歌词和声音是并列证据；任何一方不得自动覆盖另一方。
3. 反讽、隐喻、角色叙事、视角变化和有意反差均不得被算法当作错误。
4. 不推断作者的真实心理、疾病、身份、经历、政治立场或违法风险。
5. 不根据敏感属性生成处理建议，不将负面词汇等同于负面音乐目标。
6. 不输出“作品真正含义”；只输出来源、结构事实、人工声明、有限推断、
   不确定性和冲突。
7. 不生成、补写、改写或联网搜索歌词；不安装依赖，不调用外部模型。
8. 不处理音频，不自动选择 Final，不宣称 improved/mastered/completed。
9. 原歌词只进入 evidence；默认 summary 不复述整段歌词或长句。
10. 无权利/授权声明时 fail-closed，不复制或分析歌词正文。

## 3. 必读事实源

开始前完整读取：

```text
E:\moodify\docs\tasks\deepseek\DSK-MFY-LYRICS-INTENT-007\00_TASK_ORCHESTRATION.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-LYRICS-INTENT-007\02_CODEX_ACCEPTANCE_MATRIX.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-LYRICS-INTENT-007\03_PRINCIPLE_SEED.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-ONE-POINT-006\CODEX_FINAL_ACCEPTANCE_2026-08-01.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-ONE-POINT-006\ONE_POINT_CONTRACT.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-ONE-POINT-006\LANGUAGE_CANON.md
E:\moodify\docs\strategy\MOODIFY_ONE_POINT_PRINCIPLE.md
E:\moodify\docs\architecture\MOODIFY_ONE_POINT_ARCHITECTURE.md
E:\moodify\moodify-bridge\README.md
E:\moodify\moodify-bridge\src\moodify_bridge\schemas.py
E:\moodify\moodify-bridge\src\moodify_bridge\services.py
E:\moodify\moodify-bridge\src\moodify_bridge\cli.py
E:\moodify\moodify-bridge\tests\test_one_point.py
```

查找并遵守适用 `AGENTS.md`。冻结 Git/dirty 状态、Python 版本、测试基线
和只读文件哈希。现有修改和未跟踪文件全部属于用户。

## 4. 允许与禁止范围

允许修改：

```text
E:\moodify\moodify-bridge\src\moodify_bridge\
E:\moodify\moodify-bridge\tests\
E:\moodify\moodify-bridge\README.md
E:\moodify\docs\strategy\MOODIFY_ONE_POINT_PRINCIPLE.md
E:\moodify\docs\architecture\MOODIFY_ONE_POINT_ARCHITECTURE.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-LYRICS-INTENT-007\
E:\moodify\outputs\deepseek_validation\DSK-MFY-LYRICS-INTENT-007\
```

禁止修改：Core、Runtime、Workspace、DSP、Preset、MRS、Bridge migrations、
DuckDB schema、demo 原件、006 验收证据、历史输出、真实音频和客户资产；
禁止 Git 暂存、提交、推送、分支操作。需要越界时写
`SCOPE_CHANGE_REQUEST.md`，状态置为 HOLD 后停止。

## 5. 目标产品形式

唯一入口保持不变：

```powershell
py -3.12 -m moodify_bridge.cli refine prepare SPEC.yaml --output-dir NEW_DIR
```

歌词是 `OnePointSpec` 的可选证据引用。无歌词时行为与 006 完全兼容；有
歌词时，默认五中心仍为 Essence / Protect / Allow / Action / Entrust，
不得新增第六个默认标题。

建议的最小输入概念（Stage 1 根据代码事实冻结最终字段）：

```yaml
lyrics:
  path: lyrics.txt
  language: zh-CN
  version: authorized-draft
  rights_basis: owner-provided
  declared_intent: "第一人称在克制与释放之间移动。"
```

要求：UTF-8 纯文本或结构化 Markdown；路径解析规则明确；文件大小上限
明确；`rights_basis` 使用封闭枚举；不得把 `declared_intent` 冒充机器推断。

## 6. Stage 1｜立意：合同、伦理和证据层级

编码前完成：

1. `BASELINE_AND_RISK_AUDIT.md`：当前事实、攻击面、隐私/版权风险。
2. `LYRICS_EVIDENCE_CONTRACT.md`：字段、枚举、路径、编码、大小、哈希、
   状态、失败码、兼容性与证据结构。
3. `INTERPRETATION_BOUNDARY.md`：事实、人工声明、有限推断、不确定性四层；
   禁止心理/身份/真实意图断言。
4. `LYRICS_LANGUAGE_ADDENDUM.md`：不增加默认叙事中心，确定默认表面允许
   出现的最少措辞。
5. `STAGE_1_GATE.md`：逐项证明歌词是证据而非控制中心。

合同至少冻结：

- 无歌词保持既有结果和 CLI 行为；
- 路径逃逸、软链接/重解析点、非文件、超限、非 UTF-8、NUL 字节拒绝；
- 原文 SHA-256、字节数、语言/版本/rights_basis 写入 evidence；
- 正文不进入 CLI stdout、`result.json`、异常和默认 summary；
- 结构事实只允许可复现提取（段落、显式标签、完全/规范化重复）；
- 情感、主题、隐喻只来自明确人工声明，或标为有限推断并带依据与不确定性；
- 歌词与 `essence/must_preserve/desired_change/must_avoid` 冲突时不得自动
  改写合同，状态至少 `NEEDS_EVIDENCE`，由 owner 裁决；
- 不确定语言、多语混合和纯器乐不能伪装成确定结论。

Stage 1 未 PASS，禁止编码。

## 7. Stage 2｜聆听：实现最小歌词意图证据

在 Bridge 内实现兼容扩展：

1. 严格歌词引用 schema，未知字段拒绝、字符串去空白、枚举封闭。
2. 安全加载器：本地只读、UTF-8、大小上限、NUL 检查、SHA-256、稳定错误码。
3. 确定性结构器：保留段落顺序；识别显式 Verse/Chorus/Bridge 等标签；
   统计规范化重复行/段；不得使用词典情感分数伪装理解。
4. 建立 `lyrics_evidence.json`，明确分开：
   - `source_facts`
   - `declared_intent`
   - `structural_observations`
   - `uncertainties`
   - `conflicts`
5. 证据包保存授权输入的逐字节副本或等价审计副本、元数据和哈希；所有
   文件进入 `package_manifest.json`。
6. 将歌词存在性和真实动作简洁写入 Action/Entrust；不引用长歌词、不新增
   默认标题、不输出内部术语。
7. 冲突或解释不足时诚实进入 `NEEDS_EVIDENCE`；正文缺失/非法/无权利时
   预期失败无 traceback。
8. 保持 006 的 PPE、证据、相对路径和五中心合同。

必须测试：无歌词兼容、有效中英文/多语文本、空文件、空白文件、非 UTF-8、
NUL、超限、缺失文件、目录、路径逃逸、重解析点（可安全构造时）、未知
rights、缺失 rights、哈希、原文不泄漏、重复结构确定性、冲突、失败状态、
非空输出目录、双运行、旧 CLI、全量回归。

## 8. Stage 3｜留白：减法、安全与继承

1. `DEFAULT_SURFACE_AUDIT.md`：证明仍为五中心且无歌词正文泄漏。
2. `PRIVACY_COPYRIGHT_THREAT_MODEL.md`：路径、日志、异常、报告、缓存、
   evidence 副本和删除责任边界。
3. `FAILURE_LEDGER.md`：不少于 12 类失败注入，记录命令、退出码、错误码、
   traceback 与是否产生部分输出。
4. 两个全新目录双运行；规范化结果一致，所有清单哈希重算一致。
5. 无歌词 golden replay 与 006 合同回归必须通过。
6. 更新 README、One-Point 原则和架构；不把歌词包装成新的营销功能墙。
7. 生成 `VALIDATION_REPORT.md`、`INHERITANCE.md`、`PROGRESS.md`、
   `HANDOFF.md`。

最终状态只能是 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。DeepSeek 无权
宣布最终 ACCEPT。

## 9. 强制停止条件

- Stage 1 未通过即编码；
- 需要联网、外部模型、新依赖、migration 或数据库 schema；
- 原歌词出现在 stdout、异常、默认 summary 或 result；
- 未声明权利基础仍读取/复制歌词正文；
- 自动推断创作者心理、身份或“作品真正含义”；
- 歌词自动覆盖声音证据或创作者合同；
- 只读基线哈希变化或范围外写入；
- 为简化而删除 006 的证据、失败或人工主权。

## 10. 最终交付

任务目录至少包含：

```text
BASELINE_AND_RISK_AUDIT.md
LYRICS_EVIDENCE_CONTRACT.md
INTERPRETATION_BOUNDARY.md
LYRICS_LANGUAGE_ADDENDUM.md
STAGE_1_GATE.md
DEFAULT_SURFACE_AUDIT.md
PRIVACY_COPYRIGHT_THREAT_MODEL.md
FAILURE_LEDGER.md
VALIDATION_REPORT.md
INHERITANCE.md
PROGRESS.md
HANDOFF.md
```

验证证据：

```text
outputs/deepseek_validation/DSK-MFY-LYRICS-INTENT-007/
  run_a/
  run_b/
  no_lyrics_replay/
  failure_matrix/
  readonly_hashes_before.json
  readonly_hashes_after.json
  normalized_comparison.json
```

完成后停止，等待 Codex 独立验收和必要收尾。
