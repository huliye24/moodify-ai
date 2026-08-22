# W07 Acceptance Criteria

## A. Preflight
- [ ] W06_STATUS = PASS
- [ ] W07_GATE = PASS
- [ ] Track/Library/Playlist/Playback/Queue use-cases reused
- [ ] actual desktop runtime identified
- [ ] native bridge boundaries understood

## B. Action Routing
- [ ] one reusable Track action surface
- [ ] no per-view duplicated business logic
- [ ] actions map to stable use-cases
- [ ] unavailable Track handled safely

## C. Double Click
- [ ] All Songs
- [ ] Search Results
- [ ] Favorites
- [ ] Recently Played
- [ ] Playlist Detail
- [ ] queue context semantics documented

## D. File Drag & Drop
- [ ] one file import
- [ ] multi-file import
- [ ] mixed valid/invalid
- [ ] duplicate
- [ ] Chinese path
- [ ] space path
- [ ] Unicode
- [ ] import uses W02 pipeline
- [ ] no shadow importer

## E. Track → Playlist Drag
- [ ] valid Playlist drop
- [ ] target highlight
- [ ] duplicate policy reused
- [ ] unavailable Track safe
- [ ] failed write safe
- [ ] no Playlist reorder corruption

## F. Multi-select
- [ ] single select
- [ ] Ctrl toggle
- [ ] Shift range
- [ ] Ctrl+A
- [ ] Escape clear
- [ ] selection by stable ID
- [ ] view-change policy explicit
- [ ] sort behavior stable

## G. Batch Actions
- [ ] add to Playlist
- [ ] add to Queue
- [ ] favorite
- [ ] unfavorite
- [ ] remove from Library
- [ ] aggregate result
- [ ] destructive confirmation
- [ ] original files untouched

## H. Context Menus
- [ ] Track
- [ ] Playlist Item
- [ ] Queue Item
- [ ] Playlist
- [ ] actions contextual and minimal
- [ ] no visual overload

## I. Keyboard
- [ ] Enter
- [ ] Space policy
- [ ] Delete/Backspace policy
- [ ] Ctrl+A
- [ ] Escape
- [ ] typing fields do not trigger player commands
- [ ] modal focus safe

## J. Explorer
- [ ] local Track reveal works or explicitly blocked
- [ ] missing source safe
- [ ] non-local source safe
- [ ] no shell string injection
- [ ] no arbitrary command execution

## K. Referential Safety
- [ ] Playlist drag only affects Playlist relation
- [ ] Queue actions only affect Queue
- [ ] Library remove does not delete file
- [ ] no authority duplication

## L. UI Freeze
- [ ] Alpha direction preserved
- [ ] no homepage redesign
- [ ] only interaction feedback added
- [ ] no DSP/Ear/cloud UI

## M. Regression
- [ ] import
- [ ] playlist
- [ ] playback
- [ ] queue
- [ ] search
- [ ] favorite/history

## PASS Rule

只有：

```text
Desktop interactions feel native
without introducing new business truth
```

才允许：

```text
W07_STATUS = PASS
W08_GATE = PASS
```
