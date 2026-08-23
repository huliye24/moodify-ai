# Installer / Uninstaller Contract

## Installer

必须：
- install binaries
- install app identity/icon
- register uninstall
- optionally Start Menu shortcut
- optionally desktop shortcut if product chooses
- register file associations only if approved
- startup only when user setting/support allows

## Preferred Privilege

优先最低权限安装。

若必须 per-machine/admin：
需要 evidence 说明原因。

## Uninstaller

必须区分：

```text
App Binaries
User Data
Cache
Original Music
```

推荐默认：

```text
remove binaries
remove integration registrations
preserve user data
optionally clear cache
never touch original music
```

## Reinstall

如果用户数据被保留：
重新安装后应能正常读取或迁移。

## File Association Cleanup

卸载只移除 Moodify 自己注册的 association/progid，不破坏用户其他默认应用。

## Startup Cleanup

卸载清理 Moodify startup entry。
