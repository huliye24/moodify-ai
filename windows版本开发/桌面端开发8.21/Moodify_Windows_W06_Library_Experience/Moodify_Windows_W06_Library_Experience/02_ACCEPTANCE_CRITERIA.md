# W06 Acceptance Criteria

## A. Preflight
- [ ] W05_STATUS = PASS
- [ ] W06_GATE = PASS
- [ ] Track/Library/Playlist/Playback/Queue authorities reused

## B. All Songs
- [ ] one projection over Library
- [ ] title / artist / album / duration / availability
- [ ] metadata fallback
- [ ] empty state
- [ ] unavailable state
- [ ] large library usable

## C. Recently Added
- [ ] stable added timestamp
- [ ] deterministic order
- [ ] restart stable
- [ ] not based on UI mount time

## D. History / Recently Played
- [ ] one History authority
- [ ] stable Track references
- [ ] meaningful-play policy explicit
- [ ] Playback-driven writes
- [ ] repeated play behavior defined
- [ ] restart persistence
- [ ] no click-only history

## E. Favorites
- [ ] Favorite relation, not Track copy
- [ ] favorite / unfavorite
- [ ] idempotent
- [ ] restart persistence
- [ ] unavailable Track safe
- [ ] Library removal interaction explicit

## F. Search
- [ ] title / artist / album
- [ ] partial match
- [ ] Unicode / Chinese
- [ ] whitespace trim
- [ ] empty query
- [ ] null metadata
- [ ] rapid typing stable

## G. Sort
- [ ] title
- [ ] artist
- [ ] recently added
- [ ] duration or documented omission
- [ ] stable tie-break
- [ ] null-safe
- [ ] search + sort combined
- [ ] does not mutate Playlist/Queue

## H. Actions
- [ ] play
- [ ] play next
- [ ] add to queue
- [ ] add to playlist
- [ ] favorite/unfavorite
- [ ] remove from library
- [ ] same use-cases reused across views

## I. UI
- [ ] current Alpha direction preserved
- [ ] no homepage redesign
- [ ] empty states minimal
- [ ] no recommendation feed
- [ ] no Ear/DSP/Evidence UI

## J. Performance
- [ ] 100 tracks checked
- [ ] 1,000 tracks checked
- [ ] 5,000 synthetic tracks checked or blocker documented
- [ ] search/sort remain usable
- [ ] no obvious unbounded rerender/memory growth

## K. Persistence
- [ ] Favorite survives restart
- [ ] History survives restart
- [ ] original files untouched
- [ ] no shadow persistence

## PASS Rule

```text
W06_STATUS = PASS
W07_GATE = PASS
```

仅当浏览、搜索、排序、收藏、最近播放都稳定成立。
