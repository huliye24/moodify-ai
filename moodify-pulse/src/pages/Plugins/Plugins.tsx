import React from 'react'

export function Plugins() {
  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>插件市场</h1>
        <p style={styles.subtitle}>扩展沐脉功能</p>
      </header>

      <div style={styles.grid}>
        <div style={styles.card}>
          <div style={styles.cardIcon}>◆</div>
          <h3 style={styles.cardTitle}>精选</h3>
          <p style={styles.cardText}>发现高评分插件</p>
        </div>

        <div style={styles.card}>
          <div style={styles.cardIcon}>◇</div>
          <h3 style={styles.cardTitle}>已安装</h3>
          <p style={styles.cardText}>管理您的插件</p>
        </div>

        <div style={styles.card}>
          <div style={styles.cardIcon}>◈</div>
          <h3 style={styles.cardTitle}>开发者中心</h3>
          <p style={styles.cardText}>构建和发布插件</p>
        </div>
      </div>

      <div style={styles.comingSoon}>
        <div style={styles.comingSoonIcon}>◊</div>
        <h2 style={styles.comingSoonTitle}>市场即将上线</h2>
        <p style={styles.comingSoonText}>
          浏览和安装插件以扩展沐脉的功能。
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

  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 'var(--space-lg)',
    marginBottom: 'var(--space-2xl)',
  },

  card: {
    background: 'var(--color-bg-secondary)',
    borderRadius: 'var(--radius-xl)',
    padding: 'var(--space-xl)',
    textAlign: 'center' as const,
    border: '1px solid var(--color-border)',
    cursor: 'pointer',
    transition: 'all var(--transition-fast)',
  },

  cardIcon: {
    fontSize: '32px',
    color: 'var(--color-brand-primary)',
    marginBottom: 'var(--space-md)',
  },

  cardTitle: {
    fontSize: 'var(--text-lg)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-sm)',
  },

  cardText: {
    fontSize: 'var(--text-sm)',
    color: 'var(--color-text-tertiary)',
  },

  comingSoon: {
    textAlign: 'center' as const,
    padding: 'var(--space-3xl)',
    background: 'var(--color-bg-secondary)',
    borderRadius: 'var(--radius-xl)',
  },

  comingSoonIcon: {
    fontSize: '48px',
    color: 'var(--color-brand-primary)',
    marginBottom: 'var(--space-lg)',
  },

  comingSoonTitle: {
    fontSize: 'var(--text-xl)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-md)',
  },

  comingSoonText: {
    fontSize: 'var(--text-base)',
    color: 'var(--color-text-tertiary)',
  },
}
