import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App.jsx'
import './index.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#141c2d',
            color: '#e8ecf4',
            border: '1px solid rgba(255,255,255,0.06)',
            fontFamily: 'Inter, sans-serif',
          },
          success: { iconTheme: { primary: '#00d4aa', secondary: '#141c2d' } },
          error: { iconTheme: { primary: '#ef4444', secondary: '#141c2d' } },
        }}
      />
    </BrowserRouter>
  </StrictMode>
)
