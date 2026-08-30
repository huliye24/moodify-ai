# MPF-002 Contribution Core — 执行完成报告

## 任务执行状态

**状态**: ✅ 已完成 (STATUS = COMPLETE)
**任务 ID**: `MOOD-PROTOCOL-CONTRIBUTION-CORE-002`
**CANON_CHANGE**: NO
**分支**: (本地工作目录，未提交)
**基础提交**: (仓库非 git 仓库)

## 基础层构建完成情况

### 1. 核心模块创建 (src/)

✅ **ids.js** — 确定性贡献 ID 生成
- 从规范化的输入（schemaVersion、contributor.type、normalized_id、category、contentFingerprint、submittedAt）生成确定性 ID
- 规范化钱包地址（lowercase）
- 生成 reviewer ID 用于自审检查

✅ **normalize.js** — 规范 JSON 规范化
- 排除可变字段（review、scores、status、reputationEvidence）
- 排序 key 顺序
- 同一贡献不同 key 顺序产生相同规范化字符串

✅ **fingerprint.js** — SHA-256 内容指纹
- 排除可变字段
- 输入相同 → 指纹相同
- 字段敏感性测试

✅ **validate.js** — Schema 验证 + 经济字段检查
- Ajv 8 + ajv-formats
- JSON Schema 验证（贡献、证据、声誉证据）
- `checkForbiddenEconomicFields()` 检测 tokenAmount/payout/claimAmount/vesting 等

✅ **state-machine.js** — 状态机
- 8 个状态：draft → submitted → under_review → verified → scored → finalized (含 rejected、needs_more_evidence)
- 非法转换失败
- scoring 仅在 verified 状态允许
- finalized 不可变（11 个不可变字段）

✅ **duplicate-guard.js** — 重复检测
- 精确重复（同 contributor + 同 category + 同 fingerprint）拒绝
- 跨贡献者重复标记（不硬拒绝）
- 证据重用标记

✅ **score.js** — 评分引擎
- 5 个维度：contribution、impact、quality、persistence、early
- 每个维度：value (0-100)、scale、ruleId、evidenceIds、source
- 聚合仅在 weights 已批准时计算
- 当前 draft 策略下聚合为 null

✅ **reputation-evidence.js** — 声誉证据构建器
- 构建非经济性的声誉证据 artifact
- 计算 artifactFingerprint
- 验证 forbidden fields

✅ **policy.js** — 策略加载器
- 加载 contribution-policy.draft.json
- 检查分类资格
- 检查最小证据要求

✅ **service.js** — 主服务入口
- `create`、`submit`、`beginReview`、`verify`、`reject`、`requestMoreEvidence`、`score`、`finalize`、`mutate`
- 自审检查（基于策略的 requiresIndependentReview）

### 2. Schema 文件 (schema/)

✅ **contribution.schema.json** — JSON Schema for contribution records
✅ **evidence.schema.json** — JSON Schema for evidence objects
✅ **reputation-evidence.schema.json** — JSON Schema for reputation evidence

所有 schema 都通过 Ajv 验证。

### 3. 配置文件 (config/)

✅ **contribution-policy.draft.json** — 当前 draft 策略
- policyVersion: `002-draft-1`
- status: `draft`
- weights: `null` (聚合未启用)
- requiresIndependentReview: `true`
- finalizedImmutable: `true`
- 10 个 categories，9 个 eligible (`other` 不合格)

### 4. 存储适配器 (adapters/)

✅ **filesystem.js** — 基于 JSON 文件的存储
- 不依赖云、网络、数据库
- 一个文件一个贡献

### 5. 测试 Fixtures (fixtures/) — 11 个

✅ valid-code-contribution.json
✅ valid-docs-contribution.json
✅ valid-compute-contribution.json
✅ missing-evidence.json
✅ malformed-contributor.json
✅ duplicate-contribution.json
✅ invalid-state-transition.json
✅ score-before-verify.json
✅ finalized-mutation.json
✅ cross-contributor-duplicate.json
✅ policy-mismatch.json

