# Moodify CPU-First 云计算面实施方案（交付 WorkBuddy）

- 日期：2026-10-15
- 状态：**APPROVED DIRECTION — 待 WorkBuddy 实施与验收**
- CANON_CHANGE：**NO**
- 适用节点：宁夏 EC2 `i-02d2c7bcf190ae84c`（私网 `172.31.43.176`；当前公网 `68.79.41.139`）
- 实例角色：`MoodifyExperimentWorkerRole`
- 关联方案：`docs/plan/2026-10-15_CLOUD_TOPOLOGY_PLAN_V02.md`

## 0. 人类决定与本方案边界

Phase 1 不启用原规划中的宁夏 GPU 节点，优先使用当前宁夏 CPU 节点承接计算面。这里的“CPU-First”是
当前运行与成本选择，不是否定长期 GPU Provider，也不改变 Moodify 的产品身份、One Core、Judge 权威或
`HEAR → JUDGE → ACT → VERIFY → BLIND COMPARE` 流程。若未来决定从公开产品身份中永久删除
“powered by GPU computing”，那是另一项 `CANON_CHANGE = YES`，不在本次任务内。

本次只建设一个可度量、可回滚的 CPU worker；禁止借机新增第二套 Core、第二套 Job authority、第二套
状态机或独立的质量判断逻辑。CPU/GPU 只是可替换的计算 Provider。

## 1. 已核验现实（2026-10-15）

| 项目 | 实测结果 |
| --- | --- |
| OS | Ubuntu 24.04.4 LTS |
| CPU | 8 vCPU，Intel Xeon Platinum 8375C @ 2.90 GHz |
| 内存 | 30 GiB，可用约 29 GiB；无 swap |
| 系统盘 | 290 GiB，总可用约 208 GiB |
| GPU | 无 NVIDIA GPU，`nvidia-smi` 不存在 |
| Python | 3.12.3；venv 已有 boto3 / soundfile / librosa / numpy |
| 音频工具 | ffmpeg 6.1.1、ffprobe 6.1.1 |
| 容器 | Docker 未安装；本方案不要求 Docker |
| Worker | `/home/ubuntu/moodify-worker` 已部署；systemd 已安装但 disabled/inactive |
| S3 队列 | `moodify-experiments/jobs/{pending,claimed,done,failed}/` |
| S3 权限 | `worker.py --check` 已返回 READY；两桶读写验证通过 |
| IAM | 角色已附加 `AdministratorAccess`（高风险现状；本任务不得扩大或复制凭据） |

结论：这台机器足够承担单并发转码、音频元数据提取、轻量分析、规则式 HEAR/JUDGE、报告生成、清单构建
和 S3 队列调度；不应在没有基准数据的情况下承诺实时分离、大批量 Demucs、模型训练或重型推理。

## 2. 目标架构

```text
Moodify Studio（Windows）
  ├─ 发布资产 ───────────────▶ S3 moodify-dataset
  ├─ 写入任务 JSON ──────────▶ S3 moodify-experiments/jobs/pending/
  └─ 轮询结果 JSON ◀────────── S3 moodify-experiments/jobs/done|failed/
                                      │
                                      ▼
                        宁夏 CPU Worker（当前节点）
                        ├─ claim（单并发、幂等）
                        ├─ 下载输入到每任务隔离目录
                        ├─ 调用唯一 Moodify Core / CLI
                        ├─ 生成测量、日志、证据和结果
                        └─ 上传结果并清理本地临时文件

香港控制面：只处理 KB 级 manifest / 元数据，不传输大音频
Moodify App：读取 manifest，再从对象存储读取音频；不直接调用 worker
GPU Provider：默认关闭；只有 CPU 基准触发明确升级阈值时才按任务启用
```

## 3. CPU 节点职责与禁止项

### 3.1 Phase 1 允许的任务

1. `probe`：ffprobe 媒体信息、时长、编码、采样率、声道、文件哈希。
2. `transcode`：经显式参数和输出校验的 WAV/FLAC → AAC/M4A；原始资产不覆盖。
3. `analyze`：调用仓库现有 Moodify Core/CLI 只读分析能力，输出 report/evidence。
4. `judge_before`：只允许调用现有权威 Judge 契约；证据不足必须返回 `HUMAN_REQUIRED` 或 `INCONCLUSIVE`。
5. `manifest`：生成/校验作品清单与资产引用，不复制一套 App 私有状态机。
6. `smoke`：用于验证 pending → claimed → done/failed 的无损小文件测试任务。

### 3.2 Phase 1 禁止的任务

- 模型训练、微调、常驻推理 API。
- 把 Demucs/分轨写成已经生产可用；MIP/可逆性门禁未通过时不得自动进入修音。
- 在 worker 内实现第二套 DSP、Judge、作品状态或发布权威。
- 自动把 `Generated` 判为 `finished`。
- 覆盖源文件、无记录删除 S3 资产、`aws s3 sync --delete`。
- 让 App 或香港服务器通过 SSH/HTTP 直连 worker。
- 把 EC2 的管理员角色凭据导出为长期 access key。

