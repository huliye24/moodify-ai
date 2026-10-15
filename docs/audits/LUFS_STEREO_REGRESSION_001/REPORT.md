# LUFS_STEREO_REGRESSION_001 — 转交单

**状态：** FINDING — 已核实，**未修复**（本轮不动引擎代码，按 2026-10-12 人类裁决）
**发现时间：** 2026-10-12
**发现位置：** `moodify-core-package/src/moodify/auditory/loudness.py:74`
**发现时 HEAD：** `1d53f234`
**证据：** `git merge-base --is-ancestor ca0c4805 main` → **非祖先**；分支列表含 `codex/hotfix-000-measurement-correctness`

> **一句话：** HOTFIX 000（`ca0c4805`）修好的三处测量缺陷——立体声响度偏低、
> peak/RMS 走单声道下混、以及由前者派生的波峰因数假阳性——**都没有进入 main，
> 也都还活在当前树上**。本转交单只交证据，不改代码。

---

## 1. F1 — 立体声 LUFS 低约 3 dB

**规格：** ITU-R BS.1770 规定通道功率**求和**：`L_KG = -0.691 + 10·log10(Σ_i G_i·z_i)`，
其中 `G_i = 1.0`。

**实现：** 当前树写成**平均**：

```python
# moodify-core-package/src/moodify/auditory/loudness.py:74
combined = np.sum(energies, axis=0) / sum(weights)
```

单声道的 `sum(weights) == 1`，所以**只有立体声受影响**——这正是原作者写的
「mono oracle 看不见」的原因。

### 实测（`pyloudnorm` 为外部基准，本机已装）

| 信号 | Moodify | pyloudnorm | 差 |
|---|---|---|---|
| 立体声（各通道独立）@44.1k | −11.773 | −8.829 | **−2.944** |
| 立体声（双单声道）@44.1k | −11.355 | −8.408 | **−2.946** |
| 立体声（仅 L 有声）@44.1k | −14.365 | −11.419 | **−2.946** |
| 立体声（反相）@44.1k | −11.355 | −8.408 | **−2.946** |
| 单声道 @44.1k | −11.355 | −11.419 | +0.064 ✓ |
| 立体声（各通道独立）@48k | −11.794 | −8.826 | **−2.968** |
| 立体声（双单声道）@48k | −11.373 | −8.405 | **−2.968** |
| 立体声（仅 L 有声）@48k | −14.383 | −11.415 | **−2.968** |
| 立体声（反相）@48k | −11.373 | −8.405 | **−2.968** |
| 单声道 @48k | −11.373 | −11.415 | +0.043 ✓ |

（数字取自 `reproduce.py` 第二节，引擎输出已 `round(...,2)`。）

**附加症状：** Moodify 报双单声道（−11.355）与单声道（−11.355）**完全相等**；
pyloudnorm 报双单声道比单声道高 3.01 dB（−8.408 vs −11.419）。双声道各带一份功率，
本来就应该响 3 dB。

---

## 2. F2 — `sample_peak_dbfs` 与 `rms_dbfs` 走单声道下混（**比 F1 严重得多**）

**位置：** `moodify-core-package/src/moodify/auditory/metrics.py:92` 与 `:94`

```python
mono = samples.mean(axis=1) if samples.ndim > 1 else samples   # :74
...
pk = _peak_db(mono)      # :92   下混
rms = _rms_db(mono)      # :94   下混
crest = pk - rms         # :96   差值继承了下混的错
```

而同一份报告里的 `true_peak_dbfs` 是**逐声道**测的（`:90`，走
`auditory/true_peak.py`）。**一份报告混用了两个信号域。**

### 实测：反相立体声（L = −R），5 s @44.1 kHz

| 量 | 引擎报出 | 正确值 |
|---|---|---|
| `true_peak_dbfs`（逐声道） | −0.91 | −0.92 ✓ |
| `sample_peak_dbfs`（下混） | **−240.00** | −0.92 |
| `rms_dbfs`（下混） | **−240.00** | −3.93 |
| `crest_factor_db`（派生） | **0.00** | 3.01 |
| `plr_db`（派生） | **239.09** | 3.02 |

