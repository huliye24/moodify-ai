# Windows Native Integration Invariants

1. Windows 是 adapter，不是 authority。
2. Playback authority 永远属于 W04。
3. Queue sequencing 永远属于 W05。
4. Track metadata 永远来自 W02 Track authority。
5. Single Instance 是共享持久化安全要求。
6. Open With 必须复用 W02 Import。
7. 文件关联必须尊重用户默认应用选择。
8. Native Bridge 保持最小权限。
9. 禁止 shell injection。
10. Background media key 不应抢焦点。
11. second launch / Open With / tray open 才可主动激活窗口。
12. Quit 必须先服从 W08 recovery flush。
13. W09 不强制修改 Close→Tray。
14. 没有可靠 artwork 时，不为系统媒体面板另造封面系统。
15. 不为 Windows 集成修改 Moodify Canon 或公开产品身份。
