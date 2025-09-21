#!/bin/bash

# Resume Relevance Check System - Startup Script

echo "🚀 Starting Resume Relevance Check System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Download spaCy model
echo "🧠 Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# Download NLTK data
echo "📚 Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Initialize database
echo "🗄️ Initializing database..."
python scripts/setup_database.py

mkdir -p uploads
mkdir -p sample_data/jds_pdf
mkdir -p sample_data/resumes_pdf

echo "📁 Checking for PDF sample data..."
python sample_data/pdf_data_loader.py

if [ -f "sample_data/jds_pdf/*.pdf" ] 2>/dev/null || [ -f "sample_data/resumes_pdf/*.pdf" ] 2>/dev/null; then
    echo "📊 Loading PDF sample data..."
    python scripts/load_pdf_sample_data.py
else
    echo "⚠️  No PDF files found. Please add your PDF files:"
    echo "   • Job Descriptions (2 files) → sample_data/jds_pdf/"
    echo "   • Resumes (10 files) → sample_data/resumes_pdf/"
    echo "   Then run: python scripts/load_pdf_sample_data.py"
fi

echo "✅ Setup complete!"
echo ""
echo "📁 NEXT STEPS:"
echo "=============="
echo "1. Add your PDF files to the correct directories:"
echo "   • Job Descriptions (2 files) → sample_data/jds_pdf/"
echo "   • Resumes (10 files) → sample_data/resumes_pdf/"
echo ""
echo "2. Load PDF data (if not done automatically):"
echo "   python scripts/load_pdf_sample_data.py"
echo ""
echo "3. Start the system:"
echo "   • Backend API: cd backend && python main.py"
echo "   • Frontend Dashboard: streamlit run frontend/app.py"
echo ""
echo "4. Open your browser to:"
echo "   • API: http://localhost:8000"
echo "   • Dashboard: http://localhost:8501"
