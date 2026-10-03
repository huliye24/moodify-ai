// Moodify QA Desktop - Main Application

// State
let currentFile = null;
let currentTaskId = null;
let batchFiles = [];
let currentBatchId = null;

// DOM Elements
const views = {
  single: document.getElementById('singleView'),
  batch: document.getElementById('batchView'),
  history: document.getElementById('historyView')
};

const navButtons = document.querySelectorAll('.nav-btn');

// Initialize
async function init() {
  checkApiStatus();
  setupEventListeners();
  setupNavigation();

  // Check API status every 30 seconds
  setInterval(checkApiStatus, 30000);
}

// Check API Status
async function checkApiStatus() {
  const statusDot = document.getElementById('statusDot');
  const statusText = document.getElementById('statusText');

  try {
    const result = await window.electronAPI.checkApiHealth();
    if (result.success) {
      statusDot.className = 'status-dot online';
      statusText.textContent = `API Online (v${result.data.version})`;
    } else {
      statusDot.className = 'status-dot offline';
      statusText.textContent = 'API Offline';
    }
  } catch (error) {
    statusDot.className = 'status-dot offline';
    statusText.textContent = 'API Error';
  }
}

// Setup Navigation
function setupNavigation() {
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const viewName = btn.dataset.view;
      switchView(viewName);
    });
  });
}

// Switch View
function switchView(viewName) {
  // Update nav buttons
  navButtons.forEach(btn => {
    btn.classList.toggle('active', btn.dataset.view === viewName);
  });

  // Update views
  Object.keys(views).forEach(key => {
    views[key].classList.toggle('active', key === viewName);
  });
}

// Setup Event Listeners
function setupEventListeners() {
  // Single Analysis
  const uploadArea = document.getElementById('uploadArea');
  const selectFileBtn = document.getElementById('selectFileBtn');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const removeFileBtn = document.getElementById('removeFileBtn');
  const newAnalysisBtn = document.getElementById('newAnalysisBtn');
  const exportBtn = document.getElementById('exportBtn');

  // Drag and drop
  uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
  });

  uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
  });

  uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0].path);
    }
  });

  uploadArea.addEventListener('click', () => selectFile());
  selectFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    selectFile();
  });

  analyzeBtn.addEventListener('click', analyzeCurrentFile);
  removeFileBtn.addEventListener('click', removeCurrentFile);
  newAnalysisBtn.addEventListener('click', resetSingleView);
  exportBtn.addEventListener('click', exportReport);

  // Batch Analysis
  const batchUploadArea = document.getElementById('batchUploadArea');
  const selectFilesBtn = document.getElementById('selectFilesBtn');
  const clearBatchBtn = document.getElementById('clearBatchBtn');
  const analyzeBatchBtn = document.getElementById('analyzeBatchBtn');

  batchUploadArea.addEventListener('click', () => selectBatchFiles());
  selectFilesBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    selectBatchFiles();
  });
  clearBatchBtn.addEventListener('click', clearBatch);
  analyzeBatchBtn.addEventListener('click', analyzeBatch);
}

// Select File
async function selectFile() {
  const result = await window.electronAPI.selectAudioFile();
  if (result) {
    handleFileSelect(result.path, result.name, result.size);
  }
}

// Handle File Select
function handleFileSelect(path, name, size) {
  currentFile = { path, name, size };

  document.getElementById('uploadArea').style.display = 'none';
  document.getElementById('fileInfo').style.display = 'block';
  document.getElementById('resultArea').style.display = 'none';

  document.getElementById('fileName').textContent = name;
  document.getElementById('fileSize').textContent = formatFileSize(size);
}

// Remove Current File
function removeCurrentFile() {
  currentFile = null;
  document.getElementById('uploadArea').style.display = 'block';
  document.getElementById('fileInfo').style.display = 'none';
  document.getElementById('resultArea').style.display = 'none';
}

// Reset Single View
function resetSingleView() {
  removeCurrentFile();
  document.getElementById('progressArea').style.display = 'none';
}

// Analyze Current File
async function analyzeCurrentFile() {
  if (!currentFile) return;

  document.getElementById('fileInfo').style.display = 'none';
  document.getElementById('progressArea').style.display = 'block';

  const progressFill = document.getElementById('progressFill');
  const progressText = document.getElementById('progressText');

  progressFill.style.width = '30%';
  progressText.textContent = 'Uploading file...';

  try {
    const result = await window.electronAPI.analyzeAudio(currentFile.path);

    if (result.success) {
      currentTaskId = result.taskId;
      progressFill.style.width = '60%';
      progressText.textContent = 'Analyzing audio...';

      // Poll for results
      await pollForResults(result.taskId);
    } else {
      showError(result.error);
      resetSingleView();
    }
  } catch (error) {
    showError(error.message);
    resetSingleView();
  }
}

