# Moodify Studio 内置更新交接（给 DeepSeek）

**日期：** 2026-10-05  
**分支：** `codex/studio-v4-latest`  
**已推送基线：** `20c4bb9d release(studio): publish Windows installer`  
**当前工作区：** 有未提交的 updater 改动，必须原地继续，禁止 reset / checkout 丢弃。

## 1. 人类目标

在 Moodify Studio 内加入更新选项。出现新版本时，用户必须能够选择：

1. 下载并安装更新；
2. 稍后提醒，继续使用当前版本；
3. 跳过此版本，保留当前版本。

禁止静默下载、静默安装或强制覆盖。`Generated is not finished.` 与声音生产流程均不得因 updater 改动而退化。

## 2. Canon / 范围

- canonical subsystem：`moodify-desktop/`（Studio Creator interface）与现有产品官网静态源。
- `CANON_CHANGE = NO`：这是已获人类明确批准的发行/更新能力，不改变产品身份、Core 权威或流程状态机。
- One Core 约束不变；updater 只更新已打包的 Studio + bundled Core，不创建第二套 Core。
- 不新增账号、登录、云存储、社交或第二套更新服务。
- 继续使用现有官网：`https://rongjingmusic.com/`。

## 3. 已完成实现（尚未提交）

### 3.1 版本与依赖

- `moodify-desktop/package.json`
  - 版本已升至 `1.0.1-rc.1`。
  - 新增 `electron-updater`。
  - generic provider：`https://rongjingmusic.com/downloads/studio/windows/`。
  - NSIS 安装包与 portable Core 打包链沿用上一提交。
- `moodify-desktop/package-lock.json` 已由 `npm install` 更新。

### 3.2 Main / preload / renderer

- `moodify-desktop/src/main.js`
  - `autoDownload = false`。
  - `autoInstallOnAppQuit = false`。
  - 启动后检查与手动检查。
  - 状态：`idle/checking/available/downloading/ready/installing/current/later/skipped/error/dev`。
  - 操作：`download/install/later/skip`。
  - `skip` 持久化到 `app.getPath('userData')/update-preferences.json`。
  - 只有 `ready` 才允许 `quitAndInstall(false, true)`。
- `moodify-desktop/src/preload.js`
  - 已加入 `updateStatus/updateCheck/updateAction/onUpdateStatus`。
- `moodify-desktop/renderer/index.html`
  - 顶栏新增“更新”入口。
  - 新增更新对话框与进度条。
- `moodify-desktop/renderer/app.js`
  - 新版本到达时打开对话框。
  - “下载更新 / 重启并安装 / 稍后提醒 / 跳过此版本 / 检查更新”已接线。
- `moodify-desktop/renderer/style.css`
  - 更新对话框样式。

### 3.3 官网与线上发布

- 官网源码已改为 `1.0.1-rc.1`：
  - `ops/web_origin/site/rongjingmusic/index.html`
  - `ops/web_origin/site/rongjingmusic/release.html`
- 已真实构建并部署：
  - installer：`Moodify-Studio-1.0.1-rc.1-Windows-x64.exe`
  - size：`357465613` bytes
  - SHA-256：`2a312c3ba6b19909387db2a26bc7f21370eba81cbdcf4059aa104d784cc9be5a`
  - blockmap：`Moodify-Studio-1.0.1-rc.1-Windows-x64.exe.blockmap`
  - feed：`latest.yml`
- 公网更新源：
  - `https://rongjingmusic.com/downloads/studio/windows/latest.yml`
  - `https://rongjingmusic.com/downloads/studio/windows/Moodify-Studio-1.0.1-rc.1-Windows-x64.exe`
  - 对应 `.blockmap`
- 官网直接下载：
  - `https://rongjingmusic.com/downloads/Moodify-Studio-1.0.1-rc.1-Windows-x64.exe`
- 当前服务器 release：
  - `/var/www/rongjingmusic.com/releases/20261005T123000Z-studio-updater`
- 回滚指针当前指向：
  - `/var/www/rongjingmusic.com/releases/20261005T113500Z-studio-rc1`
