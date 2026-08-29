# Data Location Map

| Data | Location / ownership | Uninstall |
|---|---|---|
| App binaries | Squirrel per-user install directory | remove |
| Library, playlists, favorites, history, settings, recovery, queue | Electron `userData/moodify/local-state.json` (+ `.lkg`, migration backups) | preserve |
| Local telemetry | Electron `userData/moodify/telemetry` | preserve |
| Manual diagnostics | Electron `userData/moodify/diagnostics` | preserve |
| Logs / crash reports | no durable production implementation | n/a |
| Moodify cache / cloud temp / prepared cache | none | n/a |
| Original music | external user paths | never touch |
