# Naming Convention

## Sample ID

```text
SMP-{SOURCE}-{YYYYMMDD}-{HASH8}
```

示例：

```text
SMP-SUNO-20260712-A8F39C21
SMP-UDIO-20260712-B91D22AF
SMP-INTERNAL-20260712-7F20AA91
```

## 目录命名

```text
sample_asset_library/baseline/{sample_id}/original.wav
sample_asset_library/baseline/{sample_id}/processed/{run_id}/output.wav
sample_asset_library/baseline/{sample_id}/reports/{run_id}_report.md
```

## Run ID

```text
RUN-{YYYYMMDD}-{HASH8}
```

## Feature File

```text
features/spectral_features/{sample_id}.json
features/dynamic_features/{sample_id}.json
```
