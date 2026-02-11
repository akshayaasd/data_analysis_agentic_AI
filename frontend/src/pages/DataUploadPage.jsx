import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { dataAPI } from '../services/api';

export default function DataUploadPage() {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);
    const [preview, setPreview] = useState(null);
    const { setCurrentDataset } = useApp();
    const navigate = useNavigate();

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            setFile(droppedFile);
            setError(null);
        }
    }, []);

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
    }, []);

    const handleFileSelect = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setError(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setError(null);

        try {
            const result = await dataAPI.upload(file);
            setCurrentDataset(result.info);
            setPreview(result.preview);

            // Navigate to analysis page after 2 seconds
            setTimeout(() => {
                navigate('/analysis');
            }, 2000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to upload file');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
            <div className="text-center">
                <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-primary-400 to-purple-400 bg-clip-text text-transparent">
                    Upload Your Dataset
                </h1>
                <p className="text-gray-400">
                    Upload a CSV or Excel file to start analyzing your data with AI agents
                </p>
            </div>

            {/* Upload Area */}
            <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                className="card border-2 border-dashed border-gray-600 hover:border-primary-500 transition-colors cursor-pointer"
            >
                <div className="text-center py-12">
                    <div className="text-6xl mb-4">📁</div>
                    <p className="text-xl font-semibold mb-2 text-white">
                        Drag and drop your file here
                    </p>
                    <p className="text-gray-400 mb-4">or</p>
                    <label className="btn-primary cursor-pointer inline-block">
                        Choose File
                        <input
                            type="file"
                            accept=".csv,.xlsx,.xls"
                            onChange={handleFileSelect}
                            className="hidden"
                        />
                    </label>
                    <p className="text-sm text-gray-500 mt-4">
                        Supported formats: CSV, Excel (.xlsx, .xls)
                    </p>
                </div>
            </div>

            {/* Selected File */}
            {file && (
                <div className="card bg-primary-900/20 border-primary-700">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <div className="text-4xl">📄</div>
                            <div>
                                <p className="font-semibold text-white">{file.name}</p>
                                <p className="text-sm text-gray-400">
                                    {(file.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={handleUpload}
                            disabled={uploading}
                            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {uploading ? 'Uploading...' : 'Upload & Analyze'}
                        </button>
                    </div>
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div className="card bg-red-900/20 border-red-700">
                    <p className="text-red-400">❌ {error}</p>
                </div>
            )}

            {/* Preview */}
            {preview && (
                <div className="card animate-slide-up">
                    <h3 className="text-xl font-bold mb-4 text-white">✅ Upload Successful!</h3>
                    <p className="text-gray-400 mb-4">Preview of your data:</p>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-gray-700">
                                    {Object.keys(preview[0] || {}).map((key) => (
                                        <th key={key} className="text-left p-2 text-gray-300 font-semibold">
                                            {key}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {preview.slice(0, 5).map((row, i) => (
                                    <tr key={i} className="border-b border-gray-800">
                                        {Object.values(row).map((value, j) => (
                                            <td key={j} className="p-2 text-gray-400">
                                                {String(value)}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    <p className="text-sm text-gray-500 mt-4">
                        Redirecting to analysis page...
                    </p>
                </div>
            )}
        </div>
    );
}
