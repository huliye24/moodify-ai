# MHP：Moodify 双模型工程交接协议

> **Moodify Handoff Protocol**
> 用于 Claude、ChatGPT、用户之间进行 Moodify 项目的工程交接。
> 核心目标：让 AI 编程从"聊天式协助"升级为"工程交接流水线"。

---

## 0. 协议目的

本协议用于 Claude、ChatGPT、用户之间进行 Moodify 项目的工程交接。

- **Claude**：负责读取本地代码环境、目录结构、文件内容、运行结果与报错。
- **ChatGPT**：负责根据 Claude 提供的代码事实，进行架构判断、代码生成、重构方案、Bug 修复与下一步开发设计。
- **用户**：负责在 PyCharm / 本地环境中运行代码，并将结果反馈给两个模型。

本协议的核心原则是：

```text
事实 > 判断 > 建议
代码 > 描述
报错 > 猜测
文件路径 > 泛泛而谈
运行结果 > 模型自信
```

---

## 1. Claude → ChatGPT 交接格式

每次 Claude 向 ChatGPT 交接任务时，必须使用以下结构：

```text
【MHP 交接单】

【项目名称】
Moodify

【当前版本】
例如：v0.1.0 / 未定 / main 分支

【当前目标】
一句话说明这次要完成什么。
例如：修复音频导入后频谱图无法生成的问题。

【当前目录结构】
粘贴 tree 结果，例如：

moodify/
├── main.py
├── requirements.txt
├── audio/
│   ├── loader.py
│   ├── analyzer.py
│   └── processor.py
├── ui/
│   └── main_window.py
└── output/

【关键文件内容】
按文件路径粘贴，不要只描述。

文件：main.py
```python
这里粘贴完整代码
```

文件：audio/analyzer.py
```python
这里粘贴完整代码
```

【运行命令】
例如：
python main.py

【运行结果】
说明是否成功启动，是否生成文件，是否有界面，是否有输出。

【完整报错】
粘贴完整 traceback，不要只截取最后一行。

【Claude 的初步判断】
Claude 可以给判断，但必须和代码事实分开。
例如：
我认为问题可能出在 analyzer.py 中的采样率处理，但不确定。

【希望 ChatGPT 完成的任务】
明确写出希望 ChatGPT 做什么：

1. 修复 Bug
2. 重构某个模块
3. 新增某个功能
4. 生成完整替换文件
5. 设计下一步架构
6. 写 requirements.txt
7. 写测试脚本
```

---

## 2. ChatGPT → 用户 / Claude 回传格式

ChatGPT 回传时，优先使用以下结构：

```text
【MHP 回传单】

【问题判断】
说明我根据代码事实判断出的核心问题。

【修改范围】
列出需要修改或新增的文件：

1. audio/analyzer.py
2. audio/processor.py
3. main.py

【修改策略】
说明为什么这样改，不做过度复杂设计。

【完整代码】
按文件给出完整可替换代码。

文件：audio/analyzer.py
```python
完整代码
```

文件：audio/processor.py
```python
完整代码
```

【运行方式】
告诉用户在 PyCharm 或终端里如何运行：

```bash
python main.py
```

【测试方式】
说明怎么判断成功：

1. 能导入 wav/mp3 文件
2. 能生成频谱图
3. output 文件夹出现分析图
4. 终端没有报错

【下一步建议】
只给 1-3 个下一步，不要发散。
```

---

## 3. 文件交接规则

Claude 给 ChatGPT 文件时，必须遵守：

```text
1. 必须给文件路径
2. 必须给完整代码
3. 不要只给摘要
4. 不要说"代码大概是"
5. 不要省略 import
6. 不要省略 main 函数
7. 不要省略报错上下文
```

错误示例：

```text
audio.py 里好像有个 librosa 的错误。
```

正确示例：

````markdown
文件：audio/analyzer.py

```python
import librosa
import numpy as np


def analyze_audio(path):
    y, sr = librosa.load(path)
    return y, sr
```

运行时报错：

```text
Traceback (most recent call last):
  File "main.py", line 12, in <module>
    analyze_audio("test.wav")
  File "audio/analyzer.py", line 5, in analyze_audio
    y, sr = librosa.load(path)
...
```
````

---

## 4. 任务编号规则

每次任务使用编号，方便追踪。

