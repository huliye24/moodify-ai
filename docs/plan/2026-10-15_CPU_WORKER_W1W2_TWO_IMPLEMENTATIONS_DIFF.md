# CPU Worker W1/W2 —— 两版实现逐项差异对照

- 日期：2026-10-15
- 状态：**RESOLVED —— 已裁决，见文末 §8 裁决记录**
- CANON_CHANGE：**NO**
- 依据方案：`docs/plan/2026-10-15_CPU_FIRST_CLOUD_EXECUTION_PLAN.md` §4 W1/W2
- 生成时**未写任何代码、未部署、未触碰宁夏节点**；§8 之后的实施按裁决顺序另提交

```text
Decision: RESOLVED
Canonical source: ops/cloud_worker/
Contract authority: JSON Schema
Lifecycle values: lowercase
Error codes: uppercase canonical codes
Probe: ffprobe infrastructure adapter
Analyze: Moodify Core only
External deploy/: generated deployment mirror
```

> 本文件先作为**调查证据**提交（不含任何一版实现的代码）。契约冻结、队列语义修正、
> 测试补齐、镜像生成各自独立提交，顺序见 §8。

---

## 0. 问题是什么

### 0.1 直接问题：同一个工作包被两个会话各做了一遍，产出不兼容

方案 §4 的 W1/W2 是同一个任务，2026-10-15 下午被**两个会话并行执行**：一个把源码落在
仓库 `E:/moodify-cloud/ops/cloud_worker/`，另一个落在仓库外 `E:/亚马逊云/宁夏CPU节点/deploy/`。
两边各自写完了作业契约、worker、adapter/handler 与测试，**两边测试都全绿**，但**两边互不兼容**。

于是现在没有"哪一版还没做完"的问题，只有"哪一版是权威"的问题 —— 而在这道题被回答之前：

- 无法提交 W2（提交哪一份？）
- 无法做 W3 冒烟（跑哪一份？）
- 无法开始 W4（Studio 要对哪一套 JSON 写代码？）
- `deploy/` 与仓库两处会继续各自漂移，第三个会话接手时面对的是三份状态

**另有一个具体的破坏风险**：本会话写的 `ops/cloud_worker/scripts/mirror.py`（按人类先前决定，
把仓库镜像到 `deploy/`）一旦执行，会**删除另一版 10 个文件**。已 `--dry-run` 确认，**未执行**。

### 0.2 实质问题：五个必须先回答的分歧

不是风格差异，是"回答不同、后面代码就不同"的分歧，按代价从大到小：

| # | 问题 | 两种答案的后果 |
| - | --- | --- |
| 1 | **状态与错误用什么词汇表？** `DONE/FAILED/INCONCLUSIVE/HUMAN_REQUIRED` + 12 个错误码，还是 `done/failed/inconclusive/human_required` + 8 个错误类？ | W4 的 Studio 要按其中一套写 JSON、解析状态、渲染 UI。一旦有任务进队列或结果落盘，再改就是**改协议**，不是改代码 |
| 2 | **契约权威归谁？** 归 JSON Schema（两侧都加载它），还是归 Python 代码（schema 只是"规范性定义"、靠人手工保持一致）？ | 后者目前**没有任何测试断言两者一致**，漂移不会被发现 |
| 3 | **`analyze` 是否必须在 W3 跑通？** | 若是 → W3 之前必须先在节点装 Core（本会话第二问的答案是"先不动节点"，该路径当前**被阻塞**）；若否 → W3 的验收范围要相应收窄，方案 §4 W3.2 点名的三种任务降为两种 |
| 4 | **`probe` 走 Core 还是走 worker 自解析 ffprobe？** | 决定节点是否**强依赖 Core**：走 Core → 节点没装 Core 就什么都跑不了；自解析 → 不装也能跑，但 Worker 里多了一份 Core 已有的测量语义 |
| 5 | **源码落在哪？** 仓库内（可评审、可 CI、有 diff 历史），还是 `deploy/`（方案 §6.2 原话）？ | 两版各自遵循了不同的指令，其中一条指令是过期的 |

