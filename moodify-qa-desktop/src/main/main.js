/**
 * Moodify QA Desktop - Main Process
 *
 * Features:
 * - Auto-start backend API on app launch
 * - Manage backend lifecycle
 * - IPC handlers for renderer
 */

const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const axios = require('axios');
const fs = require('fs');

// Import backend manager
const backendManager = require('./backend-manager');

// Keep a global reference of the window object
let mainWindow;
let backendReady = false;

// API URL (using IPv4 explicitly to avoid IPv6 issues)
const API_BASE_URL = backendManager.getApiUrl();

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, '../preload/preload.js')
    },
    titleBarStyle: 'hiddenInset',
    show: false,  // Don't show until ready
    backgroundColor: '#0f0f23'
  });

  // Load the app
  mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();

    // Open DevTools in development
    if (process.env.NODE_ENV === 'development') {
      mainWindow.webContents.openDevTools();
    }
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// App event handlers
app.whenReady().then(async () => {
  try {
    // Start backend before creating window
    console.log('[Main] Starting backend...');
    const result = await backendManager.start();

    if (result.success) {
      backendReady = true;
      console.log('[Main] Backend ready, creating window...');
      createWindow();
    } else {
      console.error('[Main] Failed to start backend');
      dialog.showErrorBox(
        'Backend Error',
        'Failed to start Moodify QA backend. Please check the logs.'
      );
      app.quit();
    }
  } catch (error) {
    console.error('[Main] Error during startup:', error);
    dialog.showErrorBox(
      'Startup Error',
      `Failed to start application: ${error.message}`
    );
    app.quit();
  }
});

app.on('window-all-closed', async () => {
  // Stop backend before quitting
  await backendManager.stop();

  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Before quit
app.on('before-quit', async (event) => {
  console.log('[Main] App quitting, stopping backend...');
  await backendManager.stop();
});

// IPC Handlers

// Select audio file
ipcMain.handle('select-audio-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      {
        name: 'Audio Files',
        extensions: ['wav', 'mp3', 'flac', 'aiff', 'ogg', 'm4a']
      },
      {
        name: 'All Files',
        extensions: ['*']
      }
    ]
  });

  if (!result.canceled && result.filePaths.length > 0) {
    const filePath = result.filePaths[0];
    const stats = fs.statSync(filePath);
    return {
      path: filePath,
      name: path.basename(filePath),
      size: stats.size
    };
  }
  return null;
});

// Select multiple audio files
ipcMain.handle('select-audio-files', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections'],
    filters: [
      {
        name: 'Audio Files',
        extensions: ['wav', 'mp3', 'flac', 'aiff', 'ogg', 'm4a']
      }
    ]
  });

  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths.map(filePath => {
      const stats = fs.statSync(filePath);
      return {
        path: filePath,
        name: path.basename(filePath),
        size: stats.size
      };
    });
  }
  return [];
});

// Analyze single audio file
ipcMain.handle('analyze-audio', async (event, filePath) => {
  try {
    const FormData = require('form-data');
    const formData = new FormData();

    formData.append('file', fs.createReadStream(filePath));

    const response = await axios.post(`${API_BASE_URL}/qa/analyze`, formData, {
      headers: formData.getHeaders(),
      timeout: 30000
    });

    return {
      success: true,
      taskId: response.data.task_id,
      status: response.data.status
    };
  } catch (error) {
    console.error('Analysis error:', error);
    return {
      success: false,
      error: error.message || 'Failed to analyze audio'
    };
  }
});

// Get analysis report
ipcMain.handle('get-report', async (event, taskId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/qa/report/${taskId}`, {
      timeout: 10000
    });

    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Get report error:', error);
    return {
      success: false,
      error: error.message || 'Failed to get report'
    };
  }
});

// Batch analyze
ipcMain.handle('analyze-batch', async (event, filePaths) => {
  try {
    const FormData = require('form-data');
    const formData = new FormData();

    filePaths.forEach(filePath => {
      formData.append('files', fs.createReadStream(filePath));
    });

    const response = await axios.post(`${API_BASE_URL}/qa/batch`, formData, {
      headers: formData.getHeaders(),
      timeout: 60000
    });

    return {
      success: true,
      batchId: response.data.batch_id,
      taskIds: response.data.task_ids,
      status: response.data.status
    };
  } catch (error) {
    console.error('Batch analysis error:', error);
    return {
      success: false,
      error: error.message || 'Failed to analyze batch'
    };
  }
});

// Get batch report
ipcMain.handle('get-batch-report', async (event, batchId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/qa/batch/${batchId}`, {
      timeout: 10000
    });

    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Get batch report error:', error);
    return {
      success: false,
      error: error.message || 'Failed to get batch report'
    };
  }
});

// Check API health
ipcMain.handle('check-api-health', async () => {
  try {
    const response = await axios.get(backendManager.getHealthUrl(), {
      timeout: 5000
    });
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    return {
      success: false,
      error: error.message || 'API not available'
    };
  }
});

// Open external link
ipcMain.handle('open-external', async (event, url) => {
  const { shell } = require('electron');
  await shell.openExternal(url);
});

// Get backend status
ipcMain.handle('get-backend-status', () => {
  return {
    isRunning: backendManager.isRunning,
    apiUrl: API_BASE_URL
  };
});

// Restart backend
ipcMain.handle('restart-backend', async () => {
  try {
    await backendManager.stop();
    const result = await backendManager.start();
    return { success: result.success };
  } catch (error) {
    return { success: false, error: error.message };
  }
});
