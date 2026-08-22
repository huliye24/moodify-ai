import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  apiBaseUrl: ipcRenderer.sendSync('getApiBaseUrl'),
  platform: process.platform,
})
