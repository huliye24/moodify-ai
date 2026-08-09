# Validation — MFY-PHASE1-DEPTH-004

日期：2026-08-09
方法：E401-E407+ 合成 fixture（14 测试全绿）。

## Fixture 结果

| fixture | 断言 | 结果 |
|---|---|---|
| E401 完整削波证据 | 谱系全解析、SUPPORTED、REJECT_TECHNICAL | ✅ |
| E402 缺失测量引用 | MISSING_CRITICAL → fail-closed INCONCLUSIVE | ✅ |
| E403 源哈希不匹配 | SOURCE_LINEAGE 冲突 → CONFLICTING | ✅ |
| E404 规则版本缺失 | EVIDENCE_INCOMPLETE → 无 REJECT_TECHNICAL | ✅ |
| E405 单声道立体声判断 | OUT_OF_SCOPE + 无假零结果 | ✅ |
| E406 全局/局部上下文 | 非冲突（STATUS 冲突为零） | ✅ |
| E407 真语义冲突 | INVALID 状态 → STATUS 冲突 + fail-closed 违规暴露 | ✅ |

## 附加验证

- 不确定性：7 原因有界枚举（构造校验）
- bundle：确定性 logical hash（两次构建相等；语义变化 → 哈希变化）；保存/重载一致
- 覆盖：evaluated_domains 显式（integrity/level/spectrum/stereo）
- 置信：权威输出无任意概率字段
- 人权威：无机器艺术批准
