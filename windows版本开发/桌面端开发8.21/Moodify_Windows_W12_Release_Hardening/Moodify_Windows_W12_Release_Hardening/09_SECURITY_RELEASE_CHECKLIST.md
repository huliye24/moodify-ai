# Security Release Checklist

- [ ] no service-key/admin key in packaged client
- [ ] no DB credentials
- [ ] no third-party provider secret
- [ ] no generic native execute IPC
- [ ] no unsafe shell concatenation
- [ ] second-instance payload validated
- [ ] Open With paths validated
- [ ] signed URLs not logged
- [ ] production source maps reviewed
- [ ] installer privilege reviewed
- [ ] writable executable path risk reviewed
- [ ] temp file permissions reviewed
- [ ] update seam requires integrity verification
- [ ] cloud endpoint/config production-safe
- [ ] logs privacy-reviewed
- [ ] uninstall does not delete original files

任一 P0 安全问题：

```text
RELEASE_BLOCKED
```