下混 `max|L+R|/2 = 0.000000`——**反相内容在求和时完全抵消**。
（−240 dBFS 是 `metrics.py` 里 `+1e-12` 保护项被打到的底，不是测量值。）

**这不是偏差，是灾难性失效。** 一个实际接近满刻度的信号被报成 −240 dBFS，
即「静音」，派生出的 PLR 是 **239 dB**。

**为什么这条重要超出预期：** 反相内容正是下一个实验要碰的东西——假立体声、
相位反转的合成 pad、立体声扩展做过头的 AI 输出。如果对照实验建立在
「L = −R 的片段被读成静音」之上，结论不会只是偏差，而是完全无效。

---

## 3. F3 — 波峰因数假阳性（F2 的下游产物）

`crest_factor_db = pk − rms`，两项都走了下混，所以 F2 会**发明**出信号本来没有的波峰因数。
HOTFIX 000 的说明里写着「CREST_FACTOR_COLLAPSE 是 F2 制造出来的假阳性」。
它随 F2 一起回来。

---

## 4. 证据链

```bash
# 修复不在 main 上，也不在当前分支上
git merge-base --is-ancestor ca0c4805 main        # → 退出码 1（非祖先）
git branch -a --contains ca0c4805                 # → codex/hotfix-000-measurement-correctness 等

# 当前树仍是除N
sed -n '74p' moodify-core-package/src/moodify/auditory/loudness.py
#   combined = np.sum(energies, axis=0) / sum(weights)

# 全仓库唯一命中
grep -rn "/ sum(weights)" --include=*.py .
#   ./moodify-core-package/src/moodify/auditory/loudness.py:74

# 一并丢失的还有修复自带的 oracle 测试
git show ca0c4805 --stat
#   moodify-core-package/tests/auditory/test_measurement_channel_domain.py | 252 +++++
ls moodify-core-package/tests/auditory/test_measurement_channel_domain.py
#   （文件不存在）
```

HOTFIX 000 新增的 `test_measurement_channel_domain.py`（252 行）用 `pyloudnorm` 做外部基准，
在 stereo independent / stereo imbalanced 两种素材上断言旧的 ±3.01 dB 实现必然失败。
**该 oracle 不在当前树上**，所以即使有人重新引入这个缺陷，CI 也抓不到。

### 复现脚本

见同目录 `reproduce.py`。用法：

```bash
python docs/audits/LUFS_STEREO_REGRESSION_001/reproduce.py
```

需要 `numpy` 与 `pyloudnorm`（本机均已安装）。脚本只读仓库代码，不修改任何文件。

---

## 5. 影响范围（未逐一验证，仅列出，供裁决参考）

这两个缺陷都出现在 `auditory/metrics.py::compute_metrics` 这条主链路上，
而它是扫描、诊断、审判各层的数值来源。凡是消费 `integrated_lufs`、
`sample_peak_dbfs`、`rms_dbfs`、`crest_factor_db`、`plr_db` 的下游——
报告、阈值规则、Judge 的响度维度、以及以这些数为基准的标定——
都会继承。**我没有逐一追查下游影响，这不在本轮范围内。**

---

## 6. 附带观察（同属「本轮只报告」）

### 6.1 变量名与 BS.1770 正好互换（命名缺陷，非数值缺陷）

`auditory/loudness.py:19-22` 中：

- `_RLB_B/_RLB_A` 装的是**高架滤波器**（stage 1）的系数
- `_HS_B/_HS_A` 装的是 **RLB 高通**（stage 2）的系数

名字与内容互换。**数值与应用顺序是对的**（先高架后高通，与标准一致），
所以不影响结果，但任何人照着变量名读代码都会读反。

### 6.2 44.1 kHz 系数近似：机制与文档不一致，但结论大概率安全

文档（`loudness.py:1-8`）称「44.1 kHz 沿用 48 kHz 系数，误差 < 0.1 LU」。