## 4. WorkBuddy 实施包

### W0 — 基线与安全护栏（先做，不改业务行为）

1. 阅读根 `AGENTS.md`、四份 Canon 入口、V02 和本文件。
2. 运行并保存基线：
   - `git status --short`
   - `ssh moodify-cpu '.../worker.py --check'`
   - `ssh moodify-cpu '.../node_info.py'`
   - `systemctl is-enabled/is-active moodify-worker`
3. 不修改用户现有未提交文件；不在日志打印 STS 临时凭据。
4. 为任务工作目录设置硬上限和清理策略：每个任务独立目录，成功/失败都执行 finally 清理；结果先上传再清理。
5. systemd 继续保持 disabled，直至 W3 冒烟通过。

**验收：** 生成带时间戳的基线记录；自检 READY；服务仍未常驻；无云端对象被删除。

### W1 — 固化 Job Contract（只新增一种权威任务契约）

在现有 S3 队列上扩展，不创建新队列系统。任务 JSON 最低字段：

```json
{
  "schema_version": "moodify.cpu-job/0.1",
  "job_id": "uuid",
  "request_id": "idempotency-key",
  "job_type": "probe|transcode|analyze|judge_before|manifest|smoke",
  "input": {"bucket": "...", "key": "...", "sha256": "..."},
  "output_prefix": "results/<job_id>/",
  "created_at": "ISO-8601",
  "core_version": "resolved-at-runtime",
  "limits": {"timeout_seconds": 1800, "max_input_bytes": 2147483648}
}
```

结果必须包含：`status`、输入哈希、输出哈希、开始/结束时间、耗时、峰值内存（可测则记录）、Core/工具版本、
证据路径、错误分类、是否可重试。任何无法对齐的指标写 `not_alignable`，不得补算。

**验收：** schema 校验覆盖合法、缺字段、未知 job_type、重复 request_id、哈希不符、超限输入六类用例。

### W2 — 让 Worker 调用 Core，而不是自造处理逻辑

1. 把当前 worker 的任务分发改成 adapter：每个 `job_type` 映射到已有 Core/CLI 能力。
2. worker 只负责 claim、下载、超时、资源限制、调用、上传、状态转换与证据封装。
3. 对尚无 Core 实现的任务返回稳定失败码，例如 `TUNABLE_CORE_NOT_AVAILABLE`，不得留假产物。
4. 写入结果采用临时键 → 校验 → 最终结果键；重复 request_id 返回既有结果，不重复执行。
5. 保留 S3 claim 的非原子事实，增加过期 claimed 回收测试与双 worker 竞争测试。

**验收：** 本地单元测试全绿；相同任务重复投递只产生一个权威结果；worker 崩溃重启后任务可恢复。

### W3 — CPU 冒烟闭环（先 `--once`，后常驻）

1. 用仓库内可公开、体积小的测试音频或生成的正弦测试夹投递 `smoke`、`probe`、`analyze`。
2. 仅运行 `worker.py --once`，确认 `pending → claimed → done` 和失败路径。
3. 校验源对象不变、结果哈希一致、失败任务进入 `failed/` 且包含可操作错误。
4. 记录 CPU 时间、墙钟时间、峰值内存、输入大小、输出大小。
5. 连续 10 个小任务无丢失、无重复、无残留后，才允许：
   `sudo systemctl enable --now moodify-worker`。

**验收：** 10/10 完成或按设计失败；零静默丢失；服务重启后仍可处理；日志轮转有效。

### W4 — Studio 接入（先可开关，再切换）

1. 先实现 V02 的 `PUBLISH_BACKEND=scp|s3`，默认保持 `scp`。
2. 增加独立的 `COMPUTE_BACKEND=local|cpu_queue`，默认 `local`；非法值回退 `local` 并显式告警。
3. Studio 向 S3 写任务时只写契约 JSON，不直连 EC2，不把 AWS 凭据写入应用配置。
4. UI 显示阶段、排队、运行、完成、失败、可重试和 evidence 链接；不得只显示无限 spinner。
5. App 不感知计算节点；发布到 App 仍以作品清单和发布状态为唯一入口。

**验收：** 两个开关互不耦合；`local/scp` 完全保留旧行为；CPU worker 停机时 Studio 明确显示排队而不是数据丢失。

### W5 — 性能基准与 GPU 升级门槛

建立三档数据集：短夹 30 秒、标准单曲 3–5 分钟、长曲 8–10 分钟。每类至少 3 个样本，分别测 probe、
transcode、analyze；如果分离仍未达到 Canon 门禁，不做虚假分离基准。

GPU 只在以下任一条件被真实证据触发时进入单独提案：

