# P3 产品入口与交付权威进度

**日期：** 2026-08-22  
**状态：** `CORE_COMPLETE`  
**Canon 判定：** `CANON_CHANGE = NO`

## P3-01 Play / Download 入口统一

**状态：`COMPLETE`**

### Web Player

- 正式入口：`https://play.rongjingmusic.com/`。
- Cloudflare Tunnel 已增加 `play.rongjingmusic.com` ingress，并创建到既有 Moodify Tunnel 的 CNAME。
- Nginx Player vhost 同时接受正式域名与过渡 `.xyz` 域名。
- Product Home 的主导航、Hero、Music 页面和页脚均已切换到正式 Player 域名。
- `rongjinwenchuan.xyz` 暂时保持兼容，不执行 301/302，避免未经流量与客户端验证的中断。
- Player 源码中的默认音频 origin 已切换到 `https://play.rongjingmusic.com/audio`；历史 E2E 文档保留原环境事实。

### Android 公开稳定版

- 当前唯一公开稳定版冻结为 Moodify Music Android `2.0.0`，最低 Android 8.0。
- APK 与 release ZIP 公网和源站均为 HTTP 200。
- 官网明确标注 `Current public stable`，不把仓库中的 2.0.1 / 3.x 归档物声明为已上线版本。
- 官网增加下载完整性信息：
  - APK SHA-256：`7fc6c95f04cb9ed7063cf4f50c8eebcd461748640367490493f270c712ff6175`
  - Release ZIP SHA-256：`acb9ef240418e387d45b55a6b50bfed5962da48bde66a00fbabc29155395a14f`

### 验证证据

- Product/Company 静态站测试：`21/21 PASS`。
- Player schema contracts：`3/3 PASS`。
- Player 工程完整 TypeScript 检查仍有既存 Env/DTO 类型错误；本次不重建运行实例，未将其误写为通过。
- `https://play.rongjingmusic.com/`：HTTP 200。
- `https://play.rongjingmusic.com/healthz`：HTTP 200。
- 真实 WAV Range 请求：HTTP 206，`Content-Type: audio/wav`，`Content-Range: bytes 0-1023/47451230`。
- 浏览器 Play smoke test：播放按钮切换为“暂停”，播放进度开始变化。
- 兼容入口 `https://rongjinwenchuan.xyz/`：HTTP 200。
- Product release：`/var/www/rongjingmusic.com/releases/20260822T031442Z-product-entry`。
- Nginx 与 `cloudflared-moodify` 均为 `active`；旧配置和旧 release 保留。

### 发布事故与修复

- 法律页 release 首次上传未携带 `downloads/`；Cloudflare 缓存短期掩盖了源站 404。
- 已从前一已验证 release 恢复 APK/ZIP，源站重新返回 200，且 SHA-256 与仓库归档一致。
- 后续静态发布必须以“复制上一完整 release 后覆盖静态源码”或显式上传 downloads 的方式生成，切换前必须绕过 CDN 对源站执行下载 HEAD 与 SHA-256 检查。
- 首次 Tunnel DNS 命令使用了错误 zone 证书，生成了一条无用的 `play.rongjingmusic.com.rongjingwenchuan.com` 记录；正确 `play.rongjingmusic.com` 已随后使用对应 zone 证书创建。无用记录不影响业务，但仍需在 Cloudflare DNS 中清理。

## P3-02 Player 首屏收敛

**状态：`COMPLETE`**

- 公开首屏隐藏“授权意向”“创作者中心”“上传作品”和创作者角色标签。
- 保留发现、搜索、我的音乐、当前曲目、曲目列表与完整播放控制。
- Creator / Inbox / Studio 等后台路由与数据能力未删除，只从公开首屏撤下。
- Canonical 源码已采用 listener-first 导航；生产稳定 release 通过兼容样式补丁实现同一公开结果。

### 验证证据

- 本地 Player 测试：`36/36 PASS`。
- 生产 release：`/opt/moodify/music/releases/20260822T033500Z-listener-surface`。
- `moodify-music` 服务：`active`。
- 浏览器可见页面与 accessibility tree 均不包含“上传作品”“授权意向”“创作者中心”。
- 播放 smoke test：按钮从“开始聆听”切换为“暂停”，音频播放功能未回归。

