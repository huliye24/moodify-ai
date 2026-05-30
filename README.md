# Moodify O3ics — AI 歌词创作工具

基于 AI 的歌词生成工具，支持通过规则引擎自定义创作风格，让每一条规则都成为你的创作资产。

---

## 核心理念

```
歌词创作 = AI 生成 × 规则引擎 × 人工雕琢
```

不是"输入主题 → 输出歌词"的黑箱，而是让你定义创作规则、控制风格方向、反复迭代打磨的创作工具。

## 规则引擎

每条规则都是你的创作资产——定义一次，复用无数次：

- **风格规则**：押韵模式、段落结构、句式偏好
- **内容规则**：主题约束、意象库、情感走向
- **语言规则**：修辞手法、用词风格、节奏控制

---

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 安装

```bash
cd moodify-core-package
pip install -e .
```

### 启动

```bash
moodify serve
```

---

## 项目结构

```
moodify/
├── moodify-core-package/    # 核心引擎 (Python)
├── moodify-pulse/           # 桌面应用 (Electron + React)
├── moodify-app/             # Web 应用
├── moodify-desktop/         # 桌面端
├── moodify-system/          # 系统模块
├── docs/                    # 文档
└── 07Music/                 # 音乐库
```

---

## 许可证

Proprietary — 文川院 / Moodify 声音实验室 · 影焰实验室
