import { app, BrowserWindow, ipcMain, shell } from 'electron'
import { spawn, ChildProcess } from 'child_process'
import path from 'path'
import fs from 'fs'
import http from 'http'
import net from 'net'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged

let sidecar: ChildProcess | null = null
let actualPort = 3001

function isPortFree(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const server = net.createServer()
    server.once('error', () => resolve(false))
    server.once('listening', () => {
      server.close()
      resolve(true)
    })
    server.listen(port, '127.0.0.1')
  })
}

async function findFreePort(start = 3001, max = 3010): Promise<number> {
  for (let port = start; port <= max; port += 1) {
    if (await isPortFree(port)) return port
  }
  return start
}

function getSidecarPath(): string {
  if (isDev) {
    return path.join(__dirname, '..', '..', 'backend', 'moodify-server.exe')
  }
  return path.join(process.resourcesPath, 'moodify-server.exe')
}

function startSidecar(port: number): void {
  const sidecarPath = getSidecarPath()
  if (!fs.existsSync(sidecarPath)) {
    console.warn(`[sidecar] backend binary not found: ${sidecarPath}`)
    return
  }

  sidecar = spawn(sidecarPath, [], {
    env: {
      ...process.env,
      SERVER_PORT: String(port),
    },
    stdio: ['ignore', 'pipe', 'pipe'],
  })

  sidecar.stdout?.on('data', (data: Buffer) => {
    console.log(`[sidecar] ${data.toString().trim()}`)
  })

  sidecar.stderr?.on('data', (data: Buffer) => {
    console.error(`[sidecar] ${data.toString().trim()}`)
  })

  sidecar.on('exit', () => {
    sidecar = null
  })
}

function stopSidecar(): void {
  if (!sidecar) return

  if (process.platform === 'win32') {
    spawn('taskkill', ['/pid', String(sidecar.pid), '/f', '/t'])
  } else {
    sidecar.kill('SIGTERM')
  }
}

function waitForSidecar(port: number): Promise<void> {
  return new Promise((resolve) => {
    let attempts = 0
    const check = () => {
      attempts += 1
      const req = http.get(`http://localhost:${port}/api/health`, (res) => {
        res.resume()
        if (res.statusCode === 200 || attempts >= 20) {
          resolve()
        } else {
          setTimeout(check, 300)
        }
      })

      req.on('error', () => {
        if (attempts >= 20) {
          resolve()
        } else {
          setTimeout(check, 300)
        }
      })

      req.setTimeout(1000, () => {
        req.destroy()
        if (attempts >= 20) {
          resolve()
        }
      })
    }
    check()
  })
}

function createWindow(): void {
  const win = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 900,
    minHeight: 620,
    title: '沐脉 Pulse',
    backgroundColor: '#101113',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  win.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http')) {
      shell.openExternal(url)
    }
    return { action: 'deny' }
  })

  if (isDev) {
    win.loadURL('http://localhost:5173')
    win.webContents.openDevTools()
  } else {
    win.loadFile(path.join(__dirname, '../dist/index.html'))
  }
}

ipcMain.on('getApiBaseUrl', (event) => {
  event.returnValue = `http://localhost:${actualPort}`
})

async function bootstrap(): Promise<void> {
  actualPort = await findFreePort()
  startSidecar(actualPort)
  if (sidecar) {
    await waitForSidecar(actualPort)
  }
  createWindow()
}

app.whenReady().then(() => bootstrap())

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', stopSidecar)
