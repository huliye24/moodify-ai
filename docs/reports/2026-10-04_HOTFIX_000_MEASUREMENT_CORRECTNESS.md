# HOTFIX 000 — Core Measurement Correctness 实施报告

> **任务书：** `HOTFIX 000 — Core Measurement Correctness`
> **分支：** `codex/hotfix-000-measurement-correctness`（基于 `main` `01edc902`）
> **提交：** `ca0c4805f62f3a07cee61e4a0503ffe8216fa7e6`（已提交，未推送）
> **日期：** 2026-10-04
> **来源：** 本地桌面验收 `MOODIFY_DESKTOP_LOCAL_ACCEPTANCE_001` 发现的 F1–F4
> **配套文档：** `docs/HOTFIX_000_MEASUREMENT_CORRECTNESS.md`（简短正确性说明）

---

## Summary

修复了本地验收发现的四个正确性缺陷。改动本身很小（核心是两处聚合/信号域），但根因比表面深：**这两个缺陷在单声道上数学不可见，而现有 oracle 测试集全部只用单声道 fixture。**

- **F1** 立体声 `integrated_lufs` 低 3.0103 dB —— BS.1770 通道功率被**除以通道数**而非**求和**。
- **F2** `sample_peak_dbfs` / `rms_dbfs` 测的是单声道下混，而同报告的 `true_peak_dbfs` 是逐通道的 —— 一份报告混了两种信号域。
- **F3** `CREST_FACTOR_COLLAPSE` 误报 —— **不是独立 bug**，是 F2 凭空造出约 3 dB crest factor 所致；修复测量即消失，**未改阈值**。
- **F4** 桌面壳在专用外部运行时缺失时**静默回退系统 python** —— 改为显式 `DEPENDENCY_MISSING`。

同时修正了一条**把缺陷断言成「立体声恒等式」的测试**。

按 §32 停止：未启动 Project Model / CLI 2.0 / Sound Protocol 0.3 / Production Graph。

---

## Root Causes

### F1 — `auditory/loudness.py:74`

```python
combined = np.sum(energies, axis=0) / sum(weights)   # ← 缺陷
```

BS.1770 的聚合是**通道加权功率求和**：

```text
L_K = -0.691 + 10·log10( Σ_i G_i · z_i )
```

除以 `sum(weights)`（立体声为 2）等价于「通道取平均」，对每个立体声测量产生恒定偏差：

```text
-10·log10(2) = -3.0103 dB      ← 与验收观测的 2.97–3.03 dB 精确吻合
```

**单声道时 `sum(weights) == 1`，除法是恒等操作，缺陷完全隐身。** 这解释了它为什么能通过全部既有测试。

### F2 — `auditory/metrics.py:92-95`

```python
mono = samples.mean(axis=1) if samples.ndim > 1 else samples
...
pk  = _peak_db(mono)     # ← 下混
rms = _rms_db(mono)      # ← 下混
```

同文件的 `true_peak_dbfs` 走的是逐通道 4x 过采样（正确）。于是一份报告里，`true_peak` 在真立体声域、`sample_peak`/`rms` 在下混域。

不对称混音会被严重低估：`L=0.50 / R=0.01` 的真峰值是 −6.02 dBFS，下混峰值只有 −12.03 dBFS（差 6.01 dB）。

### F3 — 派生缺陷，非独立 bug

`crest_factor_db = sample_peak_dbfs - rms_dbfs`。F2 让峰值低估 6 dB、RMS 低估 3 dB，**净造出约 3 dB 信号本身没有的 crest factor**，从而撞上 4.0 dB 地板。

### F4 — `moodify-desktop/src/main.js`

```js
function pyExe(venvName) {
  const exe = path.join(VENVS[venvName], 'Scripts', 'python.exe');
  return fs.existsSync(exe) ? exe : PYTHON;   // ← 静默回退
}
```

`VENVS` 以 `__dirname/../..` 解析，安装版落到 `…\resources\.venv-*`、便携版落到 `%TEMP%\…\resources\.venv-*`，**两个出厂构建都没有这些目录**。回退到系统 python 后，`librosa → sklearn → pandas` 的 ABI 不匹配把「缺依赖」伪装成深层 traceback。

### 为什么整条测试线没抓住它（最值得记录的一条）

`tests/auditory/test_measurement_correctness.py` 的**每一条 oracle 测试都用单声道 fixture**（`_sine(..., channels=1)`）。单声道下两个缺陷在数学上都不可见。

更严重的是里面有一条：

