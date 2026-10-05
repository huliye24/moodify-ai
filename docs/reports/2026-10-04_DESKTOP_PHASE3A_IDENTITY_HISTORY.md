# Moodify Phase 3A — Identity / Account / Personal History（实现报告 · 第一阶段交付）

**Date:** 2026-10-04
**Status:** **PARTIALLY IMPLEMENTED · `DEPLOYMENT_BLOCKED`** — Gate 0 完成；Gate A 的服务端契约与
Gate C 的本地同步数据层已实现并测试；Gate B（真实登录）、Gate C 的 UI、Gate D（服务端删除/导出 UI）
**未完成**，且**没有**用假登录 UI 充数。
**Owner / final acceptance:** Codex（主控）
**CANON_CHANGE:** YES（已按 §3.1 记录 why / evidence / new boundary / migration / rollback）
**MIP_REQUIRED:** YES → [`MIP-0003-personal-identity-history.md`](../../protocol/mips/MIP-0003-personal-identity-history.md)（DRAFT）
**任务包:** [`docs/plan/2026-10-04_PHASE3A_ACCOUNT_PERSONAL_HISTORY.md`](../plan/2026-10-04_PHASE3A_ACCOUNT_PERSONAL_HISTORY.md)

---

## 0. 环境事实（为什么必须标记 DEPLOYMENT_BLOCKED）

本机是**真实存在的执行环境事实**，不是推测：

```text
supabase CLI   NOT FOUND
psql           NOT FOUND
docker         installed, but the daemon is NOT running
                 (npipe:////./pipe/dockerDesktopLinuxEngine → not found)
MOODIFY_SUPABASE_URL / _ANON_KEY / DATABASE_URL   全部未设置
```

因此：**没有可用数据库、没有测试项目、没有凭据** → 真实登录、RLS 执行证据、
跨设备同步与端到端验收在本机**不可能取得**。按任务包 §18：可以完成代码、迁移与本地模拟验证，
但必须标记 `DEPLOYMENT_BLOCKED`，不得声称真实账户已上线。本报告全程遵守这一点。

RLS 套件的 runner 因此被设计为**显式跳过并以 exit 2 结束**（不是 0）：

```text
$ npm --prefix moodify-desktop run test:rls
RLS suite: SKIPPED (no psql on PATH …)
  → owner boundary is NOT verified by this run; Phase 3A stays DEPLOYMENT_BLOCKED.
exit=2
```

「跑不了」永远不能被误读成「已验证」——这正是 exit 2 而不是 exit 0 的原因。

## 1. 修改文件清单

**Canon（Gate 0，先于任何实现）**
- `docs/canon/PRODUCT_DEFINITION_V3.md`：§9.1 记录 2026-10-04 人类批准的**受控例外**（原第 5 条曾是
  全面禁止 server/login/account/cloud storage）；新增 §11 定义本阶段产品结果、三种权威与硬规则。
- `docs/canon/PRODUCT_BOUNDARY.md`：non-goals 增加公共主页/关注/动态流/排行榜/评论/点赞/发布平台/
  广告画像；新增「Identity / Account / Personal History boundary」节（允许、默认禁止上传、证据边界）。
- `docs/canon/AUTHORITY_ORDER.md`：新增「三种权威」（声音生产事实 / 账户身份 / 个人历史同步）与
  「冲突判定：云端不得推进本地阶段或改写本地选择」。
- `docs/canon/CANON_CHANGELOG.md`：2026-10-04 条目（Why / Evidence / New boundary / Migration / Rollback）。
- `docs/REPOSITORY_STATUS.md`：新增 Phase 3A 行（PARTIALLY IMPLEMENTED · DEPLOYMENT_BLOCKED）。
- `protocol/mips/MIP-0003-personal-identity-history.md`（新，DRAFT）。

**服务端契约（`deployment/supabase/`，新）**
- `migrations/0001_identity_history.sql`：`profiles` / `works` / `history_events` / `deleted_works`、
  默认拒绝的 RLS、owner-only 策略、幂等 push 函数、`claim_work`、`delete_history_item`（含墓碑）、
  `export_account_data`、`delete_account`（`security definer`，仅 `service_role` 可执行）。
- `tests/local_shim.sql`：vanilla PostgreSQL 的 `auth.users` / `auth.uid()` / 角色替身（**禁止**用于 Supabase）。
- `tests/rls_two_users.sql`：两用户隔离套件（11 项断言，事务内回滚）。
- `tests/run_rls_tests.js`：runner（应用迁移 + 套件；缺工具/凭据时 **exit 2 显式跳过**）。
- `README.md`：应用方式、允许/禁止数据、exit code 语义、密钥纪律。

