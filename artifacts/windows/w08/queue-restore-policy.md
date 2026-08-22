# Queue Restore Policy

QueueItem stable IDs, duplicate Track entries, order, current item and valid source context are preserved. Malformed items and items referencing removed Tracks are dropped individually. An invalid current item becomes null; no random successor is selected. Unavailable-but-existing Tracks stay in Queue, allowing identity display and later navigation. Restore never starts playback.
