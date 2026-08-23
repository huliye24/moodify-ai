# MFD-008 Security Release Checklist

## Electron

- [ ] contextIsolation true
- [ ] nodeIntegration false
- [ ] sandbox enabled or documented
- [ ] webSecurity enabled
- [ ] no insecure content
- [ ] navigation controlled
- [ ] window.open controlled
- [ ] no raw ipcRenderer exposure
- [ ] no arbitrary shell execution
- [ ] no remote code loading

## Secrets

- [ ] no service key
- [ ] no DB password
- [ ] no OSS secret
- [ ] no Audiolla token
- [ ] no LALAL token
- [ ] no Cloudflare token
- [ ] no signing private key
- [ ] no signing password
- [ ] no plaintext auth token in local state

## Media

- [ ] signed URL temporary
- [ ] signed URL not persisted
- [ ] signed URL redacted in logs
- [ ] server authorization before manifest

## Update

- [ ] HTTPS
- [ ] allowlisted origin
- [ ] renderer cannot set arbitrary feed
- [ ] release channel known
- [ ] signing requirement known

## Logging

- [ ] Authorization absent
- [ ] refresh token absent
- [ ] signed URL query absent
- [ ] personal/private data minimized

Any failed critical secret/security item:

> ALPHA_NO_GO
