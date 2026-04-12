/**
 * API service for backend communication
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Data API
export const dataAPI = {
    upload: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post('/api/data/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    getInfo: async (datasetId) => {
        const response = await api.get(`/api/data/info/${datasetId}`);
        return response.data;
    },

    getPreview: async (datasetId, nRows = 10) => {
        const response = await api.get(`/api/data/preview/${datasetId}?n_rows=${nRows}`);
        return response.data;
    },

    getRecords: async (datasetId, limit = 5000) => {
        const response = await api.get(`/api/data/records/${datasetId}?limit=${limit}`);
        return response.data;
    },

    list: async () => {
        const response = await api.get('/api/data/list');
        return response.data;
    },

    delete: async (datasetId) => {
        const response = await api.delete(`/api/data/${datasetId}`);
        return response.data;
    },
};

// Chat API
export const chatAPI = {
    sendMessage: async (message, sessionId = null, datasetId = null, llmProvider = null) => {
        const response = await api.post('/api/chat/message', {
            message,
            session_id: sessionId,
            dataset_id: datasetId,
            llm_provider: llmProvider,
        });
        return response.data;
    },

    getHistory: async (sessionId) => {
        const response = await api.get(`/api/chat/history/${sessionId}`);
        return response.data;
    },

    clearSession: async (sessionId) => {
        const response = await api.delete(`/api/chat/session/${sessionId}`);
        return response.data;
    },
};

// Suggestions API
export const suggestionsAPI = {
    get: async (datasetId, llmProvider = null) => {
        const providerQuery = llmProvider ? `?llm_provider=${llmProvider}` : '';
        const url = `/api/suggestions/${datasetId}${providerQuery}`;
        const response = await api.get(url);
        return response.data;
    },
};

// Visualization API
export const visualizationAPI = {
    get: async (plotId) => {
        const response = await api.get(`/api/visualization/${plotId}`);
        return response.data;
    },

    list: async (datasetId) => {
        const response = await api.get(`/api/visualization/list/${datasetId}`);
        return response.data;
    },
};

export default api;
