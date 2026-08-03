# DSK-MFY-PLAYER-001：全局播放体验任务包（交接单）

**状态：** 待实施
**日期：** 2026-08-03
**定位：** 在已交付的 Media3 播放（ef32c1e）之上，补齐"播放栏 + 曲目"体验，对齐主流音乐 App 播放形态。
**交接官：** Claude A

---

## 0. 目标与用户反馈

用户真机试听后反馈：**听感可以，但没有播放栏和曲目**。即：
1. 播放栏只在作品库/详情页出现，切换页面就消失——需要**全局常驻迷你播放栏**
2. 播放时缺少**曲目信息展示**（封面、曲目名、时长、处理指标）与完整播放页
3. 隐含：曲目应能**连续播放**（播放队列），而非单曲

## 1. 已扫描事实（2026-08-03，Claude A 验证）

- 播放核心已交付（commit ef32c1e）：`PlaybackManager`（ExoPlayer + token 刷新 DataSource）+ `PlaybackBar`（进度/暂停/时间）+ 详情页 A/B 对比
- `WorkLibrary` 持久化真实作品（含 artifactId/uploadId/MRS/preset）
- 后端 `/api/v1/artifacts/{id}/download` 与 `/api/v1/uploads/{id}/download` 已 live（19 API 测试绿）
- 作品库目前有 2 首真实作品（"Je te garde…"、"demo_01.wav"），demo_01 无 artifactId（旧数据）

## 2. 设计

### 2.1 PlaybackManager 扩展（队列 + 曲目元数据）

- 新增 `QueueItem(title, subtitle, path, isOriginal, preset, mrsDelta, gatePassed)`（path 为后端 API 路径）
- `playQueue(items: List<QueueItem>, startIndex: Int)`：载入队列并播放
- `next()` / `previous()`：曲目切换（处理前/后作为同曲目的两个 QueueItem 相邻，切换按钮可快速 A/B）
- `PlaybackState` 增加：`queue: List<QueueItem>`、`queueIndex: Int`、`current: QueueItem?`
- `playQueue` 里 refreshAuthHeader 保持现有 token 逻辑

### 2.2 全局迷你播放栏（MiniPlayer）

- 新组件 `ui/components/MiniPlayer.kt`：高度约 64dp 的圆角卡片（封面渐变块 + 曲目名/副标题 + 播放/暂停 + 进度细条）
- 位置：`MoodifyApp` 的 Scaffold `bottomBar` 内，NavigationBar 上方（`Column { MiniPlayer(); NavigationBar(...) }`）
- 显示条件：`PlaybackState.current != null` 且非 CWC 全屏页
- 点击 → 打开 NowPlaying 页

### 2.3 完整播放页（NowPlayingScreen）

- 新页面 `ui/screens/NowPlayingScreen.kt`（MoodifyApp 新状态 `nowPlayingOpen`）：
  - 大封面占位（渐变 + 音波图标）、曲目名（大字号）、副标题（preset · 质量门 · MRS Δ）
  - 大进度条（可拖动 seek）+ 当前/总时长
  - 控制排：上一首 / 播放暂停 / 下一首
  - **处理前/后切换**胶囊按钮（同曲目相邻项）
  - 底部"曲目列表"区：当前队列全部曲目（点击切换）
  - 顶部返回/关闭按钮

### 2.4 接线

- 作品库 WorkCard 播放 → `PlaybackManager.playQueue(全部真实作品, index)`（连续播放能力）
- 详情页 A/B 保持（也走队列路径）
- BackHandler 支持 nowPlayingOpen

## 3. 实施任务

| # | 任务 | 产出 |
|---|---|---|
| 1 | PlaybackManager 队列扩展 | playQueue/next/previous + QueueItem + state 扩展 |
| 2 | MiniPlayer 全局组件 | bottomBar 常驻，点击开播放页 |
| 3 | NowPlayingScreen 完整播放页 | 曲目/进度/控制/切换/列表 |
| 4 | 接线 + 编译 + 单测 | MoodifyApp 集成、Kotlin 编译绿 |
| 5 | 真机验证 | 全局播放栏、曲目切换、连续播放、进度 seek |

## 3.5 追加需求：首页听歌（平台曲库，用户 2026-08-03 拍板）

用户澄清："不是处理后的播放，而是在首页听歌"——Moodify 作为音乐平台，**首页（发现页）直接听歌**。

| # | 任务 | 产出 |
|---|---|---|
| 6 | 后端平台曲库 | `GET /api/v1/catalog`（扫描 `data/demo/catalog/*.wav` → song_id/title/artist/duration/preset）+ `GET /api/v1/catalog/{id}/download`（Bearer 校验）+ 测试 |
| 7 | 曲库填充 | 拷贝 2-3 首真实歌曲到 `data/demo/catalog/`（处理产物可入曲库，体现"处理完上架自家平台"） |
| 8 | 首页接真实曲库 | HomeScreen 拉 catalog，今日推荐/热门作品显示真实曲目，点击即播放（playQueue）→ 全局播放栏/播放页联动；曲库为空回退现有展示 |

## 4. 完成定义

1. 任意页面（首页/处理/我的/作品库）播放中都有底部迷你播放栏
2. 点播放栏打开完整播放页：曲目名/封面/时长/进度可拖/上一首下一首/处理前后切换/队列列表
3. 作品库点歌进入队列连续播放（自动下一首）
4. 真机全流程验证通过；core 19 API 测试保持绿

## 5. 风险与边界

- 旧作品（demo_01.wav）无 artifactId → 不出现在可播队列（UI 按钮灰态），不阻塞
- 队列为会话内状态（App 重启清空），演示语义；平台化后由 Booming 数据层接管
- CWC 全屏页期间隐藏播放栏（与现有 bottomBar 逻辑一致）
