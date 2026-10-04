# Agent Foundation — 会话总报告（2026-10-04）

> **性质：** 交接 / 总览文档。把本会话六个任务的产出合成一处 ——
> 此前六份报告分散在五条**未合并**分支上，合并前没有任何地方能一次看全。
> **基线：** `origin/main` = `1dd5b2e1`（已核对）
> **本报告不改变任何东西**：纯文档。

---

## 一、一句话状态

**六项任务全部完成。一层已进 main，四层开着 PR，一层（CI 审计）结论是「这个门坏了」。**

```text
已合并  HOTFIX 000            → main（PR #40，merge f9a00de2）
开放    ECOSYSTEM 001/002/003  → PR #41 / #42 / #43（栈式）
开放    Project Model 0.1      → PR #44
已推送  CI 审计                → 分支 ci/temporal-texture-audit（无 PR）
```

**唯一挡在所有合并前面的，是一个从未在 main 上运行过的、自身已经坏掉的 CI 检查。** 详见第八节。

---

## 二、时间线与任务

| # | 任务 | 产出 | 报告 |
| --- | --- | --- | --- |
| 1 | **TASK 001** — Project Model 0.1 | `moodify.project`，43 测试 | `2026-10-04` 分支内 |
| 2 | **HOTFIX 000** — Core 测量正确性 | 修 F1–F4，20 测试 | ✅ 与本主题同批 |
| 3 | **ECOSYSTEM 001** — 能力生态地图 | 3 份战略文档，纯 docs | `2026-10-04_ECOSYSTEM_001_CAPABILITY_MAP.md` |
| 4 | **ECOSYSTEM 002** — Capability Registry 0.1 | `moodify.capabilities`，88 测试 | `2026-10-04_ECOSYSTEM_002_CAPABILITY_REGISTRY.md` |
| 5 | **ECOSYSTEM 003** — Provider Router 0.1 | 确定性选择，56 测试 | `2026-10-04_ECOSYSTEM_003_PROVIDER_ROUTER.md`（分支内） |
| 6 | **INTEGRATION 001** — 五层合并验证 | 零冲突，1391 绿 | `AGENT_FOUNDATION_INTEGRATION_001.md` |
| 7 | **CI_HOTFIX 001** — CI 基线真相审计 | `CI_TOOLING_BROKEN` | `CI_HOTFIX_001_TEMPORAL_TEXTURE_BASELINE_AUDIT.md` |

**期间仓库被并行操作者推进了两次**（见第三节），本报告已按最新状态核对。

---

## 三、当前真实状态（每条 hash 都核对过）

### main 的新增内容

```text
origin/main = 1dd5b2e1
  ├─ PR #36  云节点文档
  ├─ PR #37  仓库清理（untrack outputs/，新增 repo-structure CI 门）
  ├─ PR #40  HOTFIX 000  ← 本会话产出，已合并（merge f9a00de2）
  └─ PR #38  Desktop release 001（Windows RC）← 并行操作者
```

### 分支 / PR

| 分支 | Head（remote） | PR | Base | 状态 |
| --- | --- | --- | --- | --- |
| `codex/hotfix-000-measurement-correctness` | `072822b1` | **#40** | main | ✅ **MERGED** |
| `codex/ecosystem-001-capability-map` | `7dcd3b36` | #41 | main | OPEN |
| `codex/ecosystem-002-capability-registry` | `da31b7da` | #42 | main | OPEN |
| `codex/ecosystem-003-provider-router` | `96096b4f` | #43 | **002 分支** | OPEN（栈式） |
| `codex/project-model-001` | `4aba0f53` | #44 | main | OPEN |
| `integration/agent-foundation-001` | `2e90eecf` | — | — | 已推送，标注 **verification-only** |
| `ci/temporal-texture-audit` | `07ef2cc6` | — | — | 已推送，**无 PR** |

**注意两件事：**

1. **`origin/main` 已两次前进**（`5fc74d24` → `1dd5b2e1`），且**并行操作者把 main 合进了我的 hotfix 分支**（`072822b1`）后才合并 PR。我推送的 `f9c7e348` 已被其覆盖 —— 内容一致，但**这个分支现在不代表我推的东西**，它已经是 main 的一部分了。
2. **PR #41–#44 现在都落后于 main**（基于 `01edc902`）。合并前需要 rebase 或让 GitHub 处理。

---

## 四、每一层的要点

### HOTFIX 000 — 测量正确性（已进 main）

四个缺陷，根因是两个：

