import React, { useState } from 'react'
import { mockAssets } from '../../utils/mockData'

export function Library() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedGenre, setSelectedGenre] = useState('all')
  const [sortBy, setSortBy] = useState('mrs')

  const genres = ['all', 'Electronic', 'Ambient', 'Rock', 'Jazz', 'Classical', 'Hip Hop', 'Pop']

  const filteredAssets = mockAssets
    .filter(asset => {
      const matchesSearch = asset.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          asset.artist.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesGenre = selectedGenre === 'all' || asset.genre === selectedGenre
      return matchesSearch && matchesGenre
    })
    .sort((a, b) => {
      if (sortBy === 'mrs') return b.mrs.overall - a.mrs.overall
      if (sortBy === 'title') return a.title.localeCompare(b.title)
      if (sortBy === 'date') return new Date(b.lastModified).getTime() - new Date(a.lastModified).getTime()
      return 0
    })

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <h1 style={styles.title}>Audio Library</h1>
        <p style={styles.subtitle}>{mockAssets.length} audio assets</p>
      </header>

      {/* Filters */}
      <div style={styles.filters}>
        <div style={styles.searchBox}>
          <span style={styles.searchIcon}>◈</span>
          <input
            type="text"
            placeholder="Search audio assets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={styles.searchInput}
          />
        </div>

        <div style={styles.filterGroup}>
          <select
            value={selectedGenre}
            onChange={(e) => setSelectedGenre(e.target.value)}
            style={styles.select}
          >
            {genres.map(genre => (
              <option key={genre} value={genre}>
                {genre === 'all' ? 'All Genres' : genre}
              </option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            style={styles.select}
          >
            <option value="mrs">Sort by MRS</option>
            <option value="title">Sort by Title</option>
            <option value="date">Sort by Date</option>
          </select>
        </div>
      </div>

      {/* Asset Grid */}
      <div style={styles.assetGrid}>
        {filteredAssets.map(asset => (
          <div key={asset.id} style={styles.assetCard}>
            {/* Card Header */}
            <div style={styles.cardHeader}>
              <div style={styles.assetIcon}>▤</div>
              <div style={styles.mrsBadge(asset.mrs.overall)}>
                {asset.mrs.overall}
              </div>
            </div>

            {/* Card Content */}
            <div style={styles.cardContent}>
              <h3 style={styles.assetTitle}>{asset.title}</h3>
              <p style={styles.assetArtist}>{asset.artist}</p>

              <div style={styles.assetMeta}>
                <span style={styles.genreTag}>{asset.genre}</span>
                <span style={styles.moodTag}>{asset.mood}</span>
              </div>

              <div style={styles.assetStats}>
                <div style={styles.stat}>
                  <span style={styles.statLabel}>Tempo</span>
                  <span style={styles.statValue}>{asset.analysis.tempo} BPM</span>
                </div>
                <div style={styles.stat}>
                  <span style={styles.statLabel}>Energy</span>
                  <span style={styles.statValue}>{asset.analysis.energy}%</span>
                </div>
              </div>

              <div style={styles.aiHistory}>
                <span style={styles.aiIcon}>◆</span>
                <span style={styles.aiText}>AI Analyzed</span>
                <span style={styles.aiDate}>{asset.lastModified}</span>
              </div>
            </div>

            {/* Card Actions */}
            <div style={styles.cardActions}>
              <button style={styles.actionButton}>
                <span style={styles.actionIcon}>▶</span>
                Listen
              </button>
              <button style={styles.actionButton}>
                <span style={styles.actionIcon}>◈</span>
                Analyze
              </button>
              <button style={styles.actionButton}>
                <span style={styles.actionIcon}>▣</span>
                Process
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredAssets.length === 0 && (
        <div style={styles.emptyState}>
          <div style={styles.emptyIcon}>◈</div>
          <h3 style={styles.emptyTitle}>No assets found</h3>
          <p style={styles.emptyText}>Try adjusting your search or filters</p>
        </div>
      )}
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
    marginBottom: 'var(--space-xl)',
  },

  title: {
    fontSize: 'var(--text-3xl)',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-sm)',
  },

  subtitle: {
    fontSize: 'var(--text-base)',
    color: 'var(--color-text-tertiary)',
  },

  filters: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-md)',
    marginBottom: 'var(--space-xl)',
    padding: 'var(--space-md)',
    background: 'var(--color-bg-secondary)',
    borderRadius: 'var(--radius-lg)',
  },

  searchBox: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-sm)',
    background: 'var(--color-bg-primary)',
    borderRadius: 'var(--radius-md)',
    padding: 'var(--space-sm) var(--space-md)',
    border: '1px solid var(--color-border)',
  },

  searchIcon: {
    color: 'var(--color-text-muted)',
    fontSize: '16px',
  },

  searchInput: {
    flex: 1,
    border: 'none',
    background: 'transparent',
    fontSize: 'var(--text-base)',
    color: 'var(--color-text-primary)',
    outline: 'none',
  },

  filterGroup: {
    display: 'flex',
    gap: 'var(--space-sm)',
  },

  select: {
    padding: 'var(--space-sm) var(--space-md)',
    borderRadius: 'var(--radius-md)',
    border: '1px solid var(--color-border)',
    background: 'var(--color-bg-primary)',
    fontSize: 'var(--text-sm)',
    color: 'var(--color-text-secondary)',
    cursor: 'pointer',
  },

  assetGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: 'var(--space-lg)',
  },

  assetCard: {
    background: 'var(--color-bg-secondary)',
    borderRadius: 'var(--radius-xl)',
    border: '1px solid var(--color-border)',
    overflow: 'hidden',
    transition: 'all var(--transition-fast)',
  },

  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 'var(--space-md)',
    background: 'var(--color-bg-tertiary)',
  },

  assetIcon: {
    width: '40px',
    height: '40px',
    background: 'var(--color-brand-gradient)',
    borderRadius: 'var(--radius-md)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'var(--color-text-inverse)',
    fontSize: '18px',
  },

  mrsBadge: (score: number) => ({
    background: score >= 80 ? 'var(--color-mrs-excellent)' : score >= 60 ? 'var(--color-mrs-good)' : 'var(--color-mrs-poor)',
    color: 'var(--color-text-inverse)',
    fontSize: 'var(--text-sm)',
    fontWeight: 700,
    padding: 'var(--space-xs) var(--space-sm)',
    borderRadius: 'var(--radius-sm)',
  }),

  cardContent: {
    padding: 'var(--space-lg)',
  },

  assetTitle: {
    fontSize: 'var(--text-lg)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-xs)',
  },

  assetArtist: {
    fontSize: 'var(--text-sm)',
    color: 'var(--color-text-tertiary)',
    marginBottom: 'var(--space-md)',
  },

  assetMeta: {
    display: 'flex',
    gap: 'var(--space-sm)',
    marginBottom: 'var(--space-md)',
  },

  genreTag: {
    fontSize: 'var(--text-xs)',
    fontWeight: 500,
    color: 'var(--color-brand-primary)',
    background: 'var(--color-bg-tertiary)',
    padding: 'var(--space-xs) var(--space-sm)',
    borderRadius: 'var(--radius-sm)',
  },

  moodTag: {
    fontSize: 'var(--text-xs)',
    fontWeight: 500,
    color: 'var(--color-text-secondary)',
    background: 'var(--color-bg-tertiary)',
    padding: 'var(--space-xs) var(--space-sm)',
    borderRadius: 'var(--radius-sm)',
  },

  assetStats: {
    display: 'flex',
    gap: 'var(--space-lg)',
    marginBottom: 'var(--space-md)',
  },

  stat: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 'var(--space-xs)',
  },

  statLabel: {
    fontSize: 'var(--text-xs)',
    color: 'var(--color-text-muted)',
  },

  statValue: {
    fontSize: 'var(--text-sm)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
  },

  aiHistory: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-sm)',
    padding: 'var(--space-sm)',
    background: 'var(--color-bg-tertiary)',
    borderRadius: 'var(--radius-md)',
  },

  aiIcon: {
    color: 'var(--color-brand-primary)',
    fontSize: '12px',
  },

  aiText: {
    fontSize: 'var(--text-xs)',
    color: 'var(--color-text-secondary)',
  },

  aiDate: {
    fontSize: 'var(--text-xs)',
    color: 'var(--color-text-muted)',
    marginLeft: 'auto',
  },

  cardActions: {
    display: 'flex',
    borderTop: '1px solid var(--color-border)',
  },

  actionButton: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 'var(--space-xs)',
    padding: 'var(--space-sm)',
    background: 'transparent',
    border: 'none',
    fontSize: 'var(--text-sm)',
    fontWeight: 500,
    color: 'var(--color-text-secondary)',
    cursor: 'pointer',
    transition: 'all var(--transition-fast)',
  },

  actionIcon: {
    fontSize: '12px',
  },

  emptyState: {
    textAlign: 'center' as const,
    padding: 'var(--space-3xl)',
  },

  emptyIcon: {
    fontSize: '48px',
    color: 'var(--color-text-muted)',
    marginBottom: 'var(--space-md)',
  },

  emptyTitle: {
    fontSize: 'var(--text-xl)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: 'var(--space-sm)',
  },

  emptyText: {
    fontSize: 'var(--text-base)',
    color: 'var(--color-text-tertiary)',
  },
}
