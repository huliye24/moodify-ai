# Moodify Windows W05 Implementation Report

## 1. Status

```text
W05_STATUS =
W06_GATE =
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```

## 2. W04 Preflight

- W04 status:
- W05 gate:
- Playback authority:
- ended seam:
- error seam:
- Playlist order source:

## 3. Existing Queue Reality

## 4. Queue Authority

- source of truth:
- current item:
- ordering:
- writers:
- readers:

## 5. QueueItem Contract

## 6. Queue Source Policy

```text
PLAYLIST = SNAPSHOT | LIVE
LIBRARY =
```

## 7. Materialization

## 8. Play Now

## 9. Play Next

### insertion order policy
### duplicate policy

## 10. Append

## 11. Previous / Next

## 12. Ended Integration

## 13. Error Integration

## 14. Remove Policy

## 15. Reorder Policy

## 16. Clear Policy

## 17. Referential Safety

- Playlist:
- Library:
- Track:
- original files:

## 18. UI Integration

## 19. Persistence Seam

## 20. Tests

### Domain
### Integration
### Race
### Referential
### Regression

## 21. Changed Files

## 22. Evidence

## 23. Blockers / Unknowns

## 24. W06 Handoff

### Stable Queue APIs
### Stable Track/Playlist/Playback authorities
### Library ordering assumptions
### UI seams
### What W06 may extend
### What W06 must not duplicate
