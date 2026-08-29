# Previous / Next Policy

- Next selects the following QueueItem and delegates source load/play to PlaybackService.
- At the final item, Next is a no-op and ended/error state remains inspectable.
- Previous seeks current Track to zero when position exceeds 3 seconds.
- At or below 3 seconds, Previous selects the preceding QueueItem.
- At the first item, Previous is a no-op.
- With no Queue/current item, both commands fail safely.

All next/previous commands remain serialized by W04's command chain.
