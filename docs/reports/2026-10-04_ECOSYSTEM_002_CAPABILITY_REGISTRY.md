# ECOSYSTEM 002 — Capability Registry 0.1 执行报告

> **任务：** ECOSYSTEM 002 — Capability Registry 0.1
> **分支：** `codex/ecosystem-002-capability-registry`（基于 `main` `01edc902`）
> **提交：** `94beccacbe475f1ee8814d9d4c3668ee0e75fb9a`
> **日期：** 2026-10-04
> **依赖：** ECOSYSTEM 001（作为**输入阅读**，非作为分支基线 —— 见 §1）
> **参考文档：** `docs/ecosystem/MOODIFY_CAPABILITY_REGISTRY_0_1.md`（词汇表、ID 规则、API、快照格式）

---

## Summary

实现了 `moodify.capabilities/0.1` —— 稳定、与 provider 无关的能力 ID、provider 声明、共同失败词汇与确定性发现接口。

**纯元数据。** 不执行、不路由、不动态导入、不联网、不加载模型、不加依赖。它在软件层面回答一个问题:

```text
Moodify 概念上能做什么，谁来实现它，什么会失败？
```

实现的规则:**模型会换,能力留下。** `stem.separate` 在 Demucs 被替换后依然存活;`demucs.separate` 不会。

---

## 1. 分支基线决策（§3）

任务书 §3 要求「不得静默依赖未合并的本地分支」,并点名 `codex/project-model-001`。

先核实了基线状态:

```text
$ git merge-base --is-ancestor 4aba0f53 main
→ 非零退出（project-model 不在 main）

$ ls moodify-core-package/src/moodify/project/*.py
→ No such file or directory
```

因此**从 `main` (`01edc902`) 切出新分支**,而不是从 `codex/ecosystem-001-capability-map` 或 `codex/project-model-001`。

**直接后果,已写进代码与文档:** 本包**不 import `moodify.project`**(§29)。`project` 只作为概念性 `IOType` 出现。任何对 Project Model 的依赖都会在 main 上直接 ImportError,而这个包必须在 main 上成立。

**一处需要交接的副作用:** `docs/ecosystem/` 目录是在 001 分支上创建的;本任务的文档落在同一目录、但基于 main 的新分支。两个分支合并后目录才完整 —— 这不是缺陷,是本任务遵守 §3 的必然形态。

---

## 2. 证据复核（§22）—— 不照抄 ECOSYSTEM 001

任务书明确要求重新核对仓库证据,不得盲目复制 001 的分类。逐能力复核结果:

| 能力 | 复核证据 | 判定 |
| --- | --- | --- |
| `audio.decode` | `auditory/decode.py` 存在 | CANONICAL |
| `audio.analyze` | `auditory/metrics.py` + `loudness.py` | CANONICAL |
| `audio.verify` | `mix_graph/verify.py` + `auditory/evidence/`(7 模块) | CANONICAL |
| `stem.separate` | LALAL 客户端存在;**本地 DSP 脚本存在且已接线**;Demucs **仅 pyproject extra,无代码** | EXPERIMENTAL |
| `pitch.analyze` | `moodify_experimental/mamse002`(CQT) | EXPERIMENTAL |
| `rhythm.analyze` | `tempo_bpm` 3 处命中,其中**生产代码 0 个生产者** | PARTIAL |
| `structure.analyze` | `StructureContext` **生产构造点 0 处** | PARTIAL |
| `harmony` / `instrument` / `lyrics` | 各 0 命中 | ABSENT |
| `pitch.correct` / `timing.correct` | 0 命中 | ABSENT |
| `midi.transcribe` / `score.generate` | **核心无 import,仅桌面壳 CLI 调用** | IMPLEMENTED_NOT_CANONICAL |
| `noise.reduce` | 显式路由到 `INTERVENTION_NOT_SUPPORTED_V0_1` | ABSENT |
| `clipping.repair` | `intervention/primitives.py` | IMPLEMENTED_NOT_CANONICAL |
| `mix.render` / `master.render` | `mix_graph` 自述 EXPERIMENTAL;`v01_*` 为遗留 | EXPERIMENTAL |
| `delivery.export` | `v01_exporter.py` + `data_plane/delivery.py` | IMPLEMENTED_NOT_CANONICAL |

### 复核同时纠正了我自己探针的两处错误

