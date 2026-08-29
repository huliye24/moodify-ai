/**
 * Backend Manager for Moodify QA Desktop
 *
 * Manages the Python FastAPI backend process:
 * - Detect if backend is running
 * - Start backend as child process
 * - Monitor backend health
 * - Graceful shutdown on app exit
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const axios = require('axios');

// Configuration
const API_HOST = '127.0.0.1';  // Use IPv4 explicitly
const API_PORT = 8000;
const API_URL = `http://${API_HOST}:${API_PORT}`;
const HEALTH_CHECK_INTERVAL = 3000; // 3 seconds
const STARTUP_TIMEOUT = 30000; // 30 seconds

class BackendManager {
  constructor() {
    this.backendProcess = null;
    this.isRunning = false;
    this.startupPromise = null;
    this.healthCheckTimer = null;
  }

  /**
   * Check if backend API is responding
   */
  async checkHealth() {
    try {
      const response = await axios.get(`${API_URL}/health`, {
        timeout: 3000
      });
      return response.data && response.data.status === 'healthy';
    } catch (error) {
      return false;
    }
  }

  /**
   * Start the backend API
   */
  async start() {
    // Already running
    if (this.isRunning && this.backendProcess) {
      const healthy = await this.checkHealth();
      if (healthy) {
        console.log('[BackendManager] Backend already running and healthy');
        return { success: true, alreadyRunning: true };
      }
    }

    // Already starting
    if (this.startupPromise) {
      console.log('[BackendManager] Backend startup already in progress');
      return this.startupPromise;
    }

    this.startupPromise = this._doStart();
    return this.startupPromise;
  }

  /**
   * Internal start implementation
   */
  async _doStart() {
    try {
      console.log('[BackendManager] Starting backend...');

      // Find Python executable
      const pythonCommand = await this._findPython();
      console.log(`[BackendManager] Using Python: ${pythonCommand}`);

      // Find backend entry point
      const backendPath = this._findBackendPath();
      console.log(`[BackendManager] Backend path: ${backendPath}`);

      if (!fs.existsSync(backendPath)) {
        throw new Error(`Backend not found at: ${backendPath}`);
      }

      // Set environment variables
      const env = {
        ...process.env,
        PYTHONUNBUFFERED: '1',
        MOODIFY_QA_HOST: API_HOST,
        MOODIFY_QA_PORT: API_PORT.toString(),
        MOODIFY_QA_DATA_DIR: path.join(process.resourcesPath || __dirname, '..', 'data')
      };

      // Spawn backend process
      this.backendProcess = spawn(pythonCommand, [
        '-m', 'uvicorn', 'api.main:app',
        '--host', API_HOST,
        '--port', API_PORT.toString(),
        '--log-level', 'info'
      ], {
        cwd: backendPath,
        env: env,
        stdio: ['ignore', 'pipe', 'pipe'],
        detached: false  // Kill when parent dies
      });

      // Log backend output
      this.backendProcess.stdout.on('data', (data) => {
        console.log(`[Backend] ${data.toString().trim()}`);
      });

      this.backendProcess.stderr.on('data', (data) => {
        console.error(`[Backend Error] ${data.toString().trim()}`);
      });

      // Handle process exit
      this.backendProcess.on('exit', (code) => {
        console.log(`[BackendManager] Backend exited with code ${code}`);
        this.isRunning = false;
        this.backendProcess = null;
      });

      this.backendProcess.on('error', (error) => {
        console.error('[BackendManager] Backend process error:', error);
        this.isRunning = false;
        this.backendProcess = null;
      });

      // Wait for backend to be ready
      console.log('[BackendManager] Waiting for backend to be ready...');
      const started = await this._waitForStartup();

      if (!started) {
        this._killBackend();
        throw new Error('Backend failed to start within timeout');
      }

      this.isRunning = true;
      console.log('[BackendManager] Backend started successfully');

      // Start health check
      this._startHealthCheck();

      return { success: true, alreadyRunning: false };

    } catch (error) {
      console.error('[BackendManager] Failed to start backend:', error);
      this.startupPromise = null;
      throw error;
    }
  }

  /**
   * Wait for backend to be ready
   */
  async _waitForStartup() {
    const startTime = Date.now();

    while (Date.now() - startTime < STARTUP_TIMEOUT) {
      const healthy = await this.checkHealth();
      if (healthy) {
        return true;
      }
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    return false;
  }

  /**
   * Find Python executable
   */
  async _findPython() {
    const candidates = [
      'python3',
      'python',
      'py',
      '/usr/bin/python3',
      '/usr/local/bin/python3',
      path.join(process.env.USERPROFILE || '', 'AppData', 'Local', 'Programs', 'Python', 'Python311', 'python.exe'),
      path.join(process.env.USERPROFILE || '', 'AppData', 'Local', 'Programs', 'Python', 'Python310', 'python.exe'),
      'C:\\Python311\\python.exe',
      'C:\\Python310\\python.exe',
    ];

    for (const cmd of candidates) {
      try {
        const { spawnSync } = require('child_process');
        const result = spawnSync(cmd, ['--version'], { encoding: 'utf8' });
        if (result.status === 0) {
          return cmd;
        }
      } catch (e) {
        // Continue to next candidate
      }
    }

    // Fallback to python3
    return 'python3';
  }

  /**
   * Find backend code path
   */
  _findBackendPath() {
    // In development
    const devPath = path.join(__dirname, '..', '..', '..', 'moodify-qa');
    if (fs.existsSync(path.join(devPath, 'api', 'main.py'))) {
      return devPath;
    }

    // In production (packaged)
    const prodPath = path.join(process.resourcesPath || __dirname, 'backend');
    if (fs.existsSync(path.join(prodPath, 'api', 'main.py'))) {
      return prodPath;
    }

    // Relative to app
    const relativePath = path.join(__dirname, '..', 'backend');
    if (fs.existsSync(path.join(relativePath, 'api', 'main.py'))) {
      return relativePath;
    }

    throw new Error('Cannot find Moodify QA backend. Please ensure moodify-qa is installed.');
  }

  /**
   * Start health check timer
   */
  _startHealthCheck() {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
    }

    this.healthCheckTimer = setInterval(async () => {
      const healthy = await this.checkHealth();
      if (!healthy && this.isRunning) {
        console.warn('[BackendManager] Backend health check failed');
        // Could restart backend here
      }
    }, HEALTH_CHECK_INTERVAL);
  }

  /**
   * Stop the backend
   */
  async stop() {
    console.log('[BackendManager] Stopping backend...');

    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = null;
    }

    this._killBackend();
    this.isRunning = false;
    console.log('[BackendManager] Backend stopped');
  }

  /**
   * Kill backend process
   */
  _killBackend() {
    if (this.backendProcess) {
      try {
        // Try graceful shutdown first
        if (process.platform === 'win32') {
          spawn('taskkill', ['/pid', this.backendProcess.pid, '/f', '/t']);
        } else {
          this.backendProcess.kill('SIGTERM');

          // Force kill after 5 seconds
          setTimeout(() => {
            if (this.backendProcess && !this.backendProcess.killed) {
              this.backendProcess.kill('SIGKILL');
            }
          }, 5000);
        }
      } catch (error) {
        console.error('[BackendManager] Error killing backend:', error);
      }
      this.backendProcess = null;
    }
  }

  /**
   * Get API base URL
   */
  getApiUrl() {
    return `${API_URL}/api/v1`;
  }

  /**
   * Get health check URL
   */
  getHealthUrl() {
    return `${API_URL}/health`;
  }
}

// Export singleton
module.exports = new BackendManager();
