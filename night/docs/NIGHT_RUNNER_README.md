# Moodify Night Runner Pack

这是一个给 Moodify 云服务器使用的“夜间自运行包”。

## 设计原则

- 不改 Moodify 核心代码。
- 不碰正在运行的云端进程。
- 本地先写好，晚上上传服务器。
- 云端只做三件事：批量处理、记录日志、生成报告。
- 第二天只看 `manifest.csv`、`summary.json`、`night_worker.log`。

## 文件结构

```text
workers/cloud_night_worker.py     # 夜间调度主程序
configs/night_config.example.json # 配置模板
scripts/run_night_once.sh         # 立即跑一轮
scripts/schedule_tonight.sh       # 指定时间后台启动
scripts/smoke_test_night.sh       # 上云后先跑 1 首测试
```

## 放到 Moodify 项目里的位置

把这些文件复制到你的 `moodify-o3is` 根目录：

```bash
cp -r workers configs scripts /home/ubuntu/moodify-o3is/
cd /home/ubuntu/moodify-o3is
cp configs/night_config.example.json configs/night_config.json
chmod +x scripts/*.sh workers/cloud_night_worker.py
mkdir -p data/night_inputs outputs/night_runs logs
```

把今晚要处理的音频放到：

```text
data/night_inputs/
```

支持：`.wav .mp3 .flac .m4a .aac .ogg`

## 第一步：先不要直接夜跑，先 smoke test

```bash
cd /home/ubuntu/moodify-o3is
bash scripts/smoke_test_night.sh
```

成功后看：

```bash
tail -f outputs/night_runs/latest/night_worker.log
cat outputs/night_runs/latest/summary.json
```

## 第二步：确认 CLI 命令模板

`configs/night_config.json` 里最关键的是：

```json
"command_templates": [
  "{python} cli.py process --input {input} --output {output_dir} --preset {preset}",
  "{python} -m moodify.cli process --input {input} --output {output_dir} --preset {preset}",
  "{python} cli.py process {input} --output {output_dir} --preset {preset}"
]
```

如果 Moodify 当前 CLI 参数不是这样，让 Claude 先执行：

```bash
python3 cli.py process --help
```

然后只保留正确的那一条模板。

## 第三步：安排今晚自动跑

先看服务器时间：

```bash
date
```

比如想 23:30 开始：

```bash
bash scripts/schedule_tonight.sh 23:30
```

查看是否已经挂到后台：

```bash
ps aux | grep run_night_once
ps aux | grep cloud_night_worker
```

查看日志：

```bash
tail -f logs/night_schedule_*.log
tail -f outputs/night_runs/latest/night_worker.log
```

## 第二天看结果

```bash
cat outputs/night_runs/latest/summary.json
column -s, -t < outputs/night_runs/latest/manifest.csv | less -S
```

输出目录结构：

```text
outputs/night_runs/
  latest -> 20260602_233000
  20260602_233000/
    night_worker.log
    manifest.csv
    summary.json
    effective_config.json
    song_a/
      warm_vocal/
      clean_master/
      wide_space/
```

## 注意

1. 如果云端正在跑旧任务，不要覆盖它的输出目录。
2. 本包默认输出到 `outputs/night_runs/`，不会动旧输出。
3. 如果程序中断，第二次执行会因为 `--resume` 自动跳过已经完成的任务。
4. 如果出现 lock：

```bash
rm outputs/night_runs/night_worker.lock
```

但只有确认没有旧进程在跑时才能删。
