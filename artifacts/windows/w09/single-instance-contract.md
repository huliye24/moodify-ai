# Single Instance Contract

`app.requestSingleInstanceLock()` permits one long-running writer. A secondary launch receives its original Electron `commandLine` array, activates/restores the primary only for that explicit invocation, hands arguments to the primary importer and exits through Electron's denied lock path. Rapid launches converge on the same primary handler.

No secondary Library/Playlist/Queue/Recovery authority is created intentionally; the lock is requested before normal ready-time service initialization.