| 我的初测 | 复核结论 |
| --- | --- |
| 「本地 DSP 分离脚本 MISSING」 | **错** —— 是我 grep 的相对路径写错了。`moodify-desktop/scripts/dsp_separate.py` 存在(4341 字节),且 `main.js:595-596` 确实接线调用它 |
| 「`tempo_bpm` 3 处」 | 精确化:2 处在 `structure.py`(声明 + 序列化),**第 3 处是测试夹具**(`test_ch02_phase1_evidence.py:211`)。**生产代码 0 个生产者**这一结论不变,但计数要说准 |

第二条尤其值得记:ECOSYSTEM 001 报「2」,我的探针报「3」,差异来自**测试夹具算不算生产者**。正确答案是**不算** —— 一个只被测试构造的类型,仍然是没有生产者的类型。这个区分写进了 `notes`。

### 一处与 ECOSYSTEM 001 的刻意分歧

| | ECOSYSTEM 001 | 本任务 | 理由 |
| --- | --- | --- | --- |
| `master.render` | LEGACY（v01 路径） | **EXPERIMENTAL** | **能力本身是当下有效的,只有 v01 *实现路径*是遗留的。** LEGACY 应描述「能力本身属遗留」的场合。桌面壳当前走 v01 这一事实,写进了该能力的 `notes`,而不是用它污染 status |

这是 §7 里「自己推翻自己」的正当压力测试产物 —— §22 存在的意义就是让分类被重新论证一次,而不是继承。

---

## 3. 实现中的三个设计判断

### 3.1 status 与 strategic_posture 是正交的两个轴

任务书 §9 已经点明,实现时把它推到底:`ABSENT` + `INTEGRATE` 完全合法 —— 「今天没人实现」与「我们打算包一个外部引擎」是**关于同一能力的两个不同事实**。

`timing.correct` 是最清楚的例子:`ABSENT` + `DEFER` —— 没人实现,且我们刻意不 pursue。

### 3.2 `LEGACY` / `DEFERRED` 定义了但种子里未使用 —— 这是刻意的

status 枚举 7 个值,种子只用到 5 个。**我没有为了「用上枚举」去编一个 LEGACY 分类。**

在一个以「不伪造事实」为立身之本的系统里,枚举覆盖不全不是缺陷,把现实硬塞进枚举才是。「不 pursue」由 `posture = DEFER` 表达,不需要 status 也假装改变。这条判断写进了参考文档,以免后人以为漏了什么。

### 3.3 重复列表项:拒绝,而不是去重

**这一条是我自己先写错、被自己的测试抓出来的。**

我最初对 `failure_codes` / `input_types` / `output_types` 用了 `tuple(dict.fromkeys(value))` —— **静默去重**。测试 `test_duplicate_list_entries_are_rejected` 失败了,暴露出这正是 §25 明令禁止的「silently repair declarations」。

改为 `_require_unique()` 抛错。理由值得留在代码注释里:

> 静默折叠一次重复是**一次修复**,而被修复过的声明**没人能审计**:作者的意图丢失了,遗漏对下游不可见。

---

## 4. Capability IDs

`domain.operation`,恰好两段,`[a-z][a-z0-9_]*`。**拒绝版本样片段**(`stem.v2` 即使语法通过也拒),因为版本是**契约修订**,不是新能力。

种子 21 个:

```text
audio.decode  audio.analyze  audio.verify  audio.convert  metadata.read
stem.separate
rhythm.analyze  harmony.analyze  structure.analyze  instrument.identify
pitch.analyze  pitch.correct  lyrics.align
midi.transcribe  score.generate
clipping.repair  noise.reduce  timing.correct
mix.render  master.render  delivery.export
```

### 诚实边界(必须记下来)

**ID 格式检测不出厂商名。** `demucs.run` 与 `ffmpeg.convert` 是**语法合法**的。它们不是能力,只因为注册表**没有声明它们** —— 那是架构决定,不是语法决定。

测试 `test_provider_named_capabilities_are_wellformed_but_absent` 把这条边界**显式记录**下来,断言这些 ID 能通过校验、同时 `has_capability()` 返回 False。**不写成断言,读者会以为校验器覆盖了它。**

---

## 5. Status Classification

| Status | 数量 |
| --- | ---: |
| `CANONICAL` | 3 |
| `IMPLEMENTED_NOT_CANONICAL` | 4 |
| `PARTIAL` | 4 |
| `EXPERIMENTAL` | 4 |
| `ABSENT` | 6 |

**9 个能力完全没有 provider** —— `rhythm.analyze` / `structure.analyze` / `pitch.analyze`(有类型无生产者),加 6 个 `ABSENT`。