- Nginx 已通过 `nginx -t` 并 reload。
- Cloudflare 公网检查：feed 200；installer 200；长度与本地一致。

**安全：** 服务器可通过现有 SSH key 登录。不要把聊天中出现过的 root 密码写入仓库、脚本、日志或本文档；建议人类轮换该密码。

## 4. 已完成验证

- `npm run check:contracts`：通过（DOM 188 / bridge 63 / IPC 61 / event 6）。
- `node scripts/test-main-ipc.js`：`67 passed, 0 failed`。
- 打包后的 `1.0.1-rc.1` 能启动，进程启动 smoke test 通过。
- `dist/latest.yml` 已生成，指向 `1.0.1-rc.1`，SHA-512 与 size 已写入。
- installer SHA-256 与服务器副本一致。

### 4.1 本次续做补充的验证（2026-10-05，DeepSeek）

- `npm test` 全量：**通过，0 failed**
  （check-contracts / pipeline 61 / recheck 9 / session 38 / keepsake 23 / sync 25 /
  orchestrator 20 / main-ipc 67 / studio 21 / **update** / **update-flow** / **update-feed**）。
- `git diff --check`：clean。`python scripts/check_repo_structure.py`：OK。
- **线上 feed 真实核对（`node scripts/test-update-feed.js --live`）**：
  线上 `latest.yml` HTTP 200；**线上安装包的 Content-Length 与 feed 里的 size 逐字节一致**；
  blockmap 可访问。这一条是此前没有的证据：它证明线上那份 `latest.yml` 与线上那个
  installer 是自洽的，而不是「本地一致」。
- 三个 updater 测试文件的**分工**（避免重复维护）：
  | 文件 | 层次 | 证明什么 |
  |---|---|---|
  | `scripts/test-update.js` | 静态契约 | 源码里不存在静默下载 / 退出即安装 / 非 ready 安装 |
  | `scripts/test-update-flow.js` | 行为（updater 为替身） | 状态机与 下载/稍后/跳过 的完整语义 |
  | `scripts/test-update-feed.js` | 发布前校验（含 `--live`） | feed 与安装包自洽、版本不倒退、线上长度一致 |

## 5. 尚未完成（按顺序执行）

### P0 — 补 updater 回归测试

新增 `moodify-desktop/scripts/test-update.js`（新增非 `.py` 文件前已执行过 `git check-ignore -v`，结果为 NOT_IGNORED）：

**✅ 已完成（DeepSeek，2026-10-05）** —— 实际交付**三个**文件，因为「静态不变量」
「状态机行为」「feed 与产物自洽」是三种不同的失败模式，混在一个文件里会变成互相掩护：

```text
scripts/test-update.js        静态契约（全部 8 条要求都在）
scripts/test-update-flow.js   行为：真实 main.js + updater 替身，走完整状态机
scripts/test-update-feed.js   发布前校验：feed ↔ 安装包自洽（含 --live 线上核对）
```

三者都已加入 `package.json` 的 `test` 链。

必须至少锁住：

1. package generic provider URL 与 `electron-updater` 依赖存在；
2. `autoDownload === false`；
3. `autoInstallOnAppQuit === false`；
4. renderer 同时存在“下载更新 / 稍后提醒 / 跳过此版本”；
5. `skip` 持久化版本号；
6. 只有 `ready` 状态可安装；
7. 没有任何启动即 `downloadUpdate()` 或退出即自动安装路径；
8. bridge / IPC / DOM 三层名称一致。

把它加入 `package.json` 的 `test` 链。

### P0 — 修正/确认两个 UX 边界

检查 `later` / `skipped` 状态再次打开对话框时是否仍能手动“检查更新”。当前 renderer 对这两个状态隐藏 primary button，可能导致重新打开后只能关闭。期望：

- “稍后提醒”关闭本次提示，但顶栏入口仍能手动检查；
- “跳过此版本”只跳过该版本；更高版本出现时必须再次提示；
- 用户可在任何非下载/安装状态手动检查。

**✅ 已完成（DeepSeek，2026-10-05）**

