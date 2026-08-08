# DSK-MFY-CAPABILITY-ACCRETION-020｜失败台账

**日期：** 2026-08-02 UTC  
**规则：** 历史失败不得删除或改写为成功（PR-007）。

| # | 阶段 | 失败 | 根因 | 处置 |
|---|---|---|---|---|
| 1 | 测试 | 规则对不存在的 artifact 调 `stat()` 抛 FileNotFoundError | 测试传入 `"s.pdf"` 等虚构路径，规则未做存在性检查 | 规则防御性 `Path(a).exists()` 前置检查（nonzero_size/page_count/no_nan） |
| 2 | CLI | `capability validate` PASS 时仍打印失败消息 | 显示逻辑无条件打印 `result.message`（规则默认 message 是失败文案） | PASS 时不显示 detail |

## 负面知识沉淀

- EX-009 模式第三次验证：验证规则必须对**缺失/虚构路径**健壮——执行记录
  重放时产物可能已被清理，规则不能崩溃。
- 地质记录原则落地：本任务 6 条通用规则全部携带 historical_source，规则库
  扩充禁止为凑数量造规则（系列 §3.5 / 020 编排 Stage A）。

## 边界

- 本机 media.transcode 仅 ffmpeg 一个 provider，多 provider 候选/回退的
  真实触发场景未跑（机制已实现并测试，接入依赖后续任务）。
