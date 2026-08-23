# 09 — Data Plane Test Report

**W01-P03 · 2026-08-17 · 9/9 PASS（tests/test_data_plane.py）**

## 任务书 Test A..H 映射

| 测试 | 名称 | 验证 | 结果 |
|---|---|---|---|
| Test A | same source hash | 同 hash 两 track 不合并（INV-12） | PASS |
| Test B | immutable source | 同 object_id 重注册不覆盖（INV-01） | PASS |
| Test C | object provenance | render→job→track→source 链（INV-05/06） | PASS |
| Test D | evidence provenance | evidence 对 object/job/claim（INV-07） | PASS |
| Test E | idempotent register | 重复 manifest 无重复行（INV-11） | PASS |
| Test F | missing object detection | DB 引用但 store 无对象（INV-09） | PASS |
| Test G | orphan object detection | store 有对象但 DB 无引用（INV-08） | PASS |
| Test H | no large blobs in DB | schema 无 BLOB 列（INV-03） | PASS |
| +1 | key round-trip | build/parse 双向一致 | PASS |

## 执行

```text
python -m pytest moodify-core-package/tests/test_data_plane.py
9 passed in 7.15s
ruff check src/moodify/data_plane tests/test_data_plane.py
All checks passed!
```

## 覆盖说明

- 测试使用 SQLite（DataPlaneRepository 实现）与 LocalFileAdapter（dry-run）——目标 PolarDB/OSS 因 Write Gate BLOCKED 未接。
- OSSAdapter 为占位（raise OSS_WRITE_BLOCKED），无测试（避免假实现）。
- 未跑全量回归（P03 是新增包，与既有模块无交集；guard 测试已在此前验证）。
