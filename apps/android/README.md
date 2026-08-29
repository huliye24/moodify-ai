# Moodify Android

Native Android client for Moodify. Phase 1 establishes the installable shell, design system, unified navigation, home screen, and processing-state screen.

## Local build

```powershell
cd E:\moodify\apps\android
.\gradlew.bat :app:assembleDebug
```

The first vertical slice intentionally uses demonstration state. Real project import, FastAPI communication, background jobs, Media3 playback, and A/B version comparison are Phase 2–3 work.