```text
MHF-001：建立项目骨架
MHF-002：实现音频导入
MHF-003：生成频谱图
MHF-004：生成声音诊断报告
MHF-005：加入三个处理预设
MHF-006：导出处理后音频
MHF-007：加入 GUI
MHF-008：打包为 Windows EXE
```

每次 Claude 交接时，需要写：

```text
【任务编号】
MHF-003

【任务名称】
生成频谱图
```

---

## 5. Bug 反馈格式

当代码运行失败时，用户或 Claude 必须这样反馈：

````markdown
【Bug 反馈】

【任务编号】
MHF-003

【运行命令】
python main.py

【操作步骤】
1. 打开软件
2. 点击导入音频
3. 选择 test.wav
4. 点击生成频谱图

【预期结果】
应该在 output 文件夹生成 spectrum.png

【实际结果】
没有生成图片，程序崩溃

【完整报错】
```text
粘贴完整报错
```

【相关文件】
main.py

audio/analyzer.py
````

---

## 6. 功能开发格式

当要新增功能时，使用：

```text
【功能开发请求】

【任务编号】
MHF-005

【功能名称】
三个音频处理预设

【功能目标】
给用户提供三个基础预设：
1. Warm Vocal
2. Clean Master
3. Wide Space

【输入】
用户导入的音频文件

【输出】
处理后的 wav 文件

【限制】
1. 先不要做复杂 AI 模型
2. 先用 scipy / librosa / soundfile 实现
3. 保持代码简单可运行
4. 优先保证稳定

【希望 ChatGPT 输出】
1. 新增 processor.py
2. 修改 main.py
3. 给出完整代码
4. 给出测试方法
```

---

## 7. 架构决策格式

当项目需要做技术选择时，使用：

```text
【架构决策请求】

【问题】
GUI 使用 PySide6 还是 Tkinter？

【当前情况】
用户使用 Python + PyCharm，项目早期，目标是快速做出可运行版本。

【选项】
A. Tkinter
B. PySide6
C. Web UI

【限制】
1. 用户不想配置太复杂
2. 需要后续能打包 EXE
3. 软件要有一定工业质感
4. 先完成 v0.1.0

【希望 ChatGPT 判断】
给出推荐方案、理由、风险、下一步。
```

---

## 8. GitHub 交接格式

如果代码已经上传 GitHub，Claude 或用户应提供：

```text
【GitHub 信息】

【仓库地址】
https://github.com/xxx/moodify

【当前分支】
main

【最近一次提交说明】
例如：完成基础 GUI，但频谱图无法生成

【需要查看的文件】
1. main.py
2. audio/analyzer.py
3. requirements.txt

【当前问题】
说明当前最卡住的地方。
```

---

## 9. 三方角色分工

```text
用户：
负责产品方向、运行代码、测试结果、最终判断。

Claude：
负责读取本地代码、总结当前状态、整理报错、生成交接单。

ChatGPT：
负责架构设计、代码生成、Bug 修复、重构方案、开发路线。
```

---

## 10. Moodify 当前最小开发目标

Moodify v0.1.0 的核心闭环是：

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

在这个闭环跑通前，不做复杂功能，不做云端系统，不做账号系统，不做大规模 AI 模型。

优先级：

```text
稳定运行 > 功能复杂
代码清晰 > 炫技
可测试 > 模型自信
最小闭环 > 完整幻想
```

---

## 11. 推荐使用流程

完整工作流如下：

```text
Claude 看本地代码
  ↓
Claude 按 MHP 协议生成交接单
  ↓
用户把交接单发给 ChatGPT
  ↓
ChatGPT 写代码 / 架构 / 修复方案
  ↓
用户在 PyCharm 运行
  ↓
用户或 Claude 按 MHP 协议反馈结果
  ↓
进入下一轮修复或开发
```

---

## 12. 协议的本质

MHP 不是普通提示词，而是一套 AI 工程协作语言。

它解决的问题不是"模型会不会写代码"，而是：

```text
模型之间如何交接事实
代码状态如何被准确描述
报错如何被完整传递
任务如何被编号追踪
开发如何形成闭环
```

最终目标是让 Moodify 从概念进入工程生命期。

> Moodify 的开发，不应再停留在模型聊天。
> 它应该进入 AI 工程流水线。
