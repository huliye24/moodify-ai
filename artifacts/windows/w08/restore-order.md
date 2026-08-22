# Restore Order

1. Main loads/migrates LocalState, using LKG if canonical JSON is corrupt.
2. Library, Playlist, Favorite and History authorities initialize.
3. Renderer lists/refreshes Library availability.
4. RecoveryService validates Track/Playlist relations and repairs Queue.
5. Renderer resolves available Track sources through Library IPC.
6. QueueService restores stable items/order/current item.
7. PlaybackService loads current source, applies volume and clamped position without play.
8. Navigation restores or falls back to Home.
9. Main creates/clamps/restores window bounds and maximized state.
