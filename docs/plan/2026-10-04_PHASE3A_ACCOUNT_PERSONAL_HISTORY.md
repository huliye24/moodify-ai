# Moodify Phase 3A — 账户、个人作品历史与本地优先同步

**Date:** 2026-10-04  
**Status:** IMPLEMENTATION BRIEF — HUMAN APPROVED DIRECTION  
**Owner / final acceptance:** Codex（主控）  
**Implementation delegate:** DeepSeek / Claude Code  
**CANON_CHANGE:** YES  
**MIP_REQUIRED:** YES — Identity / data authority / sync schema / privacy contract  
**Recommended commodity service:** Supabase Auth + PostgreSQL（可替换边界必须保留）

## 0. 人类产品裁定

2026-10-04，人类批准 Moodify 新增：

```text
Identity
Account
Personal History
Desktop history sync
```

账户的作用不是制造登录门槛，而是让用户多年积累的作品历史不会因换电脑、重装或未来换到手机而
消失。

本阶段明确不批准：

```text
公共主页
关注 / 粉丝
动态流
排行榜
评论
点赞
公开作品发布平台
广告画像
默认上传音频
```

## 1. 产品结果

完成本阶段后，用户可以：

1. 不登录继续使用 Moodify Desktop 的完整本地完成流程；
2. 使用邮箱创建/登录个人账户；
3. 将已完成作品的轻量历史同步到自己的账户；
4. 重装或在另一台 Desktop 登录后看到个人作品历史；
5. 打开历史项时看见标题、完成日期、最终选择和自己留下的话；
6. 导出自己的账户数据；
7. 删除云端个人历史或删除账户；
8. 明确知道哪些内容留在本地、哪些内容被同步。

本阶段不上传 WAV、stems、MIDI、频谱图片、report 或 Mix Graph 全量证据。另一台设备能看见历史，
但没有本地音频时必须显示“音频仅在原设备”，不得出现不可播放的假播放按钮。

## 2. 执行前必须阅读

1. `AGENTS.md`
2. `docs/canon/CURRENT_CANON.md`
3. `docs/canon/PRODUCT_BOUNDARY.md`
4. `docs/canon/AUTHORITY_ORDER.md`
5. `docs/canon/PRODUCT_DEFINITION_V3.md`
6. `docs/canon/TECHNOLOGY_PRINCIPLES.md`
7. `docs/canon/STUDIO_PRODUCTION_PIPELINE_V4.md`
8. `GOVERNANCE.md`
9. `protocol/mips/README.md` 与模板
10. `docs/plan/2026-10-04_DESKTOP_PHASE2_3_FINISHING_POLISH.md`
11. Desktop 当前 IPC、安全边界与测试

不得复用历史 Web3、token、wallet、DAO 或已归档 MOOD Protocol 作为账户系统。

## 3. Gate 0 — Canon 与 MIP 先于实现

### 3.1 Canon change

实现前先更新：

- `docs/canon/PRODUCT_DEFINITION_V3.md`
- `docs/canon/PRODUCT_BOUNDARY.md`
- `docs/canon/AUTHORITY_ORDER.md`
- `docs/canon/CANON_CHANGELOG.md`
- `docs/REPOSITORY_STATUS.md`

必须记录：

```text
Why:
  个人作品历史需要跨安装持续存在；账户是 continuity 的承载，不是社交增长工具。

Evidence:
  Desktop 已能形成 A/B、人工选择、keepsake 与完成时刻；这些历史目前只存在单机 case。

New boundary:
  允许 account/login/server/受控云端元数据；音频默认 local-only。

Migration:
  既有 case 不自动上传；用户登录后逐项或批量明确启用历史同步。

Rollback:
  关闭 sync/account 功能后，本地声音流程、case、选择、导出与 keepsake 继续完整工作。
```

### 3.2 MIP-0003

新增 `protocol/mips/MIP-0003-personal-identity-history.md`，初始状态可为 `DRAFT`，至少冻结：

- account identity 与本地 case identity 的区别；
- 云端允许/禁止的数据；
- 数据权威；
- history event schema；
- 幂等、离线、冲突与删除语义；
- RLS/owner boundary；
- Desktop 登录回调；
- token 生命周期；
- 数据导出与删除；
- provider 替换与回滚；
- 明确不包含音频云存储和社交。

MIP 没写清前不得开始接 UI。

## 4. 权威边界

本阶段必须只有以下三种权威，不得混为一体：

```text
声音生产事实权威：本地 case 目录 + Core 产物
账户身份权威：认证服务的 user identity
个人历史同步权威：账户私有的 append-only history events + server projection
```

