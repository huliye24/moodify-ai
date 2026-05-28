# SPEC-002-REV: 情绪优化引擎 — DeepSeek 集成 · AI 可执行规格书（修订版）

**目标读者**: AI 编码智能体
**修订日期**: 2026-05-28 23:00
**替代**: SPEC-002 (2026-05-28 19:45)
**修订原因**: 原规格在 15D 参数空间做网格搜索存在维度爆炸、代理循环论证、LLM 角色分配错误三个结构性问题。修订后改为 5D 强度空间 LHS 采样，DeepSeek 专职 NL→情绪映射，craft_chain_match 评分复用为正则项。

---

## 0. 设计理由（4 条，理解后再实现）

1. **搜索 5D 强度向量，不搜索 15D 参数。** `state_transfer.py:62-98` 的 `T_EFFECTS` 已定义 5 个 transfer function（spectrum/dynamic/space/layer/master）对波场 5 维的影响。15D→5D 映射由 `spectral_chain.py:98-127` 的 `_harmonic_params`/`_percussive_params` 隐含定义。直接在 5D 空间搜索：维度低 3 倍，候选充分覆盖。

2. **T_EFFECTS 代理只做粗筛。** `T_EFFECTS` 是经验估计表，用它评估参数质量存在循环论证。代理评分仅用于从 2000 候选筛到 top-3。最终选择由真实 DSP + 真实诊断测量决定，不依赖代理的绝对值。

3. **DeepSeek 做 NL→情绪映射，不做搜索空间设计。** LLM 擅长模糊语义映射（"像清晨阳光"→情绪原型），不擅长数值优化（参数范围选择）。搜索空间永远由规则决定——可复现、可回退。

4. **复用 craft_chain_match 评分，不废弃。** `craft_chain_match.py:57-105` 已有 5 子指标评分 + 硬阻断规则。在代理评估中作为正则项使用，惩罚违反 `risk_warnings` 的候选。

---

## 0.5 环境快照

### 0.5.1 工作目录
```
E:\moodify\moodify-core-package\src\moodify\
```

### 0.5.2 已有元器件（只读，不修改）
| 文件 | 关键接口 | 用途 |
|------|---------|------|
| `diagnosis/engine.py` | `DiagnosisEngine().diagnose_quick(path) -> WaveStateDiagnosis` | Phase 1 诊断 |
| `diagnosis/defect_classifier.py` | `DefectClassifier().classify(ws, emotion?) -> list[Defect]` | 缺陷分类 |
| `diagnosis/health_scorer.py` | `HealthScorer().compute_whs(ws, defects) -> dict` (键 `"WHS"`) | WHS 评分 |
| `diagnosis/health_scorer.py` | `HealthScorer().compute_eds(ws_before, ws_after, emotion) -> float` | EDS 评分 |
| `processing/spectral_chain.py` | `SpectralDSPChain().process(audio, sr, params) -> np.ndarray` | Phase 3 真实 DSP |
| `orchestration/state_transfer.py` | `StateTransferEngine.diagnostic_to_process(ws_diag) -> WaveStateProcess` | 诊断→处理 5D |
| `orchestration/state_transfer.py` | `engine.apply_chain_transfer(ws, types, strengths, emotion) -> (WaveStateProcess, dict)` | 状态转移 |
| `orchestration/state_transfer.py` | `StateTransferEngine.T_EFFECTS: dict` | 5 函数经验效应矩阵 |
| `knowledge/craft_chains.py` | `CRAFT_CHAINS_15PARAMS: dict[str, dict]` | 8情绪×15参数 min/rec/max |
| `knowledge/craft_chains.py` | `get_recommended_params(code) -> dict[str, float]` | 提取推荐值 |
| `knowledge/craft_chains.py` | `get_chain_params(code) -> dict` | 完整工艺数据(含risk_warnings) |
| `knowledge/craft_chain_match.py` | `CraftChainMatch().match(defects, emotion, ws, cards, top_k) -> list[MatchResult]` | 工艺卡匹配评分 |
| `knowledge/emotion_targets.py` | `EMOTION_TARGETS_V2: dict` | 8 情绪完整数据 |
| `knowledge/emotion_targets.py` | `resolve_emotion(name) -> str` | 名称→emotion key |
| `knowledge/emotion_targets.py` | `get_ideal_process_vector(name) -> np.ndarray` | 情绪理想 5D 向量 |
| `knowledge/emotion_targets.py` | `get_safety_bounds(name) -> dict[str, tuple]` | 情绪安全区间 |
| `knowledge/emotion_targets.py` | `CODE_TO_KEY: dict`, `KEY_TO_CODE: dict` | 代码/Key 互转 |
| `data_types.py` | `WaveStateDiagnosis` (含 `.to_dict()` 和 `.get_auto_params()`) | 诊断数据结构 |

### 0.5.3 保持不动
```
knowledge/craft_chain_match.py   # 保留，代理评估复用其评分
knowledge/craft_chains.py        # 保留，作为搜索边界和推荐值参考
orchestration/state_transfer.py  # 保留，T_EFFECTS 直接使用
```

### 0.5.4 新增 Python 依赖
```
openai >= 1.0.0        # DeepSeek API (OpenAI 兼容协议)
```
已有: `numpy`, `scipy>=1.9` (需要 `scipy.stats.qmc`), `pydantic>=2.0`, `librosa`, `pedalboard`, `soundfile`, `pyloudnorm`

### 0.5.5 环境变量（3 个，均为可选）
```
DEEPSEEK_API_KEY      # str, 未设置 → LLM 功能静默回退
DEEPSEEK_BASE_URL     # str, 默认 "https://api.deepseek.com"
DEEPSEEK_MODEL        # str, 默认 "deepseek-chat"
```

---

## 1. 文件变更清单

### 新增文件（3 个，不含 __init__.py）

