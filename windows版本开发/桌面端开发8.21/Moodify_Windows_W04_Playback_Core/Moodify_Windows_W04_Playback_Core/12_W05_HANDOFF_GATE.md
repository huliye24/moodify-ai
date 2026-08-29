# W05 Handoff Gate — Queue

W05 只有在 Player 稳定后才可建立 Queue。

## Required

- [ ] W04_STATUS = PASS
- [ ] one Playback authority
- [ ] current Track stable
- [ ] Track load stable
- [ ] play/pause stable
- [ ] seek stable
- [ ] previous/next command seam stable
- [ ] ended seam stable
- [ ] error seam stable
- [ ] playlist context readable
- [ ] race protection verified
- [ ] source resolver stable
- [ ] no formal Queue authority exists yet

## W05 Will Build

```text
Queue
- current item
- up next
- play now
- play next
- append
- remove
- reorder
- clear
- playlist → queue materialization
- ended → queue advance
```

## W05 Must Reuse

```text
Track
Library
Playlist
PlaylistItem
Playback authority
Source Resolver
```

## W05 Must Not Rebuild

```text
Audio engine
current Track truth
Playlist truth
Track truth
```

## Gate

```text
W05_GATE = PASS | BLOCKED
```
