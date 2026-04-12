import React, { useState, useCallback, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ImageAnalysisPage() {
    const [uploadedImages, setUploadedImages] = useState([]);
    const [selectedImageId, setSelectedImageId] = useState(null);
    const [thisImage, setThisImage] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);
    const [error, setError] = useState(null);
    const [dragActive, setDragActive] = useState(false);

    // Load uploaded images
    const loadImages = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.get(`${API_BASE_URL}/api/images/list`);
            setUploadedImages(response.data.images || []);
        } catch (err) {
            console.error('Failed to load images:', err);
            setError('Failed to load images. Please try again.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadImages();
    }, [loadImages]);

    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            handleUpload(droppedFile);
        }
    }, []);

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            handleUpload(file);
        }
    };

    const handleUpload = async (file) => {
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            setError('Unsupported file type. Please upload an image.');
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await axios.post(`${API_BASE_URL}/api/images/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            const newImage = {
                image_id: response.data.image_id,
                filename: response.data.filename,
                upload_time: response.data.upload_time,
                file_size: response.data.file_size
            };

            setUploadedImages([newImage, ...uploadedImages]);
            setSelectedImageId(newImage.image_id);
            setThisImage(newImage);
            setAnalysis(null);
        } catch (err) {
            console.error('Upload failed:', err);
            setError(err.response?.data?.detail || 'Upload failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const analyzeImage = async (imageId) => {
        setAnalyzing(true);
        setError(null);
        try {
            const response = await axios.post(`${API_BASE_URL}/api/images/analyze/${imageId}`);
            setAnalysis(response.data);
        } catch (err) {
            console.error('Analysis failed:', err);
            setError(err.response?.data?.detail || 'Analysis failed. Please try again.');
        } finally {
            setAnalyzing(false);
        }
    };

    const selectImage = (image) => {
        setSelectedImageId(image.image_id);
        setThisImage(image);
        setAnalysis(null);
    };

    const deleteImage = async (imageId) => {
        if (!confirm('Delete this image?')) return;

        try {
            await axios.delete(`${API_BASE_URL}/api/images/${imageId}`);
            setUploadedImages(uploadedImages.filter((img) => img.image_id !== imageId));
            if (selectedImageId === imageId) {
                setSelectedImageId(null);
                setThisImage(null);
                setAnalysis(null);
            }
        } catch (err) {
            console.error('Delete failed:', err);
            setError('Failed to delete image.');
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-1">Image Analysis Studio</h2>
                    <p className="text-gray-400 text-sm">Upload images and get instant AI-powered insights</p>
                </div>
                <button
                    onClick={loadImages}
                    className="text-primary-400 hover:text-primary-300 text-sm font-medium transition-colors"
                >
                    Refresh List
                </button>
            </div>

            {/* Upload Area */}
            <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`card border-2 border-dashed transition-all ${
                    dragActive ? 'border-primary-500 bg-primary-500/5' : 'border-gray-700 hover:border-gray-600'
                }`}
            >
                <div className="text-center py-12">
                    <div className="text-6xl mb-4">🖼️</div>
                    <p className="text-xl font-semibold mb-2 text-white">Drag images here or click to upload</p>
                    <p className="text-gray-400 mb-4">Supported formats: JPG, PNG, GIF, BMP, WebP</p>
                    <label className="btn-primary cursor-pointer inline-block">
                        Choose Image
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleFileSelect}
                            className="hidden"
                        />
                    </label>
                </div>
            </div>

            {/* Error Message */}
            {error && (
                <div className="card bg-red-900/20 border-red-700">
                    <p className="text-red-400">❌ {error}</p>
                </div>
            )}

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                {/* Images List */}
                <div className="card bg-gray-800/40 border border-gray-700 max-h-[600px] overflow-y-auto">
                    <h3 className="text-lg font-semibold text-white mb-4 sticky top-0 bg-gray-800/40 pb-3">
                        📸 Uploaded Images ({uploadedImages.length})
                    </h3>
                    {uploadedImages.length === 0 ? (
                        <p className="text-gray-400 text-sm">No images uploaded yet</p>
                    ) : (
                        <div className="space-y-2">
                            {uploadedImages.map((image) => (
                                <div
                                    key={image.image_id}
                                    className={`p-3 rounded-lg cursor-pointer transition-all ${
                                        selectedImageId === image.image_id
                                            ? 'bg-primary-600/30 border border-primary-500'
                                            : 'bg-gray-700/40 hover:bg-gray-600/40 border border-gray-700'
                                    }`}
                                    onClick={() => selectImage(image)}
                                >
                                    <p className="text-sm font-semibold text-white truncate">{image.filename}</p>
                                    <p className="text-xs text-gray-400 mt-1">
                                        {(image.file_size / 1024).toFixed(1)} KB
                                    </p>
                                    <p className="text-xs text-gray-500">
                                        {new Date(image.upload_time).toLocaleString()}
                                    </p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Analysis Panel */}
                <div className="xl:col-span-2 space-y-4">
                    {thisImage ? (
                        <>
                            <div className="card bg-gray-800/40 border border-gray-700">
                                <h3 className="text-lg font-semibold text-white mb-3">Selected Image</h3>
                                <p className="text-gray-300 text-sm mb-3">{thisImage.filename}</p>
                                <button
                                    onClick={() => analyzeImage(selectedImageId)}
                                    disabled={analyzing}
                                    className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {analyzing ? (
                                        <span className="flex items-center justify-center space-x-2">
                                            <span className="inline-block animate-spin">⏳</span>
                                            <span>Analyzing (this may take a moment)...</span>
                                        </span>
                                    ) : (
                                        '🔍 Analyze Image'
                                    )}
                                </button>

                                {analyzing && (
                                    <div className="mt-4 text-center text-gray-400 text-sm">
                                        Processing image insights with AI...
                                    </div>
                                )}

                                <button
                                    onClick={() => deleteImage(selectedImageId)}
                                    className="w-full mt-2 text-xs text-red-400 hover:text-red-300 border border-red-700 rounded px-3 py-2 transition-colors"
                                >
                                    Delete Image
                                </button>
                            </div>

                            {analysis && (
                                <div className="card bg-primary-900/20 border border-primary-700/40 animate-slide-up">
                                    <h3 className="text-lg font-semibold text-white mb-4">✨ Analysis Results</h3>
                                    <div className="text-gray-200 space-y-3 text-sm leading-relaxed whitespace-pre-wrap">
                                        {analysis.analysis}
                                    </div>
                                    <div className="mt-4 pt-4 border-t border-primary-700/30">
                                        <p className="text-xs text-gray-400">
                                            ⏱️ Processing time: {analysis.execution_time.toFixed(1)}s
                                        </p>
                                    </div>
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="card bg-gray-800/40 border border-gray-700/50 border-dashed text-center py-12">
                            <div className="text-4xl mb-3">📷</div>
                            <p className="text-gray-400">Select an image from the list to analyze</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
