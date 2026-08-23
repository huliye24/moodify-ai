# MFD-004 Playback Engine Contract

## 1. Intent

PlaybackEngine 是 Moodify Desktop 播放行为的抽象边界。

上层不应绑定 Chromium 细节。

---

## 2. Suggested Contract

```ts
type PlaybackState =
  | 'IDLE'
  | 'LOADING'
  | 'READY'
  | 'PLAYING'
  | 'PAUSED'
  | 'ENDED'
  | 'ERROR';

type PlaybackSource = {
  playbackId: string;
  trackId: string;
  url: string;
  mimeType: string;
  durationMs: number;
  expiresAt: string;
  assetVersion: string;
};

interface PlaybackSnapshot {
  state: PlaybackState;
  positionMs: number;
  durationMs: number;
  volume: number;
  error?: PlaybackError;
}

interface PlaybackEngine {
  load(source: PlaybackSource): Promise<void>;
  play(): Promise<void>;
  pause(): Promise<void>;
  seek(positionMs: number): Promise<void>;
  stop(): Promise<void>;
  setVolume(volume: number): void;
  snapshot(): PlaybackSnapshot;
  dispose(): Promise<void>;
}
```

可根据真实代码风格调整。

---

## 3. Event Boundary

推荐事件：

```text
statechange
position
duration
ended
error
```

不要把 HTMLMediaElement Event 原封不动传播到整个应用。

---

## 4. Future Compatibility

未来 native engine 需要能够实现同一领域语义。

不要现在设计过度复杂的：

- device routing
- sample-rate negotiation
- exclusive mode
- DSP graph
- gapless scheduler

这些都不是 0.1 的 contract。
