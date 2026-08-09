# ACCESS_CWC_AUDIT_AFTER — 实施后状态

任务：DSK-MFY-ACCESS-CWC-PATCH-001
日期：2026-08-09

## 新增能力

- `moodify/access/`：6 模块 + 黄金脚本
- `configs/access_policy_v1.yaml`：唯一访问/计量策略来源
- API 8 端点（注册/推荐/CWC 余额与历史/计算 estimate/admit/settle/quota）
- CLI 5 命令（register/balance/estimate/admit/referral）
- 测试 34 个 + 7/7 黄金场景 + 报告 3 份（docs/audits/DSK-MFY-ACCESS-CWC-PATCH-001/）

## 未改变

- Pairwise Judge / N 轨排名引擎原样保留（准入接入 DEFER，见 PATCH_REPORT）
- v0.1 管线、Android、runtime、cloud 无改动
- 无新增第三方依赖

## 事实边界

- 补丁 08 已删除全部 CWC 遗留 → 本补丁在 Android 侧**零文案改动**（审计证实）；CWC 新语义（计算额度）落地在 core 计量系统
- 账本余额由事务日志重放推导（append-only），损坏尾部不会静默改变总额
- 实现期发现并修正：frozen dataclass 不允许原地改字段（QuotaState 全部改为重建模式）；consume 必须同时扣减 reserved（重放语义）；服务默认策略必须 from_yaml（配置为权威）
- 限流为分钟窗口（非滑动窗口）——文档标注

## 终态判定

`ACCESS_CWC_PATCH_ALIGNED_AND_VERIFIED`（引擎准入集成、Android 注册 UI 为后续）
