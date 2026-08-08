# DSK-MFY-CAPABILITY-ACCRETION-017｜Codex 独立验收矩阵

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| Q0-01 | P0 | 009 HANDOFF 可读且依赖边界明确 | HOLD |
| Q0-02 | P0 | Registry/manifest schema 在编码前冻结 | HOLD |
| Q0-03 | P0 | 探测只读性：无安装/下载/修改第三方 | HOLD |
| Q1-01 | P0 | 未安装能力不注册为可用（known_missing 显式） | HOLD |
| Q1-02 | P0 | manifest 未知键拒绝 + 双运行序列化一致 | HOLD |
| Q1-03 | P0 | 许可证/版本真实记录，无猜测 | HOLD |
| Q1-04 | P1 | 首批能力矩阵覆盖真实环境（≥6 能力） | REWORK |
| Q2-01 | P0 | 不 import/不修改 009/008 实现 | HOLD |
| Q2-02 | P0 | 注册表持久化 round-trip 无损 | HOLD |
| Q2-03 | P1 | 探测存在/缺失两态都有测试 | REWORK |
| Q3-01 | P0 | 未把 provider 名写成业务语言（capability 抽象） | HOLD |
| Q3-02 | P0 | 没有 MATLAB 调用、没有网络下载 | HOLD |
| Q3-03 | P1 | 测试、CLI smoke、Ruff、文档通过 | REWORK |
| Q3-04 | P1 | 架构文档包含六层定位与后续接入顺序 | REWORK |

Codex 将独立执行：伪造缺失工具路径、非法 manifest 字段、双运行、注册表
round-trip、探测真实环境、能力矩阵与真实安装对比、旧 CLI 回归、Ruff。
