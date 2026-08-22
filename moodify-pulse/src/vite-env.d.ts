/// <reference types="vite/client" />

declare global {
  interface Window {
    electronAPI?: {
      apiBaseUrl: string
      platform: string
    }
  }
}

export {}
