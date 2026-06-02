# 给本地 Claude / Codex 的任务指令

你现在负责在本地为 Moodify 写一个“夜间云端自运行包”。

## 背景

云端服务器现在正在跑任务，不要打断云端。
本地只负责写代码，晚上上传到云端执行。
当前策略是：

- v01 = 产品主线
- legacy = 研究管线
- workers = 外层调度，不侵入核心代码

## 任务目标

请在 Moodify 项目根目录新增以下文件：

```text
workers/cloud_night_worker.py
configs/night_config.example.json
scripts/run_night_once.sh
scripts/schedule_tonight.sh
scripts/smoke_test_night.sh
docs/NIGHT_RUNNER_README.md
```

## 要求

1. 不修改 v01/legacy 核心代码。
2. 不删除任何已有文件。
3. worker 只通过现有 CLI 调用 Moodify。
4. 必须支持：
   - dry-run
   - smoke test
   - resume
   - manifest.csv
   - summary.json
   - night_worker.log
   - lock file 防止重复运行
5. 所有路径必须用相对路径或 PROJECT_ROOT，不允许写死：
   - /home/ubuntu
   - /root/moodify
   - /home/moodify
6. 先跑：
   ```bash
   python3 workers/cloud_night_worker.py --config configs/night_config.json --dry-run
   ```
7. 再跑：
   ```bash
   bash scripts/smoke_test_night.sh
   ```
8. 最后输出：
   - 修改文件清单
   - smoke test 是否通过
   - 正确的 CLI command_template 是哪一条
   - 今晚云端执行命令

## 不要做的事

- 不要重构 workflow_engine.py
- 不要合并 v01 和 legacy
- 不要新增 MRS 公式
- 不要改 API
- 不要改已有处理算法
