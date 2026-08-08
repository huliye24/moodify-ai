# Ocean Listen 听觉传感器操作手册（DSK-MFY-OCEAN-ABSORPTION-001）

日期：2026-08-08
状态：已集成（默认禁用）

## 定位

Ocean Listen 是 Moodify 的**外部听觉传感器**，覆盖 hear + represent 层。
它不批准艺术决策、不干预、不把 case 直接推向 TECHNICALLY_VALIDATED。
judge/intervene/verify/learn 由 Moodify 权威控制。

## 启停

```bash
# 默认禁用（configs/ocean_adapter.json 的 enabled: false）
# 显式启用一次分析：
python -m moodify.cli case analyze <project> <case_id> --sensor ocean

# 测试用 fake 传感器（不调用 vendored 上游，不下载模型）：
python -m moodify.cli case analyze <project> <case_id> --sensor ocean --fake

# 永久启用：configs/ocean_adapter.json 改 enabled: true
```

## 配置（configs/ocean_adapter.json）

| 键 | 默认 | 说明 |
|---|---|---|
| enabled | false | 显式启用 |
| upstream_commit | 928dfba6… | pin（不允许静默改动） |
| ocean_root | third_party/ocean-listen | vendored 上游 |
| analysis_profile | shallow | shallow \| deep |
| mode | auto | auto/music/solo/voice/mixed |
| lyrics_mode | disabled | disabled/whisper/sensevoice/netease |
| timeout_seconds | 1800 | 进程超时 |
| cache_root / output_root | artifacts/ocean_* | 产物位置 |
| allow_unreviewed_commit | false | false 时强制 pin |

## 证据产物（<case_root>/06_ocean_listen/）

- `evidence_registry.json`：6 类 artifact × 10 字段（case_id/run_id/source_sha256/
  specification_hash/upstream_commit/configuration_hash/artifact_sha256/
  created_at/producer + artifact_type），原子写、确定性 run_id 幂等。
- 运行目录 `artifacts/ocean_bridge/<case_id>/<run_id>/`：
  raw/ocean_report.json、normalized/auditory_observation.v1.json、
  quality/gate_result.json、evidence/run_manifest.json、logs/stdout.log、logs/stderr.log。

## 质量门语义

- **PASS/WARN**：observation 并入 case.analysis（WARN 保留 warnings）。
- **FAIL**：证据仍注册留痕，observation **不并入**，warnings 附加。
- 传感器本身永不推进状态（ANALYZING → ANALYZED 由 case.analyze 完成）。

## 已知局限

- velocity 是模型置信度代理，不是响度；响度请用 RMS 证据。
- 分类/音色/人声部分/固定阈值结果均标记 **experimental**。
- 不推广性别推断（pitch → gender 被隔离）。
- NetEase 歌词不是默认生产依赖。
- melisma/垫音/即兴等失败分类与 Phase C 乐谱先验未实现（见 lyric_align 同级局限）。
- 双跑/重跑不覆盖证据但会占用磁盘（幂等按确定性 run_id）。

## 基准计划（benchmark）

1. 用 Phase E 验证集（`docs/verification/lyric_align_verification_set.md` 同批曲目）
   对 Ocean 浅/深报告做人工锚点评估：preclassification 准确率、note 命中率、
   RMS 动态与真实响度相关性。
2. 记录固定阈值分类的失败率（固定阈值按 ADR 语义 quarantine）。
3. 输出 `docs/verification/ocean_benchmark_report.md`；基准完成前禁止宣称
   Ocean 听音精度。

## 回滚

```bash
# 1. 删除证据与接线产物
rm -rf <case>/06_ocean_listen  artifacts/ocean_bridge artifacts/ocean_cache
# 2. 恢复状态机（可选）：ALLOWED[SPECIFIED]={ANALYZED} + 移除 begin_analysis
# 3. 删除 vendored 上游（如不再需要）
rm -rf third_party/ocean-listen third_party/ocean_listen_snapshot
# 4. config 恢复 enabled: false（默认即如此）
```
