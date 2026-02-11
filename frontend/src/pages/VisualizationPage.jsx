import React from 'react';
import { useApp } from '../context/AppContext';

export default function VisualizationPage() {
    const { currentDataset } = useApp();

    if (!currentDataset) {
        return (
            <div className="text-center py-12">
                <div className="text-6xl mb-4">📈</div>
                <h2 className="text-2xl font-bold mb-4 text-white">No Dataset Loaded</h2>
                <p className="text-gray-400 mb-6">Please upload a dataset and create visualizations first</p>
                <a href="/upload" className="btn-primary inline-block">
                    Upload Dataset
                </a>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">
            <div className="text-center">
                <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
                    📈 Visualizations
                </h1>
                <p className="text-gray-400">
                    Interactive charts and graphs for <span className="text-primary-400 font-semibold">{currentDataset.filename}</span>
                </p>
            </div>

            <div className="card">
                <div className="text-center py-12">
                    <div className="text-6xl mb-4">🎨</div>
                    <h3 className="text-xl font-semibold mb-2 text-white">Create Visualizations</h3>
                    <p className="text-gray-400 mb-6">
                        Go to the Analysis page and ask the agent to create charts
                    </p>
                    <a href="/analysis" className="btn-primary inline-block">
                        Go to Analysis
                    </a>
                </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                <div className="card">
                    <h3 className="text-lg font-semibold mb-4 text-white">Example Queries</h3>
                    <div className="space-y-2 text-sm text-gray-300">
                        <p>• "Create a bar chart of sales by region"</p>
                        <p>• "Show me a line chart of sales over time"</p>
                        <p>• "Make a scatter plot of sales vs profit"</p>
                        <p>• "Generate a histogram of product quantities"</p>
                    </div>
                </div>

                <div className="card">
                    <h3 className="text-lg font-semibold mb-4 text-white">Supported Chart Types</h3>
                    <div className="space-y-2 text-sm text-gray-300">
                        <p>📊 Bar Charts • Line Charts • Scatter Plots</p>
                        <p>📈 Histograms • Box Plots • Heatmaps</p>
                        <p>🥧 Pie Charts • Area Charts • Bubble Charts</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
