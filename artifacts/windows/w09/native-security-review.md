# Native Security Review

- IPC is fixed-channel and stable-ID/enum scoped; no generic execute API.
- Open With uses Electron's argv array, `path.isAbsolute`, extension allowlist and W02 validation.
- No manual command-line whitespace splitting.
- No `cmd.exe`, PowerShell, eval, shell string concatenation or arbitrary process execution was introduced.
- Renderer never receives the native input paths; it receives Track IDs after import.
- Preload buffers early native events and filters payload values to strings.
- Logs report only requested/accepted counts, never paths or audio content.
- External URL handling remains the existing Electron policy and is unrelated to Open File.
