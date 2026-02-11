import React from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../context/AppContext';

export default function HomePage() {
    const { currentDataset } = useApp();

    const features = [
        {
            icon: '🤖',
            title: 'Multi-Agent System',
            description: 'Specialized agents for analysis, visualization, suggestions, and RAG',
            color: 'from-blue-500 to-cyan-500',
        },
        {
            icon: '🧠',
            title: 'RAG Integration',
            description: 'Context-aware responses using vector store and past analyses',
            color: 'from-purple-500 to-pink-500',
        },
        {
            icon: '💡',
            title: 'Smart Suggestions',
            description: 'Top 3 AI-powered recommendations for insights and visualizations',
            color: 'from-orange-500 to-red-500',
        },
        {
            icon: '📊',
            title: 'Dynamic Analysis',
            description: 'Ask questions in natural language and get code-generated insights',
            color: 'from-green-500 to-emerald-500',
        },
    ];

    return (
        <div className="space-y-12 animate-fade-in">
            {/* Hero Section */}
            <div className="text-center space-y-6 py-12">
                <h1 className="text-6xl font-bold bg-gradient-to-r from-primary-400 via-purple-400 to-pink-400 bg-clip-text text-transparent animate-pulse-slow">
                    Agentic Data Analysis
                </h1>
                <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                    A production-grade multi-agent AI system for intelligent data analysis and visualization
                </p>

                {currentDataset ? (
                    <div className="card max-w-md mx-auto">
                        <p className="text-sm text-gray-400 mb-2">Current Dataset</p>
                        <p className="text-lg font-semibold text-primary-400">{currentDataset.filename}</p>
                        <p className="text-sm text-gray-400 mt-1">
                            {currentDataset.rows} rows × {currentDataset.columns} columns
                        </p>
                        <Link to="/analysis" className="btn-primary mt-4 inline-block">
                            Start Analysis →
                        </Link>
                    </div>
                ) : (
                    <Link to="/upload" className="btn-primary inline-block text-lg px-8 py-3">
                        Upload Dataset to Get Started
                    </Link>
                )}
            </div>

            {/* Features Grid */}
            <div className="grid md:grid-cols-2 gap-6">
                {features.map((feature, index) => (
                    <div
                        key={index}
                        className="card hover:scale-105 transition-transform duration-300 animate-slide-up"
                        style={{ animationDelay: `${index * 100}ms` }}
                    >
                        <div className={`text-4xl mb-4 bg-gradient-to-r ${feature.color} bg-clip-text text-transparent`}>
                            {feature.icon}
                        </div>
                        <h3 className="text-xl font-bold mb-2 text-white">{feature.title}</h3>
                        <p className="text-gray-400">{feature.description}</p>
                    </div>
                ))}
            </div>

            {/* Quick Actions */}
            <div className="card">
                <h2 className="text-2xl font-bold mb-6 text-white">Quick Actions</h2>
                <div className="grid md:grid-cols-3 gap-4">
                    <Link to="/upload" className="btn-secondary text-center py-4">
                        📤 Upload New Dataset
                    </Link>
                    <Link to="/suggestions" className="btn-secondary text-center py-4">
                        💡 Get Suggestions
                    </Link>
                    <Link to="/visualizations" className="btn-secondary text-center py-4">
                        📈 View Visualizations
                    </Link>
                </div>
            </div>

            {/* System Info */}
            <div className="card bg-gradient-to-r from-gray-800/30 to-gray-800/50">
                <h3 className="text-lg font-semibold mb-4 text-white">System Architecture</h3>
                <div className="space-y-2 text-sm text-gray-300">
                    <p>✓ <span className="font-semibold">Backend:</span> FastAPI with async support</p>
                    <p>✓ <span className="font-semibold">Agents:</span> Analysis, Visualization, Suggestions, RAG</p>
                    <p>✓ <span className="font-semibold">LLM Providers:</span> Groq (Free), OpenAI, Anthropic</p>
                    <p>✓ <span className="font-semibold">Vector Store:</span> ChromaDB for semantic search</p>
                    <p>✓ <span className="font-semibold">Frontend:</span> React + Vite + TailwindCSS</p>
                </div>
            </div>
        </div>
    );
}
