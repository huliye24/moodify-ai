"""`manifest` —— 作品清单与资产引用。

**Phase 1 不实现，返回 TUNABLE_CORE_NOT_AVAILABLE（方案 W2.3 的设计情形）。**

为什么不做
----------
「作品清单」的权威在发布链路（`moodify-desktop/src/publish.js` 的 catalogue 写入 +
`works/<work_id>/manifest.json` 键布局），不在 Core，也不在 worker。

worker 里再实现一套清单生成/校验，就等于在 §3.2 明令禁止的清单上再加一条：
「在 worker 内实现第二套 … 作品状态或发布权威」。清单一旦有两份实现，App 读哪一份、
冲突时谁赢都变成未定义行为 —— 这正是本项目反复用「第二权威」这个词拦住的事。

什么是诚实的替代路径
--------------------
1. Core 若日后提供作品清单能力，把本 adapter 指向它即可（本文件改成调用，不改契约）。
2. 发布链路的清单校验放在 Studio 侧，与清单的**生产者**同处一地。

在那之前，本任务稳定失败并说清原因，绝不生成一个看起来像清单的假产物。
"""

from __future__ import annotations

from typing import NoReturn

from .base import AdapterContext, AdapterError, AdapterResult, Artifact, read_params

ALLOWED = ("action",)

REASON = (
    "作品清单没有 Core 权威：它的权威在 Studio 发布链路 "
    "(moodify-desktop/src/publish.js 的键布局与 catalogue 写入)。"
    "worker 内实现第二套清单即构成「第二套发布权威」，被方案 §3.2 明令禁止。"
)


def run(ctx: AdapterContext) -> NoReturn:  # type: ignore[valid-type]
    read_params(ctx, ALLOWED)
    raise AdapterError("TUNABLE_CORE_NOT_AVAILABLE", "manifest 任务在当前 Core 上没有实现", REASON)


__all__ = ["run", "ALLOWED", "Artifact", "AdapterResult"]
