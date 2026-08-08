# Moodify

Moodify 是一个面向 AI 生成音乐的开源后期处理与听感工程系统。

它不负责再次生成音乐，而是把 AI 生成出来的音频当作“原料”，通过频谱分析、声音诊断、DSP 处理、前后对比、听感反馈和处理记录，让生成音乐更稳定、更耐听，也更接近可以发布或继续制作的状态。

一句话说：

> Moodify 是 AI 音乐生成之后的声音整理、修正和经验沉淀层。

```text
AI 生成音频
  -> 音频分析
  -> 声音诊断
  -> DSP 预设处理
  -> Before / After 检查
  -> Treatment Record
  -> 人工听感反馈
  -> 可复用的声音工程经验
```

## 项目是什么

Moodify 关注 AI 生成音乐常见的后期问题，例如：

- 频谱不平衡；
- 人声薄、冷、远，缺少存在感；
- 高频发硬或有塑料感；
- 低频松散或浑浊；
- 动态和瞬态不自然；
- 空间感像贴上去的；
- 生成结果能听，但还不像完成品。

Moodify 的目标不是承诺“一键变好”，而是提供一套可重复的声音处理流程：分析问题、选择处理方式、导出结果、比较前后差异，并把处理经验记录下来。

## 能做什么

当前核心能力集中在本地音频处理：

- 读取 WAV / MP3 / FLAC 等音频文件；
- 计算频谱和基础声音指标；
- 生成规则化的诊断结果；
- 使用 DSP 预设处理音频；
- 导出处理后的 WAV 和报告；
- 对比处理前后的差异；
- 保存 Treatment Records；
- 用人工听感反馈沉淀处理经验。

稳定入口是 `moodify-core-package` 里的 Python 包和 CLI。

## 不是什么

Moodify 不是：

- 文本生成音乐模型；
- 大模型训练框架；
- DAW 的替代品；
- 自动母带魔法按钮；
- 对所有音频都保证更好的算法承诺。

它更像一个声音工程实验台：让 AI 生成音乐经过可解释、可检查、可记录的后期处理流程。

## 基本流程

```text
输入音频
  -> 分析频谱和声音指标
  -> 生成诊断
  -> 选择预设
  -> 通过 DSP 链处理
  -> 导出 WAV 和报告
  -> 听感检查
  -> 记录处理结果
```

## 仓库结构

```text
moodify-core-package/   核心 Python 包和 CLI
scripts/                项目脚本和工具
docs/                   工程文档、方案和研究记录
treatment_records/      示例处理记录
data/                   参考数据和实验数据
phys-lab/               声学指标和实验代码
```

仓库里包含一些研究和实验材料。日常使用 Moodify 时，优先看 `moodify-core-package`。

## 安装

需要 Python 3.10 或更高版本。

```bash
cd moodify-core-package
pip install -e .
```

开发环境可以安装额外依赖：

```bash
pip install -e ".[dev]"
```

## CLI 示例

查看可用预设：

```bash
moodify presets
```

分析音频：

```bash
moodify analyze song.wav
```

处理音频：

```bash
moodify process song.wav --preset warm_vocal
```

输出通常会写入 `outputs/`，包括处理后的 WAV、分析图、诊断报告或其他检查文件。

## 预设

Moodify 包含一些规则化 DSP 预设，例如：

- `warm_vocal`：增强人声温度和存在感；
- `clean_master`：提升清晰度和母带稳定感；
- `wide_space`：增强空间感和立体声宽度。

预设是声音工程的起点，不是最终判断。真正的判断应来自响度匹配后的 Before / After 听感对比。

## 数据与隐私

Moodify 的核心流程是 local-first：输入音频可以只在本机处理。

如果你接入外部 API、模型或服务，请使用自己的环境变量配置，并遵守对应服务的条款。不要把 API Key、私人音频、私人数据集或未授权素材提交到仓库。

## 开源协议

Moodify 使用 GNU General Public License v3.0 开源，见 [LICENSE](LICENSE)。

除非另有说明，本仓库中的源代码和文档按 `GPL-3.0-only` 授权。输入音频、生成音频、第三方模型、第三方数据集和外部素材仍归各自权利人所有，并遵循它们自己的许可规则。
