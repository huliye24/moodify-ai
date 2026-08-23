# Playback Source Policy

Current policy remains local Library source for local Tracks and existing published BFF asset for remote catalogue Tracks. There is no verified cloud-prepared source, so W10 makes no source-selection change.

Future policy: prefer a prepared source only when READY and freshly resolved/validated; otherwise local. Load failure, expiry, offline or authorization failure must fall back to local with the same Track ID, Queue and Playlist relations. PlaybackService remains authority.
