# 01 — Object Key Convention

**W01-P03 · 2026-08-17**

## 设计约束（§2.4）

- 可读但不过度依赖文件名；
- 不依赖用户原始文件名作为唯一身份（INV-02：key 是 locator 不是 identity）；
- 不使用 DB 自增 ID 作为唯一追溯依据；
- 支持 Track / Job / Artifact Type / Version；
- 不含 Secret、不含 PII；
- Windows/Linux/cloud 安全（小写、无空格、'/' 分隔）；
- 不依赖中文文件名。

## 约定

```text
bucket: moodify
moodify/tracks/{track_id}/source/{object_id}.{ext}
moodify/tracks/{track_id}/jobs/{job_id}/stems/{object_id}.{ext}
moodify/tracks/{track_id}/jobs/{job_id}/analysis/{object_id}.{ext}
moodify/tracks/{track_id}/jobs/{job_id}/intermediate/{object_id}.{ext}
moodify/tracks/{track_id}/jobs/{job_id}/renders/{object_id}.{ext}
moodify/tracks/{track_id}/jobs/{job_id}/evidence/{object_id}.{ext}
```

## 字段规则

| 段 | 规则 |
|---|---|
| `moodify` | 固定命名空间前缀（bucket 默认同名） |
| `tracks/{track_id}` | track_id = `trk_<uuid7 24hex>`（全局唯一，跨库可解释） |
| `source` | 仅 track 级（job 无关）；source object 不可覆盖（INV-01） |
| `jobs/{job_id}` | job_id = `job_<uuid7 24hex>`；所有 pipeline 产物 job-scoped |
| `{artifact_type}` | source / stems / analysis / intermediate / renders / evidence |
| `{object_id}.{ext}` | object_id = `obj_<uuid7 24hex>`；ext = 小写 1-8 字符（非标准 → `bin`） |

## 版本与覆盖

- source：同一 object_id 永不写不同 bytes（INV-01；adapter 层 + 幂等注册双保险）。
- render：每次渲染产生**新 object_id**（versioning 通过对象表记录，不覆盖 key）。
- 生命周期前缀：intermediate → `intermediate_short` retention；renders → `render_versioned`。

## 实现

- `moodify.data_plane.object_key`：`build_object_key()` / `parse_object_key()`（已测试 round-trip）。
- 示例：
  - source: `moodify/tracks/trk_a1b2/source/obj_c3d4.wav`
  - render: `moodify/tracks/trk_a1b2/jobs/job_e5f6/renders/obj_g7h8.wav`

## 未决

- bucket 命名（单 bucket `moodify` vs 多 bucket 分域）→ P03 默认单 bucket + prefix 分域；若 OSS 开通后需要隔离（public/private），P03 后重新评估（记录 HUMAN_DECISION_REQUIRED 于验收）。
