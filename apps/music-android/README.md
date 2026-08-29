# Moodify Music for Android

**Role:** public Android player  
**Primary action:** Play  
**Application ID:** `com.moodify.music`

The Android application is a listening surface for cloud catalogue tracks, local files, and audio shared from another app. It accepts `VIEW`, `SEND`, and `SEND_MULTIPLE` audio intents and keeps playback available through a MediaSession service.

## Product boundary

- Home and Library lead to playback.
- Local or shared audio must remain playable even when internal analysis or delivery services are unavailable.
- Ear, reconstruction decisions, measurements, evidence, and processing parameters are internal implementation details, not the public product identity.
- A processing failure must not block the source track from playing.
- Machine intervention is allowed only inside an approved, versioned scope; otherwise playback uses BYPASS or escalates explicitly.

## Current implementation

- Jetpack Compose UI
- Media3 ExoPlayer and MediaSession
- background and lock-screen playback controls
- cloud catalogue through the Moodify Music BFF
- local file picker and external audio intents
- playback-delivery client with fail-safe source playback

The Gradle project currently reports the version defined in `app/build.gradle.kts`. Release APKs and their evidence belong under `deliverables/releases/`; APK binaries are not source authority.

## Build and test

Requirements:

- JDK 17
- Android SDK matching `compileSdk`

On Windows:

```powershell
.\gradlew.bat test
.\gradlew.bat assembleDebug
```

On Unix-compatible systems:

```bash
./gradlew test
./gradlew assembleDebug
```

Relevant evidence must record the source case, playback path, observed output, failure behavior, test result, and build version. A successful emulator or unit test does not by itself prove device audio-path behavior.

## Safety

- Do not commit private audio, signing keys, service credentials, or device-local media.
- Do not claim bit-perfect or improved playback without device-path evidence.
- Android notification permission, audio focus, MediaSession, and external URI handling must fail without preventing safe source playback.
