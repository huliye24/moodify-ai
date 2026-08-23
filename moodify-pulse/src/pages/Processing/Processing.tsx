import React, { useState } from 'react'
import { mockAssets } from '../../utils/mockData'

export function Processing() {
  const [selectedAsset] = useState(mockAssets[0])
  const [isProcessing, setIsProcessing] = useState(false)
  const [showComparison, setShowComparison] = useState(false)

  const parameters = [
    { id: 'lufs', label: 'LUFS', value: -14, min: -23, max: -6, unit: 'dB' },
    { id: 'dynamics', label: 'Dynamics', value: 85, min: 0, max: 100, unit: '%' },
    { id: 'stereo', label: 'Stereo Width', value: 0.82, min: 0, max: 1, unit: '' },
    { id: 'frequency', label: 'Frequency Balance', value: 78, min: 0, max: 100, unit: '%' },
    { id: 'mrs', label: 'MRS Target', value: 90, min: 0, max: 100, unit: '' },
  ]

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <h1 style={styles.title}>处理工作区</h1>
        <p style={styles.subtitle}>AI 驱动的音频优化</p>
      </header>

      {/* Workflow */}
      <div style={styles.workflow}>
        <div style={styles.workflowStep}>
          <div style={styles.stepIcon}>◈</div>
          <div style={styles.stepLabel}>原始音频</div>
        </div>
        <div style={styles.workflowArrow}>→</div>
        <div style={styles.workflowStep}>
          <div style={{ ...styles.stepIcon, background: 'var(--color-brand-gradient)' }}>◆</div>
          <div style={styles.stepLabel}>沐脉 AI</div>
        </div>
        <div style={styles.workflowArrow}>→</div>
        <div style={styles.workflowStep}>
          <div style={styles.stepIcon}>◇</div>
          <div style={styles.stepLabel}>优化完成</div>
        </div>
      </div>

      {/* Main Workspace */}
      <div style={styles.workspace}>
        {/* Before/After */}
        <div style={styles.comparison}>
          <div style={styles.comparisonHeader}>
            <div style={styles.comparisonTitle}>前后对比</div>
            <button
              style={styles.toggleButton}
              onClick={() => setShowComparison(!showComparison)}
            >
              {showComparison ? '隐藏' : '显示'}对比
            </button>
          </div>

          <div style={styles.waveformContainer}>
            {/* Original */}
            <div style={styles.waveformSection}>
              <div style={styles.waveformLabel}>原始</div>
              <div style={styles.waveform}>
                <WaveformVisualization color="var(--color-text-muted)" />
              </div>
              <div style={styles.waveformStats}>
                <div style={styles.stat}>
                  <span style={styles.statLabel}>LUFS:</span>
                  <span style={styles.statValue}>-12.5</span>
                </div>
                <div style={styles.stat}>
                  <span style={styles.statLabel}>MRS:</span>
                  <span style={styles.statValue}>74</span>
                </div>
              </div>
            </div>

            {/* After */}
            <div style={styles.waveformSection}>
              <div style={styles.waveformLabel}>优化后</div>
              <div style={styles.waveform}>
                <WaveformVisualization color="var(--color-brand-primary)" />
              </div>
              <div style={styles.waveformStats}>
                <div style={styles.stat}>
                  <span style={styles.statLabel}>LUFS:</span>
                  <span style={{ ...styles.statValue, color: 'var(--color-brand-primary)' }}>-14.0</span>
                </div>
                <div style={styles.stat}>
                  <span style={styles.statLabel}>MRS:</span>
                  <span style={{ ...styles.statValue, color: 'var(--color-brand-primary)' }}>92</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Parameters Panel */}
        <div style={styles.parametersPanel}>
          <h3 style={styles.panelTitle}>处理参数</h3>

          <div style={styles.parametersList}>
            {parameters.map(param => (
              <div key={param.id} style={styles.parameter}>
                <div style={styles.parameterHeader}>
                  <label style={styles.parameterLabel}>{param.label}</label>
                  <span style={styles.parameterValue}>
                    {param.value}{param.unit}
                  </span>
                </div>
                <input
                  type="range"
                  min={param.min}
                  max={param.max}
                  value={param.value}
                  style={styles.parameterSlider}
                />
              </div>
            ))}
          </div>

          {/* Actions */}
          <div style={styles.actions}>
            <button
              style={styles.processButton}
              onClick={() => setIsProcessing(!isProcessing)}
              disabled={isProcessing}
            >
              {isProcessing ? (
                <>
                  <span style={styles.spinner}>◌</span>
                  处理中...
                </>
              ) : (
                <>
                  <span style={styles.buttonIcon}>▶</span>
                  应用处理
                </>
              )}
            </button>

            <button style={styles.exportButton}>
              <span style={styles.buttonIcon}>↓</span>
              导出
            </button>
          </div>
        </div>
      </div>

      {/* Processing Log */}
      <div style={styles.processingLog}>
        <h3 style={styles.logTitle}>处理日志</h3>
        <div style={styles.logContent}>
          <div style={styles.logEntry}>
            <span style={styles.logTime}>14:32:05</span>
            <span style={styles.logMessage}>音频加载: {selectedAsset.title}</span>
          </div>
          <div style={styles.logEntry}>
            <span style={styles.logTime}>14:32:06</span>
            <span style={styles.logMessage}>分析完成 - MRS: {selectedAsset.mrs.overall}</span>
          </div>
          <div style={styles.logEntry}>
            <span style={styles.logTime}>14:32:07</span>
            <span style={styles.logMessage}>准备处理</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function WaveformVisualization({ color }: { color: string }) {
  // Generate random waveform bars
  const bars = Array.from({ length: 50 }, () => Math.random() * 0.8 + 0.2)

  return (
    <div style={{ ...styles.waveformBars, height: '100%' }}>
      {bars.map((height, i) => (
        <div
          key={i}
          style={{
            ...styles.waveformBar,
            height: `${height * 100}%`,
            background: color,
          }}
        />
      ))}
    </div>
  )
}