// Poll for Results
async function pollForResults(taskId) {
  const progressFill = document.getElementById('progressFill');
  const progressText = document.getElementById('progressText');

  const maxAttempts = 60;
  let attempts = 0;

  while (attempts < maxAttempts) {
    try {
      const result = await window.electronAPI.getReport(taskId);

      if (result.success) {
        const data = result.data;

        if (data.status === 'completed') {
          progressFill.style.width = '100%';
          progressText.textContent = 'Analysis complete!';
          setTimeout(() => displayResults(data), 500);
          return;
        } else if (data.status === 'failed') {
          showError('Analysis failed');
          resetSingleView();
          return;
        }
      }
    } catch (error) {
      console.error('Poll error:', error);
    }

    attempts++;
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  showError('Analysis timed out');
  resetSingleView();
}

// Display Results
function displayResults(data) {
  document.getElementById('progressArea').style.display = 'none';
  document.getElementById('resultArea').style.display = 'block';

  // Scores
  const qaScore = data.qa_score || 0;
  const technicalScore = data.technical_score || 0;
  const musicalScore = data.musical_score || 0;

  document.getElementById('qaScore').textContent = qaScore.toFixed(1);
  document.getElementById('technicalScore').textContent = technicalScore.toFixed(1);
  document.getElementById('musicalScore').textContent = musicalScore.toFixed(1);

  // Rating
  const ratingEl = document.getElementById('qaRating');
  const rating = getRating(qaScore);
  ratingEl.textContent = rating.label;
  ratingEl.className = `score-rating ${rating.class}`;

  // File Info
  const file = data.file || {};
  document.getElementById('infoDuration').textContent = `${file.duration_seconds || 0}s`;
  document.getElementById('infoSampleRate').textContent = `${file.sample_rate_hz || 0} Hz`;
  document.getElementById('infoChannels').textContent = file.channels || '-';
  document.getElementById('infoFileSize').textContent = formatFileSize(file.size_bytes || 0);

  // Breakdown
  const breakdownGrid = document.getElementById('breakdownGrid');
  breakdownGrid.innerHTML = '';

  const breakdown = data.breakdown || {};
  const technical = breakdown.technical || {};
  const musical = breakdown.musical || {};

  Object.entries(technical).forEach(([key, value]) => {
    if (key !== 'overall') {
      addBreakdownItem(breakdownGrid, key, value, 'Technical');
    }
  });

  Object.entries(musical).forEach(([key, value]) => {
    if (key !== 'overall') {
      addBreakdownItem(breakdownGrid, key, value, 'Musical');
    }
  });

  // Issues
  const issuesList = document.getElementById('issuesList');
  const issuesSection = document.getElementById('issuesSection');

  if (data.issues && data.issues.length > 0) {
    issuesSection.style.display = 'block';
    issuesList.innerHTML = '';
    data.issues.forEach(issue => addIssue(issuesList, issue));
  } else {
    issuesSection.style.display = 'none';
  }

  // Recommendations
  const recsList = document.getElementById('recommendationsList');
  const recsSection = document.getElementById('recommendationsSection');

  if (data.recommendations && data.recommendations.length > 0) {
    recsSection.style.display = 'block';
    recsList.innerHTML = '';
    data.recommendations.forEach(rec => addRecommendation(recsList, rec));
  } else {
    recsSection.style.display = 'none';
  }
}

// Add Breakdown Item
function addBreakdownItem(container, name, score, category) {
  const item = document.createElement('div');
  item.className = 'breakdown-item';
  item.innerHTML = `
    <span class="breakdown-name">${formatMetricName(name)}</span>
    <span class="breakdown-score">${score.toFixed(1)}</span>
  `;
  container.appendChild(item);
}

// Add Issue
function addIssue(container, issue) {
  const item = document.createElement('div');
  item.className = `issue-item ${issue.severity}`;

  const icon = issue.severity === 'critical' ? '!' :
               issue.severity === 'warning' ? '!' : 'i';

  item.innerHTML = `
    <span class="issue-icon">${icon}</span>
    <div class="issue-content">
      <div class="issue-title">${issue.message}</div>
      <div class="issue-meta">${issue.metric}: ${issue.value} (threshold: ${issue.threshold})</div>
    </div>
  `;
  container.appendChild(item);
}

// Add Recommendation
function addRecommendation(container, rec) {
  const item = document.createElement('div');
  item.className = 'recommendation-item';
  item.innerHTML = `
    <span class="rec-priority p${rec.priority}">${rec.priority}</span>
    <div class="rec-content">
      <h4>${rec.action}</h4>
      <p>${rec.details}</p>
    </div>
  `;
  container.appendChild(item);
}

// Get Rating
function getRating(score) {
  if (score >= 90) return { label: 'Excellent', class: 'excellent' };
  if (score >= 80) return { label: 'Good', class: 'good' };
  if (score >= 70) return { label: 'Fair', class: 'fair' };
  return { label: 'Poor', class: 'poor' };
}

// Format Metric Name
function formatMetricName(name) {
  return name
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());
}

