# MFD-004 Real Playback Test Matrix

至少使用：

- 2 首真实 READY track
- 若资源格式不一致，尽量覆盖 2 种真实格式

---

## Basic

| Test | Expected |
|---|---|
| load track A | READY |
| play | audible + PLAYING |
| pause | PAUSED |
| resume | PLAYING |
| stop | safe |
| reload same track | no duplicate audio |

## Seek

| Test | Expected |
|---|---|
| 25% | correct position |
| 50% | correct position |
| near end | continues / ends correctly |
| repeated seek | no crash |

## Queue

| Test | Expected |
|---|---|
| A → next → B | B loaded & plays |
| B → previous → A | A loaded & plays |
| end of test queue | safe behavior |

## Volume

| Test | Expected |
|---|---|
| 1.0 → 0.5 | audible lower |
| 0.5 → 0 | mute |
| 0 → 1.0 | audible restored |

## Manifest expiry

| Test | Expected |
|---|---|
| valid manifest | load |
| expired manifest | detect |
| refresh manifest | new URL |
| replay | succeeds |

## Network

| Test | Expected |
|---|---|
| disconnect during play | no app crash |
| network restored | reload/retry possible |
| API unavailable | typed error |
| media asset unavailable | typed error |

## Human audible check

- [ ] sound is audible
- [ ] no obvious speed error
- [ ] no obvious channel loss
- [ ] no obvious truncation
- [ ] no obvious added clipping/distortion
- [ ] volume behaves normally
