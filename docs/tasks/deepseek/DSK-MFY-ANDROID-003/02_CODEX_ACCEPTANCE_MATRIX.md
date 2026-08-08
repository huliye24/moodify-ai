# ANDROID-003｜Codex 验收矩阵

| ID | 级别 | 验收项 | 通过条件 |
|---|---|---|---|
| A003-01 | P0 | API 契约 | 文档、OpenAPI/schema 与实现一致 |
| A003-02 | P0 | USB 连接 | adb reverse 后 health/pair 真机成功 |
| A003-03 | P0 | 分层边界 | App 只依赖 DTO/repository，不认识 Python 内部类型 |
| A003-04 | P0 | 错误语义 | 离线、超时、未授权、版本不兼容可区分 |
| A003-05 | P0 | 凭据安全 | Keystore 保存，日志与源码无令牌 |
| A003-06 | P0 | 兼容门禁 | 022 收集门禁与 Android 构建均通过 |
| A003-07 | P1 | 局域网 | 用户显式地址可连接，无隐式扫描 |
| A003-08 | P1 | 契约测试 | 服务端与 Android fake server 测试通过 |

拒绝：硬编码电脑 IP；直接暴露 traceback/绝对路径；临时复制后端；前置门禁未满足仍宣布完成。

