/**
 * Moodify desktop shell — preload bridge.
 * Exposes exactly the product flow: pick a song, run detection, read the
 * report, render its charts. No node APIs reach the renderer.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('moodify', {
  env: () => ipcRenderer.invoke('env'),
  pickAudio: () => ipcRenderer.invoke('pick-audio'),
  listArchive: () => ipcRenderer.invoke('archive:list'),
  runAnalysis: (audioPath) => ipcRenderer.invoke('analysis:run', audioPath),
  readReport: (reportPath) => ipcRenderer.invoke('report:read', reportPath),
  renderCharts: (reportPath) => ipcRenderer.invoke('charts:render', reportPath),
});
