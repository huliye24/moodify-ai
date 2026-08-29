import React from 'react'

export function Reports() {
  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>报告</h1>
        <p style={styles.subtitle}>目录智能与分析</p>
      </header>

      <div style={styles.comingSoon}>
        <div style={styles.icon}>◈</div>
        <h2 style={styles.comingSoonTitle}>即将上线</h2>
        <p style={styles.comingSoonText}>
          为企业用户提供高级报告和分析功能。
        </p>
      </div>
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

  comingSoon: {
    textAlign: 'center' as const,
    padding: 'var(--space-3xl)',
    background: 'var(--color-bg-secondary)',
    borderRadius: 'var(--radius-xl)',
  },

  icon: {
    fontSize: '64px',
    color: 'var(--color-brand-primary)',
    marginBottom: 'var(--space-lg)',
  },

  comingSoonTitle: {
    fontSize: 'var(--text-2xl)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-md)',
  },

  comingSoonText: {
    fontSize: 'var(--text-base)',
    color: 'var(--color-text-tertiary)',
  },
}
