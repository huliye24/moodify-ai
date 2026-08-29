import React, { useState } from 'react'
import { mockAssets } from '../../utils/mockData'

export function Listening() {
  const [selectedAsset, setSelectedAsset] = useState(mockAssets[0])
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <h1 style={styles.title}>AI 聆听</h1>
        <p style={styles.subtitle}>上传音频进行智能分析</p>
      </header>

      {/* Upload Area */}
      <div style={styles.uploadArea}>
        <div style={styles.uploadIcon}>▶</div>
        <div style={styles.uploadText}>拖拽音频文件到此处</div>
        <div style={styles.uploadHint}>或点击浏览</div>
        <div style={styles.uploadFormats}>支持格式: WAV, MP3, FLAC</div>
      </div>

      {/* Analysis Result */}
      {selectedAsset && (
        <div style={styles.analysisResult}>
          <div style={styles.resultHeader}>
            <div>
              <h2 style={styles.trackTitle}>{selectedAsset.title}</h2>
              <p style={styles.trackArtist}>{selectedAsset.artist}</p>
            </div>
            <div style={styles.mrsScore}>
              <div style={styles.mrsValue}>{selectedAsset.mrs.overall}</div>
              <div style={styles.mrsLabel}>MRS 评分</div>
            </div>
          </div>

          {/* Metrics Grid */}
          <div style={styles.metricsGrid}>
            <MetricCard
              label="速度"
              value={`${selectedAsset.analysis.tempo} BPM`}
              icon="◈"
            />
            <MetricCard
              label="能量"
              value={selectedAsset.analysis.energy}
              icon="◆"
            />
            <MetricCard
              label="情绪"
              value={selectedAsset.analysis.emotion}
              icon="◎"
            />
            <MetricCard
              label="频率平衡"
              value={selectedAsset.analysis.frequencyBalance}
              icon="▣"
            />
            <MetricCard
              label="立体声宽度"
              value={selectedAsset.analysis.stereoWidth.toFixed(2)}
              icon="◇"
            />
            <MetricCard
              label="时长"
              value={`${Math.floor(selectedAsset.duration / 60)}:${(selectedAsset.duration % 60).toString().padStart(2, '0')}`}
              icon="▶"
            />
          </div>

          {/* MRS Breakdown */}
          <div style={styles.mrsBreakdown}>
            <h3 style={styles.breakdownTitle}>MRS 细分</h3>
            <div style={styles.breakdownGrid}>
              <MRSBar label="保真度" value={selectedAsset.mrs.fidelity} />
              <MRSBar label="平衡" value={selectedAsset.mrs.balance} />
              <MRSBar label="清晰度" value={selectedAsset.mrs.clarity} />
            </div>
          </div>

          {/* Recommendations */}
          <div style={styles.recommendations}>
            <h3 style={styles.recommendationsTitle}>AI 建议</h3>
            <ul style={styles.recommendationList}>
              {selectedAsset.mrs.fidelity < 85 && (
                <li style={styles.recommendationItem}>
                  <span style={styles.recommendationIcon}>▸</span>
                  建议增强高频清晰度
                </li>
              )}
              {selectedAsset.mrs.balance < 85 && (
                <li style={styles.recommendationItem}>
                  <span style={styles.recommendationIcon}>▸</span>
                  立体声场可以进一步加宽
                </li>
              )}
              {selectedAsset.mrs.clarity < 85 && (
                <li style={styles.recommendationItem}>
                  <span style={styles.recommendationIcon}>▸</span>
                  人声在混音中可以更突出
                </li>
              )}
              {selectedAsset.mrs.overall >= 85 && (
                <li style={styles.recommendationItem}>
                  <span style={styles.recommendationIcon}>✓</span>
                  音频质量优秀 - 无需修改
                </li>
              )}
            </ul>
          </div>
        </div>
      )}

      {/* Asset List */}
      <div style={styles.assetList}>
        <h3 style={styles.listTitle}>近期分析</h3>
        {mockAssets.slice(0, 5).map(asset => (
          <button
            key={asset.id}
            style={{
              ...styles.assetItem,
              ...(selectedAsset?.id === asset.id ? styles.assetItemActive : {}),
            }}
            onClick={() => setSelectedAsset(asset)}
          >
            <div style={styles.assetInfo}>
              <div style={styles.assetTitle}>{asset.title}</div>
              <div style={styles.assetMeta}>{asset.artist} • {asset.genre}</div>
            </div>
            <div style={styles.assetMRS(asset.mrs.overall)}>
              {asset.mrs.overall}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

function MetricCard({ label, value, icon }: { label: string; value: string | number; icon: string }) {
  return (
    <div style={styles.metricCard}>
      <div style={styles.metricIcon}>{icon}</div>
      <div style={styles.metricValue}>{value}</div>
      <div style={styles.metricLabel}>{label}</div>
    </div>
  )
}

function MRSBar({ label, value }: { label: string; value: number }) {
  const color = value >= 80 ? 'var(--color-mrs-excellent)' : value >= 60 ? 'var(--color-mrs-good)' : 'var(--color-mrs-poor)'

  return (
    <div style={styles.mrsBarContainer}>
      <div style={styles.mrsBarLabel}>{label}</div>
      <div style={styles.mrsBarTrack}>
        <div style={{ ...styles.mrsBarFill, width: `${value}%`, background: color }} />
      </div>
      <div style={styles.mrsBarValue}>{value}</div>
    </div>
  )
}

const styles = {
  container: {
    padding: 'var(--space-xl)',
    maxWidth: '1200px',
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

  uploadArea: {
    background: 'var(--color-bg-secondary)',
    border: '2px dashed var(--color-border)',
    borderRadius: 'var(--radius-xl)',
    padding: 'var(--space-3xl)',
    textAlign: 'center' as const,
    marginBottom: 'var(--space-2xl)',
    cursor: 'pointer',
    transition: 'all var(--transition-fast)',
  },

  uploadIcon: {
    fontSize: '48px',
    color: 'var(--color-brand-primary)',
    marginBottom: 'var(--space-md)',
  },

  uploadText: {
    fontSize: 'var(--text-xl)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-sm)',
  },

  uploadHint: {
    fontSize: 'var(--text-base)',
    color: 'var(--color-text-tertiary)',
    marginBottom: 'var(--space-sm)',
  },

  uploadFormats: {
    fontSize: 'var(--text-sm)',
    color: 'var(--color-text-muted)',
  },

  analysisResult: {
    background: 'var(--color-bg-secondary)',
    borderRadius: 'var(--radius-xl)',
    padding: 'var(--space-2xl)',
    marginBottom: 'var(--space-2xl)',
  },

  resultHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 'var(--space-2xl)',
    paddingBottom: 'var(--space-xl)',
    borderBottom: '1px solid var(--color-border)',
  },

  trackTitle: {
    fontSize: 'var(--text-2xl)',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-xs)',
  },

  trackArtist: {
    fontSize: 'var(--text-base)',
    color: 'var(--color-text-tertiary)',
  },

  mrsScore: {
    textAlign: 'center' as const,
  },

  mrsValue: {
    fontSize: '48px',
    fontWeight: 700,
    color: 'var(--color-brand-primary)',
  },

  mrsLabel: {
    fontSize: 'var(--text-sm)',
    color: 'var(--color-text-tertiary)',
  },

  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 'var(--space-lg)',
    marginBottom: 'var(--space-2xl)',
  },

  metricCard: {
    background: 'var(--color-bg-primary)',
    borderRadius: 'var(--radius-lg)',
    padding: 'var(--space-lg)',
    textAlign: 'center' as const,
  },

  metricIcon: {
    fontSize: '24px',
    color: 'var(--color-brand-primary)',
    marginBottom: 'var(--space-sm)',
  },

  metricValue: {
    fontSize: 'var(--text-xl)',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-xs)',
  },

  metricLabel: {
    fontSize: 'var(--text-sm)',
    color: 'var(--color-text-tertiary)',
  },

  mrsBreakdown: {
    marginBottom: 'var(--space-2xl)',
  },

  breakdownTitle: {
    fontSize: 'var(--text-lg)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-lg)',
  },

  breakdownGrid: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 'var(--space-md)',
  },

  mrsBarContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-md)',
  },

  mrsBarLabel: {
    width: '80px',
    fontSize: 'var(--text-sm)',
    fontWeight: 500,
    color: 'var(--color-text-secondary)',
  },

  mrsBarTrack: {
    flex: 1,
    height: '8px',
    background: 'var(--color-bg-tertiary)',
    borderRadius: '4px',
    overflow: 'hidden',
  },

  mrsBarFill: {
    height: '100%',
    borderRadius: '4px',
    transition: 'width var(--transition-normal)',
  },

  mrsBarValue: {
    width: '40px',
    fontSize: 'var(--text-sm)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    textAlign: 'right' as const,
  },

  recommendations: {
    background: 'var(--color-bg-primary)',
    borderRadius: 'var(--radius-lg)',
    padding: 'var(--space-lg)',
  },

  recommendationsTitle: {
    fontSize: 'var(--text-lg)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-md)',
  },

  recommendationList: {
    listStyle: 'none',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 'var(--space-sm)',
  },

  recommendationItem: {
    fontSize: 'var(--text-base)',
    color: 'var(--color-text-secondary)',
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-sm)',
  },

  recommendationIcon: {
    color: 'var(--color-brand-primary)',
  },

  assetList: {
    marginTop: 'var(--space-2xl)',
  },

  listTitle: {
    fontSize: 'var(--text-xl)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-lg)',
  },

  assetItem: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 'var(--space-md)',
    background: 'var(--color-bg-secondary)',
    borderRadius: 'var(--radius-lg)',
    border: '1px solid var(--color-border)',
    marginBottom: 'var(--space-sm)',
    cursor: 'pointer',
    transition: 'all var(--transition-fast)',
  },

  assetItemActive: {
    borderColor: 'var(--color-brand-primary)',
    background: 'var(--color-bg-tertiary)',
  },

  assetInfo: {
    flex: 1,
  },

  assetTitle: {
    fontSize: 'var(--text-base)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-xs)',
  },

  assetMeta: {
    fontSize: 'var(--text-sm)',
    color: 'var(--color-text-tertiary)',
  },

  assetMRS: (score: number) => ({
    background: score >= 80 ? 'var(--color-mrs-excellent)' : score >= 60 ? 'var(--color-mrs-good)' : 'var(--color-mrs-poor)',
    color: 'var(--color-text-inverse)',
    fontSize: 'var(--text-sm)',
    fontWeight: 600,
    padding: 'var(--space-xs) var(--space-sm)',
    borderRadius: 'var(--radius-sm)',
  }),
}