**Desktop 本地同步数据层（新）**
- `src/history-sync/schema.js`：事件闭集、按 type 的 payload 白名单、递归禁止字段/禁止值扫描、日志行裁剪。
- `src/history-sync/queue.js`：应用数据目录下的 append-only 队列、`request_id` 幂等、指数退避（有上限）、
  账户绑定/解绑/重绑、确认后压缩、损坏行隔离、容量上限。
- `src/history-sync/projection.js`：稳定排序与去重、`works` 投影、本地 ∪ 云端合并（本地权威 + 差异痕迹）。
- `src/history-sync/link.js`：`<case>/studio/account_link.json`（原子写、无凭据、拒绝含凭据的文件）。
- `scripts/test-sync.js`（新，25 条）：上述全部不变量。
- `package.json`：`npm test` 纳入 `test-sync.js`；新增 `test:rls`。

**尚未创建（Gate B/C-UI/D，见 §7）**：`src/account/{provider,supabase-provider,session-store,callback}.js`、
`src/history-sync/sync.js`、main/preload 的 account/history IPC、renderer 个人空间与历史 UI、
`scripts/test-account.js`。

## 2. Canon change（why / evidence / authority / migration / rollback）

```text
Why:
  个人作品历史需要跨安装持续存在；账户是 continuity 的承载，不是社交增长工具。
Evidence:
  Desktop 已能形成 A/B、人工选择、keepsake 与完成时刻（Phase 2/2.1/2.2/2.3 均已实现并测试）；
  这些历史目前只存在单机 case。
New boundary:
  允许 account/login/server/受控云端元数据；音频默认 local-only；
  公共主页/关注/动态流/排行榜/评论/点赞/发布平台/广告画像仍然禁止。
Migration:
  既有 case 不自动上传；登录后必须显式确认才启用同步；每个 case 写 account_link.json 并可随时关闭。
Rollback:
  关闭 sync/account 后，本地声音流程、case、选择、导出与 keepsake 继续完整工作；
  删除 account_link.json 与离线队列不影响任何声音产物。
```

受影响 authority 文件：`PRODUCT_DEFINITION_V3.md` / `PRODUCT_BOUNDARY.md` / `AUTHORITY_ORDER.md`
（+ `CANON_CHANGELOG.md` / `REPOSITORY_STATUS.md` 记录）。Canon 控制项 = 内部/外部能力边界 +
data authority + cloud control authority。

## 3. MIP-0003 摘要

冻结了：① account identity 与 local case identity 的区别（关联只写 `work_id`，不写凭据）；
② 云端允许/禁止数据；③ 三种权威与「云端不得推进本地阶段」；④ 数据模型与 RLS；
⑤ 幂等 / 离线 / 冲突 / 删除语义（含墓碑防复活）；⑥ 登录回调选择 **loopback + PKCE + state/nonce
一次性 + 10 分钟过期**（不同时实现 `moodify://` 两套半成品）；⑦ token 生命周期（refresh 用
`safeStorage` 加密落盘、access 只在主进程内存、renderer 拿不到原始 token）；
⑧ 数据导出与删除；⑨ provider 替换边界与回滚；⑩ 明确不含音频云存储与社交。
未决项：生产项目、发件域名、条款文本、保留期、手机端时间、未来是否允许上传音频（本阶段固定「不允许」）。

## 4. 认证流程与 token 边界（契约已冻结，实现待 Gate B）

```text
用户点「登录」 → 主进程生成 PKCE(verifier, S256 challenge) + state + nonce
  → 系统默认浏览器打开 Supabase Auth（Electron 内嵌网页永不采集密码）
  → loopback http://127.0.0.1:<随机端口>/auth/callback 接收一次性 code
  → 校验 state / 未过期(≤10min) / 单次使用 / 有等待中的请求 → 否则拒绝并回到未登录
  → 主进程用 code + verifier 换取 session
  → refresh_token 经 safeStorage 加密写入应用数据目录；access_token 只在主进程内存
  → renderer 只能通过窄 IPC 读取「账户状态视图」（脱敏身份 + 同步概况），拿不到 token
```

`safeStorage` 不可用时：**拒绝持久登录**，只允许当前会话登录并在 UI 明确显示。
token / OTP / magic-link 一律不得进入日志、错误文案、UI 或测试快照。

## 5. 数据表、RLS 与两用户隔离证据

**已写**：4 张表、默认拒绝策略、`auth.uid() = user_id` 的 `using`/`with check`、
`delete_account(uuid)` 仅授予 `service_role`、`anon` 对四张表零权限。

**执行证据：不存在**（§0）。套件覆盖并要求（`deployment/supabase/tests/rls_two_users.sql`）：

