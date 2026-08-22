import React from 'react'

function App() {
  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      background: '#101113',
      color: '#fff',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'system-ui, -apple-system, sans-serif',
    }}>
      <div style={{ textAlign: 'center' }}>
        <h1>Moodify Pulse</h1>
        <p>AI Emotional Music Container</p>
        <p style={{ color: '#888', fontSize: '14px', marginTop: '20px' }}>
          Loading...
        </p>
      </div>
    </div>
  )
}

export default App
