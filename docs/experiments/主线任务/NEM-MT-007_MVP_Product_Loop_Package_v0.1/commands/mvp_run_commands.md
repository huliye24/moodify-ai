# MVP Run Commands

以下命令为模板，需要根据实际仓库路径调整。

## 单首音频 MVP 闭环

```bash
python3 -m moodify.mvp run   --input data/mvp_inputs/example.wav   --preset balanced_reality_v0   --mrs quick_mrs   --report user_and_technical   --output-dir runs/mvp_outputs/demo_001
```

## 查看输出

```bash
ls -la runs/mvp_outputs/demo_001
cat runs/mvp_outputs/demo_001/export_manifest.json
```