```python
def test_loudness_stereo_identity_matches_mono_energy():
    # 注释声称「两个相同通道的加权和等于单通道能量」
    assert integrated_loudness_lufs(stereo_same, sr) == approx(integrated_loudness_lufs(mono, sr))
```

**这条测试把缺陷编码成了「立体声恒等式」。** 立体声两个相同通道的功率是单通道的 2 倍，正确关系是 **+3.01 dB**，不是相等。

---

## Files Changed

```text
M  moodify-core-package/src/moodify/auditory/loudness.py             (+6/-1)
M  moodify-core-package/src/moodify/auditory/metrics.py              (+9/-3)
M  moodify-core-package/tests/auditory/test_measurement_correctness.py (+29/-5)
A  moodify-core-package/tests/auditory/test_measurement_channel_domain.py (252)
M  moodify-desktop/src/main.js                                       (+32/-12)
A  moodify-desktop/src/runtime.js                                    (140)
A  moodify-desktop/scripts/test-runtime.js                           (183)
M  moodify-desktop/package.json                                      (接入 npm test)
A  docs/HOTFIX_000_MEASUREMENT_CORRECTNESS.md                        (167)
```

共 9 个文件、+799/−21。与 §27 预期的改动区域一致，未扩散到无关模块。

---

## Measurement Semantics

| 指标 | 信号域 | 定义 |
| --- | --- | --- |
| `integrated_lufs` | 全通道，**功率求和** | BS.1770-5 / EBU Tech 3341；K 计权、400 ms 块、−70 LUFS 绝对门 + −10 LU 相对门 |
| `sample_peak_dbfs` | 全采样、全通道 | `20·log10(max\|x\|)` |
| `rms_dbfs` | 全采样、全通道 | `20·log10(sqrt(mean(x²)))` —— 总能量 / 总样本数 |
| `crest_factor_db` | 派生，单一信号域 | `sample_peak_dbfs − rms_dbfs` |
| `true_peak_dbfs` | 逐通道、4x 过采样 | **未改动**（本来就正确） |

`rms_dbfs` 采用的定义与 `auditory/execution/chunking.py::chunked_peak_rms` 已使用的定义一致（全通道峰值 + 全通道能量 / 全样本数）—— 该模块本来就是对的，是仓库里的既有先例。

### §12 溯源：最小必要改动是「无需改动」

核查了 canonical registry `configs/measurement_registry_v1.yaml`：

```yaml
sample_peak_dbfs:
  definition: max abs sample level in dBFS
  method: max(|x|) -> 20*log10
rms_dbfs:
  definition: full-signal RMS in dBFS
  method: sqrt(mean(x^2)) -> 20*log10
crest_factor_db:
  method: derived from sample_peak_dbfs and rms_dbfs
integrated_lufs:
  method: channel-independent K-weighting + energy aggregation + absolute/relative gating
```

**登记表早就声明了正确的语义 —— 是代码违反了自己的权威。** 因此本次**不需要**修改 registry、method 标识或 provenance 版本，也没有 bump 产品版本。

---

## Before / After

确定性探针，44.1 kHz、20 s，与验收报告同一配置。Before 列取自验收证据，未虚构。

### Probe A — L = 0.35 @440 Hz（带调幅），R = 0.30 @880 Hz

| Metric | Before | After | Reference |
| --- | ---: | ---: | ---: |
| `integrated_lufs` | −14.96 | **−11.84** | −11.993 (pyloudnorm) |
| `sample_peak_dbfs` | −10.93 | **−9.12** | −9.12 |
| `rms_dbfs` | −17.59 | **−14.58** | −14.58 |
| `true_peak_dbfs` | −9.11 | −9.11 | — |
| `crest_factor_db` | 6.66 | 5.46 | — |

### Probe B — L = 0.50 @440 Hz，R = 0.01 @880 Hz

| Metric | Before | After | Reference |
| --- | ---: | ---: | ---: |
| `integrated_lufs` | −12.72 | **−9.69** | −9.754 (pyloudnorm) |
| `sample_peak_dbfs` | −12.03 | **−6.02** | −6.02 |
| `rms_dbfs` | −15.05 | **−12.04** | −12.04 |
| `true_peak_dbfs` | −6.02 | −6.02 | — |
| `crest_factor_db` | 3.02 | **6.02** | — |

### F3 判定

```text
CREST_FACTOR_COLLAPSE fired:
  Probe A   before=False   after=False
  Probe B   before=True    after=False     ← 缺陷导致的误报已消失
```

对应 §8 **Outcome A**：修正测量后误报消失，**不需要改阈值**。

---

## Oracle Validation

### 两个独立参考实现 + 本实现的 48 kHz 三方对照