const styles = {
  container: {
    padding: 'var(--space-xl)',
    maxWidth: '1400px',
    margin: '0 auto',
  },

  header: {
    marginBottom: 'var(--space-2xl)',
  },

  title: {
    fontSize: 'var(--text-3xl)',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-sm)',
  },

  subtitle: {
    fontSize: 'var(--text-lg)',
    color: 'var(--color-text-tertiary)',
  },

  workflow: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 'var(--space-xl)',
    marginBottom: 'var(--space-2xl)',
    padding: 'var(--space-xl)',
    background: 'var(--color-bg-secondary)',
    borderRadius: 'var(--radius-xl)',
  },

  workflowStep: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    gap: 'var(--space-sm)',
  },

  stepIcon: {
    width: '56px',
    height: '56px',
    background: 'var(--color-bg-tertiary)',
    borderRadius: 'var(--radius-lg)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'var(--color-text-inverse)',
    fontSize: '24px',
  },

  stepLabel: {
    fontSize: 'var(--text-sm)',
    fontWeight: 500,
    color: 'var(--color-text-secondary)',
  },

  workflowArrow: {
    fontSize: '24px',
    color: 'var(--color-text-muted)',
  },

  workspace: {
    display: 'grid',
    gridTemplateColumns: '1fr 360px',
    gap: 'var(--space-xl)',
    marginBottom: 'var(--space-2xl)',
  },

  comparison: {
    background: 'var(--color-bg-secondary)',
    borderRadius: 'var(--radius-xl)',
    padding: 'var(--space-xl)',
  },

  comparisonHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 'var(--space-lg)',
  },

  comparisonTitle: {
    fontSize: 'var(--text-lg)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
  },

  toggleButton: {
    background: 'var(--color-bg-tertiary)',
    color: 'var(--color-text-secondary)',
    fontSize: 'var(--text-sm)',
    padding: 'var(--space-sm) var(--space-md)',
    borderRadius: 'var(--radius-md)',
    border: 'none',
    cursor: 'pointer',
  },

  waveformContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 'var(--space-lg)',
  },

  waveformSection: {
    background: 'var(--color-bg-primary)',
    borderRadius: 'var(--radius-lg)',
    padding: 'var(--space-lg)',
  },

  waveformLabel: {
    fontSize: 'var(--text-sm)',
    fontWeight: 600,
    color: 'var(--color-text-secondary)',
    marginBottom: 'var(--space-md)',
  },

  waveform: {
    height: '100px',
    background: 'var(--color-bg-tertiary)',
    borderRadius: 'var(--radius-md)',
    marginBottom: 'var(--space-md)',
    overflow: 'hidden',
  },

  waveformBars: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '2px',
    padding: 'var(--space-md)',
  },

  waveformBar: {
    width: '4px',
    borderRadius: '2px',
    transition: 'height 0.1s ease',
  },

  waveformStats: {
    display: 'flex',
    gap: 'var(--space-lg)',
  },

  stat: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-sm)',
  },

  statLabel: {
    fontSize: 'var(--text-sm)',
    color: 'var(--color-text-tertiary)',
  },

  statValue: {
    fontSize: 'var(--text-base)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
  },

  parametersPanel: {
    background: 'var(--color-bg-secondary)',
    borderRadius: 'var(--radius-xl)',
    padding: 'var(--space-xl)',
  },

  panelTitle: {
    fontSize: 'var(--text-lg)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-lg)',
  },

  parametersList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 'var(--space-lg)',
    marginBottom: 'var(--space-2xl)',
  },

  parameter: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 'var(--space-sm)',
  },

  parameterHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },

  parameterLabel: {
    fontSize: 'var(--text-sm)',
    fontWeight: 500,
    color: 'var(--color-text-secondary)',
  },

  parameterValue: {
    fontSize: 'var(--text-sm)',
    fontWeight: 600,
    color: 'var(--color-brand-primary)',
  },

  parameterSlider: {
    width: '100%',
    height: '6px',
    WebkitAppearance: 'none' as const,
    appearance: 'none' as const,
    background: 'var(--color-bg-tertiary)',
    borderRadius: '3px',
    outline: 'none',
  },

  actions: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 'var(--space-md)',
  },

  processButton: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 'var(--space-sm)',
    background: 'var(--color-brand-gradient)',
    color: 'var(--color-text-inverse)',
    fontSize: 'var(--text-base)',
    fontWeight: 600,
    padding: 'var(--space-md)',
    borderRadius: 'var(--radius-lg)',
    border: 'none',
    cursor: 'pointer',
    transition: 'all var(--transition-fast)',
  },

  exportButton: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 'var(--space-sm)',
    background: 'var(--color-bg-tertiary)',
    color: 'var(--color-text-primary)',
    fontSize: 'var(--text-base)',
    fontWeight: 600,
    padding: 'var(--space-md)',
    borderRadius: 'var(--radius-lg)',
    border: '1px solid var(--color-border)',
    cursor: 'pointer',
  },

  buttonIcon: {
    fontSize: '16px',
  },

  spinner: {
    animation: 'spin 1s linear infinite',
  },

  processingLog: {
    background: 'var(--color-bg-secondary)',
    borderRadius: 'var(--radius-xl)',
    padding: 'var(--space-xl)',
  },

  logTitle: {
    fontSize: 'var(--text-lg)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-md)',
  },

  logContent: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 'var(--space-sm)',
  },

  logEntry: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-md)',
    fontSize: 'var(--text-sm)',
    fontFamily: 'var(--font-mono)',
  },

  logTime: {
    color: 'var(--color-text-muted)',
    minWidth: '80px',
  },

  logMessage: {
    color: 'var(--color-text-secondary)',
  },
}