这是注册表在干活:**它把缺口变成一等、可查询的事实**,而不是一个靠假设填补的空白。每条声明的 `notes` 带上判定依据,读者可复核而不是只能信。

---

## 6. Providers

9 个:`moodify.auditory` · `moodify.intervention` · `moodify.mix_graph` · `moodify.release` · `moodify.preview_separation` · `ffmpeg.system` · `lalal.cloud` · `basic_pitch.local` · `music21.local`。

构造时拒绝三类不一致:重复 ID、悬空引用、**双向不对称声明**(能力列了 provider 但 provider 没回列)。第三条最有价值 —— 两份声明**各自都合法**,只有注册表的交叉检查能发现它们互相矛盾。

---

## 7. Failure Vocabulary

15 个码,含全部 11 个必需项。**4 个可选码各有仓库依据,不是为对称性凑数:**

| 码 | 仓库依据 |
| --- | --- |
| `CONFLICT` | `auditory/evidence/conflicts.py` 已在显式建模矛盾证据 |
| `INTEGRITY_ERROR` | 内容全程 sha256 校验(证据、项目源、节点摄取) |
| `CANCELLED` | 长任务可取消(桌面单飞锁、节点队列) |
| `TIMEOUT` | 与 `RESOURCE_LIMIT` 区分:用时超限 ≠ 资源耗尽 |

`Failure.of()` 从规范表推导 `retryable`,两者不会漂移。`NOT_IMPLEMENTED` / `INVALID_INPUT` / `UNSUPPORTED_FORMAT` **不可重试** —— 重试一个确定无效的相同请求不是恢复策略。

---

## 8. License Metadata

`code_license` 与 `weights_license` **是两个字段**。三种状态必须区分:

| 值 | 含义 |
| --- | --- |
| `"MIT"` / `"Apache-2.0"` | 已声明许可 |
| `"UNKNOWN"` | 有权重但条款**未核实** —— **是风险,不是许可** |
| `None` | **根本不涉及权重** —— 系统二进制、云 API、纯算法 |

`ffmpeg.system` 的 `redistribution` 记 **UNKNOWN** 并说明理由(取决于用户 ffmpeg 的构建配置;Moodify 消费系统二进制、不分发),而不是猜一个值 —— 注册表的价值恰恰在于**把未决的许可问题暴露出来**,而不是替它下结论。`lalal.cloud` 的 `commercial_use` 是 **RESTRICTED**。

无法律执行引擎,任务书 §18 也明确不要求。

---

## 9. Files Changed

```text
A  moodify-core-package/src/moodify/capabilities/__init__.py    (133)
A  moodify-core-package/src/moodify/capabilities/failures.py   (137)
A  moodify-core-package/src/moodify/capabilities/models.py     (305)
A  moodify-core-package/src/moodify/capabilities/registry.py   (193)
A  moodify-core-package/src/moodify/capabilities/builtin.py    (549)
A  moodify-core-package/tests/test_capability_registry.py      (543)
A  docs/ecosystem/MOODIFY_CAPABILITY_REGISTRY_0_1.md           (328)
```

+2188 行,**7 个新文件,未改动任何既有代码文件**。

---

## 10. Tests

```bash
$ python -m pytest tests/test_capability_registry.py -q
88 passed

$ python -m pytest -q
1272 passed, 6 skipped, 56 warnings in 517.52s (0:08:37)

$ python -m ruff check src/moodify/capabilities/ tests/test_capability_registry.py
All checks passed!
```

**无回归的算术核对:** `main` 基线 1184(见 HOTFIX 000 报告)+ 88 新测试 = **1272** ✓。6 个 skip 与改动前完全一致,均为既有环境条件性跳过。

**§36 验收示例逐字通过。**

**副作用确认:** 导入本包**不拉入任何引擎**。探针显示 numpy 出现在模块集合中,已核实其来源是父包 `moodify/__init__.py` 的既有 eager re-export(`data_types` / `uncertainty` / `protocol` / `fingerprint` / `conservation` / `icc`),**非本包引入** —— 裸 `import moodify` 就会拉 numpy。

**测试自我修正记录:** 初版 5 个失败,其中 1 个是真实代码缺陷(§3.3 的静默去重),2 个是我的测试辅助函数在到达注册表之前就触发了模型自身的约束,1 个是 `is not` 被用于字符串身份比较(字符串驻留使其恒为 False)。**全部记在这里,而不是悄悄修掉。**

---

## 11. Compatibility

```text
NO — metadata/discovery only
```

未改动任何既有运行时行为。具体:

