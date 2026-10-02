# Layer D — 商业化前置 独立提案

**日期：** 2026-10-02
**状态：** ADJUDICATED — 四项裁决已落（§8）；D-0 工程前置已实施（§9）
**Canon 依据：** v2.1 Sound Protocol（`b6673830`）+ v2.0 Professional Finishing（`a69c3e3c`）
**上游：** `docs/plan/2026-10-02_MSP02_ANALYSIS_JOB_AND_DISPLAY_DESIGN.md` §6（Layer A `68af88e4` / B `f7ceb999` / C `a868ccdc` 已完成，五道门全绿）
**授权记录：** 2026-10-02 人类指令「去做」（对 Layer D 开工的授权）；本提案按该层自身约定「开工前须独立提案」编写

---

## 1. 问题定义

MSP 0.2 的分析/比较/校准链已在仓库内完整可跑（1121 测试、协议纪律、诚实校准面），但距离可售卖形态缺四样（上游提案 §7）：**可分发的安装形态、license 商业结构、云端计量、品牌与定价**。Layer D = 把这四样补齐或显式裁决缓做。

本提案不含任何价格数字与收入承诺；所有商业结构决策归人类（上游提案 §7 第 4 条：「全是人类决策，AI 不代填」）。

## 2. 现状事实（勘察 2026-10-02，不虚构）

| # | 事实 | 来源 |
|---|---|---|
| F1 | pip 包骨架完整：`moodify-core-package/pyproject.toml` 为唯一入口权威，三入口 `moodify` / `moodify-node` / `moodify-reconstruction`，src-layout，17 个 pinned 依赖，Python ≥3.10 | pyproject + Layer A G5 收口 |
| F2 | **版本不一致**：pyproject `version = "0.1.0"` vs 运行时 `PRODUCT_VERSION = "1.0.0-rc.1"`——发布前必须统一 | pyproject:7 / release.py:26 |
| F3 | 运行时硬依赖 ffmpeg（解码+频谱图），`moodify doctor` 依赖探测命令**未实现**（上游 §5 G6 只完成了文档声明） | grep release_cli 无 doctor |
| F4 | 法律底座：root `LICENSE` = GPL-3.0；pyproject `license = "GPL-3.0-only"`；新文件 SPDX header 纪律；版权主体单一（pyproject 署名「文川院 / Moodify 声音实验室」） | LICENSE / pyproject / 补丁包03 |
| F5 | **单一版权主体 ⇒ 双许可在法律上是干净的**（无需 CLA / 外部贡献者授权回收）；当前仓库无外部贡献者 | F4 推论 |
| F6 | API 面已有异步作业骨架：`POST /api/v1/auditory/jobs` + 结果轮询 + `POST /api/v1/auditory/analyze`；**无鉴权、无计量** | `api/main.py` 路由勘察 |
| F7 | 节点资产：LA 全球计算节点（moodify-global-engine，103.144.246.242）；阿里云接入节点（120.55.191.146）队列+资源守卫模式已验证（3 case SUCCEEDED 无 OOM，systemd worker） | 记忆 27/28 包 |
| F8 | 容器先例存在（moodify-qa Dockerfile；根目录 Dockerfile 属 3.0 时代遗留未整理），core 包**无**自己的容器化 | 磁盘勘察 |
| F9 | 品牌宪法 v1.1 冻结：公共表达「每一种声音，都值得被世界听见。 / Listen. Then Play.」，公共品牌权威在 `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md` | CANON_CHANGELOG 2026-08-19 |
| F10 | 第一客户是 **AI agent / 开发者**（上游提案 §1 用户意图：CLI 可被 AI 调用），不是终端听众 | 上游提案 §1 |

## 3. 四个工作区（决策项 vs 工程项分离）

### A. 打包分发