```
moodify-core-package/src/moodify/
│
├── optimizer/                    # 阶段 A
│   ├── __init__.py               # 空，或仅导出 search_optimal_strengths
│   └── search.py                 # ~220 行。5D 搜索空间 + LHS 采样 + 代理评估 + 强度↔参数映射
│
└── llm/                          # 阶段 B
    ├── __init__.py               # 空
    └── client.py                 # ~180 行。DeepSeek 客户端 + Prompt 模板 + Pydantic Schema（合并原 prompts.py + schemas.py）
```

### 修改文件（2 个）

```
orchestration/workflow_engine.py  # Phase 0(新) + Phase 1.5(新) + Phase 3 多版本 + 后处理选优
knowledge/emotion_targets.py      # 新增 resolve_emotion_from_nl() 函数
```

### 推迟文件

```
memory/history.py                 # 阶段 C，需 ≥50 条真实记录后实施。本规格不包含。
```

---

## 2. 阶段 A — 5D 强度空间搜索（零 LLM 依赖）

### 2.0 核心概念：15 参数 ↔ 5 强度的映射

```
5 个 transfer function 及其管辖的 DSP 参数：

spectrum 强度 → P01_vocal_presence_freq, P02_vocal_presence_gain, P03_vocal_presence_q,
                 P04_proximity_low_freq, P05_proximity_low_gain,
                 P14_high_shelf_freq, P15_high_shelf_gain         (7 参数)

dynamic  强度 → P06_compression_ratio, P07_compression_attack,
                 P08_compression_release, P09_compression_threshold (4 参数)

space    强度 → P10_reverb_t60, P11_reverb_dry_wet, P12_reverb_width  (3 参数)

layer    强度 → P13_harmonic_drive                                 (1 参数)

master   强度 → 不映射到具体参数。在 compose_params() 中保持所有参数使用插值后的值，
                不做额外调整。master 强度保留为占位维度（采样值固定 = 0.5），
                用于 apply_chain_transfer() 的第 5 个 transfer。
```

此映射逻辑来自 `spectral_chain.py:98-127` — 谐波链参数=spectrum 管辖域，打击乐链参数=dynamic+layer 管辖域，space 独立。

### 2.1 新增文件：`optimizer/search.py`

**文件路径**: `moodify-core-package/src/moodify/optimizer/search.py`

以下是该文件的完整规格。按节实现，每节是一个函数或常量。

---

#### 2.1.1 常量定义

```python
"""5D 强度空间搜索 — LHS 采样 + 代理评估 + 强度↔参数映射"""

import numpy as np
from scipy.stats import qmc

# 15 参数 → 5 个 transfer 维度的分组关系
# 来源: spectral_chain.py _harmonic_params / _percussive_params
STRENGTH_TO_PARAMS: dict[str, list[str]] = {
    "spectrum": [
        "P01_vocal_presence_freq", "P02_vocal_presence_gain", "P03_vocal_presence_q",
        "P04_proximity_low_freq", "P05_proximity_low_gain",
        "P14_high_shelf_freq", "P15_high_shelf_gain",
    ],
    "dynamic": [
        "P06_compression_ratio", "P07_compression_attack",
        "P08_compression_release", "P09_compression_threshold",
    ],
    "space": [
        "P10_reverb_t60", "P11_reverb_dry_wet", "P12_reverb_width",
    ],
    "layer": [
        "P13_harmonic_drive",
    ],
    "master": [],  # 占位维度，不映射到参数
}

# apply_chain_transfer() 调用的顺序
CHAIN_ORDER = ["spectrum", "dynamic", "space", "layer", "master"]

# 默认搜索范围（当某维不活跃时使用）
DEFAULT_RANGE = (0.3, 0.7)
```

---

#### 2.1.2 `define_strength_space()`

```python
def define_strength_space(
    defects: list,        # list[Defect] from DefectClassifier.classify()
    emotion_code: str,    # "GA", "SE", etc.
) -> dict[str, tuple[float, float]]:
    """
    基于缺陷类型确定 5 个维度的搜索范围。
    
    规则（算法化, 无歧义）:
      1. 从 craft_chains.get_chain_params(emotion_code) 读取 risk_warnings
      2. 统计每个维度的关联缺陷数
      3. 活跃维度（有关联缺陷）: range = (0.15, 0.85)
      4. 非活跃维度: range = (0.35, 0.65)，围绕中心 0.5
      5. 特殊约束（从 risk_warnings 提取）:
         - "混响" 在 risk_warnings 中出现 → space 上限收紧到 0.7
         - "压缩" in risk_warnings → dynamic 上限收紧到 0.7
         - "高频" in risk_warnings → spectrum 上限收紧到 0.7
    
    Returns: {"spectrum": (0.15, 0.85), "dynamic": (0.35, 0.65), ...}
    """
```

**实现伪代码**:
```
1. 从 craft_chains 获取 chain = get_chain_params(emotion_code)
2. risk_text = " ".join(chain.get("risk_warnings", []))
3. 缺陷参数集合: 遍历 defects, 收集所有 defect.parameter 字段
4. 对每个维度 "spectrum"/"dynamic"/"space"/"layer"/"master":
   a. 检查该维度管辖的参数是否与缺陷参数有交集
   b. 有交集 → active_range = (0.15, 0.85)
   c. 无交集 → inactive_range = (0.35, 0.65)
   d. 对 inactive_range, 确保 lo >= 0.1, hi <= 0.9
5. 应用特殊约束:
   - "混响" ∈ risk_text → space["hi"] = min(space["hi"], 0.7)
   - "压缩" ∈ risk_text → dynamic["hi"] = min(dynamic["hi"], 0.7)
   - "高频" ∈ risk_text → spectrum["hi"] = min(spectrum["hi"], 0.7)
6. master 维度范围固定为 (0.45, 0.55)
```

---

#### 2.1.3 `sample_strength_vectors()`

