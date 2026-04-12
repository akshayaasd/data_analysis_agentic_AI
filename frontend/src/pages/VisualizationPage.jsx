import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useApp } from '../context/AppContext';
import { dataAPI, visualizationAPI } from '../services/api';
import PlotViewer from '../components/PlotViewer';
import Plotly from 'plotly.js/dist/plotly.min.js';
import createPlotlyComponent from 'react-plotly.js/factory';

const Plot = createPlotlyComponent(Plotly);

const isNumericValue = (value) => {
    if (value === null || value === undefined || value === '') return false;
    return Number.isFinite(Number(value));
};

const toNumber = (value) => {
    if (!isNumericValue(value)) return null;
    return Number(value);
};

const tryParseDate = (value) => {
    if (typeof value !== 'string') return null;
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return null;
    return parsed;
};

const pearsonCorrelation = (xValues, yValues) => {
    const pairs = [];
    for (let i = 0; i < xValues.length; i += 1) {
        const x = toNumber(xValues[i]);
        const y = toNumber(yValues[i]);
        if (x !== null && y !== null) {
            pairs.push([x, y]);
        }
    }

    if (pairs.length < 3) return null;

    const n = pairs.length;
    const sumX = pairs.reduce((acc, [x]) => acc + x, 0);
    const sumY = pairs.reduce((acc, [, y]) => acc + y, 0);
    const meanX = sumX / n;
    const meanY = sumY / n;

    let covariance = 0;
    let varianceX = 0;
    let varianceY = 0;

    pairs.forEach(([x, y]) => {
        const dx = x - meanX;
        const dy = y - meanY;
        covariance += dx * dy;
        varianceX += dx * dx;
        varianceY += dy * dy;
    });

    if (varianceX === 0 || varianceY === 0) return null;

    return covariance / Math.sqrt(varianceX * varianceY);
};

const calcPercent = (part, whole) => {
    if (!whole) return 0;
    return (part / whole) * 100;
};

