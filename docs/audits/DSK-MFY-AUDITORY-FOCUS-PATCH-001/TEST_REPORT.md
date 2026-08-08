# TEST_REPORT — 减法改造测试结果

任务：DSK-MFY-AUDITORY-FOCUS-PATCH-001
日期：2026-08-08

## 1. 命令与结果

| 命令 | 结果 |
|---|---|
| `./gradlew :app:testDebugUnitTest` | ✅ 41 passed（46 − CwcRepositoryTest 5） |
| `./gradlew :app:assembleDebug` | ✅ BUILD SUCCESSFUL |
| `scan_legacy_concepts.py apps/android`（before） | 85 命中 |
| `scan_legacy_concepts.py apps/android`（after） | 45 命中（全 token 认证假阳性 + 2 函数名） |
| `scan_legacy_concepts.py moodify-core-package`（before/after） | 58 命中（零真实遗留，无需改动） |
| `verify_strategy_alignment.py moodify-core-package` | core 六概念全 true；legacy_active 全假阳性（配对 token） |

## 2. 覆盖测试

- **StringKeyParityTest**（3 用例）：6 文件 key 集一致 + snapshot 子集 + snapshot 值一致 ✅
- **LocaleKitTest / LocaleStoreFormatTest / MoodifyApiClientTest / MiniPlayerGestureLogicTest**：不受影响全绿
- **CwcRepositoryTest**：随 CWC 删除（5 例移除）
- instrumented LanguageSwitchTest：CWC seeding 移除，断言不含 CWC 字符串，无需重跑（构建通过）

## 3. 已知残余

- CollaborationHubScreen 函数名 "Marketplace"（DEFER 项，非 UI 文案）
- core 包 verify 脚本的 pair-token 假阳性（v1.py 认证，已人工核验）
