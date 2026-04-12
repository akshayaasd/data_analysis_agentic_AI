import React, { useState, useEffect } from 'react';
import { visualizationAPI } from '../services/api';
import Plotly from 'plotly.js/dist/plotly.min.js';
import createPlotlyComponent from 'react-plotly.js/factory';

const Plot = createPlotlyComponent(Plotly);

export default function PlotViewer({ plotId }) {
    const [plotData, setPlotData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPlot = async () => {
            try {
                setLoading(true);
                console.log(`Fetching plot: ${plotId}`);
                const data = await visualizationAPI.get(plotId);
                console.log('Plot data received:', data);
                setPlotData(data);
            } catch (err) {
                console.error('Failed to fetch plot:', err);
                setError('Failed to load visualization');
            } finally {
                setLoading(false);
            }
        };

        if (plotId) {
            fetchPlot();
        }
    }, [plotId]);

    if (loading) {
        return (
            <div className="bg-gray-800 rounded-lg p-8 flex flex-col items-center justify-center space-y-4 animate-pulse">
                <div className="text-4xl animate-bounce">📊</div>
                <p className="text-gray-400">Loading visualization...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 text-center">
                <p className="text-red-400">❌ {error}</p>
                <p className="text-xs text-gray-500 mt-2">{plotId}</p>
            </div>
        );
    }

    if (!plotData) return null;

    return (
        <div className="visualization-container bg-gray-900/40 border border-gray-700/50 rounded-xl p-4 overflow-hidden shadow-2xl mt-4 group transition-all duration-500 hover:border-primary-500/30">
            <Plot
                data={plotData.data.map(trace => ({
                    ...trace,
                    marker: {
                        ...trace.marker,
                        colorscale: trace.marker?.colorscale || 'Viridis',
                        line: { ...trace.marker?.line, color: 'rgba(255,255,255,0.2)', width: 1 }
                    }
                }))}
                layout={{
                    ...plotData.layout,
                    autosize: true,
                    margin: { l: 60, r: 30, t: 50, b: 60 },
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: { 
                        family: 'Outfit, Inter, sans-serif',
                        color: '#f3f4f6' 
                    },
                    xaxis: {
                        ...plotData.layout?.xaxis,
                        gridcolor: 'rgba(255,255,255,0.1)',
                        zerolinecolor: 'rgba(255,255,255,0.2)',
                        tickfont: { color: '#9ca3af' }
                    },
                    yaxis: {
                        ...plotData.layout?.yaxis,
                        gridcolor: 'rgba(255,255,255,0.1)',
                        zerolinecolor: 'rgba(255,255,255,0.2)',
                        tickfont: { color: '#9ca3af' }
                    },
                    colorway: ['#33B5E5', '#8B5CF6', '#F59E0B', '#10B981', '#EC4899', '#3B82F6'],
                    template: 'plotly_dark'
                }}
                useResizeHandler={true}
                style={{ width: '100%', height: '450px' }}
                config={{ 
                    responsive: true, 
                    displayModeBar: 'hover', 
                    displaylogo: false,
                    modeBarButtonsToRemove: ['select2d', 'lasso2d']
                }}
            />
        </div>
    );
}