```python
def sample_strength_vectors(
    space: dict[str, tuple[float, float]],
    n: int = 2000,
    seed: int = 42,
) -> list[dict[str, float]]:
    """
    Latin Hypercube Sampling 在 5D 空间产生 n 个均匀分布的强度向量。
    
    实现:
      sampler = qmc.LatinHypercube(d=5, seed=seed)
      samples = sampler.random(n=n)  # shape (n, 5), each ∈ [0,1]
      
      对每个样本 i:
        对每个维度 j (按 CHAIN_ORDER 顺序):
          lo, hi = space[CHAIN_ORDER[j]]
          value = lo + samples[i, j] * (hi - lo)
    
    Returns: [{"spectrum": 0.32, "dynamic": 0.58, ...}, ...]
             len == n
    """
```

---

#### 2.1.4 `proxy_evaluate()`

```python
def proxy_evaluate(
    strength_vector: dict[str, float],
    diagnosis,              # WaveStateDiagnosis
    emotion_code: str,      # "GA"
    craft_card,             # CraftCardV2 | None — 从 craft_chain_match 的匹配结果获取
) -> float:
    """
    不跑真实 DSP，预估强度向量对应的 EDS 改善。
    
    计算链（每步调用已有代码，不重新实现）:
    
    Step 1 — 状态转移预估:
      from moodify.orchestration.state_transfer import StateTransferEngine
      engine = StateTransferEngine()
      ws_raw = StateTransferEngine.diagnostic_to_process(diagnosis)
      
      chain_strengths = [strength_vector[t] for t in CHAIN_ORDER]
      ws_proxy, meta = engine.apply_chain_transfer(
          ws_raw, CHAIN_ORDER, chain_strengths, emotion_code
      )
    
    Step 2 — EDS 代理:
      from moodify.knowledge.emotion_targets import get_ideal_process_vector
      target = get_ideal_process_vector(emotion_code)
      dist_before = float(np.linalg.norm(ws_raw.to_array() - target))
      dist_after  = float(np.linalg.norm(ws_proxy.to_array() - target))
      
      if dist_before > 1e-8:
          eds = 100.0 * (1.0 - dist_after / dist_before)
      else:
          eds = 100.0
    
    Step 3 — 安全惩罚:
      warnings = meta.get("warnings", [])
      eds -= 5.0 * len(warnings)
    
    Step 4 — craft 正则项（如果 craft_card 不为 None）:
      from moodify.knowledge.craft_chain_match import CraftChainMatch
      from moodify.diagnosis.defect_classifier import DefectClassifier
      
      # 用 craft_card 的评分系统评估强度向量质量
      # 仅用 _wave_state_compatibility 子项（因为 ws_proxy 已知）
      matcher = CraftChainMatch()
      ws_compat = matcher._wave_state_compatibility(craft_card, ws_proxy.to_dict(), emotion_code)
      
      craft_penalty = (1.0 - ws_compat) * 15.0  # 归一化到 [0, 15]
      eds -= craft_penalty
    
    Step 5 — 限幅:
      return float(np.clip(eds, -100.0, 100.0))
    
    注意事项:
      - engine 实例在函数内创建，不缓存（避免状态污染）
      - craft_card 可以为 None（此时跳过 Step 4）
      - 不允许修改 diagnosis 或 craft_card 的任何属性
    """
```

---

#### 2.1.5 `strength_to_params()`

```python
def strength_to_params(
    strength_vector: dict[str, float],
    emotion_code: str,
) -> dict[str, float]:
    """
    5D 强度向量 → 15 DSP 参数。
    
    映射算法（对 STRENGTH_TO_PARAMS 中的每个 param）:
      1. 确定 param 属于哪个维度 dim
      2. strength = strength_vector[dim]
      3. 从 craft_chains 获取该 emotion_code 下 param 的 (min, rec, max)
      4. Linear interpolation:
           if strength <= 0.5:
               t = strength / 0.5          # [0, 1] 映射
               value = rec + t * (min - rec)  # rec→min 方向
           else:
               t = (strength - 0.5) / 0.5  # [0, 1] 映射
               value = rec + t * (max - rec)  # rec→max 方向
      5. Clamp: value = max(min_val, min(max_val, value))
      6. Round: 如果 param 是 int 类型（P01 freq, P04 freq, P14 freq）→ round to int
    
    strength=0.5 → rec value (工艺卡推荐值)
    strength=0.0 → min value
    strength=1.0 → max value
    
    对于 master 维度（无参数）: 忽略，不影响输出。
    
    Returns: {"P01_vocal_presence_freq": 3000.0, "P02_vocal_presence_gain": 2.5, ...}
             键为 PARAM_KEYS (craft_chains.py:25-41) 的全部 15 个参数
    
    边界情况:
      - 如果 emotion_code 不在 CRAFT_CHAINS_15PARAMS 中 → raise KeyError
      - 如果某 param 不在 chain 定义中 → 跳过（不输出该键）
    """
```

**验收**:
```python
from moodify.knowledge.craft_chains import get_recommended_params, PARAM_KEYS

# 强度全 0.5 → 应等于推荐值
sv = {"spectrum": 0.5, "dynamic": 0.5, "space": 0.5, "layer": 0.5, "master": 0.5}
params = strength_to_params(sv, "GA")
rec = get_recommended_params("GA")
for k in PARAM_KEYS:
    assert abs(params[k] - rec[k]) < 0.01, f"{k}: {params[k]} != {rec[k]}"
```

---

#### 2.1.6 `search_optimal_strengths()` — 主入口