规则：

- 云端 history 不能把本地 case 推进到 CHOSEN / EXPORTED；
- 云端 `selected=A` 不能替代本地 `decisions.jsonl`；
- 本地文件被删后，云端历史仍可作为记忆存在，但不能冒充音频可用；
- 用户未登录时，本地流程完全可用；
- 登录失败、断网、服务停机均不得阻断分析、处理、试听、选择或导出；
- `pipeline.js` 继续是 Desktop 阶段权威；
- account/sync 不进入 Core DSP。

## 5. 技术选择

### 5.1 认证与数据库

本阶段默认采用：

```text
Supabase Auth
PostgreSQL
Row Level Security
SQL migrations in repository
```

原因：成熟认证、标准 PostgreSQL、RLS、可托管也可迁移，符合：

```text
existing > standard library > mature OSS > commodity service > custom > experimental
```

禁止：

- Moodify 自己存储或校验密码；
- 自制 JWT 签发器；
- 把 service-role key 放入 Desktop；
- 在 renderer 直接持有高权限凭据；
- 将 Supabase 特有对象泄漏进声音 Core 或 pipeline。

### 5.2 Provider 边界

Desktop 内部建立最小接口：

```text
AccountProvider
  beginSignIn()
  completeSignIn(callback)
  session()
  refresh()
  signOut()
  currentUser()

HistorySyncProvider
  push(events)
  pull(cursor)
  exportAccountData()
  deleteHistoryItem(id)
  requestAccountDeletion()
```

第一版只实现 Supabase provider，不创建假的第二 provider。接口用于隔离供应商，不得演变为大型自研框架。

## 6. 登录体验

### 6.1 本地优先入口

首次启动不弹强制登录。侧栏或头像区域显示：

```text
个人空间
[登录]
```

未登录时所有本地生产功能正常。只有用户主动打开个人空间时说明：

```text
登录后可在设备之间保留作品历史。
音频默认不会上传。

[使用邮箱继续]
[暂不登录]
```

不要展示套餐、增长弹窗或倒计时。

### 6.2 认证方式

Phase 3A 只做一个低复杂度入口：

```text
邮箱 Magic Link / OTP（由 Supabase Auth 承担）
```

要求：

- 登录在系统默认浏览器完成；
- Desktop 使用 OAuth/OIDC 风格 PKCE 与一次性回调；
- 不在 Electron 内嵌网页中采集密码；
- 不把验证码写进日志；
- callback 必须带 state/nonce 校验和超时；
- 回调只能完成当前正在等待的登录请求；
- 重放、错 state、过期 callback 必须拒绝；
- 登录取消后返回未登录状态，不影响本地工作。

可采用受控 loopback callback 或注册的 `moodify://auth/callback`。执行代理必须根据 Electron 打包与 Windows
运行证据选择一种，并在 MIP 中写明安全模型与失败恢复。不要同时实现两套半成品。

### 6.3 Token 存储

- refresh token 使用 Electron `safeStorage` 加密后存入应用数据目录；
- access token 仅在主进程内存中存在；
- renderer 只能调用窄 IPC，不能读取原始 token；
- sign out 删除本地 token 与 session metadata，但不删除本地作品；
- 不在 console、crash log、错误 UI 或测试 snapshot 中输出 token；
- 无法使用 `safeStorage` 时拒绝持久登录，可允许仅当前会话登录并明确显示。

## 7. 云端数据模型

SQL migration 放在仓库现有 `deployment/` 权威下，建议：

```text
deployment/supabase/migrations/
```

新增非音频表：

### 7.1 `profiles`

```text
user_id uuid primary key references auth.users
display_name text nullable
created_at timestamptz
updated_at timestamptz
```

Phase 3A 不做头像上传、用户名抢占、公开 profile 或 bio。

### 7.2 `works`

账户私有作品投影：

```text
work_id uuid primary key
user_id uuid not null
title text not null
duration_ms bigint nullable
completion_mode text
selected text check in (A, B, ORIGINAL)
completed_at timestamptz
inscription text nullable
audio_availability text = LOCAL_ONLY
created_at timestamptz
updated_at timestamptz
revision bigint
```

禁止字段：

- 本地绝对路径；
- 原始音频内容；
- stems/MIDI；
- report 全文；
- 频谱图片；
- Mix Graph 参数；
- source SHA-256；
- API key、token；
- 用户未明确提供的推断标签。

不要用源音频 hash 作为跨用户去重键。相同文件属于不同用户时不能合并 ownership。

### 7.3 `history_events`

