# W02 UI Interaction Contract

本包继续冻结 Windows Alpha 视觉方向。

```text
VISUAL_REDESIGN = FORBIDDEN
```

## 允许的最小变化

### Add Songs

继续复用当前：

- 顶部 `+ 添加歌曲`
- Empty State `选择本地歌曲`

这两个入口必须汇聚到同一 import use case，不允许维护两套导入逻辑。

### Library View

如果已有“全部歌曲”或等价页面：

> 修复现有页面。

如果完全不存在而 W02 无法验证 Library：

> 新增一个极简 secondary view。

最小信息：

```text
Title
Artist
Availability
Play
Context actions
```

不要增加工程信息。

### Track Context Menu

W02 允许：

```text
播放
────────
从音乐库移除
在资源管理器中显示（如现有 native bridge 安全支持）
```

“添加到歌单”属于 W03。

### Missing Source

最小状态：

```text
无法找到本地文件
```

可禁用播放动作。

W02 不强制做完整 relink UI。

## 禁止

- 首页重做
- 新封面系统
- 搜索大改
- 多列复杂表格
- 侧栏扩张成产品目录
- Ear / stem / AI status
- cloud processing status
