# Crash Test Report

Automated approximations:

- canonical checkpoint then restart: PASS;
- interrupted write represented by truncated `.tmp`: canonical retained, PASS;
- truncated canonical after an LKG checkpoint: Library restored from LKG, PASS;
- renderer/process restart represented by new service/store instances: snapshot restored, PASS;
- malformed Queue item and missing Track: only invalid item dropped, PASS;
- source missing: Track identity/Queue retained and playback ERROR without audio, PASS;
- removed monitor/off-screen coordinates: window centered/clamped, PASS.

No destructive process kill was issued because user-running Moodify processes were left untouched. The persistence failure modes are exercised directly at the file boundary.
