# HOTFIX 000 — Final Cleanup 报告

> **任务：** HOTFIX 000 FINAL CLEANUP（修正 44.1 kHz 近似误差表述）
> **分支：** `codex/hotfix-000-measurement-correctness`
> **提交：** `d6e3e8ed2689598fd43be6ff0058f5b051fa0f8c`
> **日期：** 2026-10-04
> **范围：** 仅注释与文档。**未改算法、未改断言、未改 tolerance、未扩范围。**
> **相关文档：** `docs/HOTFIX_000_MEASUREMENT_CORRECTNESS.md`、`docs/reports/2026-10-04_HOTFIX_000_MEASUREMENT_CORRECTNESS.md`

---

## Summary

`loudness.py` 声称 44.1 kHz 复用 48 kHz K 计权系数时「error < 0.1 LU」。
**这个数字没有出处，也没有被测量过**，而且不准确：确定性探针上的实测最坏偏差是 **0.150 LU**。

本次把它替换为实测值，并让代码、测试常量、两份文档统一使用同一组三个数字。

改动共 4 个文件、+46/−16，全部是 docstring / 注释 / Markdown。

---

## 问题：那个数字是从哪来的

```python
def _k_weighted(x, sr):
    """K-weighting (RLB high-pass + high-shelf).

    Standard coefficients are defined at 48 kHz. 44.1 kHz uses the same
    coefficients (accepted, error < 0.1 LU). ...
    """
```

grep 后确认它只在两处出现（`loudness.py` 的模块 docstring 与 `_k_weighted` docstring），**没有实验记录、没有引用、没有对应测试**。它是一个「听起来合理」的量级估计，被写成了事实。

而 HOTFIX 000 新引入的确定性探针恰好能够测量它，结果与声称不符。

---

## 实测证据

在 `tests/auditory/test_measurement_channel_domain.py` 的确定性探针上，对本实现与 `pyloudnorm` 的 `integrated_loudness` 求差：

| 采样率 | Probe A（独立双音） | Probe B（强失衡） | 最大偏差 |
| --- | ---: | ---: | ---: |
| 48 kHz | +0.042 LU | +0.043 LU | **0.043 LU** |
| 44.1 kHz | +0.150 LU | +0.065 LU | **0.150 LU** |

（48 kHz 同时与 `ffmpeg ebur128` 交叉验证，落点一致。）

因此文档中写死为：

| 采样率 | K 计权系数 | 当前 oracle 验证 | 测试 tolerance |
| --- | --- | --- | --- |
| 48 kHz | 标准精确系数 | **≤ 0.05 LU** | 0.1 LU |
| 44.1 kHz | 复用 48 kHz 系数 | **最大约 0.15 LU** | **0.2 LU** |

**注意区分两件事：**

- 44.1 kHz 的 0.15 LU 是**既有、独立**的系数近似问题，与本次修复无关；
- HOTFIX 000 修的通道聚合缺陷是 **3.01 dB**（= 3.01 LU 量级），比这大两个数量级。

把两者混为一谈，正是当初那条「< 0.1 LU」最危险的后果 —— 它会让人以为 44.1 kHz 的偏差可以忽略，从而掩盖真实量级。

---

## 我自己的报告也犯了同样的错

上一轮的实现报告 `docs/reports/2026-10-04_HOTFIX_000_MEASUREMENT_CORRECTNESS.md` 里写着：

```text
原因是 loudness.py 既有的、docstring 已声明的取舍：……
（近似误差 < 0.1 LU）
```

**我把那个未经测量的数字照抄进了交付文档，并把它当成「docstring 已声明的事实」引用。** 一个没有出处的数字，因为写在了 docstring 里，就在文档链上获得了权威性 —— 这正是本次清理要切断的东西。该行已一并修正为实测表。

教训：**引用文档里的数字前，先自己测一遍。** 尤其警惕「accepted, error < X」这类既无引用也无实验的表述。

---

## Files Changed

```text
M  moodify-core-package/src/moodify/auditory/loudness.py              (模块 docstring、_k_weighted docstring、系数常量注释)
M  moodify-core-package/tests/auditory/test_measurement_channel_domain.py  (两个 tolerance 常量的说明注释)
M  docs/HOTFIX_000_MEASUREMENT_CORRECTNESS.md                          (改为三数字对照表)
M  docs/reports/2026-10-04_HOTFIX_000_MEASUREMENT_CORRECTNESS.md       (同上，并修正被照抄的那一行)
```

**未改动：** `_k_weighted` 的实现、`_RLB_*` / `_HS_*` 系数值、`integrated_loudness_lufs`、任何测试断言、`LUFS_TOLERANCE_STANDARD_SR = 0.1` / `LUFS_TOLERANCE_APPROX_SR = 0.2` 的取值。

`git diff` 已逐行核对：`loudness.py` 的改动全部落在 docstring 与注释内，无一行可执行代码变化。

---

## 验证

```bash
$ python -m pytest tests/auditory/test_measurement_channel_domain.py -q
19 passed

$ python -m pytest tests/auditory/test_measurement_correctness.py -q
25 passed

$ python -m ruff check src/moodify/auditory/loudness.py \
                   tests/auditory/test_measurement_channel_domain.py
All checks passed!

$ grep -rn "error < 0\.1" src/moodify/auditory/ docs/
无残留
```

下笔前重新实测了要写死的两个数字（48 kHz = 0.043、44.1 kHz = 0.150），确认「≤ 0.05」「约 0.15」成立，**不是照旧结论抄的**。

---

## 为什么追加提交而不是 amend

任务允许「amend 当前 HOTFIX commit 或追加一个极小 commit」。选择追加，因为 `ca0c4805`（HOTFIX 本体）之上已经压了 `d6fc1921`（实现报告），要 amend 它必须改写中间提交的历史 —— 对一个纯文档修正而言，风险明显大于收益。

---

## 最终状态

```text
d6e3e8ed  docs(auditory): correct the stated 44.1 kHz K-weighting error   ← 本次
d6fc1921  docs(reports): add the HOTFIX 000 implementation report
ca0c4805  fix(auditory): correct stereo loudness and channel-domain metrics (HOTFIX 000)
```

分支 `codex/hotfix-000-measurement-correctness`，基于 `main` `01edc902`，三个提交**均未推送**，工作区干净。

**未做（按任务要求不扩范围）：** 未改动 44.1 kHz 重采样策略、未新增 44.1 kHz 专用系数、未调整任何 tolerance 取值、未触碰 `timeline.py` / `mix_graph` / clipping 等已记录在案的同类残留。

**STOP.**
