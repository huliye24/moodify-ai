# Corruption Recovery

Writes use canonical `.tmp` then atomic rename. Before replacement, a parseable canonical file is copied to `.lkg`; the first successful write also seeds LKG. Startup priority is valid canonical → LKG → safe defaults. A stray/truncated `.tmp` is ignored.

Session repair handles empty/missing objects, wrong numeric types, impossible position/volume, future schema, unknown Track/Playlist and malformed QueueItems. Session failure does not clear valid durable data. If canonical and LKG are both unusable, the existing safe-first-run fallback applies and logs a generic warning without audio paths.
