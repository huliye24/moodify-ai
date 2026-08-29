# MFD-002 Implementation Sequence

Codex 应按以下顺序执行。

## Step 1 — Preflight

- [ ] MFD-001 gate
- [ ] repo
- [ ] branch
- [ ] clean tree
- [ ] runtime versions
- [ ] package manager
- [ ] license

## Step 2 — Bootstrap

- [ ] Electron
- [ ] TypeScript
- [ ] React
- [ ] Vite
- [ ] Forge

完成后立即跑一次空启动。

## Step 3 — Secure window

- [ ] BrowserWindow
- [ ] contextIsolation
- [ ] nodeIntegration off
- [ ] sandbox
- [ ] navigation guard
- [ ] single instance

## Step 4 — Preload bridge

- [ ] `window.moodify`
- [ ] version
- [ ] platform
- [ ] types
- [ ] no raw IPC

## Step 5 — Renderer shell

- [ ] minimal page
- [ ] error boundary
- [ ] no product UI

## Step 6 — Config / logging / errors

- [ ] config boundary
- [ ] logger
- [ ] AppError family
- [ ] safe serialization

## Step 7 — Tests

- [ ] unit
- [ ] smoke
- [ ] renderer Node isolation check

## Step 8 — Build

- [ ] typecheck
- [ ] lint
- [ ] test
- [ ] package
- [ ] Windows artifact

## Step 9 — Docs

- [ ] README
- [ ] architecture
- [ ] security
- [ ] development
- [ ] evidence

## Step 10 — Final audit

- [ ] git diff
- [ ] secret scan
- [ ] no production API
- [ ] no premature playback
- [ ] no premature UI
