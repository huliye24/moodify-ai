# Current Queue Reality

Before W05, `PlaybackService` contained `PlaybackQueue`, an array of `{trackId, source}` plus integer index. It supported set/next/previous/clear only. It had no independent item IDs, origin, Play Next, append, arbitrary selection, remove, reorder, snapshot or UI surface. Sources were duplicated into the sequence record and ended advancement lived in renderer code.

W05 repairs this path by replacing PlaybackService's sequencing dependency with one formal QueueService. The historical PlaybackQueue type remains only for older isolated tests and is no longer runtime authority.