### 0.3 一句话结论

两版**都覆盖了 W1 的六类验收用例**，且**两版测试都全绿** —— 所以这不是"谁做错了"，
而是**两套自洽的取舍撞在一起，必须选一套当权威**。上面五个问题里，第 3 个还牵出一个
方案本身的缺口：**§1 的实测清单没有记"节点没装 Moodify Core"**，而它是 W2「让 worker
调用唯一 Core」与 W3 `analyze` 冒烟的共同前提（见 §1）。

**在 0.2 的五问被回答之前，W3/W4/W5 无法开工。**

---

## 1. 事实与状态（截至 2026-10-15 18:20）

| 项 | A 版（本会话） | B 版（并行会话） |
| --- | --- | --- |
| 位置 | `E:/moodify-cloud/ops/cloud_worker/`（**仓库内**） | `E:/亚马逊云/宁夏CPU节点/deploy/`（**仓库外**） |
| 版本控制 | W1 已提交 `eda7fe6e`；W2 未提交 | **全部未提交**（`git log --all --since` 只有 A 版那一条） |
| 分支 | `codex/cloud-workspace` | 无 |
| 单元测试 | `pytest`，**101 passed** | `python test_*.py`（unittest），**21 + 12 = 33 passed** |
| 测试依赖 | 需 `pytest` + `jsonschema` | **零第三方依赖**（标准库 + 本地 Fake S3） |
| 落点决定 | 依人类 2026-10-15 选择「源码进仓库」 | 依方案 §6.2「本地权威副本在 deploy/」 |
| 活动状态 | 已停手等裁决 | 18:16、18:18 仍在写；`tests/test_worker_flow.py` 是调查过程中新出现的 |

**时间线**：W0 基线 18:01（第三方会话）。A 版 18:02 起做 W1、W2。B 版 18:07–18:18 写
`lib/job_contract.py` / `handlers.py` / `s3queue.py` / `bin/worker.py` / 两个测试文件。

**已发生的未遂破坏**：A 版的 `ops/cloud_worker/scripts/mirror.py`（把仓库镜像到
`deploy/`）`--dry-run` 显示会**删除 B 版 10 个文件**。该脚本**未执行**，B 版文件完好。

---

## 2. W1 六类验收用例覆盖度

| # | 用例 | A 版 | B 版 |
| - | --- | --- | --- |
| ① | 合法 | ✅ 默认值补齐 + 不改调用方对象 + 6 种 job_type 全通过 | ✅ `test_valid_job_passes` / `test_all_job_types_accepted` |
| ② | 缺字段 | ✅ 7 个必填字段参数化 + 嵌套缺字段 + 未知顶层键 | ✅ 9 个必填字段逐个点名 |
| ③ | 未知 job_type | ✅ 独立错误码 `UNKNOWN_JOB_TYPE`（与「缺字段」分得开） | ✅ `test_unknown_rejected` |
| ④ | 重复 request_id | ✅ 幂等索引 + 别名写入 + 索引错配判 INTERNAL_ERROR | ✅ `dedupe_key` 稳定 + worker 级「只下载一次」 |
| ⑤ | 哈希不符 | ✅ `check_input_hash` + 大小写/长度在 schema 层拦 | ✅ `verify_input_hash` |
| ⑥ | 超限输入 | ✅ 下载前 `HeadObject` 预检，不拉文件 | ✅ `check_limits`（下载后校验） |

**结论：六类用例两版都真实覆盖，不存在「谁没做验收」的问题。** 差异在通过之后的取舍。

---

## 3. 逐项差异（按对后续阶段的影响面从大到小）

### 3.1 `analyze` / `judge_before` 是否可用 ← 影响最大

| | A 版 | B 版 |
| --- | --- | --- |
| 实现 | 接到 Core 的 MSP 0.2 analyze（`moodify.sound_protocol.execute_job`，与 `moodify protocol process` 同一函数） | 无条件 `CoreUnavailable`（桩） |
| 状态映射 | Core 的 `workflow_decision` → 状态；认不出一律 `INCONCLUSIVE`，**绝不默认放行** | 无 |
| W3 后果 | `analyze` 冒烟**可以**跑（前提：节点装了 Core） | `analyze` 冒烟**必然失败**，方案 W3.2 要求的三种任务少一种 |

