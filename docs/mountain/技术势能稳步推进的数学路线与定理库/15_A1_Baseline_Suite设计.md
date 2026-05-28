# 题目 A1：Moodify Baseline Suite 设计

**来源**: 母文件 §9 题目 A1
**类型**: 后续 AI 题目规格书
**产出**: 自动化测试脚本 + 基准音频 + 基准指标 + 退化检测规则 + CI 集成

---

## 0. 题目定义

设计一套可自动运行的基准测试套件，确保每次代码变更不破坏已有稳定能力（定理 1）。

---

## 1. Baseline Suite 的构成

### 1.1 CLI 测试

```bash
# 必须通过的 CLI 命令
moodify emotions                    # 列出情绪
moodify analyze test_01.wav        # 诊断分析
moodify process test_01.wav GA     # 处理 (无 API key)
moodify serve --port 18999 &       # 启动服务
sleep 3
curl http://localhost:18999/health # 健康检查
kill %1

# 预期: 全部返回 0
```

### 1.2 Python 模块导入测试

```python
# 所有核心模块必须可导入
from moodify.diagnosis.engine import DiagnosisEngine
from moodify.processing.spectral_chain import SpectralDSPChain
from moodify.optimizer.search import search_optimal_strengths, strength_to_params
from moodify.llm.client import DeepSeekClient
from moodify.memory.history import ProcessingHistory, ProcessingRecord
from moodify.orchestration.workflow_engine import WorkflowOrchestrator
```

### 1.3 Fallback 路径测试

```python
# 1. 无 API key 时, 处理流程不崩溃
os.environ.pop("DEEPSEEK_API_KEY", None)
result = orchestrator.process("test.wav", "GA")
assert result.success

# 2. LLM 返回 None 时, 搜索正常执行
# (mock DeepSeekClient._call 返回 None)
# 验证: Phase 1.5 走搜索路径

# 3. 搜索失败时, 回退到 preset
# 验证: top_params_list 使用 get_recommended_params
```

### 1.4 音频质量测试

```python
# 对 3-5 首测试音频:
for test_file in BASELINE_AUDIO_FILES:
    result = orchestrator.process(test_file, target_emotion)
    assert result.whs_after >= result.whs_before - 2  # 容忍 2 分波动
    assert result.eds >= 0  # EDS 不应为负 (情绪方向不应反)
    assert os.path.exists(result.output_path)  # 输出文件存在
```

### 1.5 性能测试

```python
# 诊断时间
t0 = time.perf_counter()
ws = engine.diagnose_quick("test.wav")
t_diag = time.perf_counter() - t0
assert t_diag < 5.0, f"诊断时间 {t_diag:.1f}s 超过 5s 限制"

# 搜索时间
t0 = time.perf_counter()
results = search_optimal_strengths(ws, "GA", top_k=3, n_samples=2000)
t_search = time.perf_counter() - t0
assert t_search < 3.0, f"搜索时间 {t_search:.1f}s 超过 3s 限制"
```

---

## 2. 基准音频素材

### 2.1 选曲标准

```
5 首测试音频, 覆盖:
  1. 钢琴独奏 (器乐/柔和动态)
  2. 人声民谣 (中频为主/简单编曲)
  3. 电子流行 (高频丰富/压缩较重)
  4. 氛围/实验 (极端动态/空间特殊)
  5. 摇滚/重型 (高能量/失真成分)

来源: 07Music/albums/ 或公开的 AI 音乐测试素材
格式: 44.1kHz/16bit WAV, 单声道或立体声
时长: 30-90 秒 (测试用, 不需要完整歌曲)
```

### 2.2 基准指标

```
每首测试音频对每个目标情绪 (GA, SE, UD, LW, HL, DR, WL, CN) 记录:
  - 诊断时间
  - WHS_before, WHS_after
  - EDS
  - 搜索时间 (如适用)
  - 处理总时间
  - Phase 1.5 source (rag_llm / search / preset)
  - 输出文件存在且可播放

存储格式: baseline_metrics.json
```

---

## 3. 退化检测规则

```python
REGRESSION_RULES = [
    # 硬退化 (CI 直接 fail)
    {"metric": "success", "condition": "new == False", "action": "fail"},
    {"metric": "output_exists", "condition": "new == False", "action": "fail"},
    {"metric": "t_diag", "condition": "new > old * 1.5 AND new > 5.0", "action": "fail"},

    # 软退化 (CI warn)
    {"metric": "whs_after", "condition": "new < old - 5", "action": "warn"},
    {"metric": "eds", "condition": "new < old - 10", "action": "warn"},
    {"metric": "t_search", "condition": "new > old * 2.0", "action": "warn"},
]
```

---

## 4. CI 集成方案

```yaml
# .github/workflows/baseline.yml (或本地 pre-commit hook)
name: Baseline Suite
on: [push, pull_request]
jobs:
  baseline:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: {python-version: '3.11'}
      - run: pip install -e .
      - run: python scripts/run_baseline.py
      - run: python scripts/check_regression.py
```

---

## 5. 产物清单

1. `scripts/run_baseline.py` — 自动化测试脚本
2. `tests/baseline/` — 5 首基准音频
3. `tests/baseline/baseline_metrics.json` — 基准指标存储
4. `scripts/check_regression.py` — 退化检测
5. CI config (`.github/workflows/baseline.yml`)

---

## 6. 理论参考

- Beck (2003): TDD
- Feathers (2004): Working with Legacy Code
- 母文件定理 1: 单调攀登定理

---

*Moodify 题目规格书 · A1 · v1.0*
