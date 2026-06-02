# 给本地 Claude / Codex 的接力任务

你现在负责把 Moodify Daily Run System 放入 `moodify-o3is` 项目根目录，并完成本地 dry-run。

## 不要做

- 不要重构 v01
- 不要重构 legacy
- 不要删除文件
- 不要改核心 DSP 算法
- 不要强行接入正式 MRS

## 要做

1. 复制本代码库到 `moodify-o3is` 根目录。
2. 执行：

```bash
cp configs/runtime_config.example.json configs/runtime_config.json
python3 examples/generate_test_audio.py
bash scripts/smoke_test.sh
```

3. 检查当前 Moodify CLI：

```bash
python3 cli.py process --help
```

4. 修改 `configs/runtime_config.json` 中的 `command_templates`，只保留真正可用的一条。
5. 再执行：

```bash
python3 -m moodify_runtime.cli --config configs/runtime_config.json run --limit 1 --dry-run
```

6. 输出结果：

```text
- smoke test 是否通过
- 当前可用 command_template
- 是否发现路径问题
- 晚上云端应执行的命令
```
