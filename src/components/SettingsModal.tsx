import { useState, useEffect } from 'react'
import { X, Key, Check, AlertCircle } from 'lucide-react'
import { useStore } from '../stores/useStore'

const T = {
  secondary: 'rgba(107,122,143,0.5)',
  tertiary:   'rgba(107,122,143,0.35)',
  body:       'rgba(196,212,228,0.75)',
  heading:    'rgba(196,212,228,0.9)',
  white:      'rgba(196,212,228,1)',
}

interface SettingsModalProps {
  onClose: () => void
}

export default function SettingsModal({ onClose }: SettingsModalProps) {
  const { apiKey, setApiKey } = useStore()
  const [localKey, setLocalKey] = useState(apiKey || '')
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    setLocalKey(apiKey || '')
  }, [apiKey])

  const handleSave = () => {
    if (!localKey.trim()) {
      setError('请输入 API Key')
      return
    }
    setApiKey(localKey.trim())
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div
      style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}
      onClick={onClose}
    >
      <div
        style={{
          width: '100%', maxWidth: '28rem',
          background: 'rgba(107,122,143,0.04)',
          border: '1px solid rgba(107,122,143,0.15)',
          borderRadius: '0.75rem',
          boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '1rem 1.5rem',
          borderBottom: '1px solid rgba(107,122,143,0.15)'
        }}>
          <h2 style={{ fontWeight: 600, color: T.heading }}>设置</h2>
          <button
            onClick={onClose}
            style={{ padding: '0.5rem', borderRadius: '0.5rem', background: 'transparent', transition: 'background 0.2s' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = 'rgba(107,122,143,0.08)' }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = 'transparent' }}
          >
            <X className="w-5 h-5" style={{ color: T.secondary }} />
          </button>
        </div>

        <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{
              display: 'flex', fontSize: '0.875rem', color: T.secondary,
              marginBottom: '0.5rem', alignItems: 'center', gap: '0.5rem'
            }}>
              <Key className="w-4 h-4" style={{ color: 'rgba(107,122,143,0.6)' }} />
              DeepSeek API Key
            </label>
            <input
              type="password"
              value={localKey}
              onChange={(e) => setLocalKey(e.target.value)}
              placeholder="Paste your DeepSeek API key"
              className="input-field"
            />
            <p style={{ fontSize: '0.75rem', color: T.tertiary, marginTop: '0.25rem' }}>
              请从 DeepSeek 开放平台获取 API Key
            </p>
          </div>

          {error && (
            <div style={{
              background: 'rgba(220,38,38,0.08)',
              border: '1px solid rgba(220,38,38,0.15)',
              borderRadius: '0.5rem',
              padding: '0.75rem 1rem',
              display: 'flex', alignItems: 'center', gap: '0.5rem'
            }}>
              <AlertCircle className="w-4 h-4 flex-shrink-0" style={{ color: 'rgba(239,68,68,0.7)' }} />
              <span style={{ fontSize: '0.875rem', color: 'rgba(252,165,165,0.8)' }}>{error}</span>
            </div>
          )}
        </div>

        <div style={{
          padding: '1rem 1.5rem',
          borderTop: '1px solid rgba(107,122,143,0.15)',
          display: 'flex', justifyContent: 'flex-end', gap: '0.75rem'
        }}>
          <button onClick={onClose} className="btn-secondary px-4 py-2">
            <span style={{ color: T.body }}>取消</span>
          </button>
          <button onClick={handleSave} className="btn-primary px-4 py-2 flex items-center gap-2">
            {saved ? (
              <>
                <Check className="w-4 h-4" style={{ color: 'rgba(74,222,128,0.8)' }} />
                <span style={{ color: T.white }}>已保存</span>
              </>
            ) : (
              <span style={{ color: T.white }}>保存</span>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
