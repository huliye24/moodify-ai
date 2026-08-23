# Clean Install / Upgrade / Uninstall Test Plan

## A. Clean Install

近似干净机器/VM：

```text
install
launch
import
playlist
play
restart
uninstall
```

不得依赖：
- repo
- npm install
- Python setup
- developer env vars
- localhost dev server

## B. Upgrade

旧 build 先建立：

```text
Tracks
Playlists
Favorites
History
Settings
Queue/Recovery
CloudPreparation refs if available
```

然后安装 candidate。

对比：
- counts
- IDs
- ordering
- settings
- current state
- migration logs

## C. Uninstall / Reinstall

验证 user-data policy。

如果 preserve：
reinstall 后能继续读。

原始音频文件始终不受影响。
