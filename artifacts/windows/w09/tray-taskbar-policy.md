# Tray / Taskbar Policy

Electron Tray is limited to Open Moodify, Play/Pause, Next and Quit. Playback reports update the Play/Pause label. Tray Open activates the primary window; media actions do not. Tray Quit calls `app.quit`, then W08 `before-quit` flush and native teardown destroy the icon.

Close now follows W09 default product semantics: closing the final Windows window quits rather than silently hiding to tray. Taskbar work remains app identity/icon and normal minimize/restore; no decorative progress integration was added.