export default function VisualizationPage() {
    const { currentDataset } = useApp();
    const [plots, setPlots] = useState([]);
    const [records, setRecords] = useState([]);
    const [datasetInfo, setDatasetInfo] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [metricColumn, setMetricColumn] = useState('');
    const [categoryColumn, setCategoryColumn] = useState('');
    const [xScatterColumn, setXScatterColumn] = useState('');
    const [yScatterColumn, setYScatterColumn] = useState('');
    const [chartMode, setChartMode] = useState('bar');
    const [aggregation, setAggregation] = useState('mean');
    const [topN, setTopN] = useState(10);

    const loadPlots = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const [plotsData, infoData, recordsData] = await Promise.all([
                visualizationAPI.list(currentDataset.dataset_id),
                dataAPI.getInfo(currentDataset.dataset_id),
                dataAPI.getRecords(currentDataset.dataset_id, 5000),
            ]);

            setPlots(plotsData.plots || []);
            setDatasetInfo(infoData);
            setRecords(recordsData.records || []);
        } catch (error) {
            console.error('Failed to load plots:', error);
            setError('Failed to load visualization data. Please refresh and try again.');
        } finally {
            setLoading(false);
        }
    }, [currentDataset?.dataset_id]);

    useEffect(() => {
        if (currentDataset) {
            loadPlots();
        }
    }, [currentDataset, loadPlots]);

    const columns = useMemo(() => (records.length > 0 ? Object.keys(records[0]) : []), [records]);

    const numericColumns = useMemo(() => {
        return columns.filter((column) => {
            const values = records.map((row) => row[column]).filter((value) => value !== null && value !== undefined && value !== '');
            if (values.length === 0) return false;
            const numericCount = values.filter(isNumericValue).length;
            return numericCount / values.length >= 0.7;
        });
    }, [columns, records]);

    const dateColumns = useMemo(() => {
        return columns.filter((column) => {
            const values = records.map((row) => row[column]).filter((value) => typeof value === 'string' && value.trim().length > 0);
            if (values.length === 0) return false;
            const dateCount = values.filter((value) => tryParseDate(value) !== null).length;
            return dateCount / values.length >= 0.7;
        });
    }, [columns, records]);

    const categoricalColumns = useMemo(() => {
        return columns.filter((column) => !numericColumns.includes(column) && !dateColumns.includes(column));
    }, [columns, numericColumns, dateColumns]);

    useEffect(() => {
        if (!metricColumn && numericColumns.length > 0) setMetricColumn(numericColumns[0]);
        if (!categoryColumn && categoricalColumns.length > 0) setCategoryColumn(categoricalColumns[0]);
        if (!xScatterColumn && numericColumns.length > 0) setXScatterColumn(numericColumns[0]);
        if (!yScatterColumn && numericColumns.length > 1) setYScatterColumn(numericColumns[1]);
        else if (!yScatterColumn && numericColumns.length === 1) setYScatterColumn(numericColumns[0]);
    }, [numericColumns, categoricalColumns, metricColumn, categoryColumn, xScatterColumn, yScatterColumn]);

    const qualitySummary = useMemo(() => {
        if (!records.length || !columns.length) {
            return { missingCount: 0, totalCells: 0, missingPct: 0 };
        }

        let missingCount = 0;
        records.forEach((row) => {
            columns.forEach((column) => {
                const value = row[column];
                if (value === null || value === undefined || value === '') {
                    missingCount += 1;
                }
            });
        });

        const totalCells = records.length * columns.length;
        return {
            missingCount,
            totalCells,
            missingPct: calcPercent(missingCount, totalCells),
        };
    }, [records, columns]);

    const strongestCorrelation = useMemo(() => {
        if (numericColumns.length < 2) return null;

        let best = null;
        for (let i = 0; i < numericColumns.length; i += 1) {
            for (let j = i + 1; j < numericColumns.length; j += 1) {
                const xCol = numericColumns[i];
                const yCol = numericColumns[j];
                const corr = pearsonCorrelation(
                    records.map((r) => r[xCol]),
                    records.map((r) => r[yCol])
                );

                if (corr === null) continue;

                if (!best || Math.abs(corr) > Math.abs(best.value)) {
                    best = { x: xCol, y: yCol, value: corr };
                }
            }
        }

        return best;
    }, [numericColumns, records]);

    const metricStats = useMemo(() => {
        if (!metricColumn) return null;

        const values = records.map((row) => toNumber(row[metricColumn])).filter((value) => value !== null);
        if (!values.length) return null;

        const sorted = [...values].sort((a, b) => a - b);
        const sum = values.reduce((acc, value) => acc + value, 0);
        const mean = sum / values.length;
        const median = sorted[Math.floor(sorted.length / 2)];
        const min = sorted[0];
        const max = sorted[sorted.length - 1];

        return {
            mean,
            median,
            min,
            max,
            range: max - min,
            count: values.length,
        };
    }, [records, metricColumn]);

    const groupedMetric = useMemo(() => {
        if (!categoryColumn || !metricColumn) return [];

        const grouped = new Map();
        records.forEach((row) => {
            const category = row[categoryColumn] ?? 'Unknown';
            const numericValue = toNumber(row[metricColumn]);
            if (numericValue === null) return;

            if (!grouped.has(category)) {
                grouped.set(category, { total: 0, count: 0, min: numericValue, max: numericValue });
            }

            const state = grouped.get(category);
            state.total += numericValue;
            state.count += 1;
            state.min = Math.min(state.min, numericValue);
            state.max = Math.max(state.max, numericValue);
        });

        const rows = Array.from(grouped.entries()).map(([category, state]) => {
            const mean = state.total / state.count;
            return {
                category: String(category),
                value: aggregation === 'sum' ? state.total : aggregation === 'max' ? state.max : aggregation === 'min' ? state.min : mean,
                count: state.count,
            };
        });

        return rows.sort((a, b) => b.value - a.value).slice(0, topN);
    }, [records, categoryColumn, metricColumn, aggregation, topN]);

    const distributionValues = useMemo(() => {
        if (!metricColumn) return [];
        return records.map((row) => toNumber(row[metricColumn])).filter((value) => value !== null);
    }, [records, metricColumn]);

    const scatterValues = useMemo(() => {
        if (!xScatterColumn || !yScatterColumn) return [];
        const output = [];

        records.forEach((row) => {
            const x = toNumber(row[xScatterColumn]);
            const y = toNumber(row[yScatterColumn]);
            if (x === null || y === null) return;
            output.push({ x, y, label: categoryColumn ? String(row[categoryColumn] ?? 'Unknown') : '' });
        });

        return output;
    }, [records, xScatterColumn, yScatterColumn, categoryColumn]);

    const correlationHeatmap = useMemo(() => {
        if (numericColumns.length < 2) return null;

        const z = numericColumns.map((rowCol) => (
            numericColumns.map((colCol) => {
                const corr = pearsonCorrelation(
                    records.map((r) => r[rowCol]),
                    records.map((r) => r[colCol])
                );
                return corr === null ? 0 : Number(corr.toFixed(3));
            })
        ));

        return { z, labels: numericColumns };
    }, [numericColumns, records]);

    const insightNarrative = useMemo(() => {
        const lines = [];

        if (metricStats && metricColumn) {
            lines.push(`${metricColumn} average is ${metricStats.mean.toFixed(2)} with a range of ${metricStats.min.toFixed(2)} to ${metricStats.max.toFixed(2)}.`);
        }

        if (strongestCorrelation) {
            lines.push(`Strongest relationship is between ${strongestCorrelation.x} and ${strongestCorrelation.y} (r=${strongestCorrelation.value.toFixed(2)}).`);
        }

        if (groupedMetric.length > 0) {
            const leader = groupedMetric[0];
            lines.push(`${leader.category} currently leads ${metricColumn} based on ${aggregation} aggregation.`);
        }

        if (qualitySummary.totalCells > 0) {
            lines.push(`Data completeness is ${(100 - qualitySummary.missingPct).toFixed(1)}% across ${records.length} loaded rows.`);
        }

        return lines;
    }, [metricStats, metricColumn, strongestCorrelation, groupedMetric, aggregation, qualitySummary, records.length]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center py-20 animate-pulse">
                <div className="text-6xl mb-4">📊</div>
                <p className="text-gray-400">Loading your visualization gallery...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-20 bg-red-900/10 rounded-2xl border border-red-700/40 animate-fade-in">
                <div className="text-5xl mb-4">⚠️</div>
                <h3 className="text-xl font-bold text-white mb-2">Visualization Load Failed</h3>
                <p className="text-gray-300 mb-4">{error}</p>
                <button onClick={loadPlots} className="btn-primary">Try Again</button>
            </div>
        );
    }

    if (plots.length === 0 && records.length === 0) {
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
                    <h2 className="text-2xl font-bold text-white mb-1">Insight Studio</h2>
                    <p className="text-gray-400 text-sm">Interactive insights + generated chart gallery</p>
                </div>
                <button
                    onClick={loadPlots}
                    className="text-primary-400 hover:text-primary-300 text-sm font-medium transition-colors"
                >
                    Refresh Insights
                </button>
            </div>

            {records.length > 0 && (
                <>
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                        <div className="card bg-gray-800/70 border border-gray-700">
                            <p className="text-xs text-gray-400 uppercase tracking-wide">Rows Loaded</p>
                            <p className="text-3xl font-bold text-white mt-1">{records.length}</p>
                            <p className="text-xs text-gray-500 mt-1">of {datasetInfo?.rows || records.length} total rows</p>
                        </div>

                        <div className="card bg-gray-800/70 border border-gray-700">
                            <p className="text-xs text-gray-400 uppercase tracking-wide">Columns</p>
                            <p className="text-3xl font-bold text-white mt-1">{datasetInfo?.columns || columns.length}</p>
                            <p className="text-xs text-gray-500 mt-1">{numericColumns.length} numeric, {categoricalColumns.length} categorical</p>
                        </div>

                        <div className="card bg-gray-800/70 border border-gray-700">
                            <p className="text-xs text-gray-400 uppercase tracking-wide">Data Completeness</p>
                            <p className="text-3xl font-bold text-white mt-1">{(100 - qualitySummary.missingPct).toFixed(1)}%</p>
                            <p className="text-xs text-gray-500 mt-1">{qualitySummary.missingCount} missing cells</p>
                        </div>

                        <div className="card bg-gray-800/70 border border-gray-700">
                            <p className="text-xs text-gray-400 uppercase tracking-wide">Top Correlation</p>
                            <p className="text-lg font-bold text-white mt-1 truncate">
                                {strongestCorrelation
                                    ? `${strongestCorrelation.x} vs ${strongestCorrelation.y}`
                                    : 'Not enough numeric data'}
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                                {strongestCorrelation ? `r = ${strongestCorrelation.value.toFixed(2)}` : 'Need at least 2 numeric columns'}
                            </p>
                        </div>
                    </div>

                    <div className="card bg-gray-800/50 border border-gray-700 space-y-4">
                        <h3 className="text-lg font-semibold text-white">Interactive Controls</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-6 gap-3">
                            <select value={metricColumn} onChange={(e) => setMetricColumn(e.target.value)} className="bg-gray-900 text-white rounded px-3 py-2 border border-gray-700">
                                {numericColumns.map((col) => <option key={col} value={col}>{col}</option>)}
                            </select>

                            <select value={categoryColumn} onChange={(e) => setCategoryColumn(e.target.value)} className="bg-gray-900 text-white rounded px-3 py-2 border border-gray-700">
                                {categoricalColumns.map((col) => <option key={col} value={col}>{col}</option>)}
                            </select>

                            <select value={chartMode} onChange={(e) => setChartMode(e.target.value)} className="bg-gray-900 text-white rounded px-3 py-2 border border-gray-700">
                                <option value="bar">Bar</option>
                                <option value="line">Line</option>
                            </select>

                            <select value={aggregation} onChange={(e) => setAggregation(e.target.value)} className="bg-gray-900 text-white rounded px-3 py-2 border border-gray-700">
                                <option value="mean">Mean</option>
                                <option value="sum">Sum</option>
                                <option value="max">Max</option>
                                <option value="min">Min</option>
                            </select>

                            <select value={xScatterColumn} onChange={(e) => setXScatterColumn(e.target.value)} className="bg-gray-900 text-white rounded px-3 py-2 border border-gray-700">
                                {numericColumns.map((col) => <option key={col} value={col}>X: {col}</option>)}
                            </select>

                            <select value={yScatterColumn} onChange={(e) => setYScatterColumn(e.target.value)} className="bg-gray-900 text-white rounded px-3 py-2 border border-gray-700">
                                {numericColumns.map((col) => <option key={col} value={col}>Y: {col}</option>)}
                            </select>
                        </div>

                        <div className="flex items-center gap-3">
                            <label className="text-sm text-gray-300">Top Categories:</label>
                            <input
                                type="range"
                                min="3"
                                max="20"
                                step="1"
                                value={topN}
                                onChange={(e) => setTopN(Number(e.target.value))}
                                className="w-64"
                            />
                            <span className="text-sm text-white font-semibold">{topN}</span>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                        <div className="card bg-gray-800/40 border border-gray-700">
                            <h3 className="text-base font-semibold text-white mb-2">Category Performance</h3>
                            <Plot
                                data={[
                                    {
                                        type: chartMode,
                                        x: groupedMetric.map((item) => item.category),
                                        y: groupedMetric.map((item) => item.value),
                                        marker: { color: '#33B5E5' },
                                        line: { color: '#33B5E5' },
                                    },
                                ]}
                                layout={{
                                    autosize: true,
                                    paper_bgcolor: 'rgba(0,0,0,0)',
                                    plot_bgcolor: 'rgba(0,0,0,0)',
                                    font: { color: '#e5e7eb' },
                                    margin: { l: 50, r: 20, t: 30, b: 80 },
                                    xaxis: { tickangle: -30 },
                                    yaxis: { title: `${aggregation}(${metricColumn || 'metric'})` },
                                }}
                                config={{ responsive: true, displaylogo: false }}
                                style={{ width: '100%', height: 360 }}
                                useResizeHandler
                            />
                        </div>

                        <div className="card bg-gray-800/40 border border-gray-700">
                            <h3 className="text-base font-semibold text-white mb-2">Metric Distribution</h3>
                            <Plot
                                data={[
                                    {
                                        type: 'histogram',
                                        x: distributionValues,
                                        marker: { color: '#F59E0B' },
                                        nbinsx: 30,
                                    },
                                ]}
                                layout={{
                                    autosize: true,
                                    paper_bgcolor: 'rgba(0,0,0,0)',
                                    plot_bgcolor: 'rgba(0,0,0,0)',
                                    font: { color: '#e5e7eb' },
                                    margin: { l: 50, r: 20, t: 30, b: 50 },
                                    xaxis: { title: metricColumn || 'Metric' },
                                    yaxis: { title: 'Frequency' },
                                }}
                                config={{ responsive: true, displaylogo: false }}
                                style={{ width: '100%', height: 360 }}
                                useResizeHandler
                            />
                        </div>

                        <div className="card bg-gray-800/40 border border-gray-700">
                            <h3 className="text-base font-semibold text-white mb-2">Scatter Explorer</h3>
                            <Plot
                                data={[
                                    {
                                        type: 'scattergl',
                                        mode: 'markers',
                                        x: scatterValues.map((point) => point.x),
                                        y: scatterValues.map((point) => point.y),
                                        text: scatterValues.map((point) => point.label),
                                        marker: {
                                            color: '#8B5CF6',
                                            size: 7,
                                            opacity: 0.65,
                                        },
                                    },
                                ]}
                                layout={{
                                    autosize: true,
                                    paper_bgcolor: 'rgba(0,0,0,0)',
                                    plot_bgcolor: 'rgba(0,0,0,0)',
                                    font: { color: '#e5e7eb' },
                                    margin: { l: 55, r: 20, t: 30, b: 55 },
                                    xaxis: { title: xScatterColumn || 'X' },
                                    yaxis: { title: yScatterColumn || 'Y' },
                                }}
                                config={{ responsive: true, displaylogo: false }}
                                style={{ width: '100%', height: 360 }}
                                useResizeHandler
                            />
                        </div>

                        <div className="card bg-gray-800/40 border border-gray-700">
                            <h3 className="text-base font-semibold text-white mb-2">Correlation Heatmap</h3>
                            {correlationHeatmap ? (
                                <Plot
                                    data={[
                                        {
                                            type: 'heatmap',
                                            z: correlationHeatmap.z,
                                            x: correlationHeatmap.labels,
                                            y: correlationHeatmap.labels,
                                            colorscale: 'RdBu',
                                            zmin: -1,
                                            zmax: 1,
                                        },
                                    ]}
                                    layout={{
                                        autosize: true,
                                        paper_bgcolor: 'rgba(0,0,0,0)',
                                        plot_bgcolor: 'rgba(0,0,0,0)',
                                        font: { color: '#e5e7eb' },
                                        margin: { l: 80, r: 20, t: 30, b: 80 },
                                    }}
                                    config={{ responsive: true, displaylogo: false }}
                                    style={{ width: '100%', height: 360 }}
                                    useResizeHandler
                                />
                            ) : (
                                <p className="text-gray-400 text-sm">Need at least two numeric columns for correlation analysis.</p>
                            )}
                        </div>
                    </div>

                    <div className="card bg-primary-900/10 border border-primary-700/40">
                        <h3 className="text-lg font-semibold text-white mb-3">Auto Insights</h3>
                        <ul className="space-y-2 text-sm text-gray-200 list-disc pl-5">
                            {insightNarrative.map((line, idx) => (
                                <li key={`${line}-${idx}`}>{line}</li>
                            ))}
                        </ul>
                    </div>
                </>
            )}

            <div className="pt-2">
                <h3 className="text-xl font-bold text-white mb-3">Generated Chart Gallery</h3>
                <p className="text-gray-400 text-sm mb-5">Charts created by AI in chat/suggestions continue to appear here.</p>
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

            {plots.length === 0 && (
                <div className="text-center py-12 bg-gray-800/30 rounded-xl border border-gray-700/50 border-dashed">
                    <p className="text-gray-400">No AI-generated charts yet. Ask the Analysis tab to create one.</p>
                </div>
            )}
        </div>
    );
}