| 项 | 状态 |
| --- | --- |
| `auditory/inventory.py` | **原样保留,未删未改**(§35) |
| 既有测试 | 全绿(1272) |
| 依赖 / 构建文件 | pyproject / requirements / package.json / Dockerfile **未动** |
| CLI | 未加任何命令 |
| Sound Protocol | 未启动 0.3 |
| Production Graph | 未启动 |
| GUI / 桌面 | 未改动 |

### §35 的核查结论

`auditory/inventory.py` **无任何外部引用** —— `src/`、桌面壳、`ops/`、`tests/` 都不 import 它。它是一个**扫描文件系统**做分类的工具,其映射表列了 `capability_registry`、`transcription`、`score_engine`、`adapters`、`ports`、`storage` —— **这 6 个模块在 main 上都不存在**。

它假设「**模块存在 → 能力存在**」,而这正是本注册表要替换掉的推断方式。**它的陈旧是这个假设的必然结果,不是一次疏忽。** 参考文档里用对照表记录了这一点,并把它定位为「专门的、遗留的审计工具」,而非被取代后应删除的东西。

---

## 12. Deferred

provider 执行 · provider 路由 · 动态安装 · CLI 2.0 能力命令 · Sound Protocol 0.3 · Production Graph · Project Model 集成 · 第三方 provider 注册 · GPU / 权重下载 · 法律执行引擎。

**一个设计上的延后,记录理由:** `Provider` 目前**要求至少声明一个能力**(零能力的 provider 无意义)。但「provider 已存在、其全部能力尚未声明」这个中间态**没有被建模**。等 router 出现、真的需要表达「已安装但未声明」时再决定加什么,现在加就是投机。

---

## 13. Next Recommended Task

### Provider Router 骨架（元数据层，不含执行）

**理由:** 注册表回答了「有什么」,router 回答「谁来干」。它是 ECOSYSTEM 001 §9 **反锁定规则真正变得可执行**的地方 —— 今天那些规则还只是文档里的原则。

它能纯离线、无 GPU、无许可证风险地完成,因为选择策略的输入**现在全都已经在注册表里了**:`locality`、`determinism`、`commercial_use`、`status`、`execution_mode`。

**明确不推荐先做** Demucs 集成:它吃 GPU、许可证一团乱(madmom/Open-Unmix 权重禁商用、BS-RoFormer 许可不明),而且**需要先有 router 才能被选中**。也**不推荐**先做 CLI 能力命令:它需要先定 Sound Protocol 0.3 的请求形状,否则是把接口建在不稳定的数据结构上 —— 这正是 TASK 001 当初「模型先行、接口其次」的同一条理由。

---

## 14. Commit

```text
94beccacbe475f1ee8814d9d4c3668ee0e75fb9a
feat(capabilities): add the canonical capability registry 0.1
```

分支 `codex/ecosystem-002-capability-registry`,基于 `main` `01edc902`,**已提交未推送**,工作区干净。

### 会话内其余未推送分支（交接参考）

```text
codex/project-model-001           4aba0f53                  TASK 001 Project Model 0.1
codex/hotfix-000-measurement-...  ca0c4805 → f9c7e348       HOTFIX 000（含报告）
codex/ecosystem-001-capability-…  347f6ef8 → 7dcd3b36       ECOSYSTEM 001（地图 + 报告）
codex/ecosystem-002-capability-…  94beccac                  ECOSYSTEM 002（本报告）
```

**四条分支各自从 `main` 切出,互不依赖。** 唯一需要留意的合并顺序:`docs/ecosystem/` 目录由 001 创建,002 的文档落在同目录 —— 两条都合并后目录才完整。

---

## 15. 小结:这次实现验证了什么

任务书 §40 的两句话是这次工作的检验标准:

> **一个能力属于 Moodify,是因为 Moodify 显式声明并约束它 —— 不是因为一个名字好听的模块文件恰好存在。**

这一点不只体现在「不扫描文件系统」这条禁令上,更体现在**分类本身**上:`tempo_bpm` 有声明、有序列化、有测试,仍然被判 `PARTIAL`,因为**生产代码里没有生产者**。`auditory/inventory.py` 有文件、有完整分类表,仍然被判定为不能作为能力真相的来源。

> **provider 实现可以消失。capability ID 必须比它们活得久。**

结构上,这一点由三样东西保证:provider 与 capability 的双向一致校验、`provider_ids` 与 `capability_ids` 分离、以及 Production Graph 将继承的规则 —— **图节点引用 `capability_id`,永不引用 `provider_id`。**
