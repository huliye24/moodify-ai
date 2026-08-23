# Audio Output Policy

PlaybackService delegates output selection to the existing ChromiumPlaybackEngine; Settings never creates audio. `SYSTEM_DEFAULT` maps to the default sink. The preferred ID is applied before recovery/source load and immediately on change.

If a persisted device is absent or `setSinkId` rejects, playback safely falls back to System Default while remembering the preference. Device change refreshes outputs and performs the same fallback; returning hardware does not force a mid-track switch. Volume is never changed by device selection.
