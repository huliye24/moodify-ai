<p align="center"><img src="brand/assets/moodify-horizontal.png" alt="Moodify horizontal logo" width="100%"></p>

# Moodify Sound Protocol

**让声音处理成为 AI、Agent 与人都能调用、检查和复现的工作流程。**

**A sound-processing protocol with a CLI reference implementation.**

Moodify 接受一份明确的 JSON 作业，通过 CLI 调用共享声音 Core，生成处理后的音频与机器可读的执行记录。App / Player 保留播放、预览和人工审听的角色。品牌信念仍是“每一种声音，都值得被世界听见”；协议本身不替人决定什么声音应当发布。

```text
AI / Agent / Human
        │ JSON job
        ▼
 Moodify CLI ── validate / process
        │
        ▼
 Shared Core ── analysis + existing DSP pipeline
        │
        ▼
 WAV + parameters + diagnosis + file hashes
        │
        ▼
 Human listening and release decision
```

## 快速开始

需要 Python 3.10 或更新版本。从仓库根目录安装（建议使用虚拟环境）：

```bash
python -m pip install -e moodify-core-package
```

把音频放在 `audio/source.wav`，在其上级目录新建 `job.json`：

```json
{
  "protocol": "moodify.sound/0.1",
  "source": "audio/source.wav",
  "preset": "clean_master",
  "output_dir": "outputs"
}
```

```bash
moodify protocol validate job.json
moodify protocol process job.json
```

相对路径以 `job.json` 所在目录为基准。CLI 成功时向标准输出写入 JSON；校验或执行错误向标准错误输出写入 JSON，退出码为 2。执行记录包含预设参数、诊断、输出 WAV 路径以及输入/输出 SHA-256。处理状态是 `processed_review_required`，**不是“已通过质量验证”**。

当前预设：`clean_master`、`warm_vocal`、`wide_space`。详情见 [MSP/0.1 协议说明](docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md)。

## 已实现与目标

| 能力 | 当前状态 |
| --- | --- |
| JSON 作业校验与 CLI 调用 | 已实现，MSP/0.1 |
| 使用现有 Core 进行预设声音处理并导出 WAV | 已实现，MSP/0.1 |
| 返回参数、诊断和文件哈希 | 已实现；这是执行证据，不是听感验收 |
| 人工审听与发布决定 | 必须由人完成 |
| 可编辑、可旁路、可回退的 Mix Graph | 目标态，尚未由 MSP/0.1 实现 |
| 自动听感验证或云端协议服务 | 未作为 MSP/0.1 能力提供 |

Moodify 只维护一个声音 Core；CLI 和 App 不应各自实现一套相互矛盾的声音算法。旧版 `analyze`、`show`、`local-analyze` 和 `cache` 命令保留。早期分析 Demo 与研究模块仍在仓库中，但不等同于 MSP/0.1 的协议保证。

## 项目入口

- [协议规范与边界](docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md)
- [Core Python 包与 CLI](moodify-core-package/)
- [产品 Canon](docs/canon/CURRENT_CANON.md) · [仓库状态](docs/REPOSITORY_STATUS.md)
- [贡献说明](CONTRIBUTING.md) · [许可证](LICENSE)

开发者运行与本次协议相关的测试：

```bash
python -m pytest moodify-core-package/tests/test_sound_protocol.py moodify-core-package/tests/test_v01_pipeline.py -q
python scripts/canon_guard.py
```

Moodify 采用 **GNU GPL-3.0-only** 许可。提交音频或运行 Agent 前，请确认你对输入素材拥有相应权利；不要把私有音频或密钥加入仓库。
