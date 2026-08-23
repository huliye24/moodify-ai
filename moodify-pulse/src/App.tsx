import React, { useState } from 'react'
import './styles.css'
import { Sidebar } from './components/Sidebar/Sidebar'
import { Dashboard } from './pages/Dashboard/Dashboard'
import { Listening } from './pages/Listening/Listening'
import { Processing } from './pages/Processing/Processing'
import { Library } from './pages/Library/Library'
import { Reports } from './pages/Reports/Reports'
import { Plugins } from './pages/Plugins/Plugins'

function App() {
  const [activeView, setActiveView] = useState('dashboard')

  const renderView = () => {
    switch (activeView) {
      case 'dashboard':
        return <Dashboard />
      case 'listening':
        return <Listening />
      case 'processing':
        return <Processing />
      case 'library':
        return <Library />
      case 'reports':
        return <Reports />
      case 'plugins':
        return <Plugins />
      default:
        return <Dashboard />
    }
  }

  return (
    <div style={styles.container}>
      <Sidebar activeView={activeView} onViewChange={setActiveView} />
      <main style={styles.main}>
        {renderView()}
      </main>
    </div>
  )
}

const styles = {
  container: {
    display: 'flex',
    width: '100vw',
    height: '100vh',
    background: 'var(--color-bg-primary)',
    color: 'var(--color-text-primary)',
    fontFamily: 'var(--font-sans)',
  },

  main: {
    flex: 1,
    overflow: 'auto',
  },
}

export default App