**无需决策、可立即做的工程前置（D-ENG）：**
- `D-ENG-1` 版本统一：pyproject version 对齐 PRODUCT_VERSION（单一事实源， proposal 推荐 pyproject 读取或 CI 校验两者一致）。
- `D-ENG-2` `moodify doctor`：ffmpeg/依赖/Python 探测，stdout 恒 JSON——AI agent 与安装排障的第一接触面。
- `D-ENG-3` 构建验证：`python -m build` 出 sdist+wheel，干净环境安装+`moodify doctor`+冒烟作业通过（CI 化）。

**需决策（LD-2）：** 在 pip/PyPI 之外的形态——容器 vs 单二进制（推荐与影响见 §5）。

### B. License 结构（LD-1，最重决策）

三选项的事实基础：
- **双许可**（`GPL-3.0-only OR Moodify-Commercial`）：F5 成立 ⇒ 立即可行；开源面 credibility 不损，商业面可卖闭源授权。代价：SPDX 策略与 LICENSE 文件族要改写，商业许可文本需要法律起草（AI 不代拟法律文本，只搭结构）。
- **保持 GPL-3.0-only**：零改动；商业化只能卖服务/支持/托管，不能卖闭源权利。
- **开放核心**（核心 GPL + 商业模块闭源）：需要拆分代码边界（哪些模块闭源），工程侵入最大，且与 One Core 宪法有张力。

### C. 云端 API 化与计量（LD-3）

F6/F7 的含义：异步作业 API 骨架已在，LA 节点在，缺的是**鉴权（API key）与用量账本**。MVP 计量 = key 表 + 用量账本（每日聚合 JSON，对齐 24x7 报告模式）+ 配额中间件；**计费/收款对接显式后置**（没有客户前不上计费）。范围选项见 §5 LD-3。

### D. 品牌与定价（LD-4）

F9：公共品牌已冻结，无需重新发明；商业面的命名沿用 Moodify 即可与宪法一致。**定价的真实约束是没有需求数据**——推荐先完成形态（A/B/C），定价在有渠道信号后再定；若人类希望现在定结构（per-call / 订阅 / 买断 / 私有部署费），数字由人类给出，AI 只落文档结构。

## 4. 分阶段路线图（每阶段 = 独立 commit + 既有五道门）

| 阶段 | 内容 | 依赖 | 可否立即开工 |
|---|---|---|---|
| D-0 工程前置 | D-ENG-1/2/3（版本统一、doctor、构建验证） | 无 | **能** |
| D-1 License 落地 | LICENSE/NOTICE/SPDX 策略按 LD-1 裁决改写；商业许可**结构**占位（法律文本由人类/法律顾问定稿） | LD-1 | 裁决后 |
| D-2 打包发布 | PyPI（公开或私有渠道）+ 容器镜像（按 LD-2）；发布渠道即分发宪法 | LD-1, LD-2 | 裁决后 |
| D-3 云端计量 MVP | API key + 用量账本 + 配额（范围按 LD-3）；LA 节点部署 | LD-3 | 裁决后 |
| D-4 定价与品牌 | 定价结构文档 + 商业页面对齐品牌宪法 | LD-4, D-2 | 裁决后 |

## 5. HUMAN_DECISION_REQUIRED

| # | 决策 | 选项 | 推荐 | 影响 |
|---|---|---|---|---|
| LD-1 | License 结构 | (a) 双许可 GPL-3.0 OR 商业；(b) 保持 GPL-3.0-only；(c) 开放核心 | **(a) 双许可**——F5 使其立即可行，开闭两面都通；商业许可文本法律起草外包 | LICENSE 族/SPDX 策略/未来贡献条款 |
| LD-2 | pip 之外的分发形态 | (a) 容器镜像；(b) 单二进制；(c) 两者；(d) 仅 pip | **(a) 容器**——ffmpeg 外部依赖使单二进制成伪命题；容器同时服务云端与私有部署 | D-2 范围；agent 用户主要走 pip，容器服务服务器侧 |
| LD-3 | 云端 API 计量范围 | (a) MVP：API key+用量账本+配额（LA 节点，无计费）；(b) 私有部署交付，暂不上云；(c) 完整计量+计费 | **(a) MVP**——没有客户前不建计费；私有部署是 (a) 的子集形态 | D-3 是否开工 |
| LD-4 | 定价时点与结构 | (a) 延后：先形态后定价；(b) 现在定 per-call；(c) 现在定订阅；(d) 现在定买断/私有部署费 | **(a) 延后**——无渠道数据不定价；数字永远人类给 | D-4 是否开工 |

