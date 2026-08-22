# MFD-002 Security Baseline

## 必须

- [ ] contextIsolation = true
- [ ] nodeIntegration = false
- [ ] sandbox = true 或有明确不能开启的证据
- [ ] webSecurity 不关闭
- [ ] 不允许 insecure content
- [ ] 禁止 arbitrary navigation
- [ ] 禁止 arbitrary window.open
- [ ] external link 有 handler
- [ ] preload 白名单
- [ ] typed IPC
- [ ] IPC input validation
- [ ] no raw ipcRenderer exposure
- [ ] no secrets in renderer
- [ ] no server-level key in app
- [ ] no direct DB
- [ ] no remote code execution
- [ ] no runtime eval from network content

## 本地数据

MFD-002 不应保存：

- auth token
- user library
- media cache
- credentials

只允许保存非常有限的：

- window state
- development preference

如还没必要，甚至不保存。

## Electron upgrades

依赖版本应固定在一个明确、当前可维护范围。

不要使用已知 EOL 的 Electron 主版本。

## Security evidence

最终 `docs/MFD-002-EVIDENCE.md` 必须列出实际 BrowserWindow webPreferences。