| | 缺陷 | 根因 |
| --- | --- | --- |
| **F1** | 立体声 `integrated_lufs` 低 3.0103 dB | BS.1770 要求通道功率**求和**，代码**除以了通道数**。**单声道时除数是 1，所以完全隐身** |
| **F2** | `sample_peak_dbfs` / `rms_dbfs` 走单声道下混 | 同报告的 `true_peak_dbfs` 却是逐通道的 —— 一份报告混两种信号域 |
| **F3** | `CREST_FACTOR_COLLAPSE` 误报 | 不是独立 bug：F2 凭空造出约 3 dB crest factor |
| **F4** | 桌面静默回退系统 Python | 缺依赖被伪装成 numpy/pandas ABI 崩溃 |

**为什么能溜过去（最该记住的一条）：** `test_measurement_correctness.py` 里**每条 oracle 测试都用单声道 fixture** —— 单声道下两个缺陷在数学上都不可见。而且其中一条测试**断言 stereo == mono，把 bug 编码成了「立体声恒等式」**。

**验证：** 48 kHz 三方一致 —— 本实现 −11.950 / pyloudnorm −11.992 / ffmpeg ebur128 −12.0。

### ECOSYSTEM 001 — 能力生态地图（docs only）

**核心结论：Moodify 的 CANONICAL 强项集中在「信任层」（测量/证据/溯源/验证），缺口集中在「内容引擎」（转写/结构/修复）。** 策略要求它在这两处做相反的事。

外部调研印证了论点：**Demucs 原 repo 已进有限维护**（维护线是作者 fork v4.1.0，推理已移除 torchaudio）、**madmom PyPI 约 8 年未更新且权重禁商用**、**MSAF 在现代 SciPy 上导入失败**。三条都指向同一个答案：别把引擎焊进核心。

### ECOSYSTEM 002 — Capability Registry 0.1

`moodify.capabilities/0.1`。**纯元数据：不执行、不联网、不加载模型、不加依赖。**

三个设计判断值得记：

- **`status` 与 `strategic_posture` 是两个正交轴** —— `ABSENT + INTEGRATE` 完全合法。
- **`code_license` 与 `weights_license` 分开**，且三种状态必须区分：已声明 / `UNKNOWN`（有权重但条款未核实，是**风险不是许可**）/ `None`（根本不涉及权重）。
- **重复列表项是拒绝,不是去重** —— 静默折叠是一次修复,而被修复过的声明没人能审计。（这一条是我自己先写错、被自己的测试抓出来的。）

**21 个能力 + 9 个 provider。9 个能力完全没有 provider** —— 这是注册表在干活:把缺口变成一等、可查询的事实。

### ECOSYSTEM 003 — Provider Router 0.1

**`policy filters truth first, preference only ranks what remains.`**

- 硬约束消除、软偏好只排序。`privacy=LOCAL_ONLY` + `preferred=[lalal]` **不得**选中云 provider。
- **默认只收 `ACTIVE`**；`UNAVAILABLE`/`DEPRECATED` **没有开关**（声明说它已不可用，这不是偏好问题）。
- **显式正向要求绝不被 `UNKNOWN` 满足。**
- 排序末位是 `provider_id` 字典序 —— 显式、有文档、**全序**。
- **路由理由与执行失败码是两套词汇**：「被策略排除」和「崩了」是不同事实。

### Project Model 0.1（PR #44）

**用户源文件只读**；拷贝其字节并记录副本摘要；重开时重新校验,**不匹配就响亮报错,绝不静默改哈希**。路径穿越两层防御,第二层用 **resolve + 真包含判断**,所以 `project_x_evil` 不会被误认作 `project_x`。

### INTEGRATION 001

五层**零冲突**合并；每道门在合并后的树上都绿。

---

## 五、门汇总（数字核对过）

| 门 | 结果 |
| --- | --- |
| 全量核心套件（五层合并后） | **1391 passed / 6 skipped / 0 failed**（7:22） |
| 算术 | main 基线 1184 + 20 + 88 + 56 + 43 = **1391** ✓ |
| ruff | All checks passed |
| 桌面 `npm test` | exit 0 |
| repo-structure guard（PR #37 新增的门） | OK（1557 files, 6 checks） |
| 跨层导入 | **无循环依赖**；无隐藏引擎耦合 |
| **temporal-texture** | **fail —— 既有的、坏的,详见第八节** |

> 1391 这个数字是在 `5fc74d24` 基线的集成分支上测的。main 此后又吸收了 HOTFIX 000 与桌面发布,数字会有变化,但**五层本身无回归**这一结论不变。

---

## 六、最值得记住的六条

1. **`文件存在 ≠ 能力存在`。** `tempo_bpm` 有声明、有序列化、有测试,**生产代码 0 个生产者**;`StructureContext` **0 个构造点**。`auditory/inventory.py` 自己的分类表列了 **6 个 main 上不存在的模块**。

