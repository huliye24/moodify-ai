# MFD-002 — Electron Foundation
## Codex 正式执行任务书

**任务编号：** MFD-002  
**执行对象：** Codex  
**执行模式：** 工程初始化 + 安全地基 + 证据验收  
**禁止跨阶段：** 是

---

# 0. 核心目标

不要“先把界面做出来”。

本包的核心目标是：

> **创建一个不会妨碍后续 Moodify Desktop 演进的 Electron 基础工程。**

它应该足够薄、足够安全、足够可验证。

---

# 1. 前置检查

执行前：

1. 阅读 MFD-001 最终输出；
2. 确认 Desktop repository location；
3. 确认 license；
4. 确认 package manager；
5. 确认 Node 版本策略；
6. 确认当前工作区 clean；
7. 记录 branch / SHA；
8. 确认不在生产服务器执行。

如 MFD-001 决定独立仓库：

> 在指定 Desktop 仓库执行。

如决定 monorepo：

> 仅在 MFD-001 指定目录执行。

不得自行改仓库策略。

---

# 2. 技术栈基线

除非 MFD-001 明确给出冲突结论，默认：

```text
Electron
TypeScript
React
Vite
Electron Forge
```

包管理器：

> 以 MFD-001 / 仓库既有决策为准。

不要同时引入多个构建系统。

不要同时引入 Electron Builder + Forge。

本阶段默认只保留一条打包主线。

---

# 3. 目录架构

建议最小结构：

```text
src/
├── main/
│   ├── index.ts
│   ├── window.ts
│   ├── lifecycle.ts
│   └── ipc/
│
├── preload/
│   ├── index.ts
│   └── bridge.ts
│
├── renderer/
│   ├── main.tsx
│   ├── App.tsx
│   └── styles/
│
├── domain/
│   ├── playback/
│   ├── session/
│   └── library/
│
├── services/
│   ├── config/
│   ├── logging/
│   └── api/
│
└── shared/
    ├── contracts/
    ├── errors/
    └── types/
```

但不要为了“架构好看”创建几十个空文件。

原则：

> **只创建后续三包明确会使用的稳定边界。**

---

# 4. Electron 安全基线

必须：

- `contextIsolation: true`
- renderer 不拥有 Node.js
- sandbox 能开则开
- 不启用 `nodeIntegration`
- 不允许 renderer 任意 `ipcRenderer.send`
- preload 只暴露白名单 API
- 所有 IPC channel 常量集中定义
- IPC payload 有 TypeScript 类型
- 对外部 URL 使用明确 allowlist / handler
- 禁止 renderer 直接访问文件系统
- 禁止 renderer 读取环境变量
- 禁止 renderer 得到 secrets

目标模型：

```text
Renderer
   ↓ only typed bridge
Preload
   ↓ allowed IPC
Main
```

不允许：

```text
Renderer → Node fs
Renderer → shell
Renderer → process.env
Renderer → raw ipcRenderer
```

---

# 5. Window 基线

首版只允许一个主窗口。

实现：

- stable create / show / close
- single instance guard
- basic window state
- devtools 仅开发态
- production 禁止自动打开 devtools
- external links 不在 app 内任意导航
- navigation guard

不要实现：

- tray
- mini player
- floating lyrics
- multiple windows
- settings window
- login popup

这些属于后续。

---

# 6. Renderer 基线

只做一个非常简单的占位页。

页面内容建议：

```text
Moodify
Desktop Alpha Foundation

[ Ready ]
```

最多显示：

- app name
- version
- runtime state
- build environment

禁止把它提前做成正式 UI。

不要做：

- vinyl animation
- play button
- album cover
- library
- playlist
- sidebar
- settings
- theme marketplace

原因：

> 本包验证的是工程骨架，不是产品视觉。

---

# 7. Typed Bridge

至少建立一个无敏感能力的示例 bridge，例如：

```ts
window.moodify.app.getVersion()
window.moodify.app.getPlatform()
```

要求：

- Renderer 只通过 `window.moodify`
- bridge 接口有声明文件
- IPC 输入输出有类型
- 错误统一序列化
- 不能暴露 Electron 原生对象

---

# 8. Config / Secrets 边界

建立配置规则：

```text
PUBLIC_CLIENT_CONFIG
PRIVATE_BUILD_CONFIG
RUNTIME_SECRETS
```

但本包禁止接真实 secrets。

`.env.example` 只能出现：

