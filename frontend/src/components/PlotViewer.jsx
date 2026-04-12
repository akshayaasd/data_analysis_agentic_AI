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
        <div className="visualization-container bg-white rounded-lg p-2 overflow-hidden shadow-xl mt-4">
            <Plot
                data={plotData.data}
                layout={{
                    ...plotData.layout,
                    autosize: true,
                    margin: { l: 50, r: 30, t: 50, b: 50 },
                    paper_bgcolor: 'rgba(255,255,255,1)',
                    plot_bgcolor: 'rgba(255,255,255,1)',
                    font: { family: 'Inter, sans-serif' },
                }}
                useResizeHandler={true}
                style={{ width: '100%', height: '400px' }}
                config={{ responsive: true, displayModeBar: true, displaylogo: false }}
            />
        </div>
    );
}