```python
def search_optimal_strengths(
    diagnosis,            # WaveStateDiagnosis
    emotion_target: str,  # 中文名如"温柔觉醒" 或 代码如"GA"
    top_k: int = 3,
    n_samples: int = 2000,
) -> list[tuple[dict[str, float], dict[str, float], float]]:
    """
    5D 强度空间搜索主入口。
    
    流程:
      1. emotion_code = resolve_emotion(emotion_target, as_key=True)
         或直接从 CODE_TO_KEY 解析
      
      2. classifier = DefectClassifier()
         defects = classifier.classify(diagnosis, emotion_code)
      
      3. space = define_strength_space(defects, emotion_code)
      
      4. vectors = sample_strength_vectors(space, n=n_samples)
      
      5. 获取 craft_card 用于正则化:
         from moodify.knowledge.craft_chain_match import generate_craft_cards_from_data, CraftChainMatch
         cards = generate_craft_cards_from_data()
         matcher = CraftChainMatch()
         matches = matcher.match(defects, emotion_code, diagnosis, cards, top_k=1)
         craft_card = matches[0].craft_card if matches else None
      
      6. scored = []
         for vec in vectors:
             score = proxy_evaluate(vec, diagnosis, emotion_code, craft_card)
             scored.append((vec, score))
      
      7. scored.sort(key=lambda x: x[1], reverse=True)
      
      8. top_vectors = scored[:top_k]
      
      9. result = []
         for vec, score in top_vectors:
             params = strength_to_params(vec, emotion_code)
             result.append((vec, params, score))
      
      10. return result
    
    Returns:
      list of (strength_vector, params_dict, proxy_score)
      len == top_k, 按 proxy_score 降序
    
    性能约束: 整个函数调用（含 2000 次 proxy_evaluate）应在 2s 内完成。
    如果超过 3s，在函数末尾 print 一条 WARN 日志。
    """
```

**验收**:
```python
from moodify.diagnosis.engine import DiagnosisEngine

engine = DiagnosisEngine()
ws = engine.diagnose_quick("任意存在的.wav")
results = search_optimal_strengths(ws, "温柔觉醒", top_k=3)

assert len(results) == 3
assert len(results[0]) == 3           # (vec, params, score)
assert len(results[0][1]) == 15       # 15 完整参数
assert results[0][2] >= results[2][2] # 降序
assert all(0.0 <= results[i][0][d] <= 1.0 for i in range(3) for d in CHAIN_ORDER)
```

---

### 2.2 修改文件：`orchestration/workflow_engine.py`

只列出具体修改点，不重写整个文件。

#### 修改点 A：`process()` 方法 — Phase 1 之后插入 Phase 1.5

位置: `workflow_engine.py:106-108` (Phase 1 → Phase 2 之间)

```python
# 在 Phase 1 之后、Phase 2 之前插入:

# ====== Phase 1.5: 5D 强度空间搜索 ======
phase1_5 = self._run_strength_search(
    phase1.output.get("wave_state_diagnosis"),
    emotion_target
)
phases.append(phase1_5)

# 提取搜索到的参数列表
top_params_list = phase1_5.output.get("top_params_list", [])
top_strengths = phase1_5.output.get("top_strengths", [])
top_scores = phase1_5.output.get("top_scores", [])

# fallback: 搜索失败时使用推荐值
if not top_params_list:
    from moodify.knowledge.craft_chains import get_recommended_params
    from moodify.knowledge.emotion_targets import resolve_emotion, KEY_TO_CODE
    try:
        code = resolve_emotion(emotion_target)
        code = KEY_TO_CODE.get(code, "GA")
    except Exception:
        code = "GA"
    top_params_list = [get_recommended_params(code)]
    top_strengths = [{"spectrum": 0.5, "dynamic": 0.5, "space": 0.5, "layer": 0.5, "master": 0.5}]
    top_scores = [0.0]
```

#### 修改点 B：`process()` 方法 — Phase 3-6 多版本处理

位置: `workflow_engine.py:119-145` (原 Phase 3 → Phase 6)

关键改动: Phase 3 对 top_params_list 中的**每个参数组合**单独调用 `SpectralDSPChain.process()`，产生多个音频版本。Phase 4-6 分别对每个版本操作。最后测量每个版本的 WHS/EDS，选最优。

```python
# ====== Phase 3: 频谱增强 (多版本) ======
phase3 = self._run_spectral_enhancement_multi(audio, sr, top_params_list)
phases.append(phase3)
versions = phase3.output.get("versions", [audio])

# ====== Phase 4-6: 对每个版本分别处理 + 测量选优 ======
ws_diagnosis = phase1.output.get("wave_state_diagnosis")
best_eds = -999.0
best_idx = 0
best_whs_after = 0.0
best_output = ""

for i, ver_audio in enumerate(versions):
    p4 = self._run_spatial(ver_audio, sr, emotion_target, None)
    p5 = self._run_resynthesis(p4.output["audio"], sr)
    p6 = self._run_mastering(p5.output["audio"], sr, input_path, emotion_target, platform)
    
    ver_output = p6.output.get("output_path", "")
    if ver_output and os.path.exists(ver_output):
        try:
            ws_a = self._diagnose_audio(ver_output)
            whs_a = self._compute_whs(ws_a)
            eds_a = self._compute_eds(ws_diagnosis, ws_a, emotion_target)
        except Exception:
            whs_a, eds_a = 0.0, 0.0
    else:
        whs_a, eds_a = 0.0, 0.0
    
    phases.extend([p4, p5, p6])
    
    if eds_a > best_eds:
        best_eds = eds_a
        best_idx = i
        best_whs_after = whs_a
        best_output = ver_output

output_path = best_output
whs_after = best_whs_after
eds = best_eds
# best_params = top_params_list[best_idx] if best_idx < len(top_params_list) else {}
# best_strength = top_strengths[best_idx] if best_idx < len(top_strengths) else {}
```

#### 修改点 C：新增方法 `_run_strength_search()`