```text
event_id uuid primary key
user_id uuid not null
work_id uuid not null
event_type text
occurred_at timestamptz
client_id uuid
request_id uuid
schema_version text
payload jsonb
server_received_at timestamptz
unique(user_id, request_id)
```

Phase 3A 允许的 event type 闭集：

```text
WORK_COMPLETED
DECISION_CHANGED
INSCRIPTION_UPDATED
AUDIO_EXPORTED
WORK_REVISITED
```

`WORK_REVISITED` 只在用户主动打开完成作品时记录一次，不记录播放秒数、暂停次数、搜索词或细粒度行为。

payload 必须按 event type 白名单校验，禁止任意 JSON 成为遥测垃圾桶。

### 7.4 RLS

所有表默认拒绝。策略必须保证：

```text
auth.uid() = user_id
```

用户只能读写自己的 profile、works、history_events。禁止依赖客户端传入 user_id 而不做 RLS。测试必须使用
两个真实测试用户证明交叉读取、更新、删除全部失败。

## 8. 本地映射与离线队列

每个选择同步的 case 允许新增：

```text
<case>/studio/account_link.json
```

只保存：

```json
{
  "schema": "moodify.studio.account-link/0.1",
  "work_id": "uuid",
  "sync_enabled": true,
  "last_pushed_revision": 0,
  "last_pulled_cursor": "...",
  "updated_at": "..."
}
```

禁止保存 email、access token、refresh token 或远端 API key。

应用数据目录新增持久离线队列，而不是在每个 case 里复制队列。队列要求：

- append-only event；
- request_id 幂等；
- 指数退避 + 上限；
- 登录退出时保留未发送事件但去除账户绑定，重新登录同一用户后可继续；
- 登录另一账户时绝不把前一账户队列发送过去；
- 崩溃恢复；
- 成功确认后压缩已确认记录；
- 队列损坏隔离并可诊断，不阻断 Desktop。

## 9. 同步策略

### 9.1 首次登录

登录成功后不要自动上传全部历史。显示：

```text
保留个人作品历史

将同步：标题、完成日期、最终选择和你留下的话。
不会上传：音频、分轨、MIDI、频谱和制作文件。

[同步已完成作品]
[以后再说]
```

用户确认后列出将同步的作品数量。可以批量开启，但每个 case 都要写 `account_link.json`，并能逐项关闭后续同步。

### 9.2 日常同步

- 本地写入先成功，云端随后异步同步；
- 无网时显示 `等待同步`，不弹错误打断工作；
- 恢复网络后重试；
- UI 区分 `仅本地 / 等待同步 / 已同步 / 同步失败`；
- 同步失败可重试，不能把本地完成状态回滚；
- 不做后台无限高频轮询；
- 应用打开、登录完成、作品完成/改选/修改文字以及用户手动刷新时触发有界同步。

### 9.3 冲突

Phase 3A 的规则必须确定且可解释：

- events 按 server_received_at + event_id 稳定排序；
- inscription 使用最后一次明确编辑事件，不做字符级合并；
- decision history 全部保留，当前投影取最后有效事件；
- 本地 case 的真实 decision 仍是声音流程权威；
- 远端 decision 与本地冲突时只显示历史差异，不自动改写本地 `decisions.jsonl`；
- 用户可选择“以此设备当前选择更新个人历史”。

禁止静默用云端覆盖本地声音状态。

## 10. 个人空间 UI

### 10.1 登录后

侧栏个人空间显示：

```text
显示名或邮箱脱敏形式
同步状态
[作品历史]
[账户设置]
```

不要长期显示完整邮箱；默认例如 `ra***@example.com`。

### 10.2 作品历史

本阶段只做私有列表：

```text
标题
完成日期
最终选择
私人文字（最多两行预览）
音频：本机可用 / 仅在原设备
同步状态
```

排序默认按最近完成/更新。没有推荐、热度、播放量或社交数据。

打开项目：

- 本地 case 存在：进入 Phase 2.3 完成层；
- 本地 case 不存在：进入只读历史详情；
- 不显示播放按钮；
- 明确写 `音频仅在原设备`；
- 允许查看标题、日期、选择和私人文字。

### 10.3 账户设置

必须有：

- 同步内容说明；
- 手动同步；
- 导出账户数据；
- 退出登录；
- 删除个人历史；
- 删除账户入口。

删除历史/账户属于高风险动作：明确列出影响、二次确认、服务端重新认证或近期登录要求。不得把删除按钮与退出
登录混在一起。

## 11. 隐私与安全

### 11.1 数据最小化

