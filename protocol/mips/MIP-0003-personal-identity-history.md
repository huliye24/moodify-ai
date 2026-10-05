# MIP-0003 — Personal Identity, Account and History Sync

**Status:** DRAFT
**Type:** Protocol / Data authority / Privacy contract
**Created:** 2026-10-04
**Canon impact:** `CANON_CHANGE = YES`（见 `docs/canon/CANON_CHANGELOG.md` 2026-10-04 条目）
**Human approval:** 2026-10-04，人类批准 Identity / Account / Personal History / Desktop history sync
**Implementation status:** 本地可验证部分为 IMPLEMENTED；真实服务能力 `DEPLOYMENT_BLOCKED`（§Unresolved 1）

---

## Abstract

本 MIP 冻结 Moodify 的**个人身份与作品历史**契约：Desktop 可以拥有账户、可以把自己的作品历史
同步到账户私有空间，并在另一台安装上看见它。它同时冻结**不允许**发生的事：默认上传音频、
把云端当成声音生产权威、把账户做成社交增长工具。

实现采用商品化服务（Supabase Auth + PostgreSQL + RLS），但契约以 provider 边界描述，
供应商可替换。

## Motivation

Desktop 已经能形成真实作品：A/B 候选（MIP-0002）、人工选择（`decisions.jsonl`）、
完成时刻与留存（`keepsake.json`）。这些事实目前只存在于单机 case 目录：换电脑、重装、
将来换到手机都会失去。让多年积累的作品历史消失，是这个产品最不该发生的失败。

账户是 continuity 的承载。它不是登录门槛，不是社交图谱，也不是音频托管。

## Specification

### 1. 三种权威（不可混为一体）

```text
A. 声音生产事实权威   本地 case 目录 + Core 产物
                     阶段权威 = moodify-desktop/src/pipeline.js
                     选择权威 = <case>/studio/tuning/decisions.jsonl
B. 账户身份权威       认证服务（Supabase Auth）的 user identity（sub / uuid）
C. 个人历史同步权威   账户私有的 append-only history_events + server projection
```

- C 是**记忆**，不是状态机。它不得把任何本地 case 推进到 CHOSEN / EXPORTED；
- 云端 `selected=A` 不替代本地 `decisions.jsonl`；冲突时**本地胜出**，云端只显示历史差异；
- 本地 case 被删除后 C 仍可存在，但只能显示为记忆（「音频仅在原设备」），不得呈现为可播放；
- 账户服务不可用（未配置 / 断网 / 停机 / 登录失败）时 A 必须完整可用。

### 2. Account identity vs local case identity

| | account identity | local case identity |
|---|---|---|
| 产生者 | 认证服务 | Desktop（case 目录名） |
| 权威 | 服务（B） | 本地磁盘（A） |
| 生命周期 | 跨设备、跨安装 | 单机磁盘；删除即消失 |
| 关联方式 | 每个启用同步的 case 写 `<case>/studio/account_link.json`（`work_id`） | 不写入任何账户凭据 |
| 唯一性 | 一个账户可关联多台设备的多个 case | 同一 case 只属于本机 |

本地 case 与账户的关联是**可选、可撤销**的：`account_link.json` 只保存 `work_id` 与同步状态，
不保存 email、token 或任何远端密钥。

### 3. 云端允许 / 禁止的数据

**允许（白名单）：** `work_id`、`title`、`duration_ms`、`completion_mode`（DEEP / FAST_STEREO_ONLY）、
`selected`（A / B / ORIGINAL）、`completed_at`、`inscription`（用户主动写下的一句话）、
粗粒度 history events（§5）。

**禁止：** 音频字节（wav/mp3/flac）、stems、MIDI、曲谱 / MusicXML、report / evidence 全文、
频谱图片、Mix Graph 全量参数、本地绝对路径、源音频 SHA-256、token / OTP / magic-link、
终端日志、搜索历史、收听时长、播放/暂停次数等细粒度行为。

`audio_availability` 恒为 `LOCAL_ONLY`：这是产品事实，不是可配置项。

### 4. 数据模型

见 `deployment/supabase/migrations/`（仓库内 SQL 迁移是权威）：

```text
profiles        (user_id pk → auth.users, display_name, created_at, updated_at)
works           (work_id pk, user_id, title, duration_ms, completion_mode, selected,
                 completed_at, inscription, audio_availability='LOCAL_ONLY',
                 created_at, updated_at, revision)
history_events  (event_id pk, user_id, work_id, event_type, occurred_at, client_id,
                 request_id, schema_version, payload jsonb, server_received_at,
                 unique(user_id, request_id))
```

- `works` 是 `history_events` 的**投影**，不是第二份事实来源；
- 不使用源音频 hash 作为跨用户去重键；相同文件属于不同用户时不合并 ownership；
- `phase 3A` 的 event type 闭集：`WORK_COMPLETED` / `DECISION_CHANGED` /
  `INSCRIPTION_UPDATED` / `AUDIO_EXPORTED` / `WORK_REVISITED`；
