import React, { useState, useRef, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { chatAPI } from '../services/api';
import PlotViewer from '../components/PlotViewer';

export default function AnalysisPage() {
    const { currentDataset, sessionId, setSessionId, llmProvider } = useApp();
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSend = async () => {
        if (!input.trim() || !currentDataset) return;

        const userMessage = { role: 'user', content: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await chatAPI.sendMessage(
                input,
                sessionId,
                currentDataset.dataset_id,
                llmProvider
            );

            if (!sessionId) {
                setSessionId(response.session_id);
            }

            const assistantMessage = {
                role: 'assistant',
                content: response.message,
                code: response.code_executed,
                plots: response.plots,
                metadata: response.metadata,
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            const errorMessage = {
                role: 'error',
                content: error.response?.data?.detail || 'Failed to get response',
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    if (!currentDataset) {
        return (
            <div className="text-center py-12">
                <div className="text-6xl mb-4">📊</div>
                <h2 className="text-2xl font-bold mb-4 text-white">No Dataset Loaded</h2>
                <p className="text-gray-400 mb-6">Please upload a dataset first to start analysis</p>
                <a href="/upload" className="btn-primary inline-block">
                    Upload Dataset
                </a>
            </div>
        );
    }

    return (
        <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
            {/* Header */}
            <div className="card">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-white mb-1">Analysis Chat</h1>
                        <p className="text-sm text-gray-400">
                            Dataset: <span className="text-primary-400 font-semibold">{currentDataset.filename}</span>
                        </p>
                    </div>
                    <div className="text-sm text-gray-400">
                        {currentDataset.rows} rows × {currentDataset.columns} columns
                    </div>
                </div>
            </div>

            {/* Chat Messages */}
            <div className="card h-[500px] overflow-y-auto space-y-4">
                {messages.length === 0 ? (
                    <div className="text-center py-12 text-gray-500">
                        <p className="text-lg mb-4">👋 Ask me anything about your data!</p>
                        <div className="space-y-2 text-sm">
                            <p>Try: "What's the average sales by region?"</p>
                            <p>Or: "Create a bar chart of product sales"</p>
                            <p>Or: "Show me the top 5 products by profit"</p>
                        </div>
                    </div>
                ) : (
                    messages.map((msg, i) => (
                        <div
                            key={i}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-[80%] rounded-lg p-4 ${msg.role === 'user'
                                    ? 'bg-primary-600 text-white'
                                    : msg.role === 'error'
                                        ? 'bg-red-900/50 text-red-300'
                                        : 'bg-gray-700 text-gray-100'
                                    }`}
                            >
                                <p className="whitespace-pre-wrap">{msg.content}</p>
                                {msg.code && (
                                    <div className="mt-3 bg-gray-900 rounded p-3 text-sm">
                                        <p className="text-gray-400 text-xs mb-2">Code executed:</p>
                                        <pre className="text-green-400 overflow-x-auto">{msg.code}</pre>
                                    </div>
                                )}
                                {msg.plots && msg.plots.length > 0 && (
                                    <div className="mt-4 space-y-4">
                                        {msg.plots.map((plotId) => (
                                            <PlotViewer key={plotId} plotId={plotId} />
                                        ))}
                                    </div>
                                )}
                                {msg.metadata && (
                                    <p className="text-xs text-gray-400 mt-2">
                                        {msg.metadata.steps} steps • {msg.metadata.execution_time?.toFixed(2)}s
                                    </p>
                                )}
                            </div>
                        </div>
                    ))
                )}
                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-700 rounded-lg p-4">
                            <div className="flex space-x-2">
                                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="card">
                <div className="flex space-x-4">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask a question about your data..."
                        className="input-field flex-1"
                        disabled={loading}
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading || !input.trim()}
                        className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Thinking...' : 'Send'}
                    </button>
                </div>
            </div>
        </div>
    );
}
