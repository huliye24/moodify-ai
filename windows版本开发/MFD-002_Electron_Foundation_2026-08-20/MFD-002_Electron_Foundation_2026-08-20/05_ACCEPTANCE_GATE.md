# MFD-002 Acceptance Gate

## A. Foundation

- [ ] Electron app launches
- [ ] TypeScript strict enough to catch boundary errors
- [ ] React renderer loads
- [ ] Vite build works
- [ ] Forge/package path works

## B. Security

- [ ] contextIsolation true
- [ ] nodeIntegration false
- [ ] sandbox enabled or justified
- [ ] renderer cannot access `require`
- [ ] renderer cannot access `process` Node capabilities
- [ ] no raw ipcRenderer
- [ ] no server secret
- [ ] no disabled webSecurity
- [ ] external navigation controlled

## C. Structure

- [ ] main/preload/renderer separated
- [ ] shared contracts centralized
- [ ] domain placeholders minimal
- [ ] no business state machine
- [ ] no Cloud duplication
- [ ] no Ear duplication

## D. Verification

- [ ] typecheck pass
- [ ] lint pass
- [ ] tests pass
- [ ] package/build pass
- [ ] evidence captured
- [ ] limitations explicit

## E. Scope discipline

- [ ] no real Cloud
- [ ] no login
- [ ] no music playback
- [ ] no upload
- [ ] no DSP
- [ ] no WASAPI
- [ ] no product UI expansion
- [ ] no installer productization
- [ ] no update system

---

只有全部通过：

> **MFD-003 = GO**
