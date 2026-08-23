# W04 Acceptance Criteria

## A. Preflight

- [ ] W03_STATUS = PASS
- [ ] W04_GATE = PASS
- [ ] Track authority reused
- [ ] Playlist authority reused
- [ ] source resolver reused
- [ ] actual audio engine identified
- [ ] no assumed desktop stack

## B. Playback Authority

- [ ] one playback business authority
- [ ] one active current Track
- [ ] status explicit
- [ ] position explicit
- [ ] duration explicit
- [ ] volume explicit
- [ ] error explicit
- [ ] request/generation identity exists or equivalent
- [ ] UI is not business authority
- [ ] audio element/native engine is not Track authority

## C. Commands

- [ ] load
- [ ] play
- [ ] pause
- [ ] toggle
- [ ] seek
- [ ] setVolume
- [ ] previous
- [ ] next

## D. Play/Pause

- [ ] play from ready
- [ ] pause
- [ ] resume
- [ ] rapid toggle stable
- [ ] play rejection handled
- [ ] UI and engine agree

## E. Seek

- [ ] normal seek
- [ ] seek negative clamps
- [ ] seek beyond duration clamps
- [ ] duration unknown safe
- [ ] seek while loading safe
- [ ] UI updates correctly

## F. Position / Duration

- [ ] metadata load updates duration
- [ ] time updates reach UI
- [ ] track switch resets position correctly
- [ ] stale timeupdate ignored
- [ ] ended position stable

## G. Volume

- [ ] set normal volume
- [ ] clamp < 0
- [ ] clamp > max
- [ ] engine/UI sync
- [ ] no NaN
- [ ] startup value deterministic

## H. Previous / Next

- [ ] playlist previous
- [ ] playlist next
- [ ] first-track previous policy defined
- [ ] last-track next policy defined
- [ ] no context disables safely
- [ ] no Queue authority introduced

## I. Ended

- [ ] ended fires once logically
- [ ] next behavior deterministic
- [ ] final Track enters correct state
- [ ] stale ended ignored
- [ ] no random/implicit behavior

## J. Error

- [ ] unavailable source
- [ ] load failure
- [ ] decode failure or equivalent
- [ ] play rejection
- [ ] no crash
- [ ] state recoverable
- [ ] UI gets minimal understandable state
- [ ] error skip, if implemented, cannot loop forever

## K. Race Protection

- [ ] T1→T2 late events ignored
- [ ] rapid next stable
- [ ] rapid play/pause stable
- [ ] seek during load stable
- [ ] late error ignored
- [ ] playlist mutation during playback safe

## L. UI Freeze

- [ ] current Alpha direction preserved
- [ ] no homepage redesign
- [ ] previous/play/next now reflect real state
- [ ] progress minimal
- [ ] time minimal
- [ ] volume minimal
- [ ] no DSP/Ear console

## M. Tests / Evidence

- [ ] state transition tests
- [ ] source integration tests
- [ ] race tests
- [ ] error tests
- [ ] playlist-context tests
- [ ] regression tests
- [ ] evidence manifest

## PASS Rule

只有证明：

```text
Stable Playback Authority
+ Play/Pause
+ Seek
+ Volume
+ Previous/Next
+ Ended
+ Error Safety
+ Race Safety
+ UI/Engine Sync
```

才允许：

```text
W04_STATUS = PASS
W05_GATE = PASS
```
