# W05 Acceptance Criteria

## A. Preflight
- [ ] W04_STATUS = PASS
- [ ] W05_GATE = PASS
- [ ] Playback authority reused
- [ ] current Track authority reused
- [ ] ended/error seams reused
- [ ] no second player created

## B. Queue Authority
- [ ] one Queue authority
- [ ] QueueItem has stable identity
- [ ] QueueItem references Track ID
- [ ] Queue does not clone Track truth
- [ ] current Queue item explicit
- [ ] ordering explicit
- [ ] source/origin explicit or equivalent
- [ ] Playlist remains separate authority

## C. Materialization
- [ ] Playlist → Queue
- [ ] order preserved
- [ ] selected Track can become cursor
- [ ] Library direct play has deterministic context
- [ ] snapshot/live policy documented
- [ ] Queue reorder does not modify Playlist

## D. Queue Commands
- [ ] Play Now
- [ ] Play Next
- [ ] Add to Queue / Append
- [ ] Remove
- [ ] Reorder
- [ ] Clear
- [ ] Next
- [ ] Previous

## E. Duplicate Policy
- [ ] Queue duplicate Track policy explicit
- [ ] repeated same Track behaves deterministically
- [ ] QueueItem ID disambiguates duplicates if allowed

## F. Previous / Next
- [ ] next follows Queue
- [ ] previous follows defined rule
- [ ] first item behavior defined
- [ ] final item behavior defined
- [ ] no Queue context safe
- [ ] current Track maps to current Queue item

## G. Ended / Error
- [ ] ended advances once
- [ ] stale ended ignored
- [ ] final ended state correct
- [ ] error skip cannot loop forever
- [ ] final error inspectable
- [ ] Queue remains coherent after failure

## H. Mutation Safety
- [ ] remove future item safe
- [ ] remove current item policy explicit
- [ ] reorder current item safe
- [ ] reorder future items safe
- [ ] clear policy explicit
- [ ] current audio not accidentally interrupted
- [ ] current cursor remains coherent

## I. Referential Safety
- [ ] Queue remove does not affect Playlist
- [ ] Queue reorder does not affect Playlist
- [ ] Queue clear does not affect Library
- [ ] original files untouched
- [ ] no Track deletion
- [ ] no PlaylistItem deletion

## J. UI
- [ ] current Alpha visual direction preserved
- [ ] minimal Queue surface only
- [ ] Play Next available
- [ ] Add to Queue available
- [ ] reorder available
- [ ] remove available
- [ ] clear available
- [ ] no homepage redesign

## K. Tests
- [ ] domain tests
- [ ] ended integration
- [ ] error integration
- [ ] race tests
- [ ] mutation tests
- [ ] referential tests
- [ ] regression tests
- [ ] evidence manifest

## PASS Rule

只有证明：

```text
Stable Queue Authority
+ Queue/Playback Integration
+ Play Next
+ Append
+ Reorder
+ Remove
+ Ended Advance
+ Error Safety
+ Queue/Playlist Separation
```

才允许：

```text
W05_STATUS = PASS
W06_GATE = PASS
```
