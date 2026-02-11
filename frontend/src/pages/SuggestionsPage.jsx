import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { suggestionsAPI, chatAPI } from '../services/api';

export default function SuggestionsPage() {
    const { currentDataset, llmProvider } = useApp();
    const [suggestions, setSuggestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [executing, setExecuting] = useState(null);
    const [results, setResults] = useState({});

    useEffect(() => {
        if (currentDataset) {
            loadSuggestions();
        }
    }, [currentDataset]);

    const loadSuggestions = async () => {
        setLoading(true);
        try {
            const data = await suggestionsAPI.get(currentDataset.dataset_id, llmProvider);
            setSuggestions(data.suggestions);
        } catch (error) {
            console.error('Failed to load suggestions:', error);
        } finally {
            setLoading(false);
        }
    };

    const executeSuggestion = async (suggestion) => {
        setExecuting(suggestion.suggestion_id);
        try {
            const response = await chatAPI.sendMessage(
                suggestion.query,
                null,
                currentDataset.dataset_id,
                llmProvider
            );
            setResults((prev) => ({
                ...prev,
                [suggestion.suggestion_id]: response.message,
            }));
        } catch (error) {
            setResults((prev) => ({
                ...prev,
                [suggestion.suggestion_id]: 'Error: ' + (error.response?.data?.detail || 'Failed to execute'),
            }));
        } finally {
            setExecuting(null);
        }
    };

    if (!currentDataset) {
        return (
            <div className="text-center py-12">
                <div className="text-6xl mb-4">💡</div>
                <h2 className="text-2xl font-bold mb-4 text-white">No Dataset Loaded</h2>
                <p className="text-gray-400 mb-6">Please upload a dataset first to get suggestions</p>
                <a href="/upload" className="btn-primary inline-block">
                    Upload Dataset
                </a>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">
            {/* Header */}
            <div className="text-center">
                <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
                    💡 Smart Suggestions
                </h1>
                <p className="text-gray-400">
                    AI-powered recommendations for analyzing <span className="text-primary-400 font-semibold">{currentDataset.filename}</span>
                </p>
            </div>

            {loading ? (
                <div className="text-center py-12">
                    <div className="text-6xl mb-4 animate-pulse">🤖</div>
                    <p className="text-gray-400">Analyzing your dataset and generating suggestions...</p>
                </div>
            ) : (
                <div className="grid md:grid-cols-3 gap-6">
                    {suggestions.map((suggestion, index) => (
                        <div
                            key={suggestion.suggestion_id}
                            className="card hover:scale-105 transition-transform duration-300 animate-slide-up"
                            style={{ animationDelay: `${index * 100}ms` }}
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="text-3xl">
                                    {suggestion.category === 'visualization' ? '📊' : '🔍'}
                                </div>
                                <div className="flex items-center space-x-1">
                                    {[...Array(5)].map((_, i) => (
                                        <span
                                            key={i}
                                            className={`text-lg ${i < Math.round(suggestion.confidence * 5)
                                                    ? 'text-yellow-400'
                                                    : 'text-gray-600'
                                                }`}
                                        >
                                            ⭐
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <h3 className="text-xl font-bold mb-2 text-white">{suggestion.title}</h3>
                            <p className="text-gray-400 text-sm mb-4">{suggestion.description}</p>

                            <div className="bg-gray-900/50 rounded p-3 mb-4">
                                <p className="text-xs text-gray-500 mb-1">Expected Insight:</p>
                                <p className="text-sm text-gray-300">{suggestion.expected_insight}</p>
                            </div>

                            <button
                                onClick={() => executeSuggestion(suggestion)}
                                disabled={executing === suggestion.suggestion_id}
                                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {executing === suggestion.suggestion_id ? 'Executing...' : 'Execute'}
                            </button>

                            {results[suggestion.suggestion_id] && (
                                <div className="mt-4 bg-green-900/20 border border-green-700 rounded p-3">
                                    <p className="text-sm text-green-300">{results[suggestion.suggestion_id]}</p>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {!loading && suggestions.length === 0 && (
                <div className="text-center py-12">
                    <p className="text-gray-400">No suggestions available. Try uploading a different dataset.</p>
                </div>
            )}
        </div>
    );
}
