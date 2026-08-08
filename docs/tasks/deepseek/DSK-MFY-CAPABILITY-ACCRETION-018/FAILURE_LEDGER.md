# DSK-MFY-CAPABILITY-ACCRETION-018｜失败台账

**日期：** 2026-08-02 UTC  
**规则：** 历史失败不得删除或改写为成功（PR-007）。

| # | 阶段 | 失败 | 根因 | 处置 |
|---|---|---|---|---|
| 1 | Stage B | sox 真实调用 exit 1 | `--norm -1` 被 sox getopt 当成选项 `-1` | 改 `--norm=-1` 单参数形式 |
| 2 | Stage B | sox stat 输出无 artifact | sox `stat` 统计输出到 **stderr**，基类 stdout_target 只捕获 stdout | 基类在 stdout_target 模式把 stderr 合并到同一文件（subprocess.STDOUT） |
| 3 | Stage B | ffmpeg/rubberband 版本探测为 None | 版本输出在 stderr（ffmpeg `-version`、rubberband `--version`） | 基类版本探测合并 stdout+stderr 取第一行 |
| 4 | Stage B | Audacity invoke errors[0] == 'A' | `errors=("a" "b")` 相邻字符串拼接成单个 str 而非元组 | 加尾逗号 `errors=("a" "b",)` |
| 5 | 测试 | mock 断言拿到 `--version` 命令而非 invoke 命令 | `version()` 在 invoke 内部也被调用，subprocess.run 被 mock 两次 | 测试用 `call_args_list` 过滤含 `-o`/`stat` 的调用 |
| 6 | 测试 | BasicPitchAdapter.KNOWN_FAILURE_MODES 属性不存在 | 常量是模块级而非类属性 | 测试改 import 模块常量 |

## 负面知识沉淀

- EX-009（CLI 参数假设必须实测）再次验证：sox `--norm` 参数形式、stat 输出流
  均为实测发现；已作为 provider 行为记录在 sox_adapter 注释与 known_failure_modes。

## 边界

- Audacity headless 自动化明确不实现（human_handoff），非缺漏。
- BasicPitchAdapter 未做真实推理执行（耗时长，008 已验证底层）。
