# 题目 A2：EDSR 校准实验

**来源**: 母文件 §9 题目 A2
**类型**: 后续 AI 题目规格书
**产出**: 校准数据集 + Bradley-Terry 模型 + 相关性报告 + 失败样本表

---

## 0. 题目定义

建立 EDSR_proxy 与 EDSR_true 的校准实验。回答：代理指标能否代表人耳偏好？

---

## 1. 实验素材生成

### 1.1 测试曲目选择

```
10 首, 覆盖:
  2 首 Suno v4 生成
  2 首 Udio 生成
  2 首 Suno v3 / 其他生成器
  2 首从 07Music/albums 中选取
  2 首自行上传的 AI 音乐

风格覆盖: 钢琴 ≥ 2, 人声流行 ≥ 3, 电子氛围 ≥ 2, 摇滚 ≥ 1, 其他 ≥ 2
缺陷覆盖: 确保 17 种缺陷中 ≥ 10 种出现
```

### 1.2 版本生成

每首曲目生成 5 个版本:

```
V1: preset = get_recommended_params(emotion_code) [baseline]
V2: search_top1 = search_optimal_strengths top-1
V3: search_top3 = search 的另一个候选 (与 V2 不同)
V4: llm_recommend (如果 API 可用)
V5: extreme = 手动选择在某个维度上极端的参数 (如 P15=+5dB, 测试代理边界)
```

### 1.3 预测量

```
对每个版本:
  运行 DSP → 记录真实音频
  运行 diagnose → 记录 WHS
  计算 EDSR_proxy (当前实现)
  计算 WHS, LFR, ArtifactRisk 等辅助指标
```

---

## 2. 人耳评价协议

### 2.1 评价界面

```
┌─────────────────────────────────────────┐
│  请比较 A 和 B                            │
│                                          │
│  [播放 A]  [播放 B]                       │
│                                          │
│  哪个版本更好？                            │
│  ○ A 更好  ○ B 更好  ○ 无差异              │
│                                          │
│  确定程度: ○1 ○2 ○3 ○4 ○5                │
│  (1=完全不确定, 5=非常确定)                 │
└─────────────────────────────────────────┘
```

### 2.2 比较对设计

```
每首歌的 5 个版本 → C(5,2) = 10 对
每人每首歌评 10 对
共 10 首歌 → 每人 100 对
每对约 15 秒 → 每人约 25 分钟

听众: 5-10 人
总计: 500-1000 次比较
```

### 2.3 质量控制

```
插入 2 对隐藏重复 (同一对出现两次)
→ 检测听众的重复一致性
→ 一致性 < 70% 的听众数据降权或排除

插入 1 对锚定对 (已知优劣的极端对比)
→ 检测听众是否认真
→ 锚定对答错的听众标记为低信度
```

---

## 3. 数据分析

### 3.1 Bradley-Terry 建模

### 3.2 相关性计算

### 3.3 失败样本分类

（详见 P0-1 文章 §2-§3 的完整数据分析流程）

---

## 4. 产物

1. `calibration/experiment_materials/` — 10×5 个音频文件
2. `calibration/ratings.csv` — 所有比较数据
3. `calibration/bradley_terry_model.pkl` — 拟合模型
4. `calibration/correlation_report.md` — Spearman/Kendall 报告
5. `calibration/failure_samples.json` — 失败样本表
6. `calibration/proxy_revision_plan.md` — 如果 ρ < 0.3

---

## 5. 理论参考

- Bradley & Terry (1952), Thurstone (1927), Dawid & Skene (1979)
- ITU-R BS.1534-3 (MUSHRA), ITU-R BS.1116
- 母文件 P0-1, 定理 2

---

*Moodify 题目规格书 · A2 · v1.0*
