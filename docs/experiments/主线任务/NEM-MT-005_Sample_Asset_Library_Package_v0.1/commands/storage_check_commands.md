# Storage Check Commands

## 检查文件是否存在

```bash
python3 scripts/samples/check_storage_paths.py --registry sample_asset_library/metadata/sample_registry.jsonl
```

## 检查 orphan 文件

```bash
python3 scripts/samples/find_orphan_files.py --root sample_asset_library/
```

## 生成 storage manifest

```bash
python3 scripts/samples/build_storage_manifest.py --root sample_asset_library/ --out sample_asset_library/metadata/storage_manifest.json
```
