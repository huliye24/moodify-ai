# Native Adapter Boundary

The adapter has no business state:

- main: instance lock, argv filtering, W02 import, stable-ID renderer handoff, tray/window lifecycle;
- preload: buffered allowlisted `native:openTracks` subscription;
- renderer: Media Session commands and metadata projection into existing PlaybackService;
- shutdown: existing W08 LocalState flush, tray destruction and app exit.

It does not own Track, Queue, Playback, metadata copies or persistence.