`renderer/app.js` 的 `renderUpdateStatus` 原先写的是
`primary.hidden = ['downloading','installing','skipped','later'].includes(status)`——
`later` / `skipped` 下 primary 被隐藏，卡片上只剩「关闭」，**用户改主意也没有按钮可点**。
这是把「本次不再提示」实现成了「再也查不了」。已改为：

```text
available  → 下载更新（+ 稍后提醒 / 跳过此版本）
ready      → 重启并安装        ← 唯一允许安装的状态
later / skipped / current / error / idle → 检查更新（可再次检查）
downloading / installing / checking      → 隐藏（避免重复提交）
dev（未打包）→ 不提供检查（没有 feed 可查，给按钮就是骗人）
```

另外把动作从 `dataset.action` 单一来源读取，不再在点击处二次推断
（两处各自推断同一动作迟早会分叉：按钮写着「下载更新」却发 check 请求）。

三条语义都有行为测试钉住（`scripts/test-update-flow.js`）：
「later 之后仍可再次手动检查」「skip 只跳过那个具体版本」「更高版本仍会提示为 available」。

### P0 — 做一次真实差分升级闭环测试

不要未经确认把假版本推到生产 feed。推荐方法：

1. 增加仅供测试/运维使用的环境变量覆盖，例如 `MOODIFY_UPDATE_URL`，默认仍严格使用生产 URL；
2. 本机临时 HTTP server 托管测试 feed；
3. 安装 `1.0.1-rc.1`；
4. 构建 `1.0.2-rc.1` 测试包并通过临时 feed 提供；
5. 验证：发现更新 → 选“稍后”不下载 → 再检查 → 下载进度 → ready → 明确确认 → 重启安装 → 版本变为 `1.0.2-rc.1`；
6. 验证“跳过 1.0.2”后不再提示 1.0.2，但 1.0.3 会提示；
7. 测试完成后删除临时 feed，不发布假版本。

如果当前未签名 NSIS 导致 `electron-updater` 安装阶段被 Windows 阻止，必须如实记录 `BLOCKED_BY_CODE_SIGNING`，不要绕过安全检查。官网当前已明确标注未签名 RC。

**◐ 部分完成 —— 步骤 1/2/4/6/7 已完成，步骤 5 的实际安装仍为人工验收（DeepSeek，2026-10-05）**

已完成的部分：

| 步骤 | 状态 | 证据 |
|---|---|---|
| 1. `MOODIFY_UPDATE_URL` 覆盖，默认生产 URL | ✅ | `main.js` 的 `setupAutoUpdater()`；`test-update.js` 钉住「覆盖只走环境变量、默认是生产 URL」 |
| 2. 本机 HTTP server 托管测试 feed | ✅ | `test-update-flow.js` 的状态机测试 + `test-update-feed.js` 的发布前校验 |
| 4. 构建 `1.0.2-rc.1` 测试包 | ✅ | `npx electron-builder --win nsis --config.extraMetadata.version=1.0.2-rc.1`（**不改动 package.json**），产出 installer + blockmap + latest.yml |
| 6. 「跳过 1.0.2 后不再提示、1.0.3 仍提示」 | ✅ | `test-update-flow.js`：skip 持久化具体版本号；更高版本仍为 `available` |
| 7. 不发布假版本 | ✅ | 测试 feed 全程只在本机 loopback；**生产 feed 未被写入任何东西** |

**步骤 5（重启安装后版本真的变化）未自动完成 —— 如实记录为人工验收，不是 PASS。**

原因是环境限制，不是产品缺陷。我尝试把它自动化（在 `electron.exe` 里
`require('electron-updater')` 直接跑一次真实检查），但**本机 electron 33.4.11
以 Node 模式启动脚本目录、不注入 `app` API**（实测 `process.type` 为 `undefined`、
`require('electron')` 返回的是 npm 包里的可执行文件路径字符串而不是内置模块），
因此在该环境内拿不到真实的 `autoUpdater`。

我**没有**留下一个半可用的自动化壳去冒充这一步：一个「看起来会验证安装、实际从未验证过」
的测试比没有测试更危险。改为提供发布前校验器 `scripts/test-update-feed.js`
（含 `--live`），它覆盖了这条链上最容易静默失败的部分：

