# Explorer Integration

`library.reveal(trackId)` accepts only a stable Track ID. Main resolves it through `LibraryService.resolveFilePath`; only an available local file reaches Electron `shell.showItemInFolder`. Missing, unavailable, unknown and non-local sources return false. There is no shell command string, arbitrary path parameter or renderer filesystem authority.
