# Settings Authority

`SettingsService` over `LocalStateStore.settings` is the only Settings authority. Renderer state is a view of this persisted object and updates only through allowlisted IPC. Settings contains preferences only: output device, restore-volume, fixed no-autoplay policy, Close behavior and fixed startup-off seam.

Track, Library, Playlist, Queue, Playback session, Recovery, cloud records, selections and UI objects do not enter Settings. No localStorage/settings.json duplicate was created.
