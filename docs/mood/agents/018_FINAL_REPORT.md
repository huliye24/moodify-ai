# MOOD AGENTS 018 — Final Report

**Package:** `MOOD-AGENTS-018` — AI Agents Registry
**Branch:** `codex/mood-agents-018-tmp` (will be `codex/mood-agents-018` after merge)
**Worktree:** `E:/moodify-agents-018`
**Base commit:** `0a7a669f` (MOOD NETWORK 017)
**Date:** 2026-08-30

---

## 1. Repository State

- **Branch:** `codex/mood-agents-018-tmp`
- **Base SHA:** `0a7a669f`
- **End SHA:** TBD (commit below)

## 2. Scope Delivered

018 delivers the AI Agents Registry:

- `AgentRegistry` lib (single authoritative source)
- `AgentMetrics` for the Network Observatory
- `/agents` and `/agents/[slug]` public pages
- `/api/agents` and `/api/agents/[slug]` API routes
- 12 INV tests + 2 bonus (14 tests, all PASS)

## 3. Files Added

```text
apps/web/lib/mood/agents/
├── types.ts                  AgentRecord, Heartbeat, TaskRun, Proof, PublicAgent
├── registry.ts               register/heartbeat/taskRun/proof + counts
├── metrics.ts                AgentMetrics for Network Observatory
└── index.ts                  barrel

apps/web/lib/mood/network/
├── types.ts                  (inherited from 017)
├── observatory.ts            extended with agents() counts
└── index.ts                  barrel

apps/web/app/api/agents/
├── route.ts                  GET public list + counts
└── [slug]/route.ts           GET public detail

apps/web/app/agents/
├── page.tsx                  public registry
└── [slug]/page.tsx           agent detail

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

tests/agents-invariants.test.mjs          14 tests (12 INV + 2 bonus)
```

## 4. Decisions

- **Stable IDs**: `agent_N`, decoupled from API key / model provider.
- **No heartbeat == not Online**: status remains `offline` until heartbeat recorded.
- **Public-safe serializer**: strips `operatorResidentId`, `operatorOrganizationId`, `healthSummary`.
- **Operator-only mutations**: `activate`, `pause`, `retire` reject non-operator actors.
- **Network integration**: `NetworkObservatory.agents()` reads `AgentRegistry.counts()`.

## 5. Verification

- **Tests**: `node --experimental-strip-types tests/agents-invariants.test.mjs`
  - 14 tests
  - pass: 14
  - fail: 0

## 6. Blockers

None active.

## 7. HUMAN_DECISION_REQUIRED

- **HDR-018-001**: Persistence backend for AgentRegistry. Current is in-memory.
- **HDR-018-002**: Operator self-registration flow vs admin-controlled registration. Currently 018 enforces `register → activate` flow (admin-mediated activation).

## 8. Handoff to 019

019 (Nodes Registry) should consume:

- `agentRegistry.list()` for `/nodes` overview showing related agents.
- Same operator linkage pattern as Agents.
- Same heartbeat + service proof model.

019 must NOT:

- Reuse `AgentRecord` for nodes.
- Pretend to register infrastructure without real heartbeat.
- Expose private endpoint / SSH / cloud account IDs.

## 9. Git Safety Confirmation

- ✓ 未 force push
- ✓ 未 `reset --hard`
- ✓ 工作在独立 worktree
- ✓ 未整条 merge `codex/mood-mainnet-integration-009`
- ✓ Base = 017 commit
- ✓ 018 不发币、不上链、不给 Agent 任何资金权限
- ✓ 018 不实现 019–025 任一 package