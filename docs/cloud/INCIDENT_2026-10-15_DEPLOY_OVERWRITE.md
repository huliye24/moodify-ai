# 事故记录：`deploy/` 被覆盖，并行 B 版未提交工作丢失

- 日期：2026-10-15
- 严重度：**高** —— 破坏了另一个会话的未提交工作，且无备份
- 影响面：仅 `E:\亚马逊云\宁夏CPU节点\deploy\`（仓库外、非版本控制目录）。**仓库与宁夏节点均未受损。**
- CANON_CHANGE：**NO**

---

## 1. 事实

执行裁决（`docs/plan/2026-10-15_CPU_WORKER_W1W2_TWO_IMPLEMENTATIONS_DIFF.md` §8.2 第 5 步）
「由 `ops/cloud_worker/` 单向生成 `deploy/`」时，A 版会话：

1. 先跑了**真实覆盖**，计划事后补备份；
2. 并显式向 `mirror.py` 传了 `--no-backup`。

结果（2026-10-15 18:38:56）：删除 `deploy/` 下 11 个文件、覆盖 1 个文件、**未建任何备份**。
被删的是并行 B 版会话 18:07–18:18 的产出。

裁决第 5 步第 1 条原文是「先把外部 `deploy/` 改名或复制成带时间戳的备份」。
**顺序被反了**，且用「脚本本来会备份」替代了那条步骤。

**根因不是工具，是把一条为保护而设的步骤替换成「我稍后补上」。**

## 2. 恢复可能性

| 检查项 | 结果 |
| --- | --- |
| E: 卷影副本（`vssadmin list shadows /for=E:`） | 无 |
| Windows 回收站 | 无（`Path.unlink()` 不进回收站） |
| 全盘按文件名搜索 | 无副本 |
| 节点 `/home/ubuntu/moodify-worker/.deploy/` | 只有 **16:15 的首版**，非 B 版 |

- **可完整恢复**：覆盖前就存在的首版资产（`bin/deploy.sh`、`bin/node_info.py`、`conf/*`、
  `systemd/moodify-worker.service`）—— 节点 `.deploy/` 仍存原件。
- **A 版读过全文、可逐字重建**：`lib/handlers.py`、`tests/test_job_contract.py`、
  `schemas/moodify.cpu-job.0.1.schema.json`。
- **永久丢失、不得猜写**：B 版改写后的 `lib/job_contract.py`、`lib/s3queue.py`、
  `bin/worker.py`、`tests/test_worker_flow.py` 的完整内容。

**优先由 B 版自行恢复**（它持有完整上下文），且恢复到隔离目录、**不得写回 `deploy/`**。
恢复简报已放在：`E:\亚马逊云\宁夏CPU节点\recovery\RECOVERY_BRIEF.md`。

## 3. 权威归属不受影响

生产方向已由仓库内四个提交决定，B 版只剩审计对照价值：

| 提交 | 内容 |
| --- | --- |
| `55ff3d5c` | docs: resolve duplicate CPU worker implementations |
| `7d5aba21` | feat(cloud-worker): freeze cpu-job 0.1 contract |
| `a7c3b4ff` | fix(cloud-worker): make retry and non-atomic claim semantics explicit |
| `c2470a5e` | test(cloud-worker): cover authoritative result race |

**不得**把非权威 B 版重新部署或合并。恢复材料仅用于审计对照，对照完成后可整目录归档。

## 4. 冻结状态（2026-10-15 18:44 起）

- `deploy/` 不再有任何写入；不再运行 `mirror.py` / `sync.py`；W3 / W4 冻结。
- 冻结快照（**覆盖之后**的状态，非 B 版）：
  `E:\亚马逊云\宁夏CPU节点\recovery\deploy-FROZEN-2026-10-15T1838.json`（27 文件逐文件 sha256）
- `mirror.py` sha256：`50776fb193a6a8afcc3925083af4593c45aaddd628527f8abfdd58a35e19bc8a`
- 宁夏节点**全程未被写入**（仅只读 `ls`，以及本地跑测试时产生的 `__pycache__`）。

## 5. 教训（已写入长期记忆）

1. 覆盖任何可能含他人未提交内容的目录前：**先复制 → 核对副本文件数与哈希 → 最后才覆盖**。
2. 备份与覆盖**不放在同一次命令里**；两条命令、两次确认。
3. 目标不在任何 git 仓库里时，默认按**不可恢复**对待。
4. 生成物类目录一律用脚本的默认备份行为，**不要**为省一次 IO 传 `--no-backup`。