**共同前提两版都没写进方案**：节点 `/home/ubuntu/moodify-lab/.venv` 里**没有装 Moodify Core**
（`ModuleNotFoundError: No module named 'moodify'`，2026-10-15 实测）。方案 §1 的实测清单里
没有这一条。B 版据此把三个 Core 任务全做成桩；A 版按 W2.3 的意图实现，因此**必须先装 Core**。

### 3.2 契约权威归谁

| | A 版 | B 版 |
| --- | --- | --- |
| 权威 | **JSON Schema**；`contract.py` 只是加载器，两侧（JS/Python）读同一份文件 | **`lib/job_contract.py` 代码**；JSON Schema 自称「规范性定义」，其描述里写明「两者必须保持一致」 |
| 防漂移 | schema 被测试加载并校验结果，漂移会直接测红 | **无任何测试断言 schema 与代码一致** |
| 严格度 | `additionalProperties: false`（拼错键报错） | `additionalProperties: true`（顶层宽进） |
| 生产者/传输字段 | 显式区分 `RUNTIME_KEYS`（`claimed_at`/`worker_id`/`attempt`…），校验前摘除后再放回 | 无此概念（顶层宽进，天然不冲突） |

### 3.3 `probe` 算不算「调用 Core」

| | A 版 | B 版 |
| --- | --- | --- |
| probe | `core_entry.py probe` → `moodify.auditory.decode.probe`（Core 已有该函数，返回 sha256/时长/编码/采样率/声道/位深/声道布局/容器/字节数） | **worker 自己解析 ffprobe JSON**，只取时长/编码/采样率/声道 |
| transcode 输出校验 | 转码前后各调一次 Core probe 比时长漂移 | worker 自己再调 ffprobe 量时长 |

B 版 `handlers.py` 的文件头写着「不在 worker 里自造处理逻辑」，但 probe 与 transcode 的
度量确实是 worker 侧重新实现的。这是方案 §4 W2.1「让 Worker 调用 Core，而不是自造处理逻辑」
要拦的那一类；**但它同时是一个真实的工程取舍**——Core 没装时，B 版的 probe/transcode **仍能跑通**，
A 版不能。

### 3.4 状态与错误词汇表 ← W4 的隐形成本

| | A 版 | B 版 |
| --- | --- | --- |
| 状态 | 大写 `DONE` / `FAILED` / `INCONCLUSIVE` / `HUMAN_REQUIRED` | 小写 `done` / `failed` / `inconclusive` / `human_required` |
| 错误分类 | 12 个错误**码**（`INPUT_HASH_MISMATCH`…）+ 独立 retryable 映射表 | 8 个错误**类**（`validation`/`hash_mismatch`/`transient`…）+ `_RETRYABLE_BY_CLASS` |
| 非法对象 | 第三份契约 `moodify.cpu-reject/0.1` 退件单（明说「这不是结果」） | 归入 `failed(validation)` |
| 结果产物 | `outputs[]` 数组（每条带 role/sha256/bytes）+ `evidence[]` | 单个 `output_sha256` |

**这是最贵的差异**：W4（Studio 侧）要按其中一套写 JSON、解析状态、渲染 UI。
一旦有任务已经投进队列或已有结果落盘，改词汇表就是改协议。**上线前必须二选一。**

### 3.5 claim 非原子性：一个真值 vs 一个假不变量

| | A 版 | B 版 |
| --- | --- | --- |
| 测试 | `test_claim_order_creates_a_race_window`（断言动作顺序 get→put→delete）+ `test_two_workers_can_both_win_the_same_job`（**复现交错**） | `test_only_one_worker_claims`：`claim(A)` 后 `claim(B)` 返回 None，注释「第二个 pending 已删，抢不到」 |
| 性质 | 承认并演示竞争窗口存在 | 断言「只有一个 worker 抢得到」，但该结论**只在顺序执行下成立**，并行交错时两个都会成功 |

