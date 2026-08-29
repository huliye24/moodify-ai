# Moodify Music 3.0.0 for Android

Moodify 3.0 extends the 2.0 player so existing and older songs can enter Moodify directly from Android's “Open with” and sharing flows, supporting the product direction: preserve the song's identity while giving it a new listening experience.

## Install

- APK: `Moodify_Music_3.0.0_Android_20260816.apk`
- Package: `com.moodify.app`
- Version: `3.0.0` (`versionCode 30`)
- Minimum Android: 8.0 (API 26)
- Signing: same Android debug certificate as Moodify 2.0, so the installed 2.0 build can be upgraded directly.

## Added in 3.0

- Moodify appears as a candidate for audio files opened from QQ, WeChat, file managers, and compatible apps.
- Supports Android `VIEW`, `SEND`, and `SEND_MULTIPLE` handoff for `audio/*` and Ogg audio.
- The first handed-off song is loaded as the active single-song queue and starts playing in the existing Moodify player.
- The existing player surface displays the handed-off file's own name instead of a cloud catalogue title.
- A background catalogue refresh cannot replace an external song while it is playing.
- Repeated handoff reuses the existing activity and replaces the active queue without duplicating the UI.

## Explicitly unchanged

- Desktop/launcher icon and round icon.
- Existing 2.0 Compose UI, navigation, typography, colors, launch screen, and controls.
- Package/application identity and signing certificate.
- Cloud catalogue and existing streaming behavior.

Android and OEM resolver ranking is adaptive. The manifest gives Moodify a direct, specific audio match, but Android does not provide an API for an app to force itself permanently to the first position. Selecting Moodify repeatedly or setting it as the default can move it forward according to the device's resolver behavior.

## Verification

- `testDebugUnitTest`: passed.
- `assembleDebug`: passed.
- APK manifest inspected: package/version and all three audio intents present.
- 2.0 and 3.0 signer SHA-256: `721bd3ca7b6f852205eb0c866fb2e2e4d6af3d2ef39cffdb85db7e986160c38c`.
- UI and launcher resource directories have no source diff from the 2.0 release commit.

Physical-device QQ/WeChat resolver visibility still requires installation on the target phone and one manual handoff check because those apps and OEM resolvers vary.
