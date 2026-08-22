# MFD-001 Deliverable Contract

Codex 执行完成后，建议输出目录：

```text
artifacts/mfd_001/
├── 00_execution_summary.md
├── 01_repository_snapshot.md
├── 02_identity_conflict_inventory.md
├── 03_current_system_map.md
├── 04_android_reuse_map.md
├── 05_desktop_cloud_readiness.md
├── 06_product_authority_map.md
├── 07_desktop_boundary.md
├── 08_repository_strategy.md
├── 09_open_questions.md
├── 10_mfd_002_prerequisites.md
└── evidence/
    └── commands_and_paths.md
```

如仓库已有统一 artifacts 规范，可以按现有规范调整位置，但内容不得缺失。

---

# 1. `00_execution_summary.md`

必须包含：

- 输入任务；
- 执行时间；
- branch / SHA；
- 是否修改仓库；
- 修改文件；
- 未修改区域；
- 最重要的 5 个事实；
- MFD-002 是否 GO / CONDITIONAL GO / NO-GO。

---

# 2. `01_repository_snapshot.md`

只写事实。

禁止写产品营销语言。

---

# 3. `02_identity_conflict_inventory.md`

表格字段至少：

| Path | Statement | Current authority | Conflict | Action |
|---|---|---|---|---|

---

# 4. `03_current_system_map.md`

必须分：

```text
VERIFIED CURRENT
TARGET
```

不要把 target 画成 current。

---

# 5. `04_android_reuse_map.md`

使用：

| Asset / Contract | Location | Reusable | Risk | Desktop implication |
|---|---|---:|---|---|

---

# 6. `05_desktop_cloud_readiness.md`

每个客户端需要的能力标记：

| Capability | Status | Evidence | Security | MFD-003 action |
|---|---|---|---|---|

---

# 7. `06_product_authority_map.md`

明确 authority order。

建议最终层级：

```text
1. Current explicit human decision
2. Root AGENTS / current product authority
3. Current canonical architecture
4. Verified runtime / tests
5. subsystem docs
6. experimental
7. historical
```

---

# 8. `07_desktop_boundary.md`

必须有：

- owns
- consumes
- never owns
- trust boundary
- data boundary
- future extension boundary

---

# 9. `08_repository_strategy.md`

必须明确推荐：

- same repo
- separate repo
- other

并列证据。

---

# 10. `09_open_questions.md`

只留下真正需要人类决策的问题。

能由代码和事实回答的问题，不要丢给人类。

---

# 11. `10_mfd_002_prerequisites.md`

MFD-002 的入场条件。

至少：

- Desktop repository location determined；
- license determined；
- Node version policy；
- package manager policy；
- secrets model；
- API dependency boundary；
- no authority conflict；
- no accidental internal key exposure。