- `payload` 按 event type 白名单校验（`history-sync/schema.js`），未知 type 或越界字段一律拒绝，
  payload 不是遥测垃圾桶；
- `WORK_REVISITED` 只在用户主动打开完成作品时记录一次，不记录秒数与行为。

### 5. 幂等、离线、冲突与删除语义

**幂等：** 客户端为每个事件生成 `request_id`（uuid v4）；服务端 `unique(user_id, request_id)` 保证
重试只形成一个 event。重试返回既有记录，不报错。

**离线：** 本地写入先成功（本地是权威），事件进入应用数据目录下的 append-only 队列；
无网时 UI 显示 `等待同步`，不弹错误、不阻断工作；恢复网络后按指数退避重试（上限 5 分钟）。
队列与账户绑定：`signOut` 保留未发送事件但清除账户绑定；登录**另一**账户时绝不发送前一账户的队列。

**冲突：** events 按 `(server_received_at, event_id)` 稳定排序；`inscription` 取最后一次明确编辑
事件，不做字符级合并；decision history 全部保留，当前投影取最后有效事件；本地 case 的真实
decision 仍是声音流程权威；远端与本地冲突时只显示差异，用户可显式选择「以此设备当前选择更新个人历史」。
禁止静默用云端覆盖本地。

**删除：** 删除单个云端 item = 服务端硬删除该 `work` 及其 events，并在本地把
`account_link.json` 标记 `sync_enabled=false`；服务端在 `history_events` 上保留
`(user_id, work_id)` 级别的**墓碑**（`deleted_works`），使其他设备的下一次 pull 不会复活它。
删除账户由服务端受控函数（`delete_account()`，`security definer`，近期登录要求）完成，
级联删除 profile / works / events 与 auth identity；本地 case 与音频不受影响。

### 6. RLS / owner boundary

所有表 `enable row level security`，默认拒绝。策略形式固定为：

```sql
using (auth.uid() = user_id)  /  with check (auth.uid() = user_id)
```

- 客户端传入的 `user_id` 不作为信任来源；`insert` 由 `with check` 校验，`update` 不允许改 `user_id`；
- `anon` 角色对三张表没有任何权限；`authenticated` 只能读写自己的行；
- `delete_account()` 是 `security definer` 且 `revoke all from anon, authenticated`
  （只能通过受控服务端路径调用，service-role key 永不进入 Desktop）；
- 两个真实测试用户的交叉读取 / 更新 / 删除必须全部失败（测试见 `deployment/supabase/tests/`）。

### 7. Desktop 登录回调（系统浏览器 + PKCE）

- 登录在**系统默认浏览器**完成，不在 Electron 内嵌网页采集密码；
- 采用 OAuth/OIDC 风格 PKCE：Desktop 生成 `code_verifier` / `code_challenge`(S256) / `state` / `nonce`，
  只把 `code_challenge` 与 `state` 交给服务端；
- 回调只接受**一次性、未过期、state 匹配**的授权码：`state` 不匹配、重放（同一 code 或同一 state
  第二次）、超过 10 分钟一律拒绝，且拒绝后回到未登录状态、不影响本地工作；
- 回调通道二选一（本 MIP 选择 **loopback**）：`http://127.0.0.1:<随机端口>/auth/callback`，
  随机端口 + 一次性 state + 单次使用 + 60 秒内关闭；失败恢复与安全模型见
  `moodify-desktop/src/account/callback.js`。不使用 `moodify://` 自定义协议作为并行实现
  （不同时实现两套半成品）；若将来打包器证明自定义协议更可靠，替换需更新本 MIP。
- 回调只能完成**当前正在等待的那一次**登录请求；没有等待中的请求时，任何回调都被丢弃。

### 8. Token 生命周期

- `refresh_token` 用 Electron `safeStorage` 加密后写入应用数据目录（`account/session.json`）；
- `access_token` 只存在于主进程内存；renderer 只能通过窄 IPC 获得**账户状态视图**，拿不到原始 token；
- 刷新：过期前 60 秒主动刷新；刷新失败 → 降级为未登录并把队列保留为「等待同步」；
- sign out：删除本地 token 与 session metadata，**不删除**本地作品与 keepsake；
- token / OTP / magic-link URL 全量禁止进入日志、错误文案、UI 与测试快照；
- `safeStorage` 不可用时拒绝持久登录（允许仅当前会话登录，并在 UI 中明确显示）。

### 9. Provider 边界（可替换）

```text
AccountProvider        beginSignIn() completeSignIn(callback) session() refresh() signOut() currentUser()
HistorySyncProvider    push(events) pull(cursor) exportAccountData() deleteHistoryItem(id) requestAccountDeletion()
```

第一版只有 Supabase provider。接口用于隔离供应商，**不**演变为自研框架；provider 不接触
Core DSP、不接触音频文件、不接触本地路径。

