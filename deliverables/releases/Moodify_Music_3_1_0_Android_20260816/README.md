# Moodify Music 3.1.0 for Android

This release completes the local-file handoff flow used by QQ and similar apps:

`QQ file preview -> Open with -> Moodify -> play the handed-off file`

## Behavior

- Accepts the temporary `content://` file permission supplied by QQ.
- Reads audio URIs from Intent data, `EXTRA_STREAM`, or `ClipData` because sender implementations differ.
- Does not require the Moodify cloud catalogue before showing or playing the local file.
- Displays the handed-off file's actual display name on the existing Moodify player screen.
- Preserves sender order when multiple audio files are handed off; vertical swipe changes tracks as before.
- A cloud catalogue refresh cannot replace the active local queue.

## Compatibility

- Package: `com.moodify.app`
- Version: `3.1.0` (`versionCode 31`)
- Minimum Android: 8.0 (API 26)
- Same signing identity as Moodify 2.0/3.0 for direct upgrade.
- Launcher icon and visual design unchanged.

## Verification

- `testDebugUnitTest`: passed.
- `assembleDebug`: passed.
- APK SHA-256: `60acfcfac9a73c3ef74932dd4d1855d1246f8b169b0e4d66c1e2daf323874337`.

Final QQ validation requires opening a QQ-hosted audio file on the physical phone because QQ's content provider is not present on the build machine.