```python
def _run_strength_search(self, ws_diagnosis, emotion_target: str) -> PhaseResult:
    """Phase 1.5: 5D 强度空间搜索"""
    t0 = time.perf_counter()
    
    if ws_diagnosis is None:
        return PhaseResult(
            phase=1.5, name="强度搜索", status=PhaseStatus.SKIPPED,
            output={"top_params_list": [], "top_strengths": [], "top_scores": []},
            elapsed_ms=0,
        )
    
    try:
        from moodify.optimizer.search import search_optimal_strengths
        results = search_optimal_strengths(ws_diagnosis, emotion_target, top_k=3)
        
        return PhaseResult(
            phase=1.5, name="强度搜索",
            status=PhaseStatus.COMPLETED,
            output={
                "top_strengths": [r[0] for r in results],
                "top_params_list": [r[1] for r in results],
                "top_scores": [r[2] for r in results],
            },
            elapsed_ms=(time.perf_counter() - t0) * 1000,
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        return PhaseResult(
            phase=1.5, name="强度搜索",
            status=PhaseStatus.COMPLETED,  # 非 FAILED，允许后续 fallback
            output={
                "top_params_list": [],
                "top_strengths": [],
                "top_scores": [],
                "fallback_reason": str(e),
            },
            warnings=[f"Strength search failed, using recommended params: {e}"],
            elapsed_ms=(time.perf_counter() - t0) * 1000,
        )
```

#### 修改点 D：新增方法 `_run_spectral_enhancement_multi()`

```python
def _run_spectral_enhancement_multi(
    self, audio: np.ndarray, sr: int, params_list: list[dict]
) -> PhaseResult:
    """Phase 3: 对多个参数组合分别跑 HPSS 频谱增强"""
    t0 = time.perf_counter()
    from moodify.processing.spectral_chain import SpectralDSPChain
    
    chain = SpectralDSPChain()
    versions = []
    for params in params_list:
        try:
            ver = chain.process(audio, sr, params)
            versions.append(ver)
        except Exception:
            versions.append(audio)  # fallback: 透传
    
    return PhaseResult(
        phase=3, name="频谱增强",
        status=PhaseStatus.COMPLETED,
        output={"versions": versions, "count": len(versions)},
        elapsed_ms=(time.perf_counter() - t0) * 1000,
    )
```

#### 修改点 E：`process()` 方法末尾 — LLM 诊断解读 + 历史记录

在 `process()` 的 `return WorkflowResult(...)` 之前插入：

```python
# LLM 诊断解读（阶段 B 完成后才生效）
narrative = None
try:
    from moodify.llm.client import DeepSeekClient
    llm = DeepSeekClient()
    if llm.available and ws_diagnosis and output_path:
        ws_after = self._diagnose_audio(output_path)
        narrative = llm.narrate_diagnosis(
            before_dict=ws_diagnosis.to_dict(),
            after_dict=ws_after.to_dict() if ws_after else {},
            params=best_params if best_params else {},
            whs_before=whs_before,
            whs_after=whs_after,
            eds=eds,
            emotion_name=emotion_target,
        )
except Exception:
    pass
```

---

## 3. 阶段 B — DeepSeek 集成（NL 情绪映射 + 诊断解读）

**前置条件**: 阶段 A 完成且验证通过。
**不回退到阶段 A**: 阶段 A 代码不变。阶段 B 新增文件 + 修改 1 个文件。DeepSeek 不可用时所有 LLM 功能静默回退。

### 3.1 新增文件：`llm/client.py`

**文件路径**: `moodify-core-package/src/moodify/llm/client.py`

单文件包含三部分: (a) Pydantic 模型, (b) Prompt 常量, (c) DeepSeekClient 类。

---

#### 3.1.1 Pydantic 模型（内嵌在 client.py 顶部）

```python
"""DeepSeek API 客户端 — NL 情绪映射 + 诊断解读生成"""
import os, json
from pydantic import BaseModel, Field
from openai import OpenAI


class EmotionInterpretation(BaseModel):
    """DeepSeek 对自然语言情绪描述的解析结果"""
    emotion_code: str = Field(
        description="最接近的 8 情绪原型代码: GA/SE/UD/LW/HL/DR/WL/CN"
    )
    emotion_name: str = Field(
        description="情绪原型中文名"
    )
    intensity: float = Field(
        ge=0.3, le=1.0,
        description="情绪强度, 0.5=标准, >0.7=强烈, <0.4=轻微"
    )
    vector_bias: dict[str, float] = Field(
        description=(
            "对 5D 理想向量的微调偏置。键: E/D/S/T/H。"
            "每维范围 [-0.10, 0.10]。"
            "E偏高=更明亮, D偏高=更起伏, S偏高=更宏大, T偏高=更锋利, H偏高=更饱满"
        )
    )
    reasoning: str = Field(description="推理过程，50 字以内中文")


class DiagnosisNarrative(BaseModel):
    """诊断解读"""
    narrative_zh: str = Field(description="自然语言诊断报告，2-3 句中文")
    risks: list[str] = Field(description="风险提示列表，每条 ≤30 字")
    suggestions: list[str] = Field(description="改进建议列表，每条 ≤30 字")
```

---

#### 3.1.2 Prompt 常量（内嵌在 client.py 中，模块级 const str）