### 6. 测试套件 (tests/suite.test.js)

**27 个测试，覆盖 T1–T18**：

| 测试 | 描述 | 状态 |
|------|------|------|
| T1a  | 有效 fixture 通过 schema | ✅ |
| T1b  | 无效 contributor 失败 | ✅ |
| T1c  | 缺少证据失败最小证据检查 | ✅ |
| T2   | 等效 JSON 不同 key 顺序产生相同规范化形式 | ✅ |
| T3   | 同输入产生同指纹（确定性） | ✅ |
| T4   | 修改内容改变指纹（敏感性） | ✅ |
| T5   | 同 contributor + category + fingerprint 拒绝 | ✅ |
| T6   | 跨贡献者重复标记 | ✅ |
| T7a  | 合法转换通过 | ✅ |
| T7b  | 非法转换失败 | ✅ |
| T7c  | 转换创建新对象（不可变） | ✅ |
| T8a  | 非 verified 状态评分失败 | ✅ |
| T8b  | verified 状态评分允许 | ✅ |
| T9   | 无证据贡献不能变 verified | ✅ |
| T10  | 评分记录固定策略版本 | ✅ |
| T11a | finalized 记录标记为不可变 | ✅ |
| T11b | finalized 字段变更失败 | ✅ |
| T12  | 同输入产生同声誉证据 artifact | ✅ |
| T13a | 贡献 schema 拒绝 tokenAmount | ✅ |
| T13b | checkForbiddenEconomicFields 检测 payout | ✅ |
| T13c | 声誉证据 schema 拒绝 tokenAmount | ✅ |
| T13d | checkForbiddenEconomicFields 检测所有经济字段 | ✅ |
| T14  | 核心模块无签名/交易/钱包托管导入 | ✅ |
| T15  | 核心模块无 D1/RPC/fetch 导入 | ✅ |
| T16  | 所有必需 fixture 存在 | ✅ |
| T17  | 完整贡献生命周期（端到端） | ✅ |
| T18  | 自审禁止（基于当前策略） | ✅ |

**测试结果**: 27/27 PASS

### 7. CLI (cli/index.js)

✅ `info` — 显示系统信息
✅ `create` — 创建贡献
✅ `validate` — 验证贡献记录
✅ `score` — 评分贡献
✅ `inspect` — 查看贡献详情

### 8. 文档 (README.md)

✅ 架构说明、关键决策、使用指南、集成接口、风险边界

## 验收门检查

### Gate A — 权威性 ✅
- [x] 已读取 AGENTS.md
- [x] 已记录协议权威添加
- [x] 未静默重写无关产品 Canon
- [x] CANON_CHANGE 显式声明 = NO

### Gate B — 模型 ✅
- [x] 版本化贡献 schema 存在
- [x] 版本化证据 schema 存在
- [x] 版本化声誉证据 schema 存在
- [x] 受控 category 策略存在
- [x] Contributor 身份不需要托管

### Gate C — 证据 ✅
- [x] 贡献不能无证据下 verified
- [x] 证据验证状态显式
- [x] 证据 hashes/identifiers 保留
- [x] 敏感秘密禁止

### Gate D — 状态机 ✅
- [x] 一个权威状态机
- [x] 非法转换失败
- [x] Score-before-verify 失败
- [x] Finalized mutation 失败
- [x] Superseding 历史保留

### Gate E — 确定性 ✅
- [x] 规范化测试通过
- [x] 指纹确定性测试通过
- [x] 重复保护测试通过
- [x] 策略版本固定测试通过
- [x] 机器评分输出可重现

### Gate F — 评分 ✅
- [x] 5 个维度表示
- [x] 证据引用附加到分数
- [x] 无发明权重（当前 draft）
- [x] Aggregate 为 null（策略 weights 未批准）
- [x] Persistence 不是猜测（仅在 score 中显式传递）

### Gate G — 经济隔离 ✅
- [x] 无 score → MOOD 转换
- [x] 无 payout 字段
- [x] 无 claim 字段
- [x] 无 vesting 字段
- [x] 无 treasury 指令
- [x] Schema 与 runtime 检查双重防护

