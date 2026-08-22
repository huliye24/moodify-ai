# Close / Tray Policy

Default is `QUIT`. When the user explicitly chooses `MINIMIZE_TO_TRAY`, the main window close event is prevented and the window hides. The existing tray Open action restores/focuses it.

Tray Quit and OS/app quit set explicit-quit state, bypass minimization, execute W08 `before-quit` flush and destroy the tray. Preference changes apply immediately through Settings IPC; no restart is required.
