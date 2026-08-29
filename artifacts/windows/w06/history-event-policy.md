# History Event Policy

W06 uses policy A: engine-confirmed Playback Started. The renderer subscribes to the authoritative Playback snapshot and records only when status becomes `PLAYING` with a local Library Track ID. Playback `generation` is the deduplication key, so duplicate state notifications and pause/resume within one load do not duplicate history.

Resolve/load/play errors never reach the writer. Automatic Queue advance creates a new generation and records only after the next item actually reaches PLAYING. An immediate pause after confirmed PLAYING remains a valid event under policy A.