### 10. Desktop IPC（窄边界）

renderer 不直接调用数据库管理 API，也不持有凭据。IPC 只暴露：

```text
account:state          未配置 / 未登录 / 已登录（脱敏身份 + 同步概况）
account:signIn         开始登录（返回一次性 state）
account:signOut
account:syncEnableViews / account:claimWorks（首次同步确认）
history:list           本地 case ∪ 云端投影（含 audioAvailability）
history:open           work_id → 本地 case（存在则完成层，否则只读详情）
history:export / history:deleteItem / account:deleteAccount
history:syncNow
```

所有 IPC 参数做 schema 校验；case 路径继续使用现有 root guard；renderer 不能传任意 SQL、URL
或本地路径给 provider。

### 11. 数据导出

导出 = 服务端当前账户数据（profile + works + history_events + schema/version/导出时间）的 JSON。
不包含未上传的本地音频。需要有效 session。

## Rationale

- **为什么用商品化服务：** `existing > standard library > mature OSS > commodity service >
  custom > experimental`。认证、PostgreSQL、RLS 都是成熟能力；自制密码存储或自签 JWT 是
  custom，举证责任在我们，且失败代价是用户凭据泄露。
- **为什么 append-only events + projection：** 历史必须能解释「什么时候变成这样」；
  投影可以重建，事件不可改写；冲突与删除都有确定语义。
- **为什么音频默认不上传：** 用户的作品是私人资产。历史的价值是「我记得我做过这首歌」，
  不需要把母带交出去；这也让 RLS 的爆炸半径最小。
- **为什么本地优先：** 声音生产不能依赖网络。账户是附加层，任何账户故障都不得让用户无法完成作品。

## Backwards compatibility

- 既有 case 不迁移、不上传；没有 `account_link.json` 的 case 完全不受影响；
- 未登录用户的行为与 Phase 2.3 完全一致；
- `decisions.jsonl` / `keepsake.json` / `pipeline.json` 的 schema 不变；
- 关闭功能即回滚（见 Canon changelog 的 Rollback）。

## Evidence

- 本地可验证部分：`moodify-desktop/scripts/test-account.js`、`test-sync.js`、
  `test-main-ipc.js`（§14/§15）——登录回调的 state/nonce/重放/过期、token 不入 renderer、
  safeStorage roundtrip、离线队列幂等与账户隔离、投影稳定性、数据最小化断言、UI 契约。
- 服务端部分：`deployment/supabase/migrations/` + `deployment/supabase/tests/rls_two_users.sql`
  （两用户交叉失败、未认证拒绝、伪造 user_id 无效、受控删除函数不可被 anon 调用）。
  **执行证据尚不存在**（无凭据、无本地数据库）→ `DEPLOYMENT_BLOCKED`。

## Human review

需要在人类侧裁决：生产项目所有者/区域/预算、邮件发件域名、隐私政策与条款文本、数据保留期、
手机端开放时间。见任务包 §19。

## Reference implementation

```text
moodify-desktop/src/account/       provider.js supabase-provider.js session-store.js callback.js
moodify-desktop/src/history-sync/  schema.js queue.js projection.js sync.js link.js
deployment/supabase/               README.md migrations/ tests/
```

## Test plan

见 `deployment/supabase/tests/rls_two_users.sql`（RLS）与任务包 §15（Auth / Sync / 数据最小化 / UI）。
全部本地测试必须随 `npm test` 一起跑；RLS 测试在没有数据库时**显式跳过并打印原因**，
不得静默通过。

## Security and privacy considerations

- service-role key 永不进入 Desktop / renderer / 仓库；
- renderer 无 token、无 SQL、无任意 URL；
- 日志只记 `event_type` / `request_id` / status；email 仅脱敏出现在认证诊断；
- 错误报告默认不含 `inscription`；
- 测试 fixture 使用假邮箱与合成数据；真实凭据、导出包与日志不得提交；
- CSP 保持禁止任意远程脚本与 `unsafe-eval`；
- `MOODIFY_SUPABASE_ANON_KEY` 是可公开的客户端配置，但绝不可与 service-role key 混淆。

## Unresolved questions

1. **生产 Supabase project**（所有者 / 区域 / 预算）与测试项目：缺凭据 → 真实登录、RLS 执行证据、
   端到端验收均为 `DEPLOYMENT_BLOCKED`。
2. 邮件发送域名与品牌发件人（影响 magic link 送达率与信任）。
3. 隐私政策 / 服务条款正式文本。
4. 云端数据保留期（含墓碑保留多久）。
5. `moodify://` 自定义协议是否在打包后更可靠（当前选择 loopback，需打包证据才替换）。
6. 何时开放手机端登录与同步。
7. 未来是否允许用户**选择**上传音频——本阶段答案固定为「不允许」，未来若改变必须新 MIP。
