import { useState } from 'react'
import './App.css'

import 'tailwindcss'

function App() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check system preference on initial load
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode)
    // Update document class for theme
    document.documentElement.classList.toggle('dark')
  }

  return (
    // Apply theme class to container
    <div className={`min-h-screen p-4 ${isDarkMode ? 'dark bg-gray-900 text-white' : 'bg-white text-gray-900'}`}>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">graphcap Studio</h1>
          <p className="text-gray-600 dark:text-gray-400">Graph Capture and Analysis Tool</p>
        </div>
        
        <button
          onClick={toggleTheme}
          className="px-4 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          {isDarkMode ? '🌞 Light Mode' : '🌙 Dark Mode'}
        </button>
      </div>
    </div>
  )
}

export default App
