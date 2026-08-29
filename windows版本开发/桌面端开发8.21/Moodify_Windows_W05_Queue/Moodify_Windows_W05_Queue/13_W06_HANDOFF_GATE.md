# W06 Handoff Gate — Library Experience

W06 将改善“找音乐、管理音乐”的体验。

## Required

- [ ] W05_STATUS = PASS
- [ ] Track authority stable
- [ ] Library authority stable
- [ ] Playlist authority stable
- [ ] Playback authority stable
- [ ] Queue authority stable
- [ ] Playlist → Queue policy stable
- [ ] Library → Queue behavior stable
- [ ] Queue mutation does not mutate Playlist
- [ ] ended/error Queue integration stable
- [ ] current Queue item stable

## W06 Will Build

```text
All Songs
Recently Added
Recently Played
Favorites
Search
Sort
Basic metadata browsing
```

注意：

Favorites / History 在 W06 进入用户体验层，但必须基于现有 Track authority。

## W06 Must Not Rebuild

```text
Track
Library
Playlist
Playback
Queue
```

## Gate

```text
W06_GATE = PASS | BLOCKED
```