B 版这条测试把**非保证的属性写成了不变量**，与方案 §4 W2.5「保留 S3 claim 的非原子事实」相反。
测试本身不会失败，问题在于它会误导后续读者认为 claim 是原子的。

### 3.6 重试与崩溃恢复

| | A 版 | B 版 |
| --- | --- | --- |
| 退避 | 无显式退避，靠 poll 节奏 | ✅ `not_before` + `RETRY_BASE_SEC=30` 指数退避（30s/60s），**更好** |
| 重试上限 | `MAX_ATTEMPTS=3`，由 `attempt` 计数 | `MAX_RETRIES=2`，由 `retry_count` 计数 |
| 回收计数 | 回收时 `attempt += 1`，用满即判死 | ⚠️ `reap_stale_claimed` **不动 `retry_count`**（`job.pop('claimed_at')` 后直接回 pending） |
| 后果 | 一个能让 worker 崩溃的任务最多被回收重跑到上限 | 一个能让 worker 崩溃的任务会被**无限回收重跑**（每次崩溃都在 `retry_count` 递增之前） |

### 3.7 幂等命中时「新 job_id 的答案」怎么写

| | A 版 | B 版 |
| --- | --- | --- |
| 做法 | 保留权威结果原文，另写一份带 `deduplicated_from: <原 job_id>` 的别名 | `mark_done(新 job_id, 既有结果)`，而 `mark_done` 会**改写 `job_id` 字段为新值** |
| 可追溯性 | 能追回原始 job_id | 结果自称由新 job_id 产出，但证据属于原 job_id，**无字段可追回** |

### 3.8 其余小差异

| 项 | A 版 | B 版 |
| --- | --- | --- |
| 本地盘护栏 | 轮询前检查，超限不认领 | 认领前检查，超限不认领（等价） |
| `--once` 语义 | 保留 + 新增 `--drain N` | 保留 |
| 跨平台 | `resource`/`os.uname` 有 Windows 守卫（本地可测） | 直接依赖 Unix（节点上无妨） |
| 测试框架 | pytest（需装） | unittest（零依赖） |

---

## 4. 对 W3 / W4 / W5 的影响

| 阶段 | A 版赢在哪 | B 版赢在哪 |
| --- | --- | --- |
| **W3 冒烟** | `analyze` 能跑（装 Core 后）；`--drain 10` 一次跑完 10 个 | 不装 Core 也能立刻跑 `smoke`/`probe`/`transcode`；但方案 W3.2 点名的 `analyze` **恒失败** |
| **W4 Studio 接入** | 契约有单一权威文件，JS 侧可直接读 schema 校验 | 状态/错误词汇表更贴近「事件名」习惯，UI 映射可能更省事 |
| **W3 稳定性** | 回收有上限，坏任务不会无限重跑 | 指数退避更好，但回收无上限 |
| **W5 基准** | `probe`/`transcode` 走 Core，测量口径与全仓一致 | `probe` 走 ffprobe，口径与 Core 的 `probe()` 可能不同（Core 还多给位深/声道布局/容器） |

**对 W5 的一点具体提示**：方案 §7 要求「每个结果带输入/输出哈希、版本、参数、日志与 evidence」。
B 版结果是单 `output_sha256`，A 版是 `outputs[]` 数组；若一个任务产出多件产物（如 analyze 的
report 三件套 + 频谱图），B 版结构表达不了。这一条对 W5 的基准记录有实际影响。

---

## 5. 五个问题各自的证据在哪

问题清单只有一份，在 §0.2；本节只给每条问题的**原始证据位置**，避免两份清单各自漂移。

