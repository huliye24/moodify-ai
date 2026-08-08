# Moodify CWC 创作者通行证任务包

## 一、产品定义

将 CWC 作为 Moodify 的创作者邀请与首次入驻凭证。

- 中文名称：创作者通行证
- 英文缩写：CWC
- 对用户的解释：一份由创作者、品牌或机构赠送的入驻礼物与通行凭证
- 它不是永久登录密码，也不是普通公开邀请码
- 一个 CWC 只能被一个新创作者成功激活一次
- 已激活账户后续正常登录，不重复输入 CWC
- 所有邀请码统一格式：`CWC-XZ7M-42KP`
- 参考图出现的 `CWP-XZ7M-42KP` 是设计稿笔误，代码和界面必须改为 `CWC-XZ7M-42KP`

## 二、页面删减结论

六张参考图不要原样实现成六个独立页面。合并为四个页面：

1. `CwcIntroScreen`：什么是 CWC
2. `CwcAuthScreen`：登录/入驻合并页，包含 CWC 输入和已激活快捷登录两种状态
3. `CwcGiftScreen`：接受别人赠送的通行证
4. `CwcCenterScreen`：自己的通行证与分享中心

删除的重复内容：

- “登录”和“登录/入驻”合并，不做两套账号输入页面。
- “分享创作者通行证”和“创作者通行证”合并为通行证中心。
- 权益说明不在每页重复大段展示；激活页只展示 3 个核心权益，详细说明放在 Intro。

## 三、完整用户路径

### 新用户

`启动/登录 → CwcAuthScreen（入驻状态）→ 输入手机或邮箱、密码、CWC → 验证成功 → 创建账户 → 进入处理中心`

### 已激活用户

`启动/登录 → CwcAuthScreen（登录状态）→ 快捷账户或手机号密码 → 进入首页`

页面显示“已完成 CWC 激活，无需再次输入”。

### 接受好友赠送

`CWC 分享链接/二维码 → CwcGiftScreen → 接受并开始入驻 → CwcAuthScreen，自动带入 CWC → 验证并创建账户`

### 已入驻创作者赠送

`我的/创作者中心 → CwcCenterScreen → 赠送一张通行证 → 系统分享面板/复制链接/保存二维码`

## 四、页面视觉与组件结构

沿用 Moodify 现有设计系统：接近白色背景、白卡片、18–24dp 圆角、极轻阴影、深海军蓝文字，紫蓝渐变按钮。不要尝试生成参考图里的复杂 3D 玻璃素材；用现有 Logo、渐变卡片、票券轮廓图标组合代替，保证 Android 性能和一致性。

### 1. CwcIntroScreen

顶部：

- 返回
- 标题“什么是 CWC”
- 右侧小型 `CWC` 盾牌标签

首屏主卡：

- Moodify 标识
- `CWC 创作者通行证`
- 副标题“一份进入 Moodify 的创作者礼物与通行凭证”
- 说明控制在 3 行内
- 右侧使用紫蓝渐变票券/徽章图标，不制作大型 3D 图

内容只保留三组：

- “你可以把它理解为”：一份礼物 / 一张通行证 / 一份权益包
- “激活后获得”：首个作品免费入驻 / 基础作品建档 / 创作者主页开启 / 标准处理优惠
- 使用步骤：收到 CWC → 验证激活 → 导入作品 → 开始成长

底部：主按钮“开始使用 CWC”，次按钮“查看 CWC 规则”。

### 2. CwcAuthScreen

使用单页面两种状态：`AuthMode.Login` 与 `AuthMode.Onboarding`。

公共顶部：返回、Moodify Logo、标题。

Onboarding 状态：

- 标题“创作者进入 Moodify 的第一步”
- 手机号/邮箱
- 密码
- CWC 通行码（必填）
- CWC 输入自动转大写并格式化，允许用户粘贴带空格或短横线的文本
- 输入框下面实时显示：未输入 / 校验中 / 有效 / 已使用 / 已过期 / 不存在
- “什么是 CWC？”进入 Intro
- 主按钮“验证 CWC 并进入”
- 次按钮“我已经有账号，继续登录”

Login 状态：

- 已激活快捷账户卡：“泫榛 · 已完成 CWC 激活”
- 手机号/邮箱、密码
- 微信快捷登录、验证码登录
- 不出现 CWC 输入框
- 主按钮“登录并继续创作”
- 次按钮“使用其他方式登录”

不要在登录页面重复展示四张权益卡，只用一行说明“账户已激活，作品库与版权档案已同步”。

### 3. CwcGiftScreen

用于分享链接落地页。

- 顶栏“接受创作者通行证”
- 赠送者信息：“泫榛 向你赠送了一张创作者通行证”
- 一张主票券卡，显示 CWC 礼物含义
- 三个权益：首作免费入驻 / 基础版权建档 / 创作者主页
- 标准处理折扣作为小标签，不占第四张大卡
- 一段来自赠送者的话，可为空
- 主按钮“接受并开始入驻”
- 次入口“查看通行说明”

接受后跳转 `CwcAuthScreen(Onboarding)` 并自动填入邀请码。邀请码在落地页默认部分遮罩，例如 `CWC-XZ7M-••••`，避免截图滥用；进入验证页后从深链参数读取完整值。

### 4. CwcCenterScreen

入口放在“我的”页面快捷功能与创作者中心，名称统一为“创作者通行证”。

页面内容：

