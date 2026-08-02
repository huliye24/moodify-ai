# DSK-MFY-ANDROID-003｜FAILURE_LEDGER

| # | 现象 | 根因 | 修复 | 是否遗留 |
|---|---|---|---|---|
| 1 | `test_pair_is_idempotent_per_device` 失败：同 device_id 重复 pair 返回不同 token | `PairTokenStore.issue` 用 device_id 直接查 dict，但 dict key 是 token_id | 改为遍历 values 匹配 device_id 且未撤销 | 否 |
| 2 | `test_revoke_own_token` 失败：撤销后再次 revoke 返回 200 而非 401 | `find_by_token` 未排除已撤销记录 | 匹配条件增加 `not record["revoked"]` | 否 |
| 3 | 编译错误 `Unresolved reference 'Wechat'`（UploadFlowScreen + ProcessingHubScreen） | material-icons-extended 2025.06.01 无 `Icons.Outlined.Wechat` | 替换为 `Icons.Outlined.Chat` | 否 |
| 4 | 编译错误 `Checkbox` 参数不匹配：`Function0<Unit>` vs `Function1<Boolean, Unit>?` | material3 Checkbox 的 onCheckedChange 带 Boolean 参数 | `Checkbox(checked, { toggle() }, ...)` | 否 |
| 5 | 首次构建失败：JAVA_HOME 未设置；SDK location not found | 环境变量未配置 | `JAVA_HOME=<Android Studio jbr>` + `ANDROID_HOME=<SDK>`；后续构建命令文档化 | 否（运行环境问题，非代码） |
| 6 | JVM 单测 `com.sun.net.httpserver` 全部 Unresolved | 该 Android 工程 unit test 编译环境不可用 jdk.httpserver 模块 | 改用纯 `ServerSocket` 手写迷你 HTTP fake server（java.base） | 否 |
| 7 | `.gitignore` 的 `data/` 规则误伤 `com/moodify/app/data` 包 | 全局 `data/` 匹配任意层级同名目录 | 追加 `!apps/android/.../data/` 豁免规则 | 否 |
| 8 | 基线 commit 混入 494 个 gradle build 产物 | `git add apps/` 未排除 build 目录 | 追加 .gitignore 规则 + 提交清理（83d1e86/9fb4e40） | 否 |

**已知限制（如实列出，无隐藏）：**

1. 令牌存储为内存态：服务端重启后所有配对失效，客户端需重新配对（产品决策：本地短期信任，已在 docs/api/v1.md 声明）；
2. `BaseUrlStore` 目前只有默认值 + sanitize，UI 层尚未提供局域网地址编辑入口（Release 构建已拒绝非本地明文；编辑入口留待后续包）；
3. INCOMPATIBLE（版本不兼容）分类逻辑已实现于客户端与契约，未做 UI 专项展示（服务端当前版本即契约版本，无法在同机复现不兼容场景；单测路径已覆盖分类）；
4. 真机验证在 debug 构建 + cleartext 流量下进行；release 收紧（network security config 仅允许本地明文）属 ANDROID-011 安全包范围；
5. moodify-bridge 存在 10 个 pytest 收集错误（ModuleNotFoundError: moodify_bridge / typer）——属 ORDER-BEAUTY-022 修复范围，003 允许范围内不处理，已如实记录。
