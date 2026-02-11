#!/bin/bash

echo "🚀 Setting up Agentic Data Analysis System..."
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
    echo ""
fi

# Backend setup
echo "🔧 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

cd ..

# Frontend setup
echo ""
echo "🎨 Frontend is already set up!"
echo ""

# Instructions
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Edit .env file and add your API key:"
echo "   - Get free Groq API key from: https://console.groq.com"
echo "   - Add to .env: GROQ_API_KEY=gsk_your_key_here"
echo ""
echo "2. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Open http://localhost:5173 in your browser"
echo ""
echo "🎉 Happy analyzing!"
