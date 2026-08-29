# Ended and Error Integration

Ended advancement now belongs to PlaybackService + QueueService, not renderer UI. Playback generation permits one logical ended per active load; duplicate or stale events are ignored. If a successor exists it loads/autoplays; otherwise final Track remains ENDED/current.

Typed playback errors attempt bounded Queue advance. QueueItem IDs are tracked and at most three consecutive error advances are allowed. A successful play resets the visited/bound. If no successor exists, ERROR and the Queue snapshot remain inspectable. No recommendation or random Track is invented.