默认同步白名单：

```text
work_id
title
duration
completion mode
final selection
completion time
optional inscription
coarse history events
```

默认禁止上传：

```text
audio
stems
MIDI
score
report/evidence
spectrum/images
local paths
source hash
terminal logs
search history
listening duration or detailed behavior
```

### 11.2 日志

- email 仅在必要的认证诊断中脱敏；
- token、OTP、magic-link URL 全量禁止记录；
- payload 日志只记录 event_type / request_id / status；
- 错误报告默认不包含 inscription；
- 测试 fixture 使用假邮箱与合成数据。

### 11.3 CSP / IPC

- renderer 不直接调用数据库管理 API；
- 账户与同步通过受限 preload bridge；
- IPC 参数进行 schema 校验；
- 所有 case path 继续使用现有 root guard；
- 禁止 renderer 传任意 SQL、URL 或本地路径给 provider；
- production CSP 禁止任意远程脚本和 `unsafe-eval`；
- Supabase anon key 可作为公开客户端配置，但不得与 service-role key 混淆。

### 11.4 配置

仅通过环境或打包时的公开配置提供：

```text
MOODIFY_ACCOUNT_PROVIDER=supabase
MOODIFY_SUPABASE_URL=
MOODIFY_SUPABASE_ANON_KEY=
```

真实值不得提交。提供 `.env.example` 时只放占位符，并确认 `.gitignore`。没有配置时 Desktop 应显示“账户服务未配置”，
本地功能照常工作。

## 12. 数据导出与删除

### 12.1 导出

用户可下载一个 JSON 或 ZIP，包含：

- profile；
- works；
- history events；
- schema/version/导出时间。

不包含未上传的本地音频。导出应来自服务端当前账户数据，且需要有效 session。

### 12.2 删除个人历史

支持删除单个云端 history item：

- 不删除本地 case；
- 本地 `account_link.json` 标记 sync disabled；
- 服务端删除或墓碑语义必须在 MIP 中明确；
- 其他设备同步后不复活被删除记录。

### 12.3 删除账户

- 必须由服务端高权限受控函数完成，service-role key 不进入 Desktop；
- 要求近期认证；
- 删除 profile、works、events 与 auth identity；
- 明确本机 case 与音频不会被删除；
- 完成后清除本地 session、token 与所有该账户队列绑定；
- 失败时不谎报删除成功。

## 13. 代码落点

建议新增：

```text
moodify-desktop/src/account/
  provider.js
  supabase-provider.js
  session-store.js
  callback.js

moodify-desktop/src/history-sync/
  schema.js
  queue.js
  projection.js
  sync.js

deployment/supabase/
  README.md
  migrations/
  tests/
```

Renderer、preload、main 只做必要接线。不得修改 Core 音频模块。

新增任何非 `.py` 文件前执行：

```text
git check-ignore -v <path>
```

如果 structure guard 不允许所选目录，先更新 guard 的精确白名单并解释原因，不得绕过或关闭 guard。

## 14. 分阶段交付

### Gate A — 契约与安全骨架

- Canon + changelog；
- MIP-0003 DRAFT；
- SQL migrations + RLS；
- provider interface；
- token safeStorage；
- 无配置时本地降级；
- 两用户隔离测试。

### Gate B — 真实登录

- 系统浏览器认证；
- PKCE/callback/state/nonce；
- session refresh；
- sign out；
- 账户状态 UI；
- 失败恢复。

### Gate C — 历史同步

- 本地 work mapping；
- 白名单事件；
- 离线队列与幂等；
- 首次同步确认；
- 个人历史列表；
- 远端只读详情。

### Gate D — 用户控制

- 数据导出；
- 单项删除；
- 删除账户；
- 隐私文案；
- 端到端与人工验收。

每个 Gate 单独测试。不得用假登录 UI 宣称 Phase 3A 完成。

## 15. 必须新增的测试

### 15.1 Auth

- state/nonce 正确成功；
- 错 state、重放、过期 callback 拒绝；
- token 不进入 renderer、日志、错误文本；
- safeStorage roundtrip；
- token 刷新与过期；
- sign out 清理 session 但不删除本地作品；
- 未配置/断网/服务失败不影响本地生产。

### 15.2 RLS

至少使用 user A / user B：

- A 只能 CRUD 自己的数据；
- B 无法读取、猜 ID 更新或删除 A 的任何记录；
- 未认证全部拒绝；
- client 伪造 user_id 无效；
- service-only 删除函数不能被普通 anon 调用。

### 15.3 Sync

