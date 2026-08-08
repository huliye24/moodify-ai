# DSK-MFY-ANDROID-002｜Moodify Android 设计系统与核心页面

**计划日期：** 2026-08-02  
**目标完成日期：** 2026-08-02  
**依赖：** ANDROID-001 ACCEPT  
**执行 Worker：** DeepSeek  
**最终 Judge：** Codex / 授权用户  
**执行时限：** 120 分钟  
**任务状态：** PLANNED

## 1. 目标

把用户提供的两张 UI 设计稿转化为可维护的 Android 设计系统和真实导航。App 是 Moodify 的统一城门：用户只看到作品、意图、任务、试听和决定，后台模块不得直接暴露为菜单。

## 2. 产品结构

统一四个主入口：

```text
首页：新建作品、连接状态、最近任务
作品：原始音频、处理版本、导出记录
任务：上传、处理、验证、下载状态
我的：连接、存储、试听与诊断设置
```

“标准处理”保留为首页主动作；“合作计划”和付费信息在首版禁用或移出主流程。处理页必须明确演示状态与真实状态，禁止用假进度冒充后台事件。

## 3. 允许范围

```text
apps/android/app/src/main/
apps/android/app/src/test/
apps/android/app/src/androidTest/
apps/android/docs/
docs/tasks/deepseek/DSK-MFY-ANDROID-002/
outputs/deepseek_validation/DSK-MFY-ANDROID-002/
```

禁止接入真实 API、支付、合作申请、云账号、手机本地 DSP、大型素材和新 UI 框架；禁止修改电脑端业务代码。

## 4. 执行阶段

### Stage A｜设计令牌

- 定义品牌色、语义色、排版、间距、圆角、阴影、图标和动效时长；
- 组件必须使用 token，不在页面散落颜色和尺寸；
- 支持字体缩放、触摸目标和系统深浅状态栏；首版可只提供亮色主题，但不能在系统暗色下不可读。

### Stage B｜状态模型与导航

- 使用单 Activity、Compose、单向数据流；
- 页面使用明确 UiState：Loading / Empty / Content / Error / Offline；
- 统一四入口，返回键和状态恢复符合 Android 习惯；
- 演示数据集中在 fake data source，不嵌入 Composable。

### Stage C｜核心页面

- 首页、作品列表、任务列表、我的；
- 标准处理入口与处理详情；
- 空状态、错误状态、离线状态、骨架加载；
- 作品详情与 A/B 页只做结构占位，真实播放留给 005。

### Stage D｜小米视觉验收

- 检查状态栏、导航栏、安全区域、滚动和键盘；
- 360–430dp 宽度无裁切；
- 字体 1.0x/1.3x 可读；
- 截取与设计稿对应的真机页面。

## 5. P0 门槛

- 四主入口一致且返回逻辑正确；
- 首页和处理页达到设计稿核心层级，无 iOS 专属外框或交互；
- 演示状态明确标记，不冒充真实处理；
- 页面无硬编码业务数据扩散；
- 字体放大、窄屏和滚动无核心内容裁切；
- Compose UI 测试覆盖导航和主要状态；
- 001 构建与真机安装门禁持续通过。

## 6. 今日规则

今日必须完成可验收范围，不得为追求像素级相似引入未经授权资产或跳过无障碍。依赖未 ACCEPT 则 HOLD，不得并入未验证代码。最终状态仅 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。