```python
EMOTION_INTERPRETER_SYSTEM = """\
你是 Moodify 情绪波场显影引擎的情绪语义解释器。

## 已知 8 种情绪原型
| 代码 | 名称 | 核心特征 |
|------|------|---------|
| GA | 温柔觉醒 | 温暖、柔和、亲密、低频饱满、高频克制 |
| SE | 神圣空灵 | 超然、宏大、轻盈、混响深远、低频收敛 |
| UD | 都市危险 | 压迫、紧张、暗黑、压缩重、低频冲击强 |
| LW | 孤独留白 | 内省、距离、稀疏、混响深远但克制 |
| HL | 治愈温暖 | 安慰、饱满、平滑、低频温暖、谐波丰富 |
| DR | 黑暗浪漫 | 深沉、性感、神秘、中低频突出、氛围感强 |
| WL | 废土机械 | 粗粝、冲击、工业、极限压缩、高失真 |
| CN | 电影感 | 宏大、叙事、史诗、大动态、宽声场 |

## 任务
用户输入自然语言描述。你必须:
1. 映射到最接近的 8 种情绪原型之一（不允许创造新情绪）
2. 给出强度建议
3. 给出 5D 理想向量微调偏置

## 5D 向量维度说明
- E (频率均衡度): +偏置=更明亮, -偏置=更暗沉
- D (动态呼吸感): +偏置=更起伏, -偏置=更平整
- S (空间层次感): +偏置=更宏大, -偏置=更紧致
- T (瞬态清晰度): +偏置=更锋利, -偏置=更柔和
- H (谐波丰富度): +偏置=更饱满, -偏置=更纯净

## 输出格式 (严格 JSON, 无额外文字)
{"emotion_code":"GA","emotion_name":"温柔觉醒","intensity":0.65,"vector_bias":{"E":0.03,"D":0.0,"S":-0.02,"T":0.0,"H":0.02},"reasoning":"..."}
"""

DIAGNOSIS_NARRATOR_SYSTEM = """\
你是 Moodify 的音频诊断解读师。你的任务是将处理前后的技术数据转化为用户可理解的自然语言报告。

## 输入
- 处理前的 18 参数诊断数据
- 处理后的 18 参数诊断数据
- 实际应用的 15 个 DSP 参数
- WHS/EDS 变化数值

## 输出要求
- narrative_zh: 2-3 句中文。第一句描述原始状态，第二句描述改善效果，第三句（可选）提示注意事项
- risks: 风险列表。如果 WHS 下降或 EDS < 40，诚实指出
- suggestions: 改进建议。如果结果良好，可以建议"可尝试更强的XX效果"或"可尝试不同的情绪目标"

## 约束
- 所有文字用中文
- 使用具体数值增强可信度（如 "低频从 -6.2dB 提升到 -3.7dB"）
- 风险和改善必须基于数据，不编造
- 面向普通音乐爱好者，避免术语堆砌

## 输出格式 (严格 JSON)
{"narrative_zh":"...","risks":["..."],"suggestions":["..."]}
"""
```

---

#### 3.1.3 DeepSeekClient 类

```python
class DeepSeekClient:
    """DeepSeek API 客户端。
    
    所有公开方法失败时返回 None（不抛异常）。
    调用方检查返回值是否为 None 决定是否回退。
    """

    def __init__(self):
        key = os.getenv("DEEPSEEK_API_KEY")
        self._client = (
            OpenAI(
                api_key=key,
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            )
            if key else None
        )
        self._model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    @property
    def available(self) -> bool:
        return self._client is not None

    # ── 公开 API ─────────────────────────────────

    def interpret_emotion(self, nl_text: str) -> dict | None:
        """自然语言 → 结构化情绪目标。
        
        Args:
            nl_text: 用户输入的自由文本，如 "像清晨阳光穿过窗帘，温暖但不刺眼"
        
        Returns:
            {
                "emotion_code": "GA",
                "emotion_name": "温柔觉醒",
                "intensity": 0.65,
                "vector_bias": {"E": 0.03, "D": 0.0, "S": -0.02, "T": 0.0, "H": 0.02},
                "reasoning": "...",
            }
            失败返回 None
        """
        user = json.dumps({"user_input": nl_text}, ensure_ascii=False)
        raw = self._call(EMOTION_INTERPRETER_SYSTEM, user)
        if raw is None:
            return None
        try:
            result = EmotionInterpretation(**raw)
            return result.model_dump()
        except Exception:
            return None

    def narrate_diagnosis(
        self,
        before_dict: dict,
        after_dict: dict,
        params: dict,
        whs_before: float,
        whs_after: float,
        eds: float,
        emotion_name: str,
    ) -> dict | None:
        """生成诊断解读。
        
        Returns:
            {"narrative_zh": "...", "risks": [...], "suggestions": [...]}
            失败返回 None
        """
        user = json.dumps({
            "diagnosis_before": before_dict,
            "diagnosis_after": after_dict,
            "params_applied": {k: round(v, 2) for k, v in params.items()},
            "whs_before": round(whs_before, 1),
            "whs_after": round(whs_after, 1),
            "eds": round(eds, 1),
            "emotion_name": emotion_name,
        }, ensure_ascii=False)
        raw = self._call(DIAGNOSIS_NARRATOR_SYSTEM, user)
        if raw is None:
            return None
        try:
            result = DiagnosisNarrative(**raw)
            return result.model_dump()
        except Exception:
            return None

    # ── 内部 ────────────────────────────────────

    def _call(self, system_prompt: str, user_content: str) -> dict | None:
        """调用 DeepSeek API，带 3 次重试。失败返回 None。"""
        if not self.available:
            return None
        for attempt in range(3):
            try:
                r = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    response_format={"type": "json_object"},
                    timeout=15.0,
                    temperature=0.2,  # 低温度 = 更稳定
                )
                text = r.choices[0].message.content
                return json.loads(text)
            except Exception:
                if attempt == 2:
                    return None
        return None
```

**验收**:
```python
import os
os.environ["DEEPSEEK_API_KEY"] = "sk-xxx"

client = DeepSeekClient()
assert client.available

# 测试 NL 情绪映射
result = client.interpret_emotion("像清晨阳光穿过窗帘")
if result:
    assert result["emotion_code"] in ["GA","SE","UD","LW","HL","DR","WL","CN"]
    assert 0.3 <= result["intensity"] <= 1.0
    for dim in ["E","D","S","T","H"]:
        assert -0.10 <= result["vector_bias"][dim] <= 0.10

# 测试诊断解读
narrative = client.narrate_diagnosis(
    before_dict={"Spectrum": {"S3_MidClarity": 0.45}},
    after_dict={"Spectrum": {"S3_MidClarity": 0.62}},
    params={"P02_vocal_presence_gain": 2.5},
    whs_before=68.0, whs_after=78.0, eds=65.0,
    emotion_name="温柔觉醒",
)
if narrative:
    assert len(narrative["narrative_zh"]) > 10
    assert isinstance(narrative["risks"], list)
    assert isinstance(narrative["suggestions"], list)

# 测试未配置 API key 时的回退
del os.environ["DEEPSEEK_API_KEY"]
client2 = DeepSeekClient()
assert not client2.available
assert client2.interpret_emotion("任意文本") is None
assert client2.narrate_diagnosis({}, {}, {}, 0, 0, 0, "") is None
```

