# DSK-MFY-ANDROID-011｜安全、权限与合规收口

**计划日期：** 2026-08-02  
**目标完成日期：** 2026-08-02  
**依赖：** ANDROID-010 ACCEPT  
**执行 Worker：** DeepSeek  
**最终 Judge：** Codex / 授权用户  
**执行时限：** 120 分钟  
**任务状态：** PLANNED

## 1. 目标

功能完整不等于可以交付。本包收口移动端的安全、权限与合规：作品是用户资产（ADR-003 案例不可变原则在移动端的对应），App 必须证明它不泄漏、不越权、不留隐患。

## 2. 当前基线

- 010 已交付本地试听与版本决策；
- 权限为开发期宽泛配置，未按最小权限收口；
- 无网络传输安全审计、无本地数据加密策略、无隐私清单；
- 作品音频与元数据以明文存于沙箱。

## 3. 允许范围

```text
apps/android/app/src/main/
apps/android/app/src/test/
apps/android/app/src/androidTest/
apps/android/docs/
apps/android/app/proguard-rules.pro
docs/tasks/deepseek/DSK-MFY-ANDROID-011/
outputs/deepseek_validation/DSK-MFY-ANDROID-011/
```

禁止：修改电脑端代码、引入付费安全库、上传数据到第三方、Git 危险操作。

## 4. 执行阶段

### Stage A｜权限最小化

- 审计 manifest 权限：仅保留功能必需的（相册/文件选择、网络）；
- 运行时权限请求遵循最佳实践（拒绝、永久拒绝、再次请求）；
- 移除 debug-only 权限（如 Internet 在 debug 变体除外需说明）。

### Stage B｜数据保护

- 网络传输强制 HTTPS（电脑端本地服务需明确说明为开发例外）；
- 本地作品数据采用加密存储（Android Keystore + EncryptedFile，若可用）；
- 沙箱外不写任何作品文件；日志不含音频内容、路径或标识符；
- 提供"清除所有本地数据"入口，删除后无残留。

### Stage C｜合规清单

- 生成隐私清单（收集什么、存哪、谁访问、保留多久）；
- 确认无广告 SDK、无分析 SDK、无第三方崩溃上报（若需则明确用途）；
- 导出清单证明：App 不读取通讯录/位置/短信等无关权限。

### Stage D｜真机验证

- 权限拒绝/永久拒绝流程在真机验证；
- 清除数据后作品库空且无残留文件；
- HTTPS 抓包验证无明文作品传输（本地电脑端例外需文档化）；
- 001-010 门禁全绿。

## 5. P0 门槛

- manifest 权限 ≤ 功能所需，无无关权限；
- 作品数据加密存储（或明确记录为已知限制并给缓解）；
- 日志不含作品内容/路径/标识符；
- 清除数据入口可用且无残留；
- 合规清单文档化；
- 前序门禁全绿；交付四件套。

## 6. 停止条件

若需支付级安全方案、需上传数据做合规测试、需改电脑端或超时，HOLD + SCOPE_CHANGE_REQUEST.md。最终状态只能是 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。
