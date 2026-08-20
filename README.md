# Moodify

> **Every voice deserves to be heard.**
>
> **每一种声音，都值得被世界听见。**

**Moodify Music / Moodify Player** 是 Moodify 唯一的对外产品面。

产品原则：**Listen. Then Play.**

核心用户动作：**Play.**

```text
Source / Cloud-prepared Track
        ↓
      Moodify
        ↓
       PLAY
```

Moodify 把声音分析、判断、受控处理、验证和生产复杂度留在系统内部。用户不需要理解 Ear、分轨、预设、Evidence 或状态机，才能获得核心播放体验。

## Product Surfaces

- `apps/music-android/` — Moodify Music Android 播放器。
- `apps/music-web/` — Moodify Web Player / PWA。
- `moodify-music-package/` — Music API、身份、目录与 BFF。
- `ops/web_origin/site/rongjingmusic/` — Moodify Product Home。
- `ops/web_origin/site/rongjingwenchuan/` — 荣景文川 Company Home。

公开品牌语言和站点职责以 [Public Brand Authority](docs/brand/public/README.md) 为准。

## Internal Systems

以下系统支撑 Moodify，但不构成第二个公开产品身份：

- **Moodify Ear / Auditory Intelligence** — 内部听觉、判断、验证与研究系统。
- **Cloud Production System** — Intake → Analyze → Stem → Judge → Intervene → Render → Verify → Evidence。
- **Classic Reconstruction** — 决策驱动的受控重建；属于内部生产哲学，不是公开产品面。

内部复杂度不是对外卖点。Ear 不是公开工作台，Moodify 也不是自动母带、预设浏览器或 AI 音乐后处理产品。

## Current Reality

当前事实状态以 [Repository Status](docs/REPOSITORY_STATUS.md) 和 [Current Architecture](docs/canon/CURRENT_ARCHITECTURE.md) 为入口。

截至最近一次有证据的运行时核验（W01-P00，2026-08-17）：

- Android、Web Player、Music platform / BFF 和静态音乐托管已存在于仓库或已核验运行环境；
- 两台 VPS 承载核心服务与数据工厂批处理；
- 完整 Ear / reconstruction 链路存在于仓库代码，但尚无已验证的云端生产流量；
- 对象存储、云端 AI 推理和部分数据基础设施仍未验证或尚未部署。

仓库代码、路线图或文档中的能力不自动等于已上线能力。未经运行时证据验证，不应写成生产事实。

## Repository Authority

进入仓库后按以下顺序阅读：

1. [AGENTS.md](AGENTS.md)
2. [Current Canon](docs/canon/CURRENT_CANON.md)
3. [Product Boundary](docs/canon/PRODUCT_BOUNDARY.md)
4. [Authority Order](docs/canon/AUTHORITY_ORDER.md)
5. [Repository Status](docs/REPOSITORY_STATUS.md)

历史文档可以保留其原始语言，但不能覆盖当前 Canon。改变公开产品身份、内部/外部边界、状态机、证据、云控制或数据权威时，必须显式声明 `CANON_CHANGE = YES` 并记录迁移与回滚。

## Engineering Model

Moodify 的内部研究与生产使用三项学科：

- **WSE — Wave-Spectral Evolution:** 声音里发生了什么？
- **MSE — Musical-Structural Engineering:** 音乐结构是什么？
- **PPE — Production Process Engineering:** 如何可靠生产、验证与恢复？

证据资产循环：

```text
Production Case
  -> Measurement Record
  -> Evidence Artifact
  -> Theory Update
  -> Rule Update
  -> Next Production Case
```

机器只能在经过验证、版本化且明确授权的范围内作出决定。范围外、证据不足、不确定或未解决的感知案例必须进入 `HUMAN_REQUIRED`、`INCONCLUSIVE` 或定义好的失败状态。

## Core Packages

- `moodify-core-package/` — 测量、诊断、判断、干预、验证与证据能力。
- `moodify-music-package/` — Music 产品的数据和服务层。
- `moodify-core-package/src/moodify/data_factory/` — 数据工厂与算法评审。
- `schemas/canonical/` — Production Case、Measurement、Evidence 等规范。
- `docs/canon/` — 当前产品与系统权威。

核心 Python 包的本地开发安装：

```bash
cd moodify-core-package
pip install -e ".[dev]"
```

CLI 示例：

```bash
moodify analyze song.wav
moodify process song.wav --preset clean_master
```

这些命令是内部窄实现入口，不是 Moodify 的公开产品定义。

## Scope and Safety

- 不把实验指标宣传为生产事实或艺术质量结论。
- 不保证每个处理结果都会“更好”；BYPASS 是合法成功结果。
- 不提交私人音频、API Key、未授权数据集或生成的重型工件。
- 代码变更应说明服务的案例、测量、证据、验证方式、失败行为和复用路径。

## License

Moodify is licensed under **GNU GPL v3.0 only** unless otherwise stated. See [LICENSE](LICENSE).
