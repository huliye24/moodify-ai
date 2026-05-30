# Moodify

> AI 音乐二次处理与情绪声波工程系统
> From AI-generated sound to finished emotional music.

Moodify 是一个面向 AI 音乐时代的声音处理工具。
它的目标不是再次生成一首歌，而是把 AI 平台生成的粗糙原声，转化为更接近正式作品的音乐版本。

在 Moodify 中，音乐不是一段简单的音频文件，而是一种可以被分析、诊断、修正、增强和沉淀的情绪声波。

---

## 一句话定位

**Moodify 是 AI 音乐的二次处理系统，用于分析、诊断、优化和沉淀 AI 音乐的声音工艺。**

---

## 核心理念

AI 音乐的真正机会，不只在生成，而在后期工艺。

```text
AI 生成原声
  ↓
频谱分析
  ↓
声音诊断
  ↓
情绪判断
  ↓
二次处理
  ↓
母带修正
  ↓
听感测试
  ↓
参数沉淀
  ↓
工艺复用
```

生成平台解决的是“从无到有”。
Moodify 要解决的是“从粗糙到作品”。

---

## Moodify 解决什么问题？

AI 音乐常见的问题包括：

* 频谱过平
* 瞬态发软
* 人声纹理不足
* 高频发亮但不通透
* 空间感像贴上去的
* 情绪起伏不够真实
* 整体听感有“塑料感”

Moodify 的目标，是通过声音分析与二次处理，让 AI 音乐拥有更好的层次感、空间感、动态感、情绪质感和作品完成度。

---

## 当前最小目标：Moodify v0.1.0

Moodify v0.1.0 的核心目标不是做复杂系统，而是先跑通一个最小闭环：

```text
导入音频
  ↓
生成频谱图
  ↓
生成声音诊断报告
  ↓
选择处理预设
  ↓
导出优化后的音频
```

### v0.1.0 核心功能

1. 导入音频文件
2. 自动生成频谱分析图
3. 输出基础声音诊断报告
4. 提供 3 个基础处理预设
5. 导出处理后的 WAV 音频文件

---

## 三个基础处理预设

早期版本将优先实现三个稳定、可测试、可复用的处理预设：

### 1. Warm Vocal

用于增强人声温度、厚度和亲密感。

适合：

* 女声
* 法语 art-pop
* 情绪型人声
* 低速叙事歌曲

### 2. Clean Master

用于清理整体频谱，让声音更干净、更稳定。

适合：

* AI 生成原声初步优化
* demo 转作品
* 平台发布前的基础母带处理

### 3. Wide Space

用于增强空间感和听觉宽度。

适合：

* cinematic electronic
* ambient pop
* 情绪氛围音乐
* 需要空间层次的 AI 音乐

---

## 技术方向

Moodify 早期采用 Python 作为核心研发语言。

计划使用的技术栈包括：

```text
Python
NumPy
SciPy
librosa
soundfile
pyloudnorm
matplotlib
pedalboard
FastAPI
PySide6 / Electron / React
```

早期重点不是复杂界面，而是稳定跑通声音处理核心。

---

## 项目结构规划

```text
moodify/
├── moodify-core-package/        # Python 核心引擎
│   ├── src/
│   │   └── moodify/
│   │       ├── audio_loader.py  # 音频导入
│   │       ├── analyzer.py      # 频谱分析
│   │       ├── diagnostics.py   # 声音诊断
│   │       ├── processor.py     # 二次处理
│   │       ├── presets.py       # 处理预设
│   │       ├── exporter.py      # 音频导出
│   │       └── cli.py           # 命令行入口
│   ├── tests/
│   └── pyproject.toml
│
├── moodify-player/              # 本地播放器 / 测试入口
├── moodify-web/                 # 展示页面 / 产品页面
├── docs/                        # 文档与实验记录
├── experiments/                 # 声音实验与参数测试
├── assets/                      # 图片、示意图、品牌资源
└── README.md
```

