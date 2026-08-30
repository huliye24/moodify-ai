# TASK — MOOD AGENTS 018

## Gate 0 — Dependency Check

必须确认 017 已完成并被接受。

至少读取：

```text
docs/mood/CURRENT_CANON.md
docs/mood/network/017_FINAL_REPORT.md
docs/mood/contribution/016_FINAL_REPORT.md
docs/mood/passport/015_FINAL_REPORT.md
```

必须确认 017 已预留 Agent metric / activity contract。

如果缺少：

```text
BLOCKED_BY_MOOD_NETWORK_017
```

停止，不允许前端先造假 Agent 数据。

---

## Phase A — Preflight

```bash
git fetch --all --prune
git status
git branch --show-current
git rev-parse HEAD
git branch -vv
git worktree list
```

并发要求：

- 不 reset --hard
- 不 git clean
- 不 force push
- 独立 worktree
- 分支建议：`codex/mood-agents-018`

---

## Phase B — Existing Agent Capability Audit

扫描仓库所有 AI / agent / automation / worker / assistant 相关代码和文档。

重点搜索：

```text
agent
agents
worker
automation
orchestrator
llm
model
reasoning
tool
proof
task runner
```

目标：

- 识别现有真实 AI Agent / Worker 能力
- 区分“后台服务”与“网络 Agent”
- 不把普通 API worker 自动包装成 Agent

建立：

```text
docs/mood/agents/
├── 018_AGENT_INVENTORY.md
├── 018_AGENT_IDENTITY_MODEL.md
├── 018_CAPABILITY_MODEL.md
├── 018_STATUS_MODEL.md
├── 018_PROOF_MODEL.md
├── 018_OPERATOR_POLICY.md
├── 018_SECURITY_MODEL.md
├── 018_NETWORK_INTEGRATION.md
└── 018_FINAL_REPORT.md
```

---

## Phase C — Canonical Agent Model

推荐：

```ts
type AgentStatus =
  | "draft"
  | "active"
  | "paused"
  | "degraded"
  | "offline"
  | "retired";

type AgentCapability =
  | "audio-analysis"
  | "research"
  | "documentation"
  | "code-assistance"
  | "proof-verification"
  | "curation"
  | "task-assistance"
  | "node-operations"
  | "other";

type AgentRecord = {
  id: string;
  slug: string;
  name: string;
  description: string;
  status: AgentStatus;
  operatorResidentId?: string;
  operatorOrganizationId?: string;
  capabilities: AgentCapability[];
  runtimeType?: string;
  modelProvider?: string;
  modelName?: string;
  version?: string;
  public: boolean;
  createdAt: string;
  updatedAt: string;
};
```

不要把 API key、system prompt、secret endpoint 放进 public record。

---

## Phase D — Agent Identity

Agent ID 必须：

- 稳定
- 与模型 provider 解耦
- 与具体 API key 解耦
- 不因模型升级而变化
- 可保留版本历史

推荐：

```text
agent_listener_001
agent_curator_001
agent_auditor_001
```

或 UUID + slug。

必须区分：

```text
Agent Identity
Agent Runtime
Agent Version
Agent Operator
```

---

## Phase E — Operator / Ownership Policy

每个 active Agent 必须关联：

```text
Resident Operator
or
Organization / System Operator
```

至少记录：

- operator
- createdBy
- approvedBy（若需要）
- responsibility contact / role
- status changes

Agent 不能“无主运行”。

---

## Phase F — Capability Registry

每个 capability 必须有清晰定义。

示例：

### audio-analysis
输入音频，输出可审计分析结果。

### proof-verification
检查提交 evidence 的格式、完整性和一致性，但不做最终 approve。

### research
整理研究资料和生成结构化研究摘要。

### code-assistance
协助代码实现，但不能直接成为 governance authority。

禁止模糊能力：

```text
super-intelligence
all-purpose
guaranteed profit
autonomous governance
```

---

## Phase G — Agent Runtime Status

状态来源必须真实。

推荐状态：

```text
active
paused
degraded
offline
retired
```

状态可来自：

- heartbeat
- last successful task
- operator state
- health endpoint

至少记录：

```text
lastSeenAt
lastTaskAt
lastSuccessAt
lastErrorAt
healthSummary
```

如果没有真实 heartbeat：

不要显示 “Online”。

显示：

```text
Registered
Runtime status unavailable
```

---

## Phase H — Agent Task Linkage

Agent 可以参与：

```text
Contribution Task
Internal Protocol Task
Research Task
Verification Task
```

推荐建立：

```ts
type AgentTaskRun = {
  id: string;
  agentId: string;
  taskType: string;
  externalTaskId?: string;
  status:
    | "queued"
    | "running"
    | "completed"
    | "failed"
    | "cancelled";
  startedAt?: string;
  completedAt?: string;
  resultRef?: string;
};
```

Agent task execution 不等于 Contribution approval。

---

## Phase I — Proof / Evidence

每个有价值 Agent activity 应尽可能产生：

