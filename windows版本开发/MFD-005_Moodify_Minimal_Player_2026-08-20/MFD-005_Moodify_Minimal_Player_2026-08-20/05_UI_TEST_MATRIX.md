# MFD-005 UI Test Matrix

## Core states

| State | Expected |
|---|---|
| EMPTY | clear, no broken controls |
| LOADING | restrained loading feedback |
| READY | play available |
| PLAYING | pause shown |
| PAUSED | play shown |
| ENDED | correct position/state |
| ERROR | clear retry |

## Interaction

| Action | Expected |
|---|---|
| click play | plays |
| click pause | pauses |
| Space | toggle |
| Up | previous |
| Down | next |
| seek | position changes |
| volume | level changes |
| wheel if enabled | one controlled switch |

## Resize

- [ ] compact
- [ ] default
- [ ] wide
- [ ] no clipped primary control
- [ ] no useless scrollbars

## Accessibility

- [ ] focus visible
- [ ] labels
- [ ] keyboard
- [ ] sliders
- [ ] reduced motion

## Security / cleanliness

- [ ] no token
- [ ] no signed URL
- [ ] no playback_id
- [ ] no internal API
- [ ] no debug JSON
- [ ] no traceback

## Real playback

- [ ] real track A
- [ ] real track B
- [ ] next/previous
- [ ] seek
- [ ] retry after simulated error
