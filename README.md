# Agentic Data Analysis & Visualization System

A production-grade multi-agent AI system for intelligent data analysis and visualization with RAG integration.

## 🌟 Features

- **Multi-Agent Architecture**: Specialized agents for analysis, visualization, suggestions, and RAG
- **RAG Integration**: Context-aware responses using ChromaDB vector store
- **Smart Suggestions**: Top 3 AI-powered recommendations for insights
- **Natural Language Queries**: Ask questions in plain English
- **Dynamic Code Generation**: Agents write and execute Python code
- **Premium UI**: Modern React interface with TailwindCSS
- **Multi-Provider LLM**: Support for Groq (free), OpenAI, and Anthropic

## 🏗️ Architecture

```
Backend (FastAPI)
├── Orchestrator → Routes queries to specialized agents
├── Analysis Agent → Statistical analysis and insights
├── Visualization Agent → Creates Plotly charts
├── Suggestions Agent → Generates top 3 recommendations
└── RAG Agent → Context-aware responses with vector store

Frontend (React + Vite)
├── Home → Dashboard and quick actions
├── Upload → Drag-and-drop file upload
├── Analysis → Chat interface for queries
├── Visualizations → Gallery of generated charts
└── Suggestions → Top 3 AI recommendations
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- API key for at least one LLM provider (Groq recommended - it's free!)

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example .env
# Edit .env and add your API keys

# Run the server
python main.py
```

The backend will start at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Dependencies are already installed
# If needed: npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Run the development server
npm run dev
```

The frontend will start at `http://localhost:5173`

## 📝 Usage

1. **Upload Data**: Navigate to the Upload page and drag-and-drop a CSV or Excel file
2. **Get Suggestions**: Visit the Suggestions page to see top 3 AI-recommended analyses
3. **Ask Questions**: Go to the Analysis page and chat with the AI agents
4. **View Results**: Check the Visualizations page for generated charts

### Example Queries

- "What's the average sales by region?"
- "Create a bar chart showing product performance"
- "Show me the top 5 customers by revenue"
- "Analyze the correlation between price and quantity"
- "Generate a time series plot of monthly sales"

## 🔑 Getting API Keys

### Groq (Recommended - FREE!)

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Generate an API key
4. Add to `.env`: `GROQ_API_KEY=gsk_your_key_here`

### OpenAI

1. Visit [platform.openai.com](https://platform.openai.com)
2. Create an account and add billing
3. Generate an API key
4. Add to `.env`: `OPENAI_API_KEY=sk-your_key_here`

## 📊 Sample Dataset

A sample sales dataset is included at `data/sample_sales.csv` for testing.

## 🛠️ Tech Stack

**Backend:**
- FastAPI - Async web framework
- ChromaDB - Vector database for RAG
- Pandas - Data manipulation
- Plotly - Visualization library
- Groq/OpenAI/Anthropic - LLM providers

**Frontend:**
- React 18 - UI library
- Vite - Build tool
- TailwindCSS - Styling
- React Router - Navigation
- Axios - HTTP client
- Plotly.js - Interactive charts

## 📁 Project Structure

```
data_analysis/
├── backend/
│   ├── src/
│   │   ├── agents/          # Specialized AI agents
│   │   ├── core/            # Orchestrator
│   │   ├── services/        # LLM & vector services
│   │   ├── tools/           # Python REPL & data tools
│   │   ├── api/routes/      # API endpoints
│   │   └── models/          # Pydantic schemas
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages
│   │   ├── components/      # Reusable components
│   │   ├── services/        # API client
│   │   └── context/         # State management
│   └── package.json
└── data/                    # Sample datasets
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🎯 Key Concepts

### ReAct Architecture

Agents use the ReAct (Reasoning + Acting) pattern:
1. **Thought**: Agent reasons about what to do
2. **Action**: Agent executes Python code
3. **Observation**: System provides feedback
4. **Repeat**: Until final answer is reached

### Agent Orchestration

The orchestrator automatically routes queries to the right agent:
- Visualization keywords → Visualization Agent
- "Suggest" or "recommend" → Suggestions Agent
- References to past analyses → RAG Agent
- Default → Analysis Agent

### RAG Integration

Past analyses are stored in ChromaDB and retrieved for context-aware responses.

## 🤝 Contributing

This is a demonstration project. Feel free to fork and extend!

## 📄 License

MIT

## 🙏 Acknowledgments

Built with modern AI agent patterns and best practices in web development.
