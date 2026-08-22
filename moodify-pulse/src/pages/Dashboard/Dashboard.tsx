import React from 'react'
import { mockAssets, dashboardStats } from '../../utils/mockData'

export function Dashboard() {
  const recentAnalyses = dashboardStats.recentAnalyses

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <h1 style={styles.title}>Good Evening</h1>
        <p style={styles.subtitle}>Your Audio Intelligence</p>
      </header>

      {/* Stats Grid */}
      <div style={styles.statsGrid}>
        <div style={styles.statCard}>
          <div style={styles.statIcon}>▤</div>
          <div style={styles.statValue}>{dashboardStats.totalTracks}</div>
          <div style={styles.statLabel}>Total Tracks</div>
        </div>

        <div style={styles.statCard}>
          <div style={styles.statIcon}>◎</div>
          <div style={styles.statValue}>{dashboardStats.analyzedTracks}</div>
          <div style={styles.statLabel}>Analyzed</div>
        </div>

        <div style={styles.statCard}>
          <div style={styles.statIcon}>◈</div>
          <div style={styles.statValue}>{dashboardStats.averageMRS}</div>
          <div style={styles.statLabel}>Average MRS</div>
        </div>

        <div style={styles.statCard}>
          <div style={styles.statIcon}>▣</div>
          <div style={styles.statValue}>12</div>
          <div style={styles.statLabel}>Projects</div>
        </div>
      </div>

      {/* Recent Intelligence */}
      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>Recent Intelligence</h2>
        <div style={styles.intelligenceList}>
          {recentAnalyses.map(asset => (
            <div key={asset.id} style={styles.intelligenceCard}>
              <div style={styles.intelligenceHeader}>
                <div style={styles.trackInfo}>
                  <div style={styles.trackTitle}>{asset.title}</div>
                  <div style={styles.trackArtist}>{asset.artist}</div>
                </div>
                <div style={styles.mrsBadge(asset.mrs.overall)}>
                  MRS {asset.mrs.overall}
                </div>
              </div>
              <div style={styles.recommendation}>
                <span style={styles.recommendationIcon}>▸</span>
                Recommendation: {getRecommendation(asset)}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Quick Actions */}
      <section style={styles.quickActions}>
        <button style={styles.primaryButton}>
          <span style={styles.buttonIcon}>+</span>
          Analyze New Track
        </button>
      </section>
    </div>
  )
}

function getRecommendation(asset: typeof mockAssets[0]): string {
  if (asset.mrs.clarity < 80) return 'Improve vocal presence'
  if (asset.mrs.balance < 80) return 'Increase spatial depth'
  if (asset.mrs.fidelity < 80) return 'Enhance frequency clarity'
  return 'Audio quality is excellent'
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

  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: 'var(--space-lg)',
    marginBottom: 'var(--space-2xl)',
  },

  statCard: {
    background: 'var(--color-bg-secondary)',
    borderRadius: 'var(--radius-lg)',
    padding: 'var(--space-lg)',
    border: '1px solid var(--color-border)',
  },

  statIcon: {
    width: '40px',
    height: '40px',
    background: 'var(--color-brand-gradient)',
    borderRadius: 'var(--radius-md)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'var(--color-text-inverse)',
    fontSize: '18px',
    marginBottom: 'var(--space-md)',
  },

  statValue: {
    fontSize: 'var(--text-2xl)',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-xs)',
  },

  statLabel: {
    fontSize: 'var(--text-sm)',
    color: 'var(--color-text-tertiary)',
  },

  section: {
    marginBottom: 'var(--space-2xl)',
  },

  sectionTitle: {
    fontSize: 'var(--text-xl)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-lg)',
  },

  intelligenceList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 'var(--space-md)',
  },

  intelligenceCard: {
    background: 'var(--color-bg-secondary)',
    borderRadius: 'var(--radius-lg)',
    padding: 'var(--space-lg)',
    border: '1px solid var(--color-border)',
  },

  intelligenceHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 'var(--space-sm)',
  },

  trackInfo: {
    flex: 1,
  },

  trackTitle: {
    fontSize: 'var(--text-base)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-xs)',
  },

  trackArtist: {
    fontSize: 'var(--text-sm)',
    color: 'var(--color-text-tertiary)',
  },

  mrsBadge: (score: number) => ({
    background: score >= 80 ? 'var(--color-mrs-excellent)' : score >= 60 ? 'var(--color-mrs-good)' : 'var(--color-mrs-poor)',
    color: 'var(--color-text-inverse)',
    fontSize: 'var(--text-sm)',
    fontWeight: 600,
    padding: 'var(--space-xs) var(--space-sm)',
    borderRadius: 'var(--radius-sm)',
  }),

  recommendation: {
    fontSize: 'var(--text-sm)',
    color: 'var(--color-text-secondary)',
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-sm)',
  },

  recommendationIcon: {
    color: 'var(--color-brand-primary)',
  },

  quickActions: {
    display: 'flex',
    gap: 'var(--space-md)',
  },

  primaryButton: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-sm)',
    background: 'var(--color-brand-gradient)',
    color: 'var(--color-text-inverse)',
    fontSize: 'var(--text-base)',
    fontWeight: 600,
    padding: 'var(--space-md) var(--space-lg)',
    borderRadius: 'var(--radius-lg)',
    border: 'none',
    cursor: 'pointer',
    transition: 'all var(--transition-fast)',
  },

  buttonIcon: {
    fontSize: '20px',
  },
}
