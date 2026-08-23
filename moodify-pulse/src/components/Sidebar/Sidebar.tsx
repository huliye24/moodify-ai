import React from 'react'
import logoWhite from '../../assets/logo-white.png'

interface SidebarItem {
  id: string
  label: string
  icon: string
  badge?: number
}

const sidebarItems: SidebarItem[] = [
  { id: 'dashboard', label: '工作台', icon: '◆' },
  { id: 'listening', label: 'AI 聆听', icon: '◎' },
  { id: 'processing', label: '音频处理', icon: '▶' },
  { id: 'library', label: '音频库', icon: '▤' },
  { id: 'projects', label: '项目', icon: '▣' },
  { id: 'reports', label: '报告', icon: '◈' },
  { id: 'plugins', label: '插件', icon: '◊' },
  { id: 'marketplace', label: '市场', icon: '◇' },
  { id: 'settings', label: '设置', icon: '◉' },
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
        <img src={logoWhite} alt="沐脉" style={styles.logoImg} />
        <div style={styles.logoText}>沐脉</div>
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
        <div style={styles.userAvatar}>音</div>
        <div style={styles.userInfo}>
          <div style={styles.userName}>音频工程师</div>
          <div style={styles.userPlan}>专业版</div>
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

  logoImg: {
    width: '32px',
    height: '32px',
    borderRadius: 'var(--radius-md)',
    objectFit: 'contain' as const,
    background: 'var(--color-brand-gradient)',
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