- 标准单曲某一已实现任务 P95 墙钟时间 > 15 分钟；
- 持续队列积压 > 10 首或最老任务等待 > 30 分钟；
- 单任务 CPU 内存需求逼近 24 GiB，导致频繁 OOM/交换；
- 已批准的 Provider 明确要求 CUDA，且无 CPU fallback；
- 同一任务在 GPU 上经基准证明性价比或交付时限显著优于 CPU。

未触发阈值时不启 GPU。触发后 GPU 仍消费相同 Job Contract、写相同 evidence，不得成为第二套系统。

## 5. 建议运行参数

| 参数 | Phase 1 建议值 | 理由 |
| --- | --- | --- |
| 并发 | 1 | 先保证证据、恢复和内存稳定 |
| Poll 间隔 | 10 秒 | 内部生产可接受，减少空轮询 |
| 单任务超时 | 30 分钟 | 覆盖普通分析，超时可见 |
| MemoryMax | 24G | 给 OS/S3/日志留约 6G |
| CPUQuota | 700% | 给系统保留约 1 vCPU |
| Nice | 5 | 避免批处理压死维护操作 |
| 本地任务盘上限 | 150G | 保留系统和回滚空间 |
| 成功本地保留 | 0 | 结果写 S3 后清理，S3 为数据面 |
| 失败本地保留 | 最多 24 小时且脱敏 | 便于诊断，之后清理 |
| 重试 | 最多 2 次，指数退避 | 避免坏任务 crash loop |

若 systemd 现有值与上表不同，WorkBuddy 必须先报告 diff，再做最小修改并保留回滚副本。

## 6. 安全、回滚与失败语义

1. 当前 `AdministratorAccess` 是人类已批准的运行现状，但不是 worker 的业务需求证明。WorkBuddy 不得创建
   access key、不得把该权限复制给其他节点、不得顺手改 IAM。后续降为最小权限需另开任务并经人类批准。
2. 所有云端部署先备份；本地权威副本仍位于 `E:/亚马逊云/宁夏CPU节点/deploy/`。
3. 应用回滚：`COMPUTE_BACKEND=local`；发布回滚：`PUBLISH_BACKEND=scp`。
4. Worker 回滚：`sudo systemctl disable --now moodify-worker`，恢复上一版 deploy 目录与 unit 后 daemon-reload。
5. 数据回滚：不删除输入；新结果写新前缀；不覆盖当前基准。失败结果保留错误证据。
6. 任一任务证据不足、校验失败或 Core 不可用时，必须进入 `FAILED`、`INCONCLUSIVE` 或
   `HUMAN_REQUIRED`，不能为了“跑通”伪造完成。

## 7. Definition of Done

本方案完成不是“服务启动了”，而是同时满足：

- 当前 CPU 节点身份、S3、工具与资源自检可重复；
- 单一 Job Contract 有 schema、幂等、超时、恢复和错误语义；
- worker 通过 adapter 调用唯一 Core；
- 10 个冒烟任务端到端无丢失、无重复、可追溯；
- Studio 能在 `local` 与 `cpu_queue` 间安全切换并显示真实状态；
- App 无需知道计算节点；作品仍经唯一发布清单进入播放端；
- 每个结果带输入/输出哈希、版本、参数、日志与 evidence；
- CPU 性能基准形成后，才决定是否需要 GPU；
- 回滚演练至少执行一次并留下记录。

## 8. 给 WorkBuddy 的直接执行指令

> 在 `E:\\moodify` 执行 `docs/plan/2026-10-15_CPU_FIRST_CLOUD_EXECUTION_PLAN.md`。先读根
> `AGENTS.md` 与 Canon 入口，先做 W0 基线，再依序执行 W1–W5；禁止跳过验收、禁止启用 GPU、禁止
> 新建第二套 Core/队列/状态机、禁止把未实现能力写成已完成。使用 `ssh moodify-cpu` 操作
> `68.79.41.139`，但不要在输出中暴露凭据。每完成一个工作包，提交：改动文件、命令、测试结果、云端
> 运行证据、失败与回滚状态。任何涉及 IAM、删除 S3 对象、修改香港生产服务、启用收费资源或改变 Canon
> 的动作必须暂停并请求人类确认。先以 `worker.py --once` 完成 10 个冒烟任务，验收通过后才允许启用
> systemd 常驻。若 Core 不支持某任务，返回 `TUNABLE_CORE_NOT_AVAILABLE`，不得伪造产物。

## 9. 本次不做

- 不启 GPU，不安装 CUDA。
- 不部署新的公网 API，不开 80/443，不处理 ICP。
- 不把管理员权限视为架构依赖。
- 不更改香港生产控制面。
- 不删除现有 GPU 资产或历史方案；只将其降为按证据触发的可替换 Provider。
- 不修改公开产品身份和 Canon。