```text
· feed 的 sha512 与安装包不符   → 每个客户端下载完都校验失败
· feed 的 size 与安装包不符     → 进度错误 / 下载被拒
· blockmap 缺失                 → 差分下载失效
· 版本号没递增                  → 客户端永远认为「已是最新」
· feed URL 末尾缺斜杠           → 拼出 .../windowslatest.yml，404，且构建期无报错
· 先发 feed 后传包              → 窗口期内全部 404
```

**人工验收步骤（必须在一台可安装、可提权的 Windows 机器上做）：**

```powershell
# 1. 确认本机装的是 1.0.1-rc.1（无 updater 的版本需先手动装一次）
#    查看：C:\Program Files\Moodify Studio\Moodify Studio.exe 的属性 → 详细信息
# 2. 起一个本机 feed（指向已构建好的 1.0.2-rc.1 产物目录）
# 3. 用环境变量把已安装的 1.0.1-rc.1 指到本机 feed 启动：
$env:MOODIFY_UPDATE_URL = "http://127.0.0.1:<port>/"
& "C:\Program Files\Moodify Studio\Moodify Studio.exe"
# 4. 在应用内走：更新入口 → 检查更新 → 下载更新 → 重启并安装
# 5. 确认：重启后「当前版本」变成 1.0.2-rc.1，且 ~/.moodify/cases 内的
#    case / 决策账本 / 本地设置完好无损（这是最重要的一条）
```

若未签名 NSIS 导致安装阶段被 Windows 阻止，如实记录 `BLOCKED_BY_CODE_SIGNING`，
**不要绕过安全检查**。

### P1 — 完整回归

从 `moodify-desktop/` 执行：

```powershell
npm test
```

从仓库根执行：

```powershell
git diff --check
python scripts/check_repo_structure.py
```

构建验证：

```powershell
cd moodify-desktop
npx electron-builder --win nsis
```

确认生成：installer、blockmap、`latest.yml`。

### P1 — 提交与推送

确认 `dist/`、`build/runtime/` 等 generated artifacts 未进入 Git。然后提交当前改动并推送：

```powershell
git add moodify-desktop/package.json moodify-desktop/package-lock.json `
  moodify-desktop/src/main.js moodify-desktop/src/preload.js `
  moodify-desktop/renderer/index.html moodify-desktop/renderer/app.js `
  moodify-desktop/renderer/style.css moodify-desktop/scripts/test-update.js `
  ops/web_origin/site/rongjingmusic/index.html `
  ops/web_origin/site/rongjingmusic/release.html `
  docs/session-handover-2026-10-05-studio-updater.md
git commit -m "feat(studio): add user-controlled in-app updates"
git push origin codex/studio-v4-latest
```

## 6. 后续每次正式发布流程

1. 递增 `moodify-desktop/package.json` version；禁止复用版本号。
2. 测试通过。
3. 构建 installer + blockmap + `latest.yml`。
4. 未来拿到商业代码签名证书后，先签名再发布；不得签名后再修改二进制。
5. 服务器创建带时间戳 release 目录。
6. 同时发布 installer、blockmap、feed。
7. 原子切换 `current`，保留 `previous`。
8. 公网校验 feed、Content-Length、SHA-256、下载头。
9. 最后才让客户端看到新 feed，避免 feed 先到而安装包尚未上传完成。

## 7. 关键风险

- 当前安装包未商业代码签名。签名证书问题另行办理，不能在代码里伪造 publisher。
- `1.0.0-rc.1` 没有 updater，因此用户需要手动安装一次 `1.0.1-rc.1`；从 1.0.1 起才进入软件内更新路径。
- generic feed 是发布权威；错误覆盖 `latest.yml` 会影响所有已安装客户端，必须 installer/blockmap 就绪后最后发布 feed。
- 不得让 updater 改动或迁移用户的 `~/.moodify/cases`。安装升级必须保留 case、决策账本与本地设置。
- “保留原版本”指继续运行当前安装版本，不等于维护两套 Core 或并行安装两个产品身份。

