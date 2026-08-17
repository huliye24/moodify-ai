# AUTHORITY ORDER — Moodify

**Canon v1.0（W01-P01, 2026-08-17）**

当指令冲突时，按以下顺序判断。低级来源可以说明「意图」，不能覆盖高级来源证明的「现实」。

1. **Current explicit human instruction**（方向、产品边界、授权）
2. **Root `AGENTS.md`**（仓库级最高认知入口）
3. **`docs/canon/*`**（本目录：身份、边界、内部系统、权威顺序、当前架构）
4. **Verified runtime evidence**（真实存在什么；见 W01-P00 Evidence Index）
5. **Canonical main behavior + tests**（已验证主链行为与测试）
6. **Current subsystem documentation**
7. **Experimental documentation**
8. **Historical / legacy documentation**

## Clarification

- 「人类指令」解决：方向、产品边界、授权。
- 「Runtime evidence」解决：真实存在什么。
- 人类可以决定 Ear 不再对外，但不能通过产品指令让未部署的服务变成「已部署」。
- 两者不能互相偷换。

## 既有权威文档的归类

| 文档 | 归类 | 说明 |
|---|---|---|
| AGENTS.md | CANONICAL（第 2 级） | 根级最高认知入口 |
| docs/canon/* | CANONICAL（第 3 级） | 本包建立 |
| docs/LEGACY_AND_EXPERIMENTAL_POLICY.md | CANONICAL（政策） | 分类政策，属 canon 体系 |
| docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md | CANONICAL（内部生产域） | 重建生产哲学；对外表述被 CURRENT_CANON 覆盖 |
| docs/REPOSITORY_STATUS.md | 状态入口（第 5-6 级之间） | 指向 canon + 事实状态，非独立权威 |
| docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md | INTERNAL | 内部系统参考 |
| docs/ASSET_MODEL.md | INTERNAL | 认知基础设施 |
| 历史任务书 / 历史补丁包 | 第 8 级 | 不能反向覆盖当前 Canon |