| 问题（§0.2 编号） | 证据 |
| --- | --- |
| 1 词汇表 | §3.4 —— 两版的常量表逐项对照 |
| 2 契约权威 | §3.2 —— B 版 schema 描述里那句「可执行权威是 lib/job_contract.py，两者必须保持一致」；以及「无一致性断言」这一事实 |
| 3 `analyze` | §3.1 —— A 版接到 `moodify.sound_protocol.execute_job`；B 版 `_core_backed()` 桩；`ModuleNotFoundError` 实测 |
| 4 `probe` | §3.3 —— A 版 `core_entry.py probe`；B 版 `handle_probe` 内的 ffprobe JSON 解析 |
| 5 落点 | §1 表第二行 —— 两个目录、仓库内/外、提交与未提交 |

---

## 6. 两版各自已知缺陷（含本会话自己那版）

**B 版**
- `tests/test_job_contract.py::test_make_job_selfchecks` 与 `test_valid_job_passes` 断言**完全相同**，
  没有任何「自证」的检查，是一条不可能失败的测试。同仓历史上出现过同类问题（CODE_QUALITY 001）。
- `reap_stale_claimed` 不推进重试计数 → 崩溃型任务可无限重跑（§3.6）。
- `test_only_one_worker_claims` 把非保证属性写成不变量（§3.5）。
- JSON schema 与可执行代码之间**没有一致性断言**，描述里要求两者「必须保持一致」但无人检查。
- `handle_probe` 自造 ffprobe 解析，与自身文件头声明的纪律相悖（§3.3）。
- 结果结构无法表达多产物（§4）。

**A 版**
- `probe`/`transcode`/`analyze`/`judge_before` **强依赖节点已装 Core**，而 Core 当前没装 ——
  方案 §1 的实测清单里也没有这一条，是本次调查才发现的前置缺口。
- 重试退避粗糙（靠 poll 节奏），**不如 B 版的指数退避**。
- 多引入了一份契约文件（退件单 `cpu-reject/0.1`），表面更大。
- 状态用大写是**任意选择**，没有比 B 版更充分的理由。
- 测试需要 `pytest`/`jsonschema`，**不如 B 版零依赖**。

---

## 7. 事实边界（本对照表没有验证的东西）

1. **B 版仍在写入中**（18:18 仍在动）。本表基于 18:20 快照，之后可能已变。
2. 本表**未运行 B 版的端到端部署**，也**未在节点上跑过任何一版**。
3. **两版都未在宁夏节点上执行过**；W3 冒烟对两版都是空白。
4. B 版 `bin/worker.py` 我按函数结构与其自查输出阅读，**未逐行审**（完整 14626 字节）。
5. A 版 W2 未提交，B 版全部未提交 —— 两版都还没有可引用的 commit hash。
6. 「节点未装 Core」是 2026-10-15 18:0x 的实测，之后可能已被第三方会话改变。

---

## 8. 裁决记录（2026-10-15，人类）

**问题不是「选 A 还是 B」，而是先冻结协议，再以仓库内实现为基线吸收另一版的优点。**

### 8.1 唯一权威