---

## 开发原则

Moodify 遵循以下工程原则：

```text
稳定运行 > 功能复杂
代码清晰 > 炫技
可测试 > 模型自信
最小闭环 > 完整幻想
实验记录 > 一次性灵感
参数沉淀 > 临时处理
```

在 v0.1.0 跑通之前，暂不优先开发：

* 账号系统
* 云端服务
* 商业支付
* 大规模 AI 模型
* 复杂插件市场
* 完整工业级 GUI

---

## 情绪声波工程学

Moodify 背后的长期理论方向是：

**情绪声波工程学，Emotional Wave Engineering。**

它研究声音中的频率、能量、相位、动态、空间、纹理与人的情绪感知之间的关系。

Moodify 不是单纯的音频工具，而是一个实验型声学工程系统。

它的长期路径是：

```text
理论研究
  ↓
工程建模
  ↓
Python 实验
  ↓
参数测试
  ↓
声音诊断
  ↓
处理工艺
  ↓
软件功能
  ↓
工艺库沉淀
```

---

## AI 协作开发方式

Moodify 使用双模型工程协作方式推进。

```text
Claude
  ↓
读取本地代码、目录、报错、运行结果

ChatGPT
  ↓
进行架构判断、代码生成、重构、修复与开发规划

PyCharm
  ↓
本地运行、测试、反馈真实结果

GitHub
  ↓
作为项目代码事实层
```

为了降低模型之间的信息损耗，Moodify 使用：

**MHP：Moodify Handoff Protocol**
即 Moodify 双模型工程交接协议。

核心原则：

```text
事实 > 判断 > 建议
代码 > 描述
报错 > 猜测
文件路径 > 泛泛而谈
运行结果 > 模型自信
```

---

## 当前开发路线

### v0.1.0 — 最小声音处理闭环

* 音频导入
* 频谱图生成
* 声音诊断报告
* 三个基础处理预设
* WAV 导出

### v0.2.0 — 本地 GUI

* 简单桌面界面
* 文件选择
* 分析结果展示
* 预设按钮
* 导出按钮

### v0.3.0 — 批量处理

* 多文件导入
* 批量分析
* 批量导出
* 参数记录

### v0.4.0 — 工艺参数库

* 保存处理参数
* 记录声音诊断结果
* 建立歌曲处理档案
* 支持实验复盘

### v0.5.0 — 声音评分系统

* 频谱评分
* 动态评分
* 空间评分
* 情绪质感评分
* AI 音乐塑料感诊断

### v1.0.0 — Moodify Pulse

* 完整桌面应用
* 声音诊断系统
* 工艺库系统
* 本地项目管理
* 面向 AI 音乐创作者的正式工具

---

## 安装与运行

### 环境要求

```text
Python 3.10+
Windows / macOS / Linux
```

### 安装核心包

```bash
cd moodify-core-package
pip install -e .
```

### 启动命令

```bash
moodify serve
```

或在开发阶段直接运行：

```bash
python -m moodify.cli
```

---

## 目标用户

Moodify 面向：

* AI 音乐创作者
* Suno / Udio 用户
* 独立音乐人
* 声音实验者
* AI 音乐后期处理研究者
* 情绪音乐产品开发者
* 想把 AI demo 打磨成作品的人

---

## 项目愿景

Moodify 的长期目标，是成为 AI 音乐时代的声音工艺系统。

它不只是一个播放器，不只是一个生成器，也不只是一个后期插件。

Moodify 要做的是：

```text
让 AI 音乐从生成品，变成作品；
让声音处理从经验，变成工艺；
让工艺参数从一次性操作，变成可复用资产；
让音乐重新成为人看见自己的情绪镜子。
```

---

## License

Proprietary
文川院 / Moodify 声音实验室 / 影焰实验室

---

## Status

Moodify is currently in early prototype stage.

当前阶段：
**v0.1.0 最小声音处理闭环开发中。**
