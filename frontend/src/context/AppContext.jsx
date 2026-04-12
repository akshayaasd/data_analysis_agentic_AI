/**
 * Application Context for global state management
 */
import React, { createContext, useContext, useState, useEffect } from 'react';

const AppContext = createContext();

export const useApp = () => {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useApp must be used within AppProvider');
    }
    return context;
};

export const AppProvider = ({ children }) => {
    const allowedProviders = new Set(['groq']);

    // Initial state from localStorage with error handling
    const [currentDataset, setCurrentDataset] = useState(() => {
        try {
            const saved = localStorage.getItem('currentDataset');
            return saved ? JSON.parse(saved) : null;
        } catch (e) {
            console.error('Failed to parse currentDataset from localStorage:', e);
            localStorage.removeItem('currentDataset');
            return null;
        }
    });

    const [sessionId, setSessionId] = useState(() => {
        return localStorage.getItem('sessionId') || null;
    });

    const [llmProvider, setLlmProvider] = useState(() => {
        const saved = (localStorage.getItem('llmProvider') || '').toLowerCase().trim();
        return allowedProviders.has(saved) ? saved : 'groq';
    });

    const [apiKey, setApiKey] = useState(() => {
        return localStorage.getItem('apiKey') || '';
    });

    const [messages, setMessages] = useState(() => {
        try {
            const saved = localStorage.getItem('messages');
            const parsed = saved ? JSON.parse(saved) : [];
            return Array.isArray(parsed) ? parsed : [];
        } catch (e) {
            console.error('Failed to parse messages from localStorage:', e);
            localStorage.removeItem('messages');
            return [];
        }
    });

    const [suggestionsList, setSuggestionsList] = useState(() => {
        try {
            const saved = localStorage.getItem('suggestionsList');
            const parsed = saved ? JSON.parse(saved) : [];
            return Array.isArray(parsed) ? parsed : [];
        } catch (e) {
            console.error('Failed to parse suggestionsList from localStorage:', e);
            localStorage.removeItem('suggestionsList');
            return [];
        }
    });

    const [suggestionResults, setSuggestionResults] = useState(() => {
        try {
            const saved = localStorage.getItem('suggestionResults');
            return saved ? JSON.parse(saved) : {};
        } catch (e) {
            console.error('Failed to parse suggestionResults from localStorage:', e);
            localStorage.removeItem('suggestionResults');
            return {};
        }
    });

    // Persistence Hooks
    useEffect(() => {
        if (currentDataset) localStorage.setItem('currentDataset', JSON.stringify(currentDataset));
        else localStorage.removeItem('currentDataset');
    }, [currentDataset]);

    useEffect(() => {
        if (sessionId) localStorage.setItem('sessionId', sessionId);
        else localStorage.removeItem('sessionId');
    }, [sessionId]);

    useEffect(() => {
        const normalized = (llmProvider || '').toLowerCase().trim();
        const safeProvider = allowedProviders.has(normalized) ? normalized : 'groq';
        if (safeProvider !== llmProvider) {
            setLlmProvider(safeProvider);
            return;
        }
        localStorage.setItem('llmProvider', safeProvider);
    }, [llmProvider]);

    useEffect(() => {
        localStorage.setItem('apiKey', apiKey);
    }, [apiKey]);

    useEffect(() => {
        localStorage.setItem('messages', JSON.stringify(messages));
    }, [messages]);

    useEffect(() => {
        localStorage.setItem('suggestionsList', JSON.stringify(suggestionsList));
    }, [suggestionsList]);

    useEffect(() => {
        localStorage.setItem('suggestionResults', JSON.stringify(suggestionResults));
    }, [suggestionResults]);

    const value = {
        currentDataset,
        setCurrentDataset,
        sessionId,
        setSessionId,
        llmProvider,
        setLlmProvider,
        apiKey,
        setApiKey,
        messages,
        setMessages,
        suggestionsList,
        setSuggestionsList,
        suggestionResults,
        setSuggestionResults,
    };

    return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
