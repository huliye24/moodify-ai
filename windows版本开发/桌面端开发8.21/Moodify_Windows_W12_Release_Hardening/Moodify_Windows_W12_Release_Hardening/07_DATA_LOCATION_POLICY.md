# Data Location Policy

W12 必须绘制真实路径图。

至少：

```text
App Binaries
Library DB
Playlist/Favorite/History
Settings
Recovery Snapshot
Queue Snapshot
Logs
Crash Reports
Cache
Cloud Temp
Prepared Source Cache
```

## Rules

- 不依赖 repository cwd
- 不写开发者 home path
- 不把 mutable user data 放不可写 app install dir
- uninstall policy 与路径对应
- upgrade 前后路径保持稳定或有 migration
- cache 可删
- durable data 不可被 cache cleanup 删除

## Original Music

用户原始音乐仍在用户自己的文件系统位置，不进入 Moodify uninstall scope。
