# 04 — Pipeline Version Contract

**W01-P05 · 2026-08-17 · 实现：production_fingerprint()**

## Pipeline Version 语义

pipeline version 绑定一套影响最终音频产物的生产语义集合：

- stage order + enabled/disabled stages
- adapter versions（analyzer/judger/renderer/separator）
- tool/model versions（v01/ffmpeg 等）
- analysis schema
- judgment policy
- intervention/profile version
- render policy（container/codec/rate/bit depth/channels/loudness）
- verify policy

**不是随便的 Git commit**（Git commit 可包含不影响产物的改动）。

## Production Fingerprint

```text
sha256({
  pipeline_version, input_hashes(sorted), stage_config,
  profile_version, tool_versions, render_policy
})
```

- 用途：判断两次处理是否"语义上同一次生产配置"、replay、audit、cache/idempotency hint。
- **不能代替 Job ID**。
- 确定性：相同语义 → 相同指纹（TST-10）；改变 profile/参数 → 指纹变化（TST-06）。

## Profile / Preset 版本化（§11）

- 禁止只记录 `clean_master` 字符串而无真实参数版本。
- profile 记录：profile_id + profile_version + reason + source judgment + parameters/chain reference + compatibility。
- 修改 preset 内容必须 bump profile_version（否则 fingerprint 失真）。

## 版本注册（P03 versions 表）

pipeline_version / profile_version / tool_versions 可注册进 versions 表（version_kind=pipeline/profile/tool），由 P03 P04 流程写入（当前代码未接 DB，测试用字符串标识）。
