# Search Contract

Fields: title, artist, album. Query is trimmed, locale-lowercased, Unicode/Chinese safe and partial-matched. Empty query returns the base view. Metadata fallbacks participate safely. Search is synchronous and pure; rapid input can only replace the current React projection and cannot create or mutate Tracks.
