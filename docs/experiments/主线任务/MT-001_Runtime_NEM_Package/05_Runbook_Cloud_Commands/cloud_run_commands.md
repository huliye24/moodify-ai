# MT-001 云端运行命令手册

## 1. 进入项目目录

```bash
cd /path/to/moodify-o3is
```

---

## 2. 查看当前输入样本

```bash
ls -lh data/night_inputs/
cat input_registry.jsonl
```

---

## 3. 查看任务队列

```bash
cat run_queue.jsonl
```

---

## 4. Dry-run

```bash
python3 -m moodify_runtime.runner --config configs/runtime_config.json --dry-run
```

---

## 5. 后台启动 Day Run

```bash
nohup python3 scripts/day_run_24h.py > logs/day_run_001_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

---

## 6. 查看进程

```bash
ps aux | grep day_run_24h | grep -v grep
```

---

## 7. 查看日志

```bash
tail -20 logs/day_run_001_*.log
```

---

## 8. 查看最终总结

```bash
cat logs/day_run_001_final_summary.txt
```

---

## 9. 查看输出结果

```bash
find runs/day_run_001 -type f | head -50
```

---

## 10. 停止进程

先查 PID：

```bash
ps aux | grep day_run_24h | grep -v grep
```

再停止：

```bash
kill <PID>
```

---

## 11. MT-001 的核心要求

运行系统必须满足：

```text
不用看屏幕等它；
Claude 不监视；
系统自己跑；
跑完停止；
跑完出结果。
```
