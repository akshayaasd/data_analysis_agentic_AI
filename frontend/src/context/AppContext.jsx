/**
 * Application Context for global state management
 */
import React, { createContext, useContext, useState } from 'react';

const AppContext = createContext();

export const useApp = () => {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useApp must be used within AppProvider');
    }
    return context;
};

export const AppProvider = ({ children }) => {
    const [currentDataset, setCurrentDataset] = useState(null);
    const [sessionId, setSessionId] = useState(null);
    const [llmProvider, setLlmProvider] = useState('groq');
    const [apiKey, setApiKey] = useState('');

    const value = {
        currentDataset,
        setCurrentDataset,
        sessionId,
        setSessionId,
        llmProvider,
        setLlmProvider,
        apiKey,
        setApiKey,
    };

    return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
