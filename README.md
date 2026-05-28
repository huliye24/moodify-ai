# Moodify — AI 音乐情绪波场显影器

## 一句话定位

**Moodify 是一个 AI 音乐后期处理引擎**。它不做音乐生成，而是对 AI（Suno/Udio）生成的原始音频进行诊断、重构和情绪显影——像暗房把底片显影成照片一样，把 AI 音乐的原始情绪波场变成清晰、稳定、可发布的成品。

---

## 理论基础

Moodify 建立在**情绪波工程学（Emotional Wave Engineering, EWE）**理论之上。

完整理论见：[WCAE-EWE-PRINCIPLE-001：Moodify 核心引擎原理极限文件](docs/product/WCAE-EWE-PRINCIPLE-001_Moodify核心引擎原理极限文件_耶鲁格式_中文.md)

### 第一性原理

```
AI 音乐不是成品，而是一个可被诊断、重构、显影的原始情绪波场。
```

### 产品定义

```
Moodify = 情绪波场显影器
```

### 核心工程公式

```
不可控 AI 复合波 → 可控情绪波
```

### 三层结构

```
对象：原始情绪波场
方法：波场塑形
目标：情绪显影
```

Moodify 不是普通母带工具、音质增强器或插件预设库。它的目标不是"让音频更好听"，而是**让原始波场中的情绪胚胎更准确、更清晰、更稳定、更可发布**。

---

## 核心工作流

```
输入: AI 原始音频 (.wav/.mp3/flac) + 目标情绪
  │
  ▼
Phase 1: 诊断 — 18 参数 WaveState 提取 + 缺陷分类 + WHS 健康分
  │
  ▼
Phase 2: 源分离 — Demucs 将音频分离为人声/鼓/贝斯/其他
  │
  ▼
Phase 3: 分层增强 — 基于工艺卡参数对每个 stem 应用 EQ/压缩/谐波/混响
  │
  ▼
Phase 4: 空间重构 — M/S 处理 + 立体声宽度 + 深度重建
  │
  ▼
Phase 5: 再合成 — Stem 混合 + 增益平衡
  │
  ▼
Phase 6: 情绪显影 + 母带 — 平台自适应响度 + 限幅 + 质检
  │
  ▼
输出: 成品音频 + 前后对比报告
```

---

## 五维波场模型

AI 音乐的"波场"有五个维度，每个维度有对应的诊断参数：

| 维度 | 参数 | 含义 |
|------|------|------|
| **Spectrum** 频谱 | S1-S5 | 频率能量分布（低频存在感、温暖度、中频清晰度、空气感、频谱倾斜） |
| **Dynamics** 动态 | D1-D4 | 响度起伏与冲击力（LRA、段落对比、微动态、峰值响度比） |
| **Space** 空间 | SP1-SP4 | 立体声场与深度（相关性、前后分离、混响一致性、宽度健康度） |
| **Layers** 层级 | L1-L4 | 声部清晰度与分离度（人声 SNR、贝斯清晰度、鼓检测、层数） |
| **Emotion** 情绪 | E1-E4 | 情绪表达质量（方向、丰富度、疲劳风险、段落连贯性） |

---

## 八种标准情绪工艺

每种情绪对应一组完整的 15 参数 DSP 链：

| 代码 | 情绪 | 核心特征 |
|------|------|----------|
| GA | 温柔觉醒 | 温暖人声 + 低频增强 + 轻压缩 + 短混响 + 柔和高频 |
| SE | 神圣空灵 | 轻盈人声 + 克制低频 + 极轻压缩 + 宏大混响 + 开放高频 |
| UD | 都市危险 | 紧张人声 + 压迫低频 + 重度压缩 + 工业谐波 + 紧致空间 |
| LW | 孤独留白 | 内省人声 + 中性低频 + 保留动态 + 深远混响 + 暗调高频 |
| HL | 治愈温暖 | 温暖人声 + 饱满低频 + 柔和压缩 + 温暖谐波 + 柔光高频 |
| DR | 黑暗浪漫 | 性感人声 + 深沉低频 + 中等压缩 + 暗色谐波 + 深邃混响 |
| WL | 废土机械 | 锋利人声 + 冲击低频 + 极限压缩 + 重度失真 + 极干空间 |
| CN | 电影感 | 叙事人声 + 宽广低频 + 保留动态 + 史诗混响 + 影院高频 |

