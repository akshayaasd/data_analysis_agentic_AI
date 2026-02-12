import React, { useState, useEffect, useCallback } from 'react';
import { useApp } from '../context/AppContext';
import { suggestionsAPI, chatAPI } from '../services/api';
import PlotViewer from '../components/PlotViewer';

export default function SuggestionsPage() {
    const {
        currentDataset,
        llmProvider,
        suggestionsList,
        setSuggestionsList,
        suggestionResults,
        setSuggestionResults
    } = useApp();
    const [loading, setLoading] = useState(false);
    const [executing, setExecuting] = useState(null);

    const loadSuggestions = useCallback(async () => {
        setLoading(true);
        try {
            const data = await suggestionsAPI.get(currentDataset.dataset_id, llmProvider);
            setSuggestionsList(data.suggestions);
        } catch (error) {
            console.error('Failed to load suggestions:', error);
        } finally {
            setLoading(false);
        }
    }, [currentDataset?.dataset_id, llmProvider, setSuggestionsList]);

    useEffect(() => {
        if (currentDataset && suggestionsList.length === 0) {
            loadSuggestions();
        }
    }, [currentDataset, suggestionsList.length, loadSuggestions]);

    const executeSuggestion = async (suggestion) => {
        setExecuting(suggestion.suggestion_id);
        try {
            const response = await chatAPI.sendMessage(
                suggestion.query,
                null,
                currentDataset.dataset_id,
                llmProvider
            );
            setSuggestionResults((prev) => ({
                ...prev,
                [suggestion.suggestion_id]: {
                    message: response.message,
                    plots: response.plots
                },
            }));
        } catch (error) {
            setSuggestionResults((prev) => ({
                ...prev,
                [suggestion.suggestion_id]: 'Error: ' + (error.response?.data?.detail || 'Failed to execute'),
            }));
        } finally {
            setExecuting(null);
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between mb-2">
                <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                    <span>💡</span>
                    <span>AI-Generated Insights</span>
                </h2>
                <button
                    onClick={loadSuggestions}
                    disabled={loading}
                    className="text-xs font-semibold text-primary-400 hover:text-primary-300 transition-colors uppercase tracking-widest disabled:opacity-50"
                >
                    {loading ? 'Refreshing...' : 'Refresh Suggestions'}
                </button>
            </div>

            {/* Suggestions List */}
            {loading ? (
                <div className="text-center py-12">
                    <div className="text-6xl mb-4 animate-pulse">🤖</div>
                    <p className="text-gray-400">Analyzing your dataset and generating suggestions...</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {suggestionsList.map((suggestion, index) => (
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

                            {suggestionResults[suggestion.suggestion_id] && (
                                <div className="mt-4 bg-gray-900/40 border border-gray-700 rounded p-4">
                                    <p className="text-sm text-gray-200 mb-2">
                                        {typeof suggestionResults[suggestion.suggestion_id] === 'string'
                                            ? suggestionResults[suggestion.suggestion_id]
                                            : suggestionResults[suggestion.suggestion_id].message}
                                    </p>

                                    {suggestionResults[suggestion.suggestion_id].plots && suggestionResults[suggestion.suggestion_id].plots.length > 0 && (
                                        <div className="mt-4 space-y-4">
                                            {suggestionResults[suggestion.suggestion_id].plots.map((plotId) => (
                                                <PlotViewer key={plotId} plotId={plotId} />
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {!loading && suggestionsList.length === 0 && (
                <div className="text-center py-12">
                    <p className="text-gray-400">No suggestions available. Try uploading a different dataset.</p>
                </div>
            )}
        </div>
    );
}
