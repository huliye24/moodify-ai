# NEM-MT-005｜样本资产库

**节点类型**：NEM｜Node Evolution Molecule｜节点进化分子  
**所属工程链**：Moodify 主线工程链  
**节点主题**：建立真实 AI 音乐样本体系，把输入音频、处理结果、MRS 记录和工艺实验沉淀为可复用数据资产  
**计划周期**：2026.7 - 2026.9  
**前置依赖**：Runtime 可稳定运行；存储规范初步确定；MRS / preset 实验开始产生结果  
**节点目标**：建立 Moodify 的样本资产库，使真实 AI 音乐样本可以被登记、存储、追踪、分层、评估、复用和长期积累。

---

## 1. 一句话定义

**MT-005 是 Moodify 从“运行实验”走向“积累数据资产”的节点。**

MT-001 解决 Runtime 稳定运行；MT-002 解决 MRS 跑分判断标准；MT-003 解决 MRS 批量生产瓶颈；MT-004 解决 preset 工艺沉淀；MT-005 则解决一个更底层的问题：

```text
所有真实 AI 音乐样本，如何被长期保存、标注、追踪、复用和转化为 Moodify 的数据资产？
```

没有样本资产库，Moodify 的实验会停留在一次性处理。  
有了样本资产库，每一次处理、每一次评分、每一次 preset 试验，都会变成可复用的工程资产。

---

## 2. 为什么 MT-005 重要

Moodify 的长期护城河，不只是 Runtime、MRS 或 preset，而是三者共同作用后沉淀出来的真实样本资产。

AI 音乐后处理系统要变强，必须依赖长期样本积累：

1. 不同生成平台的声音问题不同；
2. 不同音乐类型的频谱、动态、空间问题不同；
3. 同一个 preset 在不同样本上的效果不同；
4. MRS 需要真实样本分布来校准；
5. 工艺库需要样本反馈来升级；
6. 未来算法和模型需要结构化数据；
7. 团队协作需要统一样本命名和存储规则。

因此，MT-005 是 Moodify 的数据资产地基。

---

## 3. 节点核心产物

MT-005 的核心产物不是“收集很多音频文件”，而是建立一套可持续演化的样本资产体系。

| 产物 | 作用 |
|---|---|
| Sample ID System | 每个样本拥有唯一身份 |
| Sample Registry | 记录样本来源、平台、类型、状态和路径 |
| Storage Layout | 规范原始音频、处理结果、报告和特征文件的存储位置 |
| Metadata Schema | 统一样本元数据字段 |
| Rights & Usage Record | 记录样本使用范围、版权/授权/内部测试状态 |
| Dataset Split Rule | 区分 baseline / validation / stress / production 样本集 |
| Processing Lineage | 记录原始样本到处理版本的完整链路 |
| MRS History | 保存样本多次处理后的 MRS 变化历史 |
| Sample Quality Tier | 对样本质量和可用性分层 |
| Asset Report | 定期输出样本资产库报告 |

---

## 4. 样本资产库的基本思想

MT-005 的核心判断是：

```text
音频文件本身不是资产；
可追踪、可复用、可比较、可进入实验闭环的音频样本，才是资产。
```

所以一个样本进入资产库时，必须同时具备：

1. 唯一 sample_id；
2. 原始文件路径；
3. 来源记录；
4. 音频基础信息；
5. 音乐类型 / 情绪 / 平台标签；
6. 使用权限状态；
7. Runtime 处理记录；
8. MRS 评分历史；
9. preset 使用历史；
10. 当前资产状态。

---

## 5. 推荐样本分层

样本资产库不要一开始只按文件夹堆放。建议从第一天就做分层。

| 层级 | 名称 | 用途 |
|---|---|---|
| L0 | raw_inbox | 临时输入区，尚未登记 |
| L1 | registered | 已登记，有 sample_id |
| L2 | baseline | 基准样本，用于 MRS 和 preset 对比 |
| L3 | validation | 验证样本，用于判断公式和工艺是否稳定 |
| L4 | stress_test | 压力样本，用于测试极端问题 |
| L5 | production_candidate | 可进入产品化测试的高价值样本 |
| L6 | archived | 归档样本，保留但不主动参与实验 |

这套分层可以防止样本库变成混乱网盘。

---

## 6. 推荐目录结构

MT-005 的样本资产库建议采用以下存储结构：

```text
sample_asset_library/
  raw_inbox/
  registered/
  baseline/
  validation/
  stress_test/
  production_candidate/
  archived/

  metadata/
    sample_registry.jsonl
    sample_rights.jsonl
    sample_tags.jsonl
    dataset_splits.jsonl

  lineage/
    processing_lineage.jsonl
    preset_usage_history.jsonl
    mrs_history.jsonl

  features/
    spectral_features/
    dynamic_features/
    spatial_features/
    embedding_features/

  reports/
    sample_asset_report.md
    dataset_quality_report.md
    missing_metadata_report.md
```

这个结构的重点是：原始音频、元数据、处理链、评分历史和特征文件必须分开。

---

## 7. Sample ID 规则

样本必须有不可重复的 ID。建议格式：