---

## 不可牺牲原则

1. **诊断先于处理** — No Diagnosis, No Processing
2. **情绪先于参数** — 所有参数动作必须回答"是否帮助目标情绪显影？"
3. **状态转移必须可记录** — 每一步 DSP 记录 WS_before → WS_after + ΔWS
4. **风险门控不可绕过** — 红/橙/黄/绿四级风险输出
5. **人耳是最终仲裁者** — 所有高价值工艺链必须经过盲测
6. **工艺知识必须沉淀** — 成功经验进入工艺库，可复现才算能力

---

## 北极星指标

**EDSR（Emotion Development Success Rate）**：

```
EDSR = N_prefer_processed / N_total
```

EDSR 回答的是：处理后情绪是否更符合目标？——而不是"声音是否更响"或"频谱是否更漂亮"。

---

## 项目结构

```
moodify/
├── moodify-core-package/       # 核心引擎 (Python)
│   └── src/moodify/
│       ├── diagnosis/          # 诊断引擎 — 18 参数波场提取
│       ├── knowledge/          # 知识库 — 8 情绪 × 15 参数工艺链
│       ├── processing/         # DSP 引擎 — pedalboard 效果器链
│       ├── orchestration/      # 工作流编排 — 六阶段流水线
│       └── api/                # FastAPI 服务 — REST 接口
│
├── moodify-pulse/              # 桌面应用 (Electron + React)
│   ├── src/
│   │   ├── App.tsx             # 主界面 — 五阶段处理向导
│   │   ├── components/         # UI 组件
│   │   └── api/client.ts       # API 客户端
│   └── electron/main.ts        # Electron 主进程
│
├── 07Music/                    # 音乐库 — 测试音频与实验记录
│   ├── albums/                 # AI 音乐批次
│   └── tools/                  # 离线批处理脚本
│
├── docs/
│   ├── product/                # 产品文档
│   │   ├── PRINCIPLE-001       # 原理极限文件 (S+ 级)
│   │   ├── PRD.md              # 产品需求文档
│   │   └── ROADMAP.md          # 产品路线图
│   └── engineering/            # 工程文档
│
├── python/                     # 旧版 Python 模块 (逐步迁移中)
├── backend/                    # 旧版 Go 后端 (已弃用)
└── logo/                       # Logo 资源
```

---

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- Windows 10+ / macOS / Linux

### 安装核心引擎

```powershell
cd moodify-core-package
pip install -e .
```

### 启动后端 API

```powershell
moodify serve
# 或
python -m uvicorn moodify.api.main:app --host 127.0.0.1 --port 8000
```

API 文档：http://localhost:8000/docs

### 启动前端开发服务器

```powershell
cd moodify-pulse
npm install
npm run dev
```

前端界面：http://localhost:5173

### CLI 命令（开发调试用）

```powershell
moodify emotions              # 列出 8 种情绪
moodify analyze song.wav      # 诊断分析
moodify process song.wav "温柔觉醒"  # 一键处理
moodify batch ./samples "神圣空灵"   # 批量处理
```

---

## 当前版本

v0.2.0 — MVP 阶段

已实现：
- 18 参数波场诊断
- 8 种情绪工艺卡 × 15 DSP 参数
- 六阶段处理流水线（诊断 → 源分离 → 增强 → 空间 → 再合成 → 母带）
- 会话管理 + 文件下载
- React/Electron 桌面 UI
- CLI 命令行工具

---

## 许可证

Proprietary — 文川院 / Moodify 声音实验室 · 影焰实验室

---

*情绪波工程学 · 文川院 / Moodify 声音实验室 · 影焰实验室*