- placeholder
- non-secret config

禁止：

- service-key
- API token
- OSS secret
- DB password
- Audiolla token
- Cloudflare token

README 要明确：

> Desktop 客户端永远不应该持有服务器级永久 secret。

---

# 9. 日志基线

建立最小日志模块：

至少覆盖：

- app start
- app version
- window create
- uncaught error
- renderer fatal error event
- package/build version

禁止默认记录：

- token
- secret
- full auth header
- private media URL
- password
- user personal data

日志应可替换。

不要绑定重型 observability SDK。

---

# 10. 错误边界

建立：

- main process unhandled error handling
- renderer error boundary
- IPC error contract

错误至少分：

```text
AppError
ConfigError
IpcError
NetworkPlaceholderError
PlaybackPlaceholderError
```

后两者可以是类型占位，不实现网络和播放。

---

# 11. Domain 占位

只定义未来边界，不实现业务。

可以定义最小 interface：

```text
SessionService
LibraryService
PlaybackService
```

但所有真实方法可以为空 interface / placeholder。

重要：

> 不要创建 mock cloud 后把它当成真实生产协议。

如需演示，只允许本地 static stub，并显式标记：

`DEVELOPMENT_STUB_ONLY`

---

# 12. 测试

至少包含：

### Unit
- bridge 类型 / handler
- config parsing
- error serialization

### Smoke
- Electron 启动
- window create
- preload bridge 可访问
- renderer 不具备 Node API

### Build
- typecheck
- lint
- test
- package

如 CI 环境无法启动 GUI：

> 明确区分 unit CI 与 local Windows smoke。

不要假造 GUI test 已通过。

---

# 13. Scripts

建议：

```text
dev
build
package
make
lint
typecheck
test
verify
```

其中：

`verify`

应尽可能串联：

```text
typecheck
→ lint
→ test
→ build/package validation
```

避免人类记忆多个命令。

---

# 14. Windows 构建

本包至少做到：

> 在 Windows 环境可以生成可运行的 unpacked/package artifact。

是否生成 installer 取决于 Forge 默认 maker 与本包约束。

MFD-007 才负责产品化安装器。

所以本包不必处理：

- 正式安装体验
- 签名
- auto-update
- release channel

---

# 15. CI

如果仓库已有 GitHub Actions：

- 复用既有规范；
- 不破坏其他项目 CI。

如果独立 Desktop repo：

建议至少增加：

```text
typecheck
lint
test
build
```

对 Windows packaging 若成本较高，可以先作为明确 job。

不得引入依赖生产 secret 的 CI。

---

# 16. 文档

至少创建：

```text
README.md
docs/ARCHITECTURE.md
docs/SECURITY_BOUNDARY.md
docs/DEVELOPMENT.md
docs/MFD-002-EVIDENCE.md
```

README 只解释：

- 这是什么
- 怎么运行
- 怎么验证
- 当前不是什么

不要重新写 Moodify 品牌长文。

---

# 17. 禁止项

本包严禁：

- 真实用户登录
- 真实 API token
- 真实云端播放
- service key
- 连接数据库
- 调 Ear
- 调 Audiolla
- 调 LALAL
- 音频上传
- 音频处理
- WASAPI
- C++ addon
- ffmpeg binary bundle
- remote code loading
- arbitrary web navigation
- `nodeIntegration: true`
- `contextIsolation: false`
- preload 暴露 `ipcRenderer`
- renderer 直接 `require`
- 关闭 webSecurity
- 使用 `allowRunningInsecureContent`
- 硬编码生产域名而没有 config boundary

---

# 18. Definition of Done

本包完成必须有证据：

1. Electron dev 启动成功；
2. Window 正常；
3. Renderer 正常；
4. typed preload bridge 正常；
5. renderer 无 Node；
6. contextIsolation 开启；
7. typecheck pass；
8. lint pass；
9. unit tests pass；
10. smoke tests 有真实结果；
11. Windows package/build 成功；
12. 无 secret；
13. 无真实 Cloud 依赖；
14. 无业务逻辑跨阶段；
15. 产出 evidence 文档。

---

# 19. 最终回复格式

Codex 最终只需报告：

1. repository / branch / SHA
2. created files
3. architecture
4. security defaults
5. commands
6. tests
7. Windows build artifact
8. known limitations
9. MFD-003 readiness
10. diff summary

最后给：

> `MFD-003: GO / CONDITIONAL GO / NO-GO`
