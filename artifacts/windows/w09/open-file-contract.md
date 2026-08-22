# Open File / Open With Contract

`extractAudioFileArgs` accepts absolute paths with the real W02 extensions only and preserves argv order, spaces, Chinese, Unicode, `&`, parentheses and duplicates. It does not split or execute strings. Directories/unsupported/overlong values are rejected or left to W02 validation.

```text
initial/second-instance argv
-> W02 LibraryService.importPaths
-> ordered stable Track IDs
-> buffered allowlisted native:openTracks
-> resolve current Library sources
-> W05 Library queue context
-> W04 play first valid Track
```

Invalid items do not prevent other valid imports. Explicit second launch activates the existing window; media commands do not.