实测：滤波器**响应**差 +0.17 dB @100 Hz、+0.21 dB @1 kHz、+0.00 dB @10 kHz；
但**整体 LUFS** 在合成节目素材上只差 **+0.009 LU**。
机制不是文档说的那样（不是「近似可忽略」，而是两个频段的误差部分抵消），
结论却大概率安全。**代价与节目频谱有关**，重低音曲目上可能不同——
R001 实验正在 11 首真实歌曲上把它量出来。

### 6.3 注册表三处已核实的不一致

| # | 不一致 |
|---|---|
| 1 | `true_peak_dbfs` 单位：`docs/metrics/METRIC_REGISTRY_V1.md:21` 写 dBTP，`configs/measurement_registry_v1.yaml:38` 与 `auditory/metrics.py:91` 写 dBFS |
| 2 | `near_clipping_sample_count` 阈值：MD 写 0.9（`:50`），YAML 与代码写 0.95（`yaml:114` / `metrics.py:105`）——**实际是 0.95** |
| 3 | `crest_factor_db` 在 YAML 标 `judgment_eligible: false`（`:78`），却在 `auditory/judgment.py:28-29` 当判决规则用 |

### 6.4 频段口径不统一

`reality_metrics.py` 用的 `BANDS_6`（sub 20-60 / bass 60-250 / low_mid 250-500 /
mid 500-2000 / presence 2000-5000 / air 8000-16000）与注册表的**规范 9 频段**
不是同一套。两者不可互换。

### 6.5 死代码

`auditory/metrics.py:27` 的 `true_peak_db`（zero-stuff + Hann 低通）被 `:79`
导入的同名函数遮蔽，`compute_metrics` 实际用的是 `auditory/true_peak.py` 那份。
`:27` 那份无人调用。

### 6.6 未跟踪的既有资产

`git ls-files '*.m'` 在全仓库返回 **0 条**。以下全部处于未跟踪状态，
一次 `git clean -fd` 即丢失：

- `E:\moodify\research\matlab\`（23 个 `.m`，约 4893 行，含已跑过的 S001–S003 产物）
- `E:\moodify\research\hear_judge\`
- `E:\moodify\docs\canon\JUDGE_CORE_PRINCIPLE.md`（**正典文件本身未跟踪**）

### 6.7 另一套互补实现里的一个未定义函数

`E:\荣景文川 文化集团 2026\逍遥仙\挑选\重制_贝叶斯双版本\matlab\` 有一套
`+mfyaudit`（38 个 `.m`）。其 `audit_run.log` 记录了一次崩溃：

```
未定义与 'double' 类型的输入参数相对应的函数 'env'
出错 mfyaudit.referenceMetrics>modSpectrumDistance (第 156 行)
ea = env(monoA, hop);
MATLAB_EXIT=1
```

`env` 未定义或被遮蔽。未修复，仅记录。

---

## 7. 本轮未做的事

- **未修改任何引擎代码。** 按 2026-10-12 人类裁决，本轮只交证据。
- **未追查下游影响面**（哪些报告/阈值/Judge 维度依赖这些数）。
- **未修复 `+mfyaudit` 的 `env` 缺陷。**
- **未提交任何未跟踪文件**（含正典 `JUDGE_CORE_PRINCIPLE.md`）。

## 8. 建议的下一步（供人类裁决，不是本轮动作）

1. 判定是**把 `ca0c4805` 重新落到 main**，还是**按当前树重做一份修复**——
   两者不等价：`ca0c4805` 之后 main 上可能有其他改动。
2. 修复必须**连同 oracle 一起落**（`test_measurement_channel_domain.py`）。
   本轮已证明：没有 oracle，同一个缺陷可以同时活在树上和「已修复」的记录里。
3. 补一条 F2 的 oracle：**反相立体声**。现有的双单声道探针抓不到 F2，
   因为真正的下混是 `cross = np.sum(weights * [0.5, 0.5], axis=1)`——
   它与 `cross = np.mean(audio, axis=1)` 在双单声道上**完全同值**，只有反相内容能分开。
