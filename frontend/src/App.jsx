import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppProvider, useApp } from './context/AppContext';
import Dashboard from './pages/Dashboard';
import './index.css';

function Navigation() {
  const { llmProvider, setLlmProvider } = useApp();

  return (
    <nav className="bg-gray-800 border-b border-gray-700 h-16 flex items-center justify-between px-6 sticky top-0 z-50">
      <div className="flex items-center space-x-3">
        <Link to="/" className="flex items-center space-x-2">
          <span className="text-3xl">🚀</span>
          <span className="text-xl font-bold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
            AnalystAgent
          </span>
        </Link>
      </div>

      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-3">
          <span className="text-sm text-gray-400 font-medium italic">Powered by</span>
          <select
            value={llmProvider}
            onChange={(e) => setLlmProvider(e.target.value)}
            className="bg-gray-700 text-white text-sm rounded-lg px-4 py-2 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all font-semibold"
          >
            <option value="groq">Groq (Llama 3.3)</option>
          </select>
        </div>
      </div>
    </nav>
  );
}

function AppContent() {
  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 font-sans selection:bg-primary-500/30">
      <Navigation />
      <main>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          {/* Fallback to root for any other path */}
          <Route path="*" element={<Dashboard />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <AppProvider>
      <Router>
        <AppContent />
      </Router>
    </AppProvider>
  );
}

export default App;
