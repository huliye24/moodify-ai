# Track Switch and Race Control

- PlaybackService increments an operation generation per load and ignores completion/error from superseded generations.
- ChromiumPlaybackEngine increments a load generation; superseded metadata/error/timeout listeners reject as aborted instead of overwriting the active load.
- Track-scoped stale events are filtered before state/UI delivery.
- next/previous/toggle use a serialized command chain.
- new loads reset position/error before resolution.
- Playlist reorder/removal does not mutate the active audio object; a new context is read on the next explicit playlist start.

Tests cover stale ended/error, rapid toggle, ten concurrent next commands and play rejection. Formal concurrent Queue mutation remains W05 scope.
