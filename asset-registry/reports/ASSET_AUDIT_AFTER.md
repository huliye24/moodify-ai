# ASSET_AUDIT_AFTER — 资产审计后状态

任务：DSK-RJWC-ASSET-REGISTRY-001
日期：2026-08-09

## 注册表交付

- `/asset-registry/`：assets(17 记录) + indexes(8) + evidence(candidates) + reports(6) + policies(schema) + legacy
- 资产记录：schema 合规（asset_id pattern/必填/枚举/OWNED 证据/PRODUCTION 版本）
- 索引：6 个 Moodify core family + RJWC 类别索引 + 非资产索引
- 报告 6 份：AUDIT_BEFORE/AFTER、SUMMARY、GAPS、THIRD_PARTY_DEPENDENCIES、OWNERSHIP_UNCERTAINTIES

## 验证（AT-01~13）

| AT | 结果 |
|---|---|
| AT-01 注册表根 | ✅ asset-registry/ 机器可读记录 |
| AT-02 唯一 ID | ✅ 17/17 唯一且符合 `(MFY\|RJWC)-(CLASS)-NNNN` |
| AT-03 六类索引 | ✅ 6/6 family 覆盖（verify 自动断言） |
| AT-04 证据 | ✅ 活跃资产含 evidence_refs 或显式 UNKNOWN |
| AT-05 所有权 | ✅ OWNED 必须有证据；未知项标 UNKNOWN 不静默 OWNED |
| AT-06 第三方分离 | ✅ THIRD_PARTY_DEPENDENCIES.md + non_assets 依赖索引 |
| AT-07 运维能力分离 | ✅ non_assets.index（部署/审计/CI 环境） |
| AT-08 模型追溯 | ✅ Judge/Ranker 链接代码+策略+版本+黄金证据 |
| AT-09 数据集追溯 | ✅ 案例/偏好语料含来源/存储/控制状态 |
| AT-10 生产系统 | ✅ 控制脊/证据管线/CWC 计量/队列已登记 |
| AT-11 遗留安全 | ✅ RJWC-CIP-0002 等 LEGACY_UNVERIFIED 保留 |
| AT-12 报告 | ✅ 6 份生成 |
| AT-13 验证器 | ✅ 零 fatal schema 错误 |

## 终态

`ASSET_REGISTRY_ALIGNED_AND_VERIFIED`

## 人类决策清单（不可从证据解决）

1. RJWC-BRD-0001：Moodify 品牌/域名/商标注册状态与持有实体
2. RJWC-CIP-0002：音乐样本语料的来源授权/版权归属
3. MFY-INF-0015：云主机合同/成本归属（当前 CONTROLLED_RESOURCE）