```text
Probe A:  Mine -11.950  |  pyloudnorm -11.992  |  ffmpeg ebur128 -12.0 LUFS
Probe B:  Mine  -9.712  |  pyloudnorm  -9.754  |  ffmpeg ebur128  -9.7 LUFS
```

`pyloudnorm` 与 `ffmpeg ebur128` 彼此一致，本实现落点与二者均在 **0.05 LU** 内。

### 44.1 kHz 的已知偏差（既有、已记录，与本次无关）

```text
Probe A  delta = +0.150 LU
Probe B  delta = +0.065 LU
```

原因是 `loudness.py` **既有的、docstring 已声明的**取舍：44.1 kHz 复用 48 kHz 的 K 计权系数。

**误差事实（本次清理已修正此前 docstring 中不准确的「< 0.1 LU」表述）：**

| 采样率 | K 计权系数 | 当前 oracle 验证 | 测试 tolerance |
| --- | --- | --- | --- |
| 48 kHz | 标准精确系数 | **≤ 0.05 LU**（对 pyloudnorm 与 ffmpeg ebur128） | 0.1 LU |
| 44.1 kHz | 复用 48 kHz 系数 | **确定性探针上最大约 0.15 LU** | **0.2 LU** |

按 §10 要求，**没有盲目放宽容差**：48 kHz 用精确系数配 0.1 LU，44.1 kHz 仅在**该采样率**放宽到 0.2 LU 并写明理由。聚合缺陷本身是 3 dB，仍远超任一容差。

### 峰值 / RMS 对照

确定性 PCM 输入下与解析真值差 **0.00 dB**（见上表），容差断言取 0.05 dB。

---

## Runtime Behavior

| 场景 | 行为 |
| --- | --- |
| 专用 venv 存在 | `resolveRuntime()` 返回该解释器路径 ✅ |
| 专用 venv 缺失 | 抛 `RuntimeMissingError` → `{ ok:false, code:'DEPENDENCY_MISSING', runtime, reason, candidates }` ✅ |
| 解析失败之后 | **不 spawn 任何子进程**；失败结果里不含任何可执行文件 ✅ |
| 运行时在、`basic-pitch.exe` 缺 | 同样 `DEPENDENCY_MISSING`，且 `runtime` 仍标识为 `basic-pitch` ✅ |
| 运行时名拼错 | 抛普通 `Error`（编程错误 ≠ 缺依赖，两者可区分）✅ |
| `MOODIFY_VENV_*` 环境变量覆盖 | 显式设置的**同一个专用 venv**，排在前面的候选项并参与校验 —— 这是「显式配置」，与「静默回退」是两件事 ✅ |

渲染层既有代码已经渲染 `code` 字段，因此用户看到的是：

```text
分离失败（code DEPENDENCY_MISSING 缺少必需的 Moodify 外部运行时：basic-pitch（…））
```

不再是 pandas/numpy ABI traceback。

**已知局限（§18 允许，已记录）：** 运行时校验只检查可执行文件存在，不做 `import basic_pitch` 能力探针 —— 一个存在但损坏的 venv 仍会被解析成功。选择推迟是为了避免每次解析都付启动开销。

---

## Tests

```bash
# 新增：信道域回归
$ python -m pytest tests/auditory/test_measurement_channel_domain.py -q
19 passed

# 既有听觉套件（含被修正的那条测试）
$ python -m pytest tests/auditory/ -q
165 passed

# 全量核心套件
$ python -m pytest -q
1204 passed, 6 skipped, 56 warnings in 646.09s (0:10:46)

# 桌面运行时解析器（已接入 npm test）
$ node scripts/test-runtime.js
12 checks, all passed

# 桌面全套（npm test 等价）
$ node scripts/check-contracts.js   → exit 0
$ node scripts/test-pipeline.js     → 33 passed, 0 failed
$ node scripts/test-studio.js       → 21 passed, 0 failed
$ node scripts/test-runtime.js      → all runtime checks passed

# 静态检查
$ python -m ruff check <changed files>
All checks passed!
```

**无回归的算术核对：** `main` 基线 1184 + 本次新增 20 条 = **1204** ✓

**6 个 skip 与改动前完全一致**（ffmpeg 不在 PATH、golden 源缺失、`test_api_v01` 整模块 skip），**均为既有环境条件性跳过，非本次引入**。

### 测试确实咬得住（§11）

