import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import DataUploadPage from './DataUploadPage';
import AnalysisPage from './AnalysisPage';
import SuggestionsPage from './SuggestionsPage';
import VisualizationPage from './VisualizationPage';

export default function Dashboard() {
    const { currentDataset, llmProvider, setLlmProvider } = useApp();
    const [activeTab, setActiveTab] = useState(currentDataset ? 'analysis' : 'upload');

    const tabs = [
        { id: 'upload', name: 'Data Upload', icon: '📂' },
        { id: 'analysis', name: 'Chat Analysis', icon: '💬', disabled: !currentDataset },
        { id: 'suggestions', name: 'AI Suggestions', icon: '💡', disabled: !currentDataset },
        { id: 'gallery', name: 'Chart Gallery', icon: '📈', disabled: !currentDataset },
    ];

    return (
        <div className="flex h-[calc(100vh-64px)] overflow-hidden">
            {/* Sidebar */}
            <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
                <div className="p-4 space-y-2 flex-1 overflow-y-auto">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => !tab.disabled && setActiveTab(tab.id)}
                            disabled={tab.disabled}
                            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${activeTab === tab.id
                                    ? 'bg-primary-600 text-white shadow-lg shadow-primary-900/20'
                                    : tab.disabled
                                        ? 'opacity-30 cursor-not-allowed grayscale'
                                        : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                                }`}
                        >
                            <span className="text-xl">{tab.icon}</span>
                            <span className="font-medium">{tab.name}</span>
                        </button>
                    ))}

                    <div className="pt-6">
                        <div className="text-xs font-semibold text-gray-500 uppercase tracking-widest px-4 mb-3">Settings</div>
                        <div className="px-4 space-y-4">
                            <div>
                                <label className="text-xs text-gray-400 block mb-1">LLM Provider</label>
                                <select
                                    value={llmProvider}
                                    onChange={(e) => setLlmProvider(e.target.value)}
                                    className="w-full bg-gray-900 text-white text-xs rounded border border-gray-700 px-2 py-2 focus:ring-1 focus:ring-primary-500 outline-none"
                                >
                                    <option value="groq">Groq (Llama 3.3)</option>
                                    <option value="gemini">Gemini (Google)</option>
                                    <option value="openai">OpenAI (GPT-4)</option>
                                    <option value="anthropic">Anthropic (Claude 3.5)</option>
                                    <option value="mcp">⚡ MCP Bridge</option>
                                    <option value="ollama">Ollama (Local)</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Dataset Summary in Sidebar */}
                {currentDataset && (
                    <div className="p-4 bg-gray-900/50 border-t border-gray-700">
                        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Current Dataset</div>
                        <div className="text-sm font-medium text-white truncate mb-1">{currentDataset.filename}</div>
                        <div className="text-xs text-gray-400">
                            {currentDataset.rows} rows • {currentDataset.columns} cols
                        </div>
                    </div>
                )}
            </div>

            {/* Main Content Area */}
            <div className="flex-1 overflow-y-auto p-6 bg-gray-900">
                <div className="max-w-6xl mx-auto">
                    {activeTab === 'upload' && (
                        <div className="animate-fade-in">
                            <h2 className="text-2xl font-bold text-white mb-6">Upload Dataset</h2>
                            <DataUploadPage onUploadSuccess={() => setActiveTab('analysis')} />
                        </div>
                    )}

                    {activeTab === 'analysis' && currentDataset && (
                        <div className="animate-fade-in">
                            <AnalysisPage />
                        </div>
                    )}

                    {activeTab === 'suggestions' && currentDataset && (
                        <div className="animate-fade-in">
                            <SuggestionsPage />
                        </div>
                    )}

                    {activeTab === 'gallery' && currentDataset && (
                        <div className="animate-fade-in">
                            <VisualizationPage />
                        </div>
                    )}

                    {!currentDataset && activeTab !== 'upload' && activeTab !== 'images' && (
                        <div className="text-center py-20">
                            <div className="text-6xl mb-4">📥</div>
                            <h2 className="text-2xl font-bold text-white mb-2">Ready to Start?</h2>
                            <p className="text-gray-400 mb-6">Upload a CSV or Excel file to get started with analysis.</p>
                            <button onClick={() => setActiveTab('upload')} className="btn-primary">
                                Go to Upload
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
