# 03 — Data Identity Contract

**W01-P03 · 2026-08-17 · 唯一关系：Track / Job / Object / Hash / Version / Evidence / Provenance**

## 1. Track → Source

每个 canonical Track 有且只有一个 canonical source reference：

```text
tracks.track_id --source_object_id--> objects(object_id, artifact_type='source')
tracks.source_hash = sha256(source bytes)
```

## 2. Job → Track

每个 Job 属于一个 Track：`jobs.track_id FK -> tracks.track_id`（NOT NULL）。

## 3. Object → Track

每个 canonical object 可追溯到 Track：`objects.track_id FK`（NOT NULL）。

## 4. Produced Object → Job

pipeline 产物必须追溯 producer Job：`objects.job_id FK`（source 除外——source 非 job 产物）。

## 5. Evidence → Claim

Evidence 必须说明证明什么（INV-07）：`evidence.claim` 非空；且挂 subject（track/job/object 至少一个）。

## 6. Version → Production

每个 final render 必须能回答（INV-06）：

- 哪个 pipeline version → `objects.pipeline_version`
- 哪个 processing profile/preset version → `jobs.processing_profile_version`
- 哪个 producer/tool version → `objects.producer_version`
- 哪些 source/stem inputs → `objects.parent_object_id` 链 + track 的 source_object_id
- 哪个 job → `objects.job_id`

## 7. Provenance Chain（反向追溯）

```text
READY Render (objects)
  → Producer Job (jobs)
  → Pipeline/Preset/Tool Version (objects.pipeline_version / jobs.processing_profile_version / objects.producer_version)
  → Input Objects (objects.parent_object_id)
  → Canonical Source (objects, artifact_type='source')
  → Source Hash (tracks.source_hash)
  → Track (tracks)
```

实现：`moodify.data_plane.repository.provenance_chain(object_id)` → [object, job, track, source_object]（Test C 验证）。

## 8. 不变约束（本契约的硬性条款）

| 条款 | 内容 |
|---|---|
| Source 不可覆盖 | INV-01（Test B） |
| Key ≠ identity | INV-02（object_id 是身份） |
| DB 无大音频 | INV-03（Test H） |
| OSS 无 authoritative job state | INV-04 |
| READY 可追溯 | INV-05（Test C） |
| render 有 pipeline version | INV-06 |
| evidence 有 claim | INV-07（Test D） |
| orphan/missing 可检测 | INV-08/09（Test F/G） |
| 幂等写入 | INV-11（Test E） |
| ownership ≠ hash | INV-12（Test A） |

## 9. 数据类

| Class | 内容 | 访问 |
|---|---|---|
| PUBLIC_METADATA | track 标题级元数据（当前无） | 公开 |
| PRIVATE_SOURCE | source bytes | 私有（signed URL / service） |
| RENDER | render bytes | 私有/受控 |
| EVIDENCE | evidence 记录 | 内部 |

## 10. 本契约不定义

- authoritative job state machine（P04）
- 权限系统（P06 用户体系）
- 播放 API（P06）