---

### 3.2 修改文件：`knowledge/emotion_targets.py`

#### 新增函数 `resolve_emotion_from_nl()`

在 `resolve_emotion()` 函数之后（约 line 607 之后）追加:

```python
def resolve_emotion_from_nl(nl_text: str) -> dict:
    """
    自然语言情绪描述 → 结构化情绪目标。
    
    优先级:
      1. 查预设 alias 表 (EMOTION_ALIASES)
      2. 调 DeepSeek 做语义映射
      3. 回退到默认值 (GA, intensity=0.6, zero bias)
    
    Returns:
        {
            "emotion_key": str,      # EMOTION_TARGETS_V2 中的 key, 如 "gentle_awakening"
            "emotion_code": str,     # "GA"
            "intensity": float,
            "vector_bias": dict,     # {"E": 0.0, "D": 0.0, "S": 0.0, "T": 0.0, "H": 0.0}
            "source": "preset" | "deepseek" | "fallback",
        }
    """
    # Step 1: 尝试预设匹配
    try:
        key = resolve_emotion(nl_text)
        code = KEY_TO_CODE.get(key, "GA")
        return {
            "emotion_key": key,
            "emotion_code": code,
            "intensity": 0.6,
            "vector_bias": {"E": 0.0, "D": 0.0, "S": 0.0, "T": 0.0, "H": 0.0},
            "source": "preset",
        }
    except KeyError:
        pass
    
    # Step 2: 调 DeepSeek
    try:
        from moodify.llm.client import DeepSeekClient
        client = DeepSeekClient()
        if client.available:
            result = client.interpret_emotion(nl_text)
            if result:
                code = result["emotion_code"]
                key = CODE_TO_KEY.get(code, "gentle_awakening")
                return {
                    "emotion_key": key,
                    "emotion_code": code,
                    "intensity": result["intensity"],
                    "vector_bias": result["vector_bias"],
                    "source": "deepseek",
                }
    except Exception:
        pass
    
    # Step 3: 回退
    return {
        "emotion_key": "gentle_awakening",
        "emotion_code": "GA",
        "intensity": 0.6,
        "vector_bias": {"E": 0.0, "D": 0.0, "S": 0.0, "T": 0.0, "H": 0.0},
        "source": "fallback",
    }
```

---

### 3.3 修改文件：`orchestration/workflow_engine.py`（追加）

#### 修改点 F：Phase 0 — 自然语言情绪解析

在 `process()` 方法的 Phase 1 之前插入:

```python
# ====== Phase 0: 情绪解析 (NL → 结构化目标) ======
emotion_parsed = None
try:
    from moodify.knowledge.emotion_targets import resolve_emotion_from_nl
    emotion_parsed = resolve_emotion_from_nl(emotion_target)
except Exception:
    pass

if emotion_parsed is None:
    # 极端回退
    emotion_parsed = {
        "emotion_key": "gentle_awakening",
        "emotion_code": "GA",
        "intensity": 0.6,
        "vector_bias": {"E": 0.0, "D": 0.0, "S": 0.0, "T": 0.0, "H": 0.0},
        "source": "fallback",
    }

# 将解析结果注入 Phase 1 的 emotion 参数
resolved_emotion_key = emotion_parsed["emotion_key"]
```

然后将 Phase 1 调用中的 `emotion_target` 参数替换为 `resolved_emotion_key`:

```python
phase1 = self._run_diagnosis(input_path, resolved_emotion_key)
```

---

## 4. 阶段 C — 记忆闭环

**前置条件**: `outputs/processing_history.jsonl` 中存在 ≥ 50 条记录。
**实施时机**: 阶段 A 和 B 稳定运行 ≥ 2 周，积累足够数据后。
**本规格不包含阶段 C 的具体实现。** 仅预留接口设计。

### 4.1 接口设计（留档）

```python
# memory/history.py (阶段 C 时创建)

@dataclass
class ProcessingRecord:
    diagnosis_vector: list[float]  # 14 自动参数 → L2 归一化
    strength_vector: dict          # 5D 强度值
    params: dict                   # 15 参数
    whs_before: float
    whs_after: float
    eds: float
    proxy_score: float
    emotion_code: str
    timestamp: str

class ProcessingHistory:
    def save(self, record: ProcessingRecord) -> None: ...
    def find_similar(self, query_vector: list[float], top_k: int = 5) -> list[tuple[ProcessingRecord, float]]: ...
    def count(self) -> int: ...
```

### 4.2 写入点

`workflow_engine.py` 的 `process()` 末尾，在 LLM 解读之后、`return` 之前：

```python
# 阶段 C 启用时记录历史
try:
    from moodify.memory.history import ProcessingHistory, ProcessingRecord
    h = ProcessingHistory(self._output_dir)
    if h.count() < 50:
        # 预热阶段，只记录不读取
        pass
    h.save(ProcessingRecord(
        diagnosis_vector=diagnosis_to_vector(ws_diagnosis),
        strength_vector=best_strength if best_strength else {},
        params=best_params if best_params else {},
        whs_before=whs_before, whs_after=whs_after,
        eds=eds, proxy_score=float(top_scores[best_idx]) if top_scores else 0.0,
        emotion_code=emotion_parsed["emotion_code"],
        timestamp=datetime.now().isoformat(),
    ))
except Exception:
    pass
```

---

## 5. 执行顺序（严格按此顺序实施）

