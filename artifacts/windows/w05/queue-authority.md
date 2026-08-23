# Queue Authority

`QueueService` is the single session sequencing authority. It owns ordered QueueItems, explicit `current_item_id`, source context and update timestamp. PlaybackService owns resolved playback sources and consumes Queue decisions; it does not decide session order independently.

Queue is renderer-session memory only in W05. It is not stored in LocalState, so W08 remains the sole future recovery authority.