## 6. Canon 边界（预判，落地时按 R7 记录）

- License 结构变化 = 法律层变更：CANON_CHANGELOG 记录（预计 `CANON_CHANGE = NO`——不改产品身份/authority order，但属 R7 可见性要求的高影响变更；若人类裁决涉及对外身份表述，另评）。
- 产品身份不变：Moodify — AI-native Professional Audio Finishing System；CLI = Creator Side 权威执行面。
- 本提案不修改任何代码；D-0 起每个阶段独立提案内裁决已含（§5 即裁决清单）。

## 7. 明确不做

定价数字、收款/支付集成、市场推广、官网改版、token/链上任何动作、App 消费端商业化、对尚不存在的客户做任何承诺。

## 8. 裁决记录（2026-10-02，人类逐项裁决）

| # | 裁决 | 与推荐的差异 | 落地含义 |
|---|---|---|---|
| LD-1 | **保持 GPL-3.0-only** | 否决了双许可推荐 | LICENSE/SPDX 零改动；商业化 = 服务/支持/托管，不卖闭源授权 |
| LD-2 | **仅 pip** | 否决了容器推荐 | pip/PyPI 是唯一分发形态；云端与私有部署均用裸 Python 安装；无容器、无单二进制 |
| LD-3 | **先私有部署交付** | 否决了云 MVP 推荐 | 不上云、不建 API key/账本；交付物 = 可安装包 + 部署/安装文档 + doctor 探测 |
| LD-4 | **定价延后** | 与推荐一致 | 只落定价结构占位（计价维度候选 + 数字 HUMAN_DECISION_REQUIRED），见下 |

**定价结构占位（LD-4，数字永远人类给）：**
- 计价维度候选：per-audio-minute（分析/完成时长）、per-seat（私有部署年费，含更新与支持）、per-project（按项目打包）。
- 原则占位：GPL-3.0-only 下可售的是**服务与劳动**（部署、集成、调优、支持、托管），不是软件许可本身；定价文档落地时必须引用本条。

## 9. D-0 工程前置实施记录（2026-10-02，代码见后续 commit）

| 项 | 状态 | 证据 |
|---|---|---|
| D-ENG-1 版本统一 | ✅ pyproject `0.1.0` → `1.0.0-rc.1`，与 `release.PRODUCT_VERSION` 一致；测试钉死两者相等 | `tests/test_layer_d_packaging.py::test_package_version_matches_runtime_version` |
| D-ENG-2 doctor | ✅ `moodify doctor`：stdout 恒 JSON，python/core/判断规则版本/ffmpeg（复用运行时解析器 `_which_ffmpeg`，含 winget 路径）/8 个关键依赖可导入性+版本；诊断恒 exit 0，可用性由 `ready` 字段承载；缺失时给 `hint` | 同上 3 个 doctor 测试 |
| D-ENG-3 构建验证 | ✅ `python -m build` 出 sdist+wheel（`moodify-1.0.0rc1`）；干净 venv 安装 + `moodify --version` + `moodify doctor` 冒烟 | `artifacts/msp02_layer_d_001/`（build_dist/ + doctor_clean_install.json） |

**未做（被裁决或显式后置）：** D-1 license 落地 = 按 LD-1 为零改动（无工作）；D-2 发布渠道 = 公开 PyPI 上架是外部发布动作，须人类另行明确指令；D-3 云端计量 = 按 LD-3 关闭（改为私有部署交付路径，已由 D-0 三项 + doctor 覆盖）；D-4 = 结构占位已落 §8，等人类给数字。

---

*事实边界：§2 勘察快照为 2026-10-02 状态。F7 节点事实来自记忆与既有证据包，未做当日连通性验证——云端方向已按 LD-3 关闭，该验证仅在推翻裁决时需要。*
