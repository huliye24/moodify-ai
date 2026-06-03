# Runtime Integration Commands

## Queue 中加入 preset 字段

```json
{"task_id":"TASK_xxx","sample_id":"SMP_xxx","preset":"PRESET-CATEGORY-NAME-v0.1","scoring":"mrs_open_v031"}
```

## 检查 preset 是否可调用

```bash
python3 scripts/presets/check_preset_callable.py --preset PRESET-CATEGORY-NAME-v0.1
```