- 同一 request_id 重试只形成一个 event；
- 离线完成 → 重启 → 登录同一账户 → 成功续传；
- 登录另一账户不会发送旧账户队列；
- 乱序/重复事件投影稳定；
- 云端冲突不覆盖本地 decision；
- inscription 更新与 decision history 守恒；
- 删除记录不会在其他设备复活；
- 队列损坏隔离，不阻断 Desktop。

### 15.4 数据最小化

自动断言所有上传 payload 不含：

```text
wav/mp3 bytes
absolute path
source_sha256
report/evidence
token/OTP/magic-link
stems/MIDI/score
```

### 15.5 UI

- 未登录不出现功能锁；
- 登录入口明确说明音频默认不上传；
- 首次同步需要用户确认；
- 本机无音频的远端历史不显示播放按钮；
- 同步状态准确；
- 删除操作二次确认；
- 账户服务未配置时本地 UI 可继续使用。

### 15.6 回归

必须通过：

```text
cd moodify-desktop && npm test
python scripts/check_repo_structure.py
python -m ruff check moodify-core-package/src moodify-core-package/tests
Supabase local migration + RLS tests
```

## 16. 真实端到端验收

使用测试 Supabase project 和两个测试账户，不使用生产用户：

1. 未登录完成一首合成测试歌曲；
2. 确认分析、A/B、选择、导出完全不受影响；
3. 账户 A 通过系统浏览器登录；
4. 明确确认同步已完成作品；
5. 服务端只出现允许的 metadata，无音频与本地路径；
6. 模拟断网，修改 inscription/decision，状态变为等待同步；
7. 恢复网络，事件幂等同步；
8. 另一 Desktop profile 登录账户 A，看见历史但无本地音频时不能播放；
9. 账户 B 无法读取账户 A 数据；
10. 导出账户 A 数据并核对守恒；
11. 删除一个历史项，另一 profile 同步后不复活；
12. 删除测试账户 A，确认云端清除、本地 case 保留；
13. 退出登录后本地完成流程继续正常。

测试账户、URL、token、导出包与日志均不得提交。

## 17. Definition of Done

```text
不登录也能完整使用 Moodify Desktop
真实账户可以创建、登录、刷新与退出
认证不由 Moodify 自制密码系统承担
token 安全存储且不暴露给 renderer
用户明确确认后才同步既有历史
只同步白名单 metadata，默认零音频上传
作品历史可跨 Desktop 安装查看
无本地音频时不出现假播放能力
离线队列、幂等、冲突与删除行为有测试
两个账户被 RLS 严格隔离
用户可以导出数据、删除历史与删除账户
云端状态不能改写本地声音生产权威
Canon、MIP、隐私与回滚文档齐全
全部回归与真实端到端验收通过
```

仅有登录按钮、mock user、内存 session、假同步列表或未验证 RLS 不算完成。

## 18. 停止条件

出现以下任一情况必须停止并报告：

- 需要把 service-role key 放入 Desktop；
- 需要 Moodify 自制密码存储或 JWT 签发；
- 必须上传音频才能实现历史同步；
- 供应商无法提供严格 owner isolation；
- callback 无法验证 state/nonce 或防重放；
- 断网会阻断本地生产流程；
- 云端 history 必须成为本地 pipeline/decision 权威；
- 删除语义无法防止记录复活；
- 需要扩展到社交、公开发布、付费或推荐系统；
- 真实部署凭据缺失。

凭据缺失时可以完成代码、迁移和本地模拟验证，但必须标记 `DEPLOYMENT_BLOCKED`，不得声称真实账户已上线。

## 19. HUMAN_DECISION_REQUIRED

执行过程中只允许把以下未裁决项带回，不得自行扩张：

1. 生产 Supabase project 的所有者、区域和预算；
2. 邮件发送域名与品牌发件人；
3. 隐私政策与服务条款的正式文本；
4. 数据保留期；
5. 何时开放手机端登录与同步；
6. 未来是否允许用户选择上传音频——本阶段答案固定为“不允许”。

## 20. 交付报告

执行代理必须提供：

1. 修改文件清单；
2. Canon change 的 why/evidence/authority/migration/rollback；
3. MIP-0003 摘要；
4. 认证流程与 token 边界；
5. 数据表、RLS 和两用户隔离证据；
6. 实际上传 payload 样本（脱敏）；
7. 离线、重试、冲突与删除测试；
8. Desktop 登录/历史/设置截图；
9. 全部测试结果；
10. 部署状态与所有 `HUMAN_DECISION_REQUIRED`。

最终是否通过由主控独立验收，执行代理自评不构成完成。
