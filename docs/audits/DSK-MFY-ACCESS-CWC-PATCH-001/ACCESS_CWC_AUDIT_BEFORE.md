# ACCESS_CWC_AUDIT_BEFORE — 开放注册 + 计算额度实施前审计

任务：DSK-MFY-ACCESS-CWC-PATCH-001
日期：2026-08-09

## 运行时 / 栈

- Python 3.11 + moodify-core-package（v2.0.0，canonical 身份 "The Ear of AI"）
- API：FastAPI `/api/v1`（mobile v1 错误契约：400 + error.code）
- CLI：`cli_v2/main.py`（case 子命令为主）

## 邀请门现状（Android）

- 补丁包 08（DSK-MFY-AUDITORY-FOCUS-PATCH-001）已删除 CWC 全部遗留：CwcAuthScreen/首启登录门/深链/intent-filter/87 个 i18n key
- 当前 Android 无邀请码硬门、无 CWC 钱包/平台币文案 → AT-01/03/04/10 的 Android 部分**已满足**（补丁 08 减法生效）

## 配额/队列现状（Core）

- **无** access/quota/rate-limit/concurrency 模块（grep 无命中）
- moodify_runtime 存在 queue/scheduler（PR #15 资产矿，见 pr15 RUNTIME_DUPLICATION_MAP），但未规范化为用户级计算准入
- A/B Judge（2e26fa4）与 N 轨排名（59d0b29）引擎**未接入**成本估算/余额检查/排队

## 关键事实（预检）

- 补丁 11 与补丁 08 的战略一致性：CWC 重定义为 Compute Work Credit（非金融工具）；不 reintroduce 交易中心/钱包/藏品
- `configs/` 已有 pairwise/ntrack 策略 YAML 先例；本补丁新增 `access_policy_v1.yaml` 为唯一阈值来源
- 用户级账本需新持久化：`outputs/access/`（MOODIFY_ACCESS_ROOT 可覆盖）