```text
Proof Record
```

例如：

```ts
type AgentProof = {
  id: string;
  agentId: string;
  taskRunId?: string;
  proofType:
    | "artifact"
    | "report"
    | "commit"
    | "analysis"
    | "verification"
    | "other";
  uri?: string;
  hash?: string;
  summary: string;
  createdAt: string;
};
```

如果没有可验证 proof：

不要产生 Reputation。

---

## Phase J — Contribution Integration

Agent 可以：

- 提交 evidence
- 辅助 Resident 完成 task
- 独立提交 machine contribution（若 policy 允许）
- 提供 review suggestion

但 v1 禁止：

- Agent approve 自己
- Agent 自动 approve 他人
- Agent 自动写 Reputation
- Agent 自动发 Pending Reward

所有 Reputation / Reward 必须经过 016 的权威流程。

---

## Phase K — Agent Reputation

建议先建立独立：

```text
Agent Reputation
```

不要与 Resident Reputation 混为同一字段。

可由：

- approved agent contributions
- verified task success
- uptime / reliability（后续）
- quality review

构成。

但 018 可以只建立接口和事件模型，不必马上做复杂评分。

---

## Phase L — `/agents`

建立：

```text
/agents
```

展示：

```text
MOOD AGENT NETWORK

Registered Agents
Active
Degraded
Offline

Agent Cards:
- Name
- Capability
- Status
- Operator
- Version
- Last Activity
```

只展示真实 registry 数据。

---

## Phase M — `/agents/[slug]`

详情页：

```text
Agent Name
Status
Operator
Capabilities
Version
Runtime
Recent Tasks
Recent Proofs
Contribution History
Health
Source / Repository
```

禁止展示：

- API key
- secret prompt
- private endpoint
- hidden chain-of-thought
- internal credentials

---

## Phase N — Network Observatory Integration

017 `/network` 应开始显示真实：

```text
Agents Total
Agents Active
Agents Degraded
Last Agent Activity
```

并支持 public events：

```text
AgentRegistered
AgentStatusChanged
AgentTaskCompleted
AgentProofSubmitted
```

如果 registry 中真实 agent 数是 0：

可以显示 0。

如果 registry 不可读取：

显示 unavailable。

---

## Phase O — Agent Registration

v1 推荐 admin / operator-controlled registration。

不要开放匿名 public self-register 立刻变 active。

流程：

```text
Draft
↓
Review
↓
Active
```

可选：

```text
Resident proposes agent
↓
Admin/Protocol review
↓
Register
```

治理化放到未来 package。

---

## Phase P — Security

至少审查：

- prompt injection
- tool abuse
- SSRF
- arbitrary command execution
- secret leakage
- privilege escalation
- agent impersonation
- forged heartbeat
- fake proof
- duplicate task completion
- recursive agent loops
- runaway cost
- unbounded tool calls
- autonomous funds movement

硬约束：

> 018 Agent 不允许拥有资金操作权限。

如果现有 Agent 有 production credentials：

只做 inventory / boundary，不复制 secret。

---

## Phase Q — Cost / Resource Guard

记录可观察字段：

```text
taskCount
successCount
failureCount
lastActivityAt
optional tokenUsage
optional computeUsage
```

但注意：

- 不公开 provider API secret
- 不必公开精确内部成本
- 不做“Agent 盈利率”

若有 usage metrics，作为运维数据，不作为投机叙事。

---

## Phase R — Documentation

新增：

```text
docs/mood/agents/
├── 018_AGENT_INVENTORY.md
├── 018_AGENT_IDENTITY_MODEL.md
├── 018_CAPABILITY_MODEL.md
├── 018_STATUS_MODEL.md
├── 018_PROOF_MODEL.md
├── 018_OPERATOR_POLICY.md
├── 018_SECURITY_MODEL.md
├── 018_NETWORK_INTEGRATION.md
└── 018_FINAL_REPORT.md
```

---

## Phase S — Tests

### INV-018-01
每个 active Agent 有稳定 ID。

### INV-018-02
每个 active Agent 有 operator。

### INV-018-03
没有 heartbeat 时不显示 Online。

### INV-018-04
Agent proof 必须绑定真实 task / activity。

### INV-018-05
Agent 不能 approve 自己的 Contribution。

### INV-018-06
Agent 不能直接修改 Resident Reputation。

### INV-018-07
Agent 不能直接触发 Pending Reward settlement。

### INV-018-08
Public Agent API 不泄露 secrets。

### INV-018-09
Unknown Agent status fail closed / unavailable。

### INV-018-10
Network Agent metrics 来自真实 registry。

### INV-018-11
Agent registry 不依赖未来 MOOD Token。

### INV-018-12
Agent 无资金操作权限。

---

## Phase T — Final Output

严格使用 `OUTPUT_TEMPLATE.md`。

给 019 Nodes Registry handoff：

- Agent identity contract
- runtime status contract
- heartbeat pattern
- proof model
- network metrics integration
- operator linkage