- 标题“创作者通行证”
- 品牌说明卡：“把一个位置，留给值得被听见的人”
- 我的可赠送通行证：数量，例如 3 张
- 主按钮“赠送一张通行证”
- 分享面板：微信发送 / 复制链接 / 生成海报 / 保存二维码
- 邀请记录：已发送、已激活、已过期
- 规则入口

分享码卡显示：

- `CWC-XZ7M-42KP`
- 状态：可使用 / 已激活 / 已过期
- 赠送者：泫榛
- 到期时间

不要在主页面同时放“立即分享”和“赠送一张通行证”两个同义主按钮，只保留一个主按钮；点击后弹出分享方式 BottomSheet。

## 五、权益规则（前端演示模型）

激活 CWC 后写入账户：

```kotlin
data class CwcBenefits(
    val freeFirstWorkOnboarding: Boolean = true,
    val basicCopyrightArchive: Boolean = true,
    val creatorProfileEnabled: Boolean = true,
    val standardProcessingCouponPercent: Int = 20,
)
```

注意：参考图同时出现“8 折优惠券”“标准处理券 ×1”“额外 10GB”，存在冲突。MVP 统一采用：

- 首个作品免费入驻
- 基础版权建档
- 创作者主页开启
- 1 张标准处理 8 折券

暂不加入额外 10GB，避免权益与 Pro 云空间体系冲突。

激活成功后，免费入驻只影响入驻/建档服务，不等于免费 DSP 标准处理。文案必须区分。

## 六、状态模型

先使用本地演示 Repository，接口留好：

```kotlin
enum class CwcStatus { AVAILABLE, REDEEMED, EXPIRED, INVALID }

data class CreatorPass(
    val code: String,
    val inviterName: String,
    val expiresAt: String,
    val status: CwcStatus,
)

sealed interface CwcValidationState {
    data object Idle : CwcValidationState
    data object Loading : CwcValidationState
    data class Valid(val pass: CreatorPass) : CwcValidationState
    data class Error(val message: String) : CwcValidationState
}
```

演示校验规则：

- `CWC-XZ7M-42KP` → 可用
- `CWC-USED-0001` → 已使用
- `CWC-OLD0-0001` → 已过期
- 其他 → 不存在

不要把真实邀请码安全逻辑永久放在客户端。正式版必须由服务端原子校验并兑换，防止重复激活。

## 七、导航接入

推荐新增文件：

- `ui/screens/CwcIntroScreen.kt`
- `ui/screens/CwcAuthScreen.kt`
- `ui/screens/CwcGiftScreen.kt`
- `ui/screens/CwcCenterScreen.kt`
- `data/CwcRepository.kt`
- `model/CreatorPass.kt`

在 `MoodifyApp.kt` 增加独立状态或 sealed route：

- `cwcIntroOpen`
- `cwcAuthOpen`
- `cwcGiftOpen`
- `cwcCenterOpen`

推荐逐步把当前大量 Boolean 页面状态迁移为：

```kotlin
sealed interface AppPage {
    data object Main : AppPage
    data object CwcIntro : AppPage
    data class CwcAuth(val mode: AuthMode, val prefilledCode: String? = null) : AppPage
    data class CwcGift(val code: String) : AppPage
    data object CwcCenter : AppPage
}
```

本轮不强制重构所有旧页面，避免扩大范围。

入口：

- “我的”快捷功能新增“创作者通行证”
- 创作者中心新增 CWC 状态卡
- 未登录启动流程进入 `CwcAuthScreen`
- 深链预留：`moodify://cwc/CWC-XZ7M-42KP`

## 八、交互细节

- 验证按钮在手机号、密码或 CWC 为空时禁用。
- 校验中显示进度，不允许重复提交。
- 激活成功后显示一次轻量成功页/对话框，然后进入处理中心。
- 分享使用 Android Sharesheet；微信未安装时仍可复制链接。
- 复制邀请码或链接后显示 Snackbar。
- 二维码 MVP 可先用占位网格，不引入重量级依赖；后续再接 ZXing。
- 返回键必须保存已输入的手机号和 CWC，密码可清空。
- 所有页面可滚动，适配小米 10，内容不能被三项底栏遮挡。

## 九、视觉资源策略

参考图中的 3D CWC 卡、礼盒、玻璃徽章仅作为视觉方向，当前不要求 DeepSeek 复刻。使用以下替代：

- 紫蓝渐变圆角票券容器
- `ConfirmationNumber` / `CardGiftcard` / `VerifiedUser` Outlined 图标
- MoodifyMark + “CWC”大字
- 轻微半透明圆形与星点背景

若以后提供切好的透明 PNG，再替换占位视觉；布局不得依赖 PNG 的固定尺寸。

## 十、验收清单

- [ ] 所有地方统一写 CWC，不出现 CWP
- [ ] 新用户必须输入有效 CWC，老用户登录不重复输入
- [ ] 四个页面可完整互相跳转与返回
- [ ] Gift 深链能预填邀请码
- [ ] 有效、已用、过期、无效状态文案明确
- [ ] CWC 中心能打开 Android 分享面板并复制链接
- [ ] 权益文案统一，不出现 10GB/免费处理等冲突承诺
- [ ] 姓名统一为“泫榛”
- [ ] 底部导航仍然只有：首页 / 处理 / 我的
- [ ] Kotlin 编译成功并安装到小米 10

## 十一、执行边界

只实现 CWC 相关代码和必要接线。不要重写首页、合作计划、数据中心等现有页面。保留用户现有改动。使用 `apply_patch` 修改源码，编译错误逐项修复。