1. 未认证会话看到 0 行且不能插入；2. A 只看到自己那行；3. A 猜 B 的 `work_id` 读不到；
4. A 改/删 B 的行影响 0 行；5. 伪造 `user_id` 被 `with check` 拒绝；
6. 同一 `request_id` push 两次只形成 1 个 event；7. 删除写墓碑、重新 claim 被拒（不复活）；
8. 导出只含本人数据且不含音频/路径/hash；9. `delete_account` 不能被 anon/authenticated 执行；
10. `anon` 无表权限；11. fixture 在回滚事务内清理。

## 6. 实际上传 payload 样本（脱敏，来自测试）

```json
{ "event_type": "WORK_COMPLETED",
  "work_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
  "request_id": "9f1c…", "occurred_at": "2026-10-04T14:45:22.739Z",
  "schema_version": "moodify.studio.history-event/0.1",
  "payload": { "title": "Je ne blesserai pas ta fragilité", "duration_ms": 123320,
               "completion_mode": "FAST_STEREO_ONLY", "selected": "A",
               "completed_at": "2026-10-04T14:45:22.739Z",
               "inscription": "é中文😀 写给这首歌" } }
```

同一批次里**没有**：音频字节、`.wav/.mid`、stems、`report.json`、spectrum、`sha256`、
`E:\` 或 `/Users/` 绝对路径、JWT、token、`listening_ms`、`play_count`（测试逐字断言），
而用户自己写的那句话被原样保留。日志行只含 `event_type / request_id / status`。

## 7. 测试结果与剩余工作

```text
cd moodify-desktop && npm test
  → check-contracts ✓（DOM id 179 · 桥接 59 · IPC 58）
    pipeline 61/61 · recheck 9/9 · session 38/38 · keepsake 23/23 · **sync 25/25**
    orchestrator 20/20 · main-ipc 67/67 · studio 21/21
python scripts/check_repo_structure.py → OK（1557 tracked files）
python -m ruff check moodify-core-package/src moodify-core-package/tests → All checks passed
npm --prefix moodify-desktop run test:rls → SKIPPED, exit 2  ← **§15.6 的 RLS 行未通过，是 BLOCKED 不是 green**
```

`test-sync.js` 覆盖任务包要求：§15.3（幂等、离线重启续传、账户切换隔离、乱序/重复投影稳定、
云端冲突不改本地、inscription/decision 守恒、删除不复活、队列损坏隔离）与 §15.4（数据最小化自动断言）。

**未完成（诚实列表，无一项被伪装成完成）：**

| 项 | Gate | 状态 |
|---|---|---|
| Canon + MIP-0003 | 0 | ✅ 完成 |
| SQL 迁移 + RLS + 受控删除 | A | ✅ 已写；执行证据 BLOCKED |
| provider 接口 + Supabase provider | A/B | ❌ 未写 |
| token safeStorage 存储 / 回调 / PKCE | B | ❌ 未写 |
| 无配置时本地降级（UI 措辞「账户服务未配置」） | A | ❌ 未接线 |
| 两用户 RLS 执行证据 | A | ⛔ BLOCKED（无数据库/凭据） |
| 离线队列 + 幂等 + 投影 + account_link | C | ✅ 完成并测试 |
| sync 编排（有界触发/状态机/重试/冲突提示） | C | ❌ 未写 |
| 首次同步确认、历史列表、远端只读详情 UI | C | ❌ 未写（**刻意不接假登录 UI**） |
| 导出 / 单项删除 / 删除账户（客户端侧） | D | ❌ 未写 |
| 真实登录 + 跨设备 + 端到端验收 | B/D | ⛔ BLOCKED |

## 8. 停止条件核验（任务包 §18）

未触发任何「必须停止并报告」之外的扩张：没有 service-role key 进 Desktop（迁移里只授予
`service_role`）、没有自制密码/JWT、没有上传音频、RLS 是 owner-only、回调契约要求 state/nonce 与
防重放、断网不影响本地生产（队列与投影均为纯本地模块）、云端不是本地权威。
第 10 条「真实部署凭据缺失」**已触发** → 本交付标记 `DEPLOYMENT_BLOCKED`。

## 9. HUMAN_DECISION_REQUIRED（仅任务包 §19 授权的 6 项）

1. 生产 Supabase project 的所有者 / 区域 / 预算（以及是否提供测试项目）；
2. 邮件发送域名与品牌发件人；
3. 隐私政策与服务条款正式文本；
4. 数据保留期（含墓碑保留时长）；
5. 何时开放手机端登录与同步；
6. 未来是否允许用户选择上传音频（本阶段答案固定为「不允许」，改变需新 MIP）。
