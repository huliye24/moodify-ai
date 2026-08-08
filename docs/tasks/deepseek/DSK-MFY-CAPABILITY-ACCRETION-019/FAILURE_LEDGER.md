# DSK-MFY-CAPABILITY-ACCRETION-019｜失败台账

**日期：** 2026-08-02 UTC  
**规则：** 历史失败不得删除或改写为成功（PR-007）。

| # | 阶段 | 失败 | 根因 | 处置 |
|---|---|---|---|---|
| 1 | 测试 | 成功执行测试 assert failed | 测试夹具用假 WAV（`RIFF\x00` 20 字节），ffprobe 报 `Invalid data found` exit 1 | 改用合法 8kHz 440Hz 正弦波 wave 模块生成 fixture |
| 2 | 测试 | 篡改测试断言 `"serves"` 失败 | 篡改 capability_id 后签名必然失效，网关在签名层拦截（早于 provider 校验）——这是不可变性的设计保证 | 断言改为 `signature mismatch`，测试更名 `test_tampered_envelope_rejected_at_gateway` |

## 负面知识沉淀

- EX-009 再次验证：测试 fixture 必须是**真实可解析**的输入（假 WAV 导致
  ffprobe 真实失败），假 fixture 会让 E2E 测试误报——已改为合法正弦波。
- 不可变性设计证明：任何对 envelope 的篡改（含 output_dir 路径逃逸尝试）
  都在签名层被拦截，无法到达 provider——这比在 gateway 里逐个字段校验
  更强，是 019 的核心安全保证。

## 边界

- 未接入 cli_v2 case 系统（编排明确不强行接入）；对接顺序在
  CAPABILITY_ACCRETION_ARCHITECTURE.md 注明。
- 本地签名（CLI approve）是模拟批准；真实人工审批签名机制是后续工作。
