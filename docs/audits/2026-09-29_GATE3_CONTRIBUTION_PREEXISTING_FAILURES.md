# GATE-3 失败转交单 → 结案记录：Contribution 域 17 个预存失败

**日期：** 2026-09-29（发现）→ 2026-09-29（裁决与结案）
**发现于：** Mix Graph v0.1 工程包落地四道门（Gate 3 全量 pytest）
**状态：** RESOLVED —— 域内 39/39 全绿，修复随 Gate 4 修复序列落地

---

## 1. 最初快照（发现时）

```text
17 failed, 1072 passed, 5 skipped, pytest exit 1
17 个失败 100% 集中：tests/contribution_test.py（13）+ tests/integration/test_complete_workflow.py（4）
```

## 2. 归因更正（诚实记录）

最初归因写的是"代码允许 rejected → under_review，测试断言 rejected 终态，二者自相矛盾"。
**这个细节判断是错的。** 深入逐点对质后，真实情况是：

1. **状态机代码本来就是终态语义**：`state_machine.py` 中 `REJECTED: []`（注释明写 "Immutable once rejected"），`is_terminal_state` 包含 rejected。A/B 之争里的 A 侧代码早已存在。
2. **真正的问题是 Python 镜像内部不一致**（commit `4f2b2386` 引入，代码与测试互相矛盾，且二者都与参考包部分偏离）：

| 矛盾点 | 嵌入式 schema | 参考包 | 测试 | 代码其他部分 |
|---|---|---|---|---|
| evidence 类型字段 | 要求 `evidenceType` | 要求 `type` | 用 `type` | `to_dict`/`evidence.py` 输出 `type` |
| digest 规则 | `^[a-f0-9]+$`（拒绝冒号） | `^(sha256:[0-9a-f]{64})?$` | `sha256:abc123`（假数据） | — |
| 顶层 `review` | 无（additionalProperties=False 还会拒收） | 有（`object\|null`，见 CONTRIBUTION_SPEC.md 记录形状） | 断言存在 | apply_transition 只写 metadata.review |
| finalDecision | 发明了 `enum: ['approved','rejected']` | 无此字段 | 用 `'Approved for production'` | — |
| review API | — | — | 期望 submit 后一步 review | apply_transition 只接受单步转移 |
| reputation 评分 | — | 五维嵌套于 dimensions | 顶层五维 + 因子派生两种模式 | scorer 顶层五维但硬性全必填，杀死因子派生路径 |

三条最初证据线索中仍然成立的部分：失败确为 `4f2b2386` 同 commit 引入；contribution 模块不依赖 pydantic/httpx，与环境漂移无关；全量门在本分支从未绿过。

## 3. 裁决（用户委托："我不知道，你自己选择"）

**裁决一（rejected 语义）：A —— rejected 为终态（吸收态）。**
理由：与参考 CONTRIBUTION_SPEC.md 的历史不可变哲学一致（"corrections require a new record; the new record must point to the old record through supersedes"）；代码本已如此实现；对 agent 驱动的贡献网络，复活已拒贡献会引入治理模糊。翻案走新 contribution + `supersedes`。

**裁决二（契约权威）：参考包 MOOD_PROTOCOL_CONTRIBUTION_CORE_002（schemas + spec）为准；测试是行为契约，代码修向测试与参考；测试中的懒惰假数据（假 digest、忘传 fixture、静态错指纹）按测试意图修。**
理由：参考包是 MPF-002 镜像的源头权威；测试整体上更忠实于参考包（`type` 字段、终态断言、两步 review 语义、因子派生评分均与参考或明显测试意图一致）；代码的偏离（evidenceType、 invented enums、内部 schema/dataclass/IO 三方不一致）是镜像移植缺陷。

## 4. 修复清单（全部落地）

代码侧（`src/moodify/contribution/`）：
- `schema/contribution.py`：evidence 项 required `evidenceType`→`type`（对齐参考+测试+自身 IO 层）；digest pattern 对齐参考 `^(sha256:[0-9a-f]{64})?$`；新增顶层 `review: object|null`（对齐参考记录形状）；删除镜像作者发明的 `finalDecision` enum；`ContributionSchema.from_dict` 的 evidence 映射改为显式 camelCase→snake_case（原 `**evidence` 会在合法输入上 TypeError）
- `state_machine.py`：apply_transition 的 review 处理优雅化（缺 reviewer/reviewDate 用确定性默认值，不再 KeyError）；可选键 reasons/reason 透传；metadata.review 同时落顶层 `review`
- `core.py`：create_contribution 前置贡献者身份校验（contributor={} 不再 KeyError 而是域错误）；review_contribution 复合转移（submitted→under_review→decision，保持严格状态图同时 API 一步到位；draft 直跳仍被拒）；metadata.history 历史账本（create/submit/review/score/finalize 各追加一条，review 只记最终决定一条）；get_contribution_history 优先返回账本
- `validate.py`：公开 `validate_contributor_identity`
- `scorer.py`：维度校验放宽为"显式分数验证类型/范围，缺省走因子派生"（原硬性全必填使因子派生路径不可达）；因子提取对非数值（嵌套 dict、bool）跳过而非崩溃

测试侧（懒数据修正）：
- `tests/contribution_test.py`：两处假 digest `sha256:abc123` → 64 位 hex；`test_valid_contribution`/`test_invalid_contributor` 改用真实计算指纹；`test_add_evidence` 把已引入却未传的 sample_evidence 传给 create

## 5. 结案验证

```text
tests/contribution_test.py + tests/integration/test_complete_workflow.py：39 passed
Gate 1 ruff（CI 同命令 src tests ../tests）：绿
Gate 2 pytest -m v01：169 passed, 5 skipped
canon_guard：6 passed
Gate 3 全量（CI 同范围 tests ../tests）：见本次提交的 CI 运行
Gate 4 GitHub Actions：待 push 确认
```

## 6. 复现（结案前）

```bash
cd moodify-core-package
PYTHONPATH=src python -m pytest tests/contribution_test.py tests/integration/test_complete_workflow.py -q
```

## 7. 遗留与边界

- 参考包五维 reputation 在参考 schema 中嵌套于 `dimensions`，镜像与其测试采用顶层扁平 + adjustments。本次按"测试即契约"保留扁平形状；若未来与 web 3.0 网络主链对接，需按参考包收紧——这是一次独立提案，不在本单范围。
- 参考包位于仓库未跟踪目录 `web 3.0/`，权威 schema 尚未进 git；长期应将其纳入版本管理或至少在镜像旁放置 schema 副本。