```
阶段 A — 零 LLM 依赖
├── 01. pip install openai>=1.0  (确认 scipy>=1.9)
├── 02. mkdir optimizer/ + 创建 __init__.py
├── 03. 创建 optimizer/search.py ← 按 2.1.1→2.1.6 顺序实现
├── 04. python -c "from moodify.optimizer.search import search_optimal_strengths"  # 导入验证
├── 05. 修改 workflow_engine.py ← 修改点 A,B,C,D
├── 06. smoke_test.py 或 CLI 命令处理 1 首测试曲
└── 07. 确认输出目录有处理结果，日志显示 Phase 1.5 耗时 < 2s

阶段 B — 需要 DEEPSEEK_API_KEY
├── 08. mkdir llm/ + 创建 __init__.py
├── 09. 创建 llm/client.py ← 按 3.1.1→3.1.3 顺序实现
├── 10. 修改 knowledge/emotion_targets.py ← 追加 resolve_emotion_from_nl()
├── 11. 修改 workflow_engine.py ← 修改点 E (LLM 解读) + 修改点 F (Phase 0)
├── 12. $env:DEEPSEEK_API_KEY="sk-xxx" → CLI 测试 NL 情绪输入
└── 13. $env:DEEPSEEK_API_KEY="" → CLI 测试 fallback 路径

阶段 C — 推迟
└── 等待 ≥50 条真实记录积累
```

---

## 6. 验证命令集

```bash
# === 阶段 A 验证 ===
cd moodify-core-package
pip install -e .

# 导入验证
python -c "
from moodify.optimizer.search import (
    search_optimal_strengths, strength_to_params,
    define_strength_space, sample_strength_vectors, proxy_evaluate
)
print('All imports OK')
"

# 强度→参数 映射验证
python -c "
from moodify.optimizer.search import strength_to_params
from moodify.knowledge.craft_chains import get_recommended_params, PARAM_KEYS
sv = {'spectrum':0.5,'dynamic':0.5,'space':0.5,'layer':0.5,'master':0.5}
params = strength_to_params(sv, 'GA')
rec = get_recommended_params('GA')
for k in PARAM_KEYS:
    assert abs(params[k] - rec[k]) < 0.05, f'{k}: {params[k]} vs {rec[k]}'
print('strength_to_params @ 0.5 == rec: OK')
"

# LHS 采样验证
python -c "
from moodify.optimizer.search import sample_strength_vectors
space = {d: (0.2, 0.8) for d in ['spectrum','dynamic','space','layer','master']}
vecs = sample_strength_vectors(space, n=500)
assert len(vecs) == 500
for d in space:
    vals = [v[d] for v in vecs]
    assert all(0.2 <= x <= 0.8 for x in vals), f'{d} out of bounds'
print('LHS sampling OK')
"

# 完整搜索验证 (需要真实音频文件)
python -c "
from moodify.diagnosis.engine import DiagnosisEngine
from moodify.optimizer.search import search_optimal_strengths
engine = DiagnosisEngine()
ws = engine.diagnose_quick('test_audio.wav')  # ← 替换为实际文件
results = search_optimal_strengths(ws, 'GA', top_k=3)
print(f'Search returned {len(results)} candidates')
print(f'Top proxy score: {results[0][2]:.1f}')
assert len(results[0][1]) == 15
"

# === 阶段 B 验证 ===
# 设置 key
$env:DEEPSEEK_API_KEY="sk-xxxxxxxx"

python -c "
from moodify.llm.client import DeepSeekClient
client = DeepSeekClient()
assert client.available, 'DeepSeek not available'
result = client.interpret_emotion('像清晨阳光穿过窗帘')
if result:
    print(f'Mapped to: {result[\"emotion_code\"]} ({result[\"emotion_name\"]})')
    print(f'Bias: {result[\"vector_bias\"]}')
    print(f'Reasoning: {result[\"reasoning\"]}')
"

# 清除 key 测试 fallback
$env:DEEPSEEK_API_KEY=""

python -c "
from moodify.llm.client import DeepSeekClient
client = DeepSeekClient()
assert not client.available, 'Should be unavailable without key'
assert client.interpret_emotion('任意文本') is None
print('Fallback path OK')
"

python -c "
from moodify.knowledge.emotion_targets import resolve_emotion_from_nl
# 预设测试
r = resolve_emotion_from_nl('GA')
assert r['source'] == 'preset'
# 未知输入测试 (无 API key 时走 fallback)
r2 = resolve_emotion_from_nl('像清晨阳光穿过窗帘')
assert r2['source'] in ('preset', 'deepseek', 'fallback')
assert r2['emotion_code'] in ['GA','SE','UD','LW','HL','DR','WL','CN']
print('resolve_emotion_from_nl OK')
"
```

---

## 7. 附录：与原 SPEC-002 的关键差异

| 维度 | SPEC-002 原版 (19:45) | SPEC-002-REV (本规格) |
|------|----------------------|---------------------|
| 搜索空间 | 15D 参数空间，网格离散化 | 5D 强度空间，LHS 采样 |
| 候选生成 | `np.meshgrid` 维数爆炸 | `scipy.stats.qmc.LatinHypercube` |
| 代理评分 | 新建 `compute_edsr_proxy()` | 复用 `apply_chain_transfer()` + craft_match 正则 |
| LLM 角色 | `define_search_space` — 参数范围选择 | `interpret_emotion` — NL→情绪原型映射 |
| craft_chain_match | `# DEPRECATED` 废弃 | 保留，评分复用到 `proxy_evaluate` 的 Step 4 |
| 新增文件数 | 7 (.py 文件) | 3 (.py 文件) |
| 参数映射方向 | 15 参数 → 5 强度（正向） | 5 强度 → 15 参数（反向, `strength_to_params`） |
| Phase 0 | 不存在 | NL 情绪解析（`resolve_emotion_from_nl`） |
| 阶段 C 触发条件 | 无条件 | ≥50 条真实记录 |
| API 温度 | 0.3 | 0.2（更稳定） |
