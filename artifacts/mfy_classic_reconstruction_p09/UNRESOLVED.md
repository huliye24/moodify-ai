# MFY-CR-P09 — Unresolved Items

| ID | Title | Severity | Category | Description | Blocked By | Suggested Resolution |
|---|---|---|---|---|---|---|
| U-09-01 | HTTP client not wired | MEDIUM | Cloud | ReconstructionClient uses stub responses; no real network calls to P08 API | Networking stack decision (OkHttp vs Ktor) | Decide networking lib, implement Retrofit/Ktor client, add interceptors for auth/retry |
| U-09-02 | Gradle build environment broken | HIGH | Tooling | native-platform.dll locked; gradlew cannot compile or test on this machine | Windows file-system state (possibly WorkBuddy sandbox holding lock) | Open project in Android Studio IDE, or reboot Windows session |
| U-09-03 | No real-device verification | LOW | Testing | P09 §39 requires at least one physical device smoke test | User directive: skip real-device testing | Schedule for RC1 verification phase |
| U-09-04 | POST_NOTIFICATIONS permission not requested at runtime | LOW | Platform | Android 13+ requires runtime request for POST_NOTIFICATIONS; manifest declares it but Activity doesn't prompt | Implementation oversight | Add ActivityCompat.requestPermissions in MainActivity.onCreate for SDK 33+ |
| U-09-05 | MediaSessionService notification has no artwork | LOW | UX | Lock-screen shows generic music icon instead of album art | Needs artwork pipeline | Wire LocalTrack.artworkUriIfAvailable to MediaSession metadata once available |
| U-09-06 | No network-loss reconstruction recovery | MEDIUM | Robustness | If network drops during upload/polling, job state may be stuck in UPLOADING/RECONSTRUCTING | Not implemented | Add connectivity observer + exponential backoff + "Retry" button in Library UI |
| U-09-07 | ReconstructionManager is not persisted | MEDIUM | Data | App restart loses all LocalTrack entries and job bindings | No Room/DataStore persistence | Add DataStore serialization of track list for v0.2 |