| 事项 | 裁决 |
| --- | --- |
| 源码权威 | 仓库内 `ops/cloud_worker/`。仓库外 `E:\亚马逊云\宁夏CPU节点\deploy\` **只作为部署产物**；**禁止反向成为源码权威**；**暂不运行 `mirror.py`**（它承担不了冲突合并） |
| 契约权威 | **JSON Schema**。`moodify.cpu-job/0.1` 的 Schema 是唯一协议定义；Python 数据类、校验器、Studio JSON、测试样本都从它派生或被契约测试约束。**CI 必须检测 Schema 与 Python 常量是否漂移** |
| 生命周期状态 | **小写**：`pending` / `claimed` / `done` / `failed` / `inconclusive` / `human_required`。理由：跨 Studio、S3、Python、JSON 的协议值，小写与既有 S3 路径一致。**已无生产任务，现在是最后一个低成本冻结窗口** |
| 错误码 | **大写机器码**，保留较完整的集合：`INPUT_HASH_MISMATCH`、`CORE_NOT_AVAILABLE` …… 状态与错误码不是同一层 —— 状态用小写生命周期词，错误码用稳定大写码；**不要退化成 8 个宽泛「异常类」**，Studio 要据错误码决定重试/停止/要求人工 |
| `media_probe` | **允许直接调用 ffprobe**。它只提取容器、编码、时长、采样率、声道等**媒体事实**，不是声音分析、DSP 或 Judge，因此不违反 One Core。契约中明确命名为 `media_probe`，并写清边界 |
| `analyze` | **必须调用 Moodify Core**。不接受无条件成功桩；Core 未安装时返回 `CORE_NOT_AVAILABLE`，**不能制造分析产物** |
| W3 | 拆成两个门禁：**W3A** = `smoke + media_probe`（无需 Core）；**W3B** = 安装固定版本 Core 后跑 `analyze`。**W3B 通过前不得宣称 CPU 分析链已跑通** |

### 8.2 执行顺序

1. **提交调查证据**（本文件）。不与任一实现混成一个难以审查的大提交。
2. **冻结契约**：状态改小写；保留整理错误码集合；Schema 为唯一权威；加 Schema↔Python
   一致性测试；加**旧大写状态拒绝测试**（无生产任务，不需要兼容迁移层）；写清
   `media_probe` 与 `analyze` 的能力边界。完成后**给 Schema 算 SHA-256**，W4 Studio 按该版本开发。
3. **修正队列语义**：不得把「只有一个 worker claim 成功」当作 S3 的真实性保证；承认 claim
   非原子；用 `request_id` 幂等索引 + 最终结果**条件写入**保证只有一个权威结果；重复执行必须
   得到同一结果或明确 `ALREADY_COMPLETED`；`reap_stale_claimed` 每次回收**必须推进 `attempt`**；
   超过最大次数进入 `failed`，**禁止无限重跑**；竞争测试改测「**最终只有一个权威结果**」，
   而不是「只有一个 worker 读到任务」。
4. **处理 Core 前置条件**：W1/W2 合并前**不动服务器**，先让仓库测试全绿。进入 W3 时：
   先 W3A；再为 `moodify-core-package` 构建**固定版本 wheel**；在节点 venv 安装 wheel 并记录
   版本与哈希；再跑 W3B。Core 缺失必须失败为 `CORE_NOT_AVAILABLE`。**不要让 worker 从仓库源码
   路径临时 import Core** —— 节点只安装可复现的版本化包。
5. **生成部署产物**：仓库实现全绿后才允许同步 —— 先把外部 `deploy/` 改名或复制成带时间戳备份；
   `mirror.py --dry-run` 输出必须进入验收记录；禁止镜像 `__pycache__`；由 `ops/cloud_worker/`
   **单向**生成 `deploy/`；逐文件校验哈希；先 `worker.py --once`，**不立即启用 systemd**。

### 8.3 提交拆分

| # | 提交信息 | 内容 |
| - | --- | --- |
| 1 | `docs: resolve duplicate CPU worker implementations` | 本文件 |
| 2 | `feat(cloud-worker): freeze cpu-job 0.1 contract` | 小写状态、大写错误码、Schema 唯一权威、边界说明 |
| 3 | `fix(cloud-worker): make retry and non-atomic claim semantics explicit` | 条件写入、`ALREADY_COMPLETED`、回收推进 attempt、终止上限 |
| 4 | `test(cloud-worker): cover schema parity and authoritative result race` | 一致性测试、权威结果竞争测试 |
| 5 | `ops(cloud-worker): generate external deployment mirror` | 镜像生成与哈希校验 |

**不得**先把两版全部文件一起提交、再删掉一套 —— 那会污染历史。

### 8.4 基线取用说明

本裁决以 A 版（仓库内）为基线，但**吸收 B 版的两处优点**，记此备查：

- **指数退避**：B 版 `RETRY_BASE_SEC=30` + `not_before` 的退避节奏优于 A 版靠 poll 节奏的粗糙做法，
  合入 A 版。
- **零依赖测试**：B 版测试仅用标准库即可运行。A 版保留 pytest（评测面更宽），但这一点作为
  已知取舍记录在案，不作为缺陷。

