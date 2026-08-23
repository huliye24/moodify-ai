# Missing Source Behavior

Every Library list/source resolution refresh checks that the stored locator is a readable regular file.

```text
normal file -> AVAILABLE -> resolvable moodify-local:// source
rename/move/delete/unreadable -> UNAVAILABLE -> Track remains -> resolver returns null
```

The renderer disables unavailable tracks and displays `无法找到本地文件`. Retry refreshes availability. No source failure deletes a Track or playlist data. Relink UX is intentionally deferred, but `source_ref` and stable Track identity provide the repair seam.

Automated tests cover deletion and safe resolution. Rename/move have the same filesystem-observable transition. A deterministic permission-denied test is not portable under the current Windows Administrator account; runtime handling uses the same read-access failure path and is recorded as not manually reproduced.
