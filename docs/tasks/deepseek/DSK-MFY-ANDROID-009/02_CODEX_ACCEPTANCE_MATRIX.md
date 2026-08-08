# DSK-MFY-ANDROID-009｜Codex 独立验收矩阵

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| Q0-01 | P0 | 前序 HANDOFF 可读且依赖 ACCEPT | HOLD |
| Q0-02 | P0 | 真机证据（截图/Logcat/设备信息）非 Preview | HOLD |
| Q1-01 | P0 | 无假进度/假状态；演示与真实明确区分 | HOLD |
| Q1-02 | P0 | 作品资产 SHA-256 可校验，无越权/泄漏 | HOLD |
| Q2-01 | P0 | 失败注入（断网/超时/4xx/5xx）行为可审计 | HOLD |
| Q2-02 | P0 | 不修改电脑端代码、不引入未授权依赖 | HOLD |
| Q3-01 | P0 | 前序门禁回归全绿 | HOLD |
| Q3-02 | P1 | Compose/单元测试覆盖主要状态与导航 | REWORK |
| Q3-03 | P1 | 已知限制如实列出，无隐藏 | REWORK |
| Q3-04 | P1 | PROGRESS/VALIDATION/FAILURE_LEDGER/HANDOFF 齐全 | REWORK |

Codex 将独立执行：真机复现、失败注入复测、SHA-256 校验、权限/日志审计、
前序回归、与电脑端契约核对。