2. **一个测量工具返回「貌似合理但错误」的数字,比它跑不起来更危险。** 而它之所以能溜过去,是因为 oracle 测试集只覆盖了单声道。

3. **声明表才是权威。** `measurement_registry_v1.yaml` 本来就写着 `max(|x|)`、`sqrt(mean(x^2))`、`full-signal RMS` —— 是**代码违反了自己的登记表**。所以 HOTFIX 000 不需要改 registry 或 provenance。

4. **引用文档里的数字前先自己测一遍。** 我曾把 docstring 里一个**从未被测量过**的「error < 0.1 LU」照抄进交付报告;实测是 48 kHz 0.043、44.1 kHz 0.150。

5. **栈式 PR 不能假设改基后自动成立。** 003 含 002 是**按祖先关系**验证的(`git merge-base --is-ancestor`),不是靠文件名。合并顺序 **#40→#41→#42→#43→#44**,**#43 绝不能早于 #42**。

6. **基线是证据,不是许可。** 见第八节。

---

## 七、需要人决定的事

| # | 事项 | 为什么不是我能定的 |
| --- | --- | --- |
| 1 | **temporal-texture 的 109 个 error 级发现**：接受还是修？ | 这是关于「可接受代码质量」的政策决定。重生成基线等于把它们追认为已接受欠债 |
| 2 | **temporal-texture 是否作为合并门槛** | 它现在在 main 上就是红的,不是一个有效信号 |
| 3 | **PR #38（桌面）/ #39（Linux）的时序** | 并行操作者的工作线,不在本会话范围 |
| 4 | **是否给 `ci/temporal-texture-audit` 开 PR** | 目前这份审计**没有任何评审者能在 GitHub 上看到** |

---

## 八、挡在所有合并前面的事：temporal-texture

**它不是一个「我们的 PR 引入的」问题。** 复现过的事实:

```text
在 main 本身上跑 CI 的确切命令 →  exit 1
  (在 5fc74d24 上: new=200, new_errors=21, resolved=191)
  (在 1dd5b2e1 上: new=213, new_errors=21, resolved=192)   ← 最新 main 仍然红
```

- 运行史 **52 失败 / 9 成功**,且**全部 9 次成功都在 2026-08-08/09**（workflow 刚诞生）;
- 该 workflow **只在 `pull_request` 触发,从不在 main 上跑**;
- 基线内容生成于 **2026-08-20**,此后 main 落了 **273 个提交**,**没有任何东西刷新它**;
- **五分之四的规则把行号嵌进了 fingerprint** —— 在长行上方插一行注释,就会让该文件所有同类 finding 变成 new;
- **21 个 error 里 0 个落在本会话任何分支触碰过的文件里。**

**结论 `CI_TOOLING_BROKEN`:** 这个门现在分不清自己的基线和被审查的分支,所以 `red` 不携带关于变更的信息。

**我本可以用一条命令让它变绿,我没有跑那条命令** —— 那需要先把 109 个 error 追认为已接受欠债,而 §13 明确要求这件事停下来交给人类。

**建议顺序:** ①人对那 109 个做决定 → ②修 fingerprint **并同批**从记录过的干净 commit 重生成基线 → ③补契约测试 → ④加 `push: branches: [main]` → ⑤此后才可作合并权威。

---

## 九、事实边界

**我没做：** 未合并任何 PR、未推送 main、未改动任何 CI 文件、未修 109 个 error、未实现任何 provider、未开始 ECOSYSTEM 004 / Provider Certification / Sound Protocol 0.3 / Production Graph / CLI 2.0。

**未验证：** 桌面 GUI 渲染（本会话早期的验收里四种截图方法全部失败,只能记「未验证」）;真实听感;`ci/temporal-texture-audit` 分支上报的那份审计**没有 PR,无人评审**。

**有时效性：** ECOSYSTEM 001 的外部调研采集于 **2026-10-04**。该领域的引擎生命周期以月计（Demucs/madmom/MSAF 三例即为证）,外部那部分**有明确保质期**。

**并行操作风险：** 本会话期间至少有一次并行的 main 推进与一次对我分支的推送。**任何交接前都应重新核对 hash,不要相信本报告里的数字仍然成立。**

---

## 十、建议的下一步

```text
1. 人对 temporal-texture 的 109 个 error 做决定          ← 唯一真正的阻塞点
2. 合并 #41（docs only，可随时合并）
3. 合并 #42，然后 rebase 003 → 改指 #43 base → 重跑测试 → 合并 #43
4. 合并 #44
5. 此后才谈 ECOSYSTEM 004 / Provider Certification
```

第 3 步里 **rebase 后必须重跑注册表 + 路由 + 全量测试** —— 不要假设栈式 PR 改基后自动成立。
