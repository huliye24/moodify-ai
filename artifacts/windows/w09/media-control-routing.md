# Media Control Routing

```text
MediaSession play/pause -> PlaybackService play/pause
previoustrack/nexttrack -> PlaybackService previous/next -> QueueService
seekto(seconds) -> PlaybackService.seek(milliseconds)
Tray Play/Pause/Next -> allowlisted playback command -> same renderer handlers
```

Commands operate in background without activating the window. Missing-source/no-current playback errors remain W04 typed/safe failures. Playback state projects as playing, paused or none. Renderer cleanup removes handlers and clears the system session.