### 构建与回滚证据

- 第一个完整源码候选 build 成功，但生产启动因 Node 自托管环境不支持 `cloudflare:` ESM scheme 而失败；健康门禁阻止验收，并立即回滚到稳定 release。
- 第二个基于旧 release 重建的候选仍暴露相同运行时问题，未切换。
- 最终采用稳定构建资产上的新版本 CSS 文件与 manifest 引用切换，避免 immutable CDN 缓存继续提供旧首屏。
- 所有失败候选和旧 release 均保留，未冒充成功部署。

## P3-03 Player 自托管发布权威

**状态：`COMPLETE`**

- 根因：普通 `npm run build` 未启用自托管别名，导致 `cloudflare:workers` 虚拟模块进入 Node server bundle。
- 正确构建边界：LA Node 生产环境必须使用 `MOODIFY_SELF_HOSTED=1`，由 fail-closed adapter 代替 Cloudflare-only bindings。
- 新增稳定命令：`npm run build:self-hosted`，避免发布人员再次遗漏环境标志。
- README 已将 `play.rongjingmusic.com` 更新为 verified live canonical host，并记录 `.xyz` 为兼容入口。

### 验证证据

- `MOODIFY_SELF_HOSTED=1` Linux build：`PASS`。
- 产物扫描：不存在 `cloudflare:workers`。
- 相关远端测试：`10/10 PASS`；本地完整 Player 测试：`36/36 PASS`。
- 候选 release 在独立 `127.0.0.1:3101` 成功启动并返回首页。
- 完整源码 release 已切换为 `/opt/moodify/music/releases/20260822T032348Z-listener-home`。
- 生产 `moodify-music`：`active`；浏览器 title 为 `Moodify — Play`。
- 公开首屏不含 Creator/Upload/Inbox，官网与公司链接可见。
- 播放 smoke test：进入“暂停”状态，进度从 0 增长至 0.9 秒。

## P3-04 TypeScript 基线

**状态：`COMPLETE`**

- 增加 Cloudflare `DB` / `MEDIA` binding 的项目级 Env 声明。
- `BootstrapUser.id` 保持真实的 nullable 契约；Library / Playlists 在调用用户 API 前显式收窄。
- `TrackDto` 增加 Library API 实际返回的可选顶层 `audio_asset_key`。
- R2 Range 响应显式处理 offset/length 与 suffix 两种联合类型，并为缺省 offset/length 提供符合对象大小的边界值。
- 删除 Playlists 中依赖非空断言的用户 ID 调用。

### 验证证据

- 本地 `npx tsc --noEmit`：`PASS`。
- 本地完整 Player 测试：`36/36 PASS`。
- Linux `npm run build:self-hosted`：`PASS`。
- Linux 相关部署测试：`10/10 PASS`。
- 产物扫描无 `cloudflare:workers`。
- 候选在 `127.0.0.1:3101` 独立启动成功。
- 生产 release：`/opt/moodify/music/releases/20260822T034620Z-types-green`；服务 `active`。
- 公网浏览器 smoke test：title = `Moodify — Play`、Creator 首屏入口不存在、播放进入暂停态且进度增长。

## P3 剩余项

| 项目 | 状态 | 下一步 |
|---|---|---|
| `.xyz` 兼容策略 | `PENDING` | 观察正式域名后再由人类决定 301、302 或长期兼容 |
| Android 下一稳定版 | `PENDING` | 选择候选版本后执行构建、签名、安装 smoke test、哈希与原子发布 |
| Player 公开表面收敛 | `COMPLETE` | 首屏与无障碍树已移除 Creator/上传/授权入口，播放 smoke test 通过 |
| Player TypeScript 基线 | `COMPLETE` | build、tests 与本地 `tsc --noEmit` 均通过 |
| 错误 DNS 记录清理 | `PENDING` | 删除 `play.rongjingmusic.com.rongjingwenchuan.com`，不得删除正确正式域名 |

## 下一个最小任务

> **P4-01：统一 Product、Company、Player 三站的品牌导航、页脚语法与返回路径。**
