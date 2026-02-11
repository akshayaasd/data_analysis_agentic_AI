import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import HomePage from './pages/HomePage';
import DataUploadPage from './pages/DataUploadPage';
import AnalysisPage from './pages/AnalysisPage';
import VisualizationPage from './pages/VisualizationPage';
import SuggestionsPage from './pages/SuggestionsPage';
import './index.css';

function Navigation() {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: '🏠' },
    { path: '/upload', label: 'Upload Data', icon: '📤' },
    { path: '/analysis', label: 'Analysis', icon: '📊' },
    { path: '/visualizations', label: 'Visualizations', icon: '📈' },
    { path: '/suggestions', label: 'Suggestions', icon: '💡' },
  ];

  return (
    <nav className="bg-gray-800/80 backdrop-blur-md border-b border-gray-700 sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="text-2xl">🤖</div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
              Agentic Data Analysis
            </h1>
          </div>

          <div className="flex space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-4 py-2 rounded-lg transition-all duration-200 flex items-center space-x-2 ${location.pathname === item.path
                    ? 'bg-primary-600 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
              >
                <span>{item.icon}</span>
                <span className="font-medium">{item.label}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <AppProvider>
      <Router>
        <div className="min-h-screen">
          <Navigation />
          <main className="container mx-auto px-6 py-8">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/upload" element={<DataUploadPage />} />
              <Route path="/analysis" element={<AnalysisPage />} />
              <Route path="/visualizations" element={<VisualizationPage />} />
              <Route path="/suggestions" element={<SuggestionsPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AppProvider>
  );
}

export default App;
