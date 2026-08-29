const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // File selection
  selectAudioFile: () => ipcRenderer.invoke('select-audio-file'),
  selectAudioFiles: () => ipcRenderer.invoke('select-audio-files'),

  // Analysis
  analyzeAudio: (filePath) => ipcRenderer.invoke('analyze-audio', filePath),
  getReport: (taskId) => ipcRenderer.invoke('get-report', taskId),
  analyzeBatch: (filePaths) => ipcRenderer.invoke('analyze-batch', filePaths),
  getBatchReport: (batchId) => ipcRenderer.invoke('get-batch-report', batchId),

  // Health check
  checkApiHealth: () => ipcRenderer.invoke('check-api-health'),

  // Backend management
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
  restartBackend: () => ipcRenderer.invoke('restart-backend'),

  // External links
  openExternal: (url) => ipcRenderer.invoke('open-external', url)
});
