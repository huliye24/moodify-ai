import React from 'react'
import './styles.css'

interface SidebarItem {
  id: string
  label: string
  icon: string
  badge?: number
}

const sidebarItems: SidebarItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: '◆' },
  { id: 'listening', label: 'AI Listening', icon: '◎' },
  { id: 'processing', label: 'Processing', icon: '▶' },
  { id: 'library', label: 'Audio Library', icon: '▤' },
  { id: 'projects', label: 'Projects', icon: '▣' },
  { id: 'reports', label: 'Reports', icon: '◈' },
  { id: 'plugins', label: 'Plugins', icon: '◊' },
  { id: 'marketplace', label: 'Marketplace', icon: '◇' },
  { id: 'settings', label: 'Settings', icon: '◉' },
]

interface SidebarProps {
  activeView: string
  onViewChange: (view: string) => void
}

export function Sidebar({ activeView, onViewChange }: SidebarProps) {
  return (
    <aside style={styles.sidebar}>
      {/* Logo */}
      <div style={styles.logo}>
        <div style={styles.logoIcon}>◈</div>
        <div style={styles.logoText}>Moodify</div>
      </div>

      {/* Navigation */}
      <nav style={styles.nav}>
        {sidebarItems.map(item => (
          <button
            key={item.id}
            style={{
              ...styles.navItem,
              ...(activeView === item.id ? styles.navItemActive : {}),
            }}
            onClick={() => onViewChange(item.id)}
          >
            <span style={styles.navIcon}>{item.icon}</span>
            <span style={styles.navLabel}>{item.label}</span>
            {item.badge && (
              <span style={styles.badge}>{item.badge}</span>
            )}
          </button>
        ))}
      </nav>

      {/* User */}
      <div style={styles.user}>
        <div style={styles.userAvatar}>A</div>
        <div style={styles.userInfo}>
          <div style={styles.userName}>Audio Engineer</div>
          <div style={styles.userPlan}>Pro Plan</div>
        </div>
      </div>
    </aside>
  )
}

const styles = {
  sidebar: {
    width: 'var(--sidebar-width)',
    height: '100%',
    background: 'var(--color-bg-secondary)',
    borderRight: '1px solid var(--color-border)',
    display: 'flex',
    flexDirection: 'column' as const,
    padding: 'var(--space-md)',
  },

  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-sm)',
    padding: 'var(--space-md)',
    marginBottom: 'var(--space-lg)',
  },

  logoIcon: {
    width: '32px',
    height: '32px',
    background: 'var(--color-brand-gradient)',
    borderRadius: 'var(--radius-md)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'var(--color-text-inverse)',
    fontSize: '16px',
    fontWeight: 600,
  },

  logoText: {
    fontSize: 'var(--text-xl)',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
  },

  nav: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 'var(--space-xs)',
    flex: 1,
  },

  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-sm)',
    padding: 'var(--space-sm) var(--space-md)',
    borderRadius: 'var(--radius-md)',
    border: 'none',
    background: 'transparent',
    color: 'var(--color-text-secondary)',
    fontSize: 'var(--text-sm)',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all var(--transition-fast)',
    textAlign: 'left' as const,
  },

  navItemActive: {
    background: 'var(--color-bg-tertiary)',
    color: 'var(--color-text-primary)',
  },

  navIcon: {
    width: '20px',
    height: '20px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '14px',
  },

  navLabel: {
    flex: 1,
  },

  badge: {
    background: 'var(--color-brand-primary)',
    color: 'var(--color-text-inverse)',
    fontSize: 'var(--text-xs)',
    fontWeight: 600,
    padding: '2px 6px',
    borderRadius: '10px',
  },

  user: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-sm)',
    padding: 'var(--space-md)',
    borderTop: '1px solid var(--color-border)',
    marginTop: 'auto',
  },

  userAvatar: {
    width: '36px',
    height: '36px',
    borderRadius: '50%',
    background: 'var(--color-brand-gradient)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'var(--color-text-inverse)',
    fontSize: '14px',
    fontWeight: 600,
  },

  userInfo: {
    flex: 1,
  },

  userName: {
    fontSize: 'var(--text-sm)',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
  },

  userPlan: {
    fontSize: 'var(--text-xs)',
    color: 'var(--color-text-muted)',
  },
}
