# Codex 独立验收矩阵｜DSK-MFY-DAW-BACKENDS-014

## P0

| ID | 验收项 | 失败处置 |
|---|---|---|
| P0-01 | 全流程无需 GUI、窗口、鼠标、键盘和默认音频设备 | REWORK |
| P0-02 | 原音频只读且前后 hash 一致，输出仅进入新目录 | HOLD |
| P0-03 | CLI DAW project/processing/render evidence 是事实源 | REWORK |
| P0-04 | 未支持节点、缺失工具、超时和非零退出 fail closed | REWORK |
| P0-05 | 子进程参数数组化，无 shell 注入面 | HOLD |
| P0-06 | 无联网安装、插件下载、许可接受和全局配置修改 | HOLD |
| P0-07 | 稳定退出码、JSON 结果、证据可回读 | REWORK |
| P0-08 | 旧 CLI 与相关 Core 回归通过 | REWORK |
| P0-09 | 不把 REAPER/Ardour/Audacity/Audition 当核心依赖 | REWORK |

## 功能

| ID | 验收项 |
|---|---|
| F-01 | Project/Track/Clip/Bus/Send/Master/Processing/Automation 严格类型 |
| F-02 | schema version、严格校验、非法/循环路由拒绝 |
| F-03 | NativeDSPBackend 复用既有处理链 |
| F-04 | FFmpegBackend probe、plan、render、verify 成立 |
| F-05 | trim/offset/fade/gain/pan/mute/solo、多轨、bus/master 成立 |
| F-06 | stems/buses/master、manifest/log/hash/指标完整 |
| F-07 | engines/validate/plan/render/verify 五个 CLI 成立 |
| F-08 | GUI DAW 仅 exporter/handoff 声明，未实现明确 NOT_IMPLEMENTED |

## 验证

| ID | 验收项 |
|---|---|
| V-01 | mono/stereo、采样率、bit depth、Unicode 路径 |
| V-02 | 缺失源/工具/能力、未知节点、错误路由失败注入 |
| V-03 | 超时、取消、非零退出、半成品行为可证明 |
| V-04 | 双运行字节一致或有合同定义的内容级等价 |
| V-05 | 源 hash 不变、输出树和证据 hash 一致 |
| V-06 | 测试、相关回归、CLI smoke、lint/type check 可追溯 |

最终由 Codex 独立重跑关键命令并抽查证据；DeepSeek 自报 PASS 不等于验收通过。
