import React, { useState, useEffect, useCallback } from 'react';
import { useApp } from '../context/AppContext';
import { visualizationAPI } from '../services/api';
import PlotViewer from '../components/PlotViewer';

export default function VisualizationPage() {
    const { currentDataset } = useApp();
    const [plots, setPlots] = useState([]);
    const [loading, setLoading] = useState(false);

    const loadPlots = useCallback(async () => {
        setLoading(true);
        try {
            const data = await visualizationAPI.list(currentDataset.dataset_id);
            setPlots(data.plots || []);
        } catch (error) {
            console.error('Failed to load plots:', error);
        } finally {
            setLoading(false);
        }
    }, [currentDataset?.dataset_id]);

    useEffect(() => {
        if (currentDataset) {
            loadPlots();
        }
    }, [currentDataset, loadPlots]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-pulse">
                <div className="text-6xl mb-4">📊</div>
                <p className="text-gray-400">Loading your visualization gallery...</p>
            </div>
        );
    }

    if (plots.length === 0) {
        return (
            <div className="text-center py-20 bg-gray-800/30 rounded-2xl border border-gray-700/50 border-dashed animate-fade-in">
                <div className="text-6xl mb-4">📉</div>
                <h3 className="text-xl font-bold text-white mb-2">No Visualizations Yet</h3>
                <p className="text-gray-400 max-w-md mx-auto">
                    Go to the Chat Analysis tab and ask the AI to create some charts!
                    They will automatically appear here once generated.
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-1">Chart Gallery</h2>
                    <p className="text-gray-400 text-sm">All visualizations generated for this dataset</p>
                </div>
                <button
                    onClick={loadPlots}
                    className="text-primary-400 hover:text-primary-300 text-sm font-medium transition-colors"
                >
                    Refresh Gallery
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {plots.map((plotId, index) => (
                    <div
                        key={plotId}
                        className="card overflow-hidden group hover:border-primary-500/50 transition-all duration-500 animate-slide-up"
                        style={{ animationDelay: `${index * 100}ms` }}
                    >
                        <div className="p-4 border-b border-gray-700 bg-gray-800/50 flex items-center justify-between">
                            <span className="text-xs font-mono text-gray-400 uppercase tracking-wider">
                                {plotId.split('_').slice(1).join('_') || 'Visualization'}
                            </span>
                            <div className="w-2 h-2 rounded-full bg-primary-500 shadow-[0_0_8px_rgba(var(--color-primary-500),0.6)]"></div>
                        </div>
                        <div className="p-2">
                            <PlotViewer plotId={plotId} />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