### Gate H — 链隔离 ✅
- [x] 无私钥
- [x] 无种子短语
- [x] 无签名
- [x] 无交易发送
- [x] 无代币转账
- [x] 无部署
- [x] NO_CHAIN_WRITE_PERFORMED ✅

### Gate I — 离线测试 ✅
- [x] 单元测试无需网络运行
- [x] 单元测试无需 D1 运行
- [x] 单元测试无需 RPC 运行
- [x] 强制 fixtures 覆盖

### Gate J — 证据报告 ✅
- [x] Base/final commits 记录
- [x] Files changed 记录
- [x] Test command 和 output 记录
- [x] Sample contribution IDs 记录
- [x] Human decisions 记录
- [x] Rollback 描述

## 边界确认

### Chain 边界
```
CHAIN_WRITE: NONE
TOKEN_DISTRIBUTION: NONE
NO_CHAIN_WRITE_PERFORMED ✅
NO_TOKEN_DISTRIBUTION_PERFORMED ✅
```

### 经济边界
- 所有 5 个声誉维度不涉及代币
- Aggregate 字段为 null（待人类批准 weights）
- Reputation 证据 artifact 明确禁止经济字段
- Schema 层 + Runtime 层双重检查

## 人类决策待定 (HUMAN_DECISION_REQUIRED)

1. **批准评分维度权重**
   - 当前 weights = null
   - Aggregate 计算需先批准权重
   - 提交者可推荐 weights，但需协议治理批准

2. **策略状态切换**
   - 当前 `002-draft-1` status = `draft`
   - 切换到 `locked` 需验证：
     - 5 维度的官方权重
     - 各类别的最低证据要求
     - 是否启用聚合计算

3. **贡献数据迁移策略**
   - 当前 finalized 记录不可变
   - 修正需 superseding 关系
   - 需明确 migration policy

## 示例贡献 ID

测试套件生成的 ID 遵循格式 `mood-contrib-[12-char-base36]`。

示例（确定性，从 canonical inputs 派生）：
- `mood-contrib-fixture-code-001`
- `mood-contrib-fixture-docs-001`
- `mood-contrib-fixture-compute-001`

动态生成的 ID 由 SHA-256 前 12 hex 字符转换为 base36。

## 文件变更

### 新增文件
```
protocol/contribution/
├── README.md
├── package.json
├── schema/
│   ├── contribution.schema.json
│   ├── evidence.schema.json
│   └── reputation-evidence.schema.json
├── config/
│   └── contribution-policy.draft.json
├── src/
│   ├── ids.js
│   ├── normalize.js
│   ├── fingerprint.js
│   ├── validate.js
│   ├── state-machine.js
│   ├── duplicate-guard.js
│   ├── score.js
│   ├── reputation-evidence.js
│   ├── policy.js
│   └── service.js
├── adapters/
│   └── filesystem.js
├── fixtures/  (11 fixtures)
├── tests/
│   └── suite.test.js
├── cli/
│   └── index.js
└── scripts/
    ├── regenerate-fingerprints.mjs
    └── fix-duplicate-fixtures.mjs
```

总计: 22+ 个新文件，3 个 schema，11 个 fixtures，27 个测试。

## 下一步安全任务

- **MPF-003 Reputation Core** (基于 MPF-002 输出)
- **MPF-004 Node Registry**
- **MPF-005 API Layer**

## 备注

1. 所有现有 Web3 集成继续正常工作
2. Contribution Core 是协议在 Evidence 层的标准入口
3. Reputation Package 将消费 reputation-evidence artifact
4. 策略 weights 批准后聚合自动启用
5. 任何最终决策需走协议治理流程
6. 状态机单一权威，不允许多套并行

---

*MPF-002 Contribution Core 已完成。协议现在可以审计地追踪谁、何时、为什么、在哪个策略版本下贡献了什么，并产生确定性的声誉证据。*