# Playback Persistence Seam for W08

`PlaybackService.getPlaybackSnapshot()` exposes only serializable business state:

```text
currentTrackId
positionMs
volume
context.type / context.id
status (for policy input only)
```

W08 may checkpoint on pause, Track switch, app close or a throttled interval. It must not persist engine objects, promises, callbacks, source URLs or generation. `wasPlaying` restoration remains a W08 product decision; restart should not unexpectedly emit audio. Volume can be reapplied via the existing clamped command.