```text
SMP-{SOURCE}-{YYYYMMDD}-{HASH8}
```

示例：

```text
SMP-SUNO-20260712-A8F39C21
SMP-UDIO-20260712-B91D22AF
SMP-INTERNAL-20260712-7F20AA91
```

其中：

- `SMP` 表示 sample；
- `SOURCE` 表示来源类型；
- `YYYYMMDD` 表示登记日期；
- `HASH8` 表示文件内容 hash 的前 8 位。

Sample ID 一旦创建，不应随文件移动而改变。

---

## 8. 样本元数据字段

每个样本至少应包含以下字段：

```json
{
  "sample_id": "SMP-SUNO-20260712-A8F39C21",
  "original_filename": "song_demo.wav",
  "source_platform": "suno",
  "source_type": "ai_generated_music",
  "created_or_collected_at": "2026-07-12",
  "registered_at": "2026-07-12",
  "file_format": "wav",
  "duration_sec": 183.2,
  "sample_rate": 44100,
  "bit_depth": 16,
  "channels": 2,
  "genre_tags": ["electronic", "art_pop"],
  "emotion_tags": ["warm", "melancholic"],
  "quality_tier": "baseline",
  "rights_status": "internal_research_only",
  "storage_path": "sample_asset_library/baseline/SMP-SUNO-20260712-A8F39C21/original.wav",
  "status": "active"
}
```

---

## 9. 权限与使用边界

MT-005 必须建立样本使用边界。否则样本资产库后期会变成风险库。

建议使用以下权限状态：

| 状态 | 含义 |
|---|---|
| internal_research_only | 仅用于内部研究和测试 |
| user_owned | 用户自有或明确授权 |
| public_domain | 公共领域素材 |
| licensed | 已获得授权 |
| uncertain | 权限不确定，不能进入产品训练或公开展示 |
| restricted | 受限制，不可继续使用 |

规则：

```text
权限不确定的样本，可以用于内部技术验证，不能用于公开发布、商业展示或模型训练。
```

---

## 10. 与 Runtime / MRS / preset 的关系

MT-005 不是孤立样本库，它必须和前面节点形成闭环。

```text
MT-001 Runtime
  负责产生处理结果

MT-002 MRS
  负责判断真实度变化

MT-003 MRS Performance
  负责让评分可以批量运行

MT-004 Preset Library
  负责沉淀有效处理工艺

MT-005 Sample Asset Library
  负责保存样本、结果、评分和工艺使用历史
```

也就是说，MT-005 是 Moodify 的“记忆层”。

---

## 11. 节点执行路线

MT-005 建议分 6 个 Gate 推进：

| Gate | 名称 | 目标 |
|---|---|---|
| Gate 0 | 节点建档 | 建立样本资产库规则、模板和目录 |
| Gate 1 | 样本身份系统 | 建立 sample_id、registry 和 metadata schema |
| Gate 2 | 存储结构落地 | 建立 raw / registered / baseline / validation 等目录 |
| Gate 3 | Runtime 联动 | Runtime 输出能自动写入 lineage 和 mrs_history |
| Gate 4 | 样本质量分层 | 样本可按质量、用途、权限和平台分层 |
| Gate 5 | 数据资产采纳 | 形成第一版可复用真实 AI 音乐样本体系 |

---

## 12. 初始样本规模建议

MT-005 初期不要追求数量，而要追求结构正确。

建议阶段：

| 阶段 | 样本规模 | 目标 |
|---|---:|---|
| Smoke Sample Set | 3 - 5 首 | 验证登记、路径和报告 |
| Baseline Set v0.1 | 10 - 30 首 | 支撑 MRS 与 preset 初步验证 |
| Validation Set v0.1 | 30 - 100 首 | 支撑稳定性和跨类型评估 |
| Stress Set v0.1 | 20 - 50 首 | 测试极端问题和失败样本 |
| Production Candidate Set | 100+ 首 | 为产品化前测试做准备 |

---

## 13. 节点完成标准

MT-005 完成，不是因为“文件夹里有很多音乐”，而是因为 Moodify 形成了可持续积累数据资产的能力。

最低完成标准：

```text
1. 已建立 sample_id 规则；
2. 已建立 sample_registry.jsonl；
3. 已建立 storage layout；
4. 已建立 metadata schema；
5. 已建立 rights / usage 记录；
6. 已建立 processing_lineage；
7. 已建立 mrs_history；
8. 已有 10 - 30 首真实 AI 音乐样本；
9. Runtime 处理结果可以回写到样本资产库；
10. 能生成第一版 sample asset report。
```

理想完成标准：

```text
形成 100 首以上结构化 AI 音乐样本资产，
每个样本都有来源、权限、标签、处理历史、MRS 历史和 preset 使用记录，
并能为 MRS 校准、工艺库升级和未来算法研究提供数据基础。
```

---

## 14. 节点结论

MT-005 是 Moodify 的数据资产地基。

它把散落的音频文件变成样本；  
把样本变成可追踪数据；  
把数据变成实验资产；  
把实验资产变成工艺和算法的长期燃料。

从 MT-005 开始，Moodify 不再只是处理声音，而是开始建立自己的真实 AI 音乐样本体系。
