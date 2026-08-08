# DSK-MFY-CAPABILITY-ACCRETION-017｜失败台账

**日期：** 2026-08-02 UTC  
**规则：** 历史失败不得删除或改写为成功（PR-007）。

| # | 阶段 | 失败 | 根因 | 处置 |
|---|---|---|---|---|
| 1 | Stage B | ffmpeg/sox 探测 found=False（尽管 winget 已安装） | winget 目录布局有 `bin/` 子目录（ffmpeg）与根目录（sox）两种；候选查找只检查 `build/bin/<exe>` | 候选查找同时检查 `build/bin/<exe>` 与 `build/<exe>` |
| 2 | Stage B | winget glob 返回空（第二轮仍 False） | `(WINGET_ROOT / 'Gyan.FFmpeg_*').glob('*')` 把通配符当成字面路径 | 改为 `WINGET_ROOT.glob('Gyan.FFmpeg_*')` |
| 3 | Stage B | basic_pitch 版本探测取到 `WARNING:root:Coremltools...` 行 | `basic_pitch.__version__` 不存在，且 import 输出 WARNING 到 stdout | 改用 `importlib.metadata.version('basic-pitch')` + 取最后一行 |
| 4 | Stage B | moodify_self found=False | `parents[2]` 指向 src 而非包目录，score_engine 路径判断失败 | 改为 `parents[1]`（moodify 包目录） |
| 5 | Stage C | `moodify capabilities list` 报 unrecognized arguments | `capabilities` 命令名被 cli_v2 顶层占用（既有静态清单） | 改用 `capability`（单数），cli_v2 不动 |
| 6 | 测试 | `test_found_implies_binary_path` 失败 | moodify_self 是内部能力（无 binary_path），断言过严 | 测试排除 moodify_self（内部能力语义） |

## 负面知识沉淀

- EX-009（CLI 参数假设必须实测）再次验证：winget 两种布局差异就是"工具包布局
  假设"失败的实例——已写入探测器的已知失败模式注释。

## 边界

- 注册表快照（`capability_registry.json`）在环境变化后需 `capability regenerate`
  刷新；探测本身只读、可重复。
