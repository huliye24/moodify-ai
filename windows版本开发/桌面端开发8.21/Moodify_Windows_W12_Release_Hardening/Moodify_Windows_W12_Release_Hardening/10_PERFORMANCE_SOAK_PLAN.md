# Performance Regression & Soak Plan

## Baseline

至少：

```text
Cold Start
Warm Start
1000 Track Library
5000 Track Search
Playlist Open
Playback Start
Next Track
Queue Reorder
Settings Open
30 min Memory
```

## Soak

建议：

```text
2–4 hours
```

包含：

- continuous playback
- automatic next
- manual next/previous
- pause/resume
- minimize/background
- network on/off
- cloud status refresh when active

## Watch

- memory growth
- CPU runaway
- duplicate event listeners
- log flood
- stuck player
- Queue cursor drift
- source leaks
- unreleased files

## Gate

有明显 release-blocking regression：
不得 Beta。