// Format File Size
function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Show Error
function showError(message) {
  alert('Error: ' + message);
}

// Export Report
function exportReport() {
  if (!currentTaskId) return;
  // Implementation for exporting report
  alert('Export feature coming soon!');
}

// ========== Batch Analysis ==========

// Select Batch Files
async function selectBatchFiles() {
  const result = await window.electronAPI.selectAudioFiles();
  if (result && result.length > 0) {
    batchFiles = result;
    updateBatchList();
  }
}

// Update Batch List
function updateBatchList() {
  const batchUploadArea = document.getElementById('batchUploadArea');
  const batchFilesSection = document.getElementById('batchFiles');
  const batchList = document.getElementById('batchList');
  const fileCount = document.getElementById('fileCount');

  if (batchFiles.length === 0) {
    batchUploadArea.style.display = 'block';
    batchFilesSection.style.display = 'none';
    return;
  }

  batchUploadArea.style.display = 'none';
  batchFilesSection.style.display = 'block';
  fileCount.textContent = batchFiles.length;

  batchList.innerHTML = '';
  batchFiles.forEach((file, index) => {
    const item = document.createElement('div');
    item.className = 'batch-item';
    item.innerHTML = `
      <span class="batch-item-icon">&#9836;</span>
      <div class="batch-item-info">
        <div class="batch-item-name">${file.name}</div>
        <div class="batch-item-size">${formatFileSize(file.size)}</div>
      </div>
      <button class="batch-item-remove" onclick="removeBatchFile(${index})">&times;</button>
    `;
    batchList.appendChild(item);
  });
}

// Remove Batch File
function removeBatchFile(index) {
  batchFiles.splice(index, 1);
  updateBatchList();
}

// Clear Batch
function clearBatch() {
  batchFiles = [];
  updateBatchList();
  document.getElementById('batchProgress').style.display = 'none';
  document.getElementById('batchResults').style.display = 'none';
}

// Analyze Batch
async function analyzeBatch() {
  if (batchFiles.length === 0) return;

  document.getElementById('batchFiles').style.display = 'none';
  document.getElementById('batchProgress').style.display = 'block';

  const progressFill = document.getElementById('batchProgressFill');
  const completedCount = document.getElementById('completedCount');
  const totalCount = document.getElementById('totalCount');

  totalCount.textContent = batchFiles.length;

  try {
    const filePaths = batchFiles.map(f => f.path);
    const result = await window.electronAPI.analyzeBatch(filePaths);

    if (result.success) {
      currentBatchId = result.batchId;
      progressFill.style.width = '50%';

      // Poll for batch results
      await pollForBatchResults(result.batchId);
    } else {
      showError(result.error);
      updateBatchList();
    }
  } catch (error) {
    showError(error.message);
    updateBatchList();
  }
}

// Poll for Batch Results
async function pollForBatchResults(batchId) {
  const progressFill = document.getElementById('batchProgressFill');
  const completedCount = document.getElementById('completedCount');

  const maxAttempts = 120;
  let attempts = 0;

  while (attempts < maxAttempts) {
    try {
      const result = await window.electronAPI.getBatchReport(batchId);

      if (result.success) {
        const data = result.data;
        const completed = data.completed || 0;
        const total = data.total || 1;

        completedCount.textContent = completed;
        progressFill.style.width = `${(completed / total) * 100}%`;

        if (data.status === 'completed') {
          setTimeout(() => displayBatchResults(data), 500);
          return;
        }
      }
    } catch (error) {
      console.error('Batch poll error:', error);
    }

    attempts++;
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  showError('Batch analysis timed out');
  updateBatchList();
}

// Display Batch Results
function displayBatchResults(data) {
  document.getElementById('batchProgress').style.display = 'none';
  document.getElementById('batchResults').style.display = 'block';

  // Summary
  document.getElementById('batchAvgScore').textContent =
    data.average_score ? data.average_score.toFixed(1) : '-';
  document.getElementById('batchCompleted').textContent = data.completed || 0;
  document.getElementById('batchFailed').textContent = data.failed || 0;

  // Reports
  const reportsContainer = document.getElementById('batchReports');
  reportsContainer.innerHTML = '';

  if (data.reports && data.reports.length > 0) {
    data.reports.forEach(report => {
      const item = document.createElement('div');
      item.className = 'batch-item';
      const rating = getRating(report.qa_score || 0);
      item.innerHTML = `
        <span class="batch-item-icon">&#9836;</span>
        <div class="batch-item-info">
          <div class="batch-item-name">${report.file?.name || 'Unknown'}</div>
          <div class="batch-item-size">QA Score: ${(report.qa_score || 0).toFixed(1)} - ${rating.label}</div>
        </div>
      `;
      reportsContainer.appendChild(item);
    });
  }
}

// Start the app
init();