- `test_channel_mean_aggregation_cannot_pass` —— 断言结果与 oracle 的距离在容差内，**同时**断言远离 `ref − 3.0103`。重新引入「除 N」必然失败。
- `test_rms_is_not_the_mono_downmix_rms` / `test_sample_peak_matches_the_louder_channel_not_the_downmix` —— 断言与下混值相差 > 2.5 dB / > 5 dB。
- `test_old_downmix_crest_would_have_fired` —— 解析复现旧缺陷签名（< 4.0 dB）并断言修复后 > 4.0 dB，证明该测试真的能咬住。
- `test_loudness_antiphase_stereo_is_not_cancelled` —— 反相立体声不得被当作静音。

---

## Compatibility

**无变更。**

| 项目 | 状态 |
| --- | --- |
| 报告 schema（`auditory_report.json` 等） | 未变，只改数值不改形状 |
| `case.json` / `measurements.json` / `scan/metrics.json` | 未变 |
| `ProductionCase` / `release.py` / `reopen_case` | 未变 |
| compare（`ab_compare` / `comparison`） | 未变 |
| 人类权威语义（`HUMAN_REQUIRED` / `INCONCLUSIVE` / `review_required`） | **未削弱**（§29） |
| 既有 case bundle | **未重写** —— 历史报告保持原样（§12） |
| registry / provenance 版本 / 产品版本 | **未变**（理由见 Measurement Semantics） |

---

## Deferred

以下问题**未修复**，均记录在 `docs/HOTFIX_000_MEASUREMENT_CORRECTNESS.md`，以免被误认为已修：

1. **`auditory/timeline.py` 的窗口 `sample_peak_dbfs` / `rms_dbfs` 仍是单声道域** —— 与 F2 同类缺陷，且位于**同一份 `scan/timeline_metrics.jsonl` 证据**中。需独立任务与独立 oracle。
2. **`mix_graph/verify.py` 的 RMS 走单声道下混**（其 peak 已是全通道）—— 与 F2 同形状，在完成/修音路径。
3. **`clipping_sample_count` 与静音分析走单声道下混** —— 单边削波可能被漏掉。
4. **4.0 dB crest 地板仍是未标定的工程默认值** —— 其自身 provenance 已声明「无标准依据、无实验推导」。纯正弦的 crest factor 在定义上就是 3.01 dB，仍会误报。这是**规则标定问题，不是测量 bug**（§8 Outcome C：证据不足时不发明新阈值，保留不确定性并如实记录）。
5. **`loudness_range_lu` 的 mono 策略是登记表声明的策略**（`channel_policy: mono downmix for short-term loudness`），非缺陷；是否合规是另一个问题。
6. **运行时只校验可执行文件存在**，不做 import 能力探针（见 Runtime Behavior）。
7. **打包层仍缺 `.venv-*`** —— 本次只让失败变**显式**；供给运行时属独立发布任务（§16）。

---

## Commit

```text
ca0c4805f62f3a07cee61e4a0503ffe8216fa7e6
fix(auditory): correct stereo loudness and channel-domain metrics (HOTFIX 000)
```

分支 `codex/hotfix-000-measurement-correctness`，基于 `main` `01edc902`，**已提交、未推送**，工作区干净。

---

## 验收门核对（§25 / §30）

| 门 | 项 | 状态 |
| --- | --- | --- |
| 测量 | `integrated_lufs` 与 oracle 一致 | ✅ ≤0.05 LU @48 kHz |
| 测量 | ~3.01 dB 立体声偏差消除 | ✅ |
| 测量 | `sample_peak_dbfs` 测多通道而非下混 | ✅ |
| 测量 | `rms_dbfs` 遵循已记录的多通道定义 | ✅ |
| 测量 | true peak / sample peak 信号域一致 | ✅ |
| 诊断 | 缺陷导致的 `CREST_FACTOR_COLLAPSE` 误报消失 | ✅ |
| 诊断 | 残余 crest 规则局限已如实记录 | ✅ |
| 运行时 | 缺运行时不再静默回退系统 python | ✅ |
| 运行时 | 缺运行时产生显式依赖失败 | ✅ |
| 运行时 | 正常专用运行时仍可用 | ✅ |
| 回归 | 新测试通过 | ✅ 19 + 12 |
| 回归 | 既有听觉测试通过 | ✅ 165 |
| 回归 | 桌面/运行时测试通过 | ✅ |
| 回归 | 无无关行为被改动 | ✅ |
| 负向 | 未启动 Project Model / CLI 2.0 / Protocol 0.3 / Production Graph / 新 GUI | ✅ |

---

> **核心原则（§33）：** 一个 Agent 的可靠性，上限取决于它所信任的测量。
> 让 Moodify 更强之前，先让它更正确。
