# 04 — Data Plane Invariants

**W01-P03 · 2026-08-17 · 实现状态：全部有代码/测试对应或明确记录**

| # | Invariant | 实现 | 验证 |
|---|---|---|---|
| INV-01 | Source object 不可原位覆盖 | key 约定 source 仅 track 级；register_object 幂等（同 id 不覆盖）；适配器 put 由调用方约束 | Test B |
| INV-02 | Object key 不是业务身份 | object_id（UUIDv7）为唯一身份；key 仅 locator | 模型设计 |
| INV-03 | DB 不保存大音频二进制 | objects 表只有元数据（byte_size 等）；migration SQL 无 BLOB | Test H |
| INV-04 | OSS 不保存 authoritative job state | jobs 表在 DB；OSS 只存对象 | 模型设计 |
| INV-05 | READY 可追溯到 source | provenance_chain：object→job→track→source_object | Test C |
| INV-06 | final render 有 pipeline version | objects.pipeline_version（producer 必填） | Test C（断言字段） |
| INV-07 | evidence 有 claim | register_evidence claim 非空强校验 | Test D |
| INV-08 | orphan object 可检测 | repository.orphan_objects(adapter) | Test G |
| INV-09 | missing object 可检测 | repository.missing_objects(adapter) | Test F |
| INV-10 | 引用删除显式 | 本包无 delete 路径（删除语义 P04）；注册即引用 | 设计记录 |
| INV-11 | 写入幂等 | register_* 以 id 幂等（UNIQUE 约束 + 存在即返回） | Test E |
| INV-12 | ownership ≠ hash | track 唯一性按 track_id 而非 hash；owner_scope 独立 | Test A |
| INV-13 | 客户端无长期云凭据 | Android 仅持公开 URL（P02 R7）；本包无客户端凭据路径 | 设计记录 |
| INV-14 | 现实胜过 schema | 05 mapping 尊重既有 19 表/本地资产；migration 非破坏性 | 05/06 报告 |
