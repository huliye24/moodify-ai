# Offline Regression

Architecture/code evidence: Library, Playlist, local Playback, Queue, Settings and Recovery depend on LocalState and local files, not cloud bootstrap. Cloud catalogue failures are caught and do not block startup. Unit tests pass. A packaged network-disabled manual run remains outstanding, so `OFFLINE = CODE_VERIFIED / MANUAL_PENDING`.
