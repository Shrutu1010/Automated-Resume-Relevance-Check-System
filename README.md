# Resume Relevance Check System

A comprehensive automated resume evaluation system for placement teams, built for hackathons and real-world deployment.

## 🚀 Features

- **Automated Resume Parsing**: Extract skills, projects, education, and certifications from PDF/DOCX files
- **Job Description Analysis**: Parse and structure job requirements automatically  
- **Dual Scoring System**: Combines hard keyword matching with semantic similarity using embeddings
- **LLM-Powered Suggestions**: Generate actionable improvement recommendations
- **Interactive Dashboard**: Streamlit-based interface for placement teams
- **Batch Processing**: Evaluate multiple resumes against job descriptions simultaneously
- **Comprehensive Analytics**: Insights into skills gaps, candidate rankings, and hiring trends

## 🏗️ Architecture

\`\`\`
resume_relevance_system/
├── backend/                 # FastAPI backend
│   ├── main.py             # API entry point
│   ├── models.py           # Database models
│   ├── routes/             # API route handlers
│   └── services/           # Core business logic
│       ├── parser.py       # Resume/JD parsing
│       ├── scorer.py       # Scoring algorithms
│       ├── semantic.py     # Embeddings & similarity
│       └── suggestions.py  # LLM suggestions
├── frontend/               # Streamlit dashboard
│   └── app.py             # Dashboard interface
├── database/              # Database schema
├── sample_data/           # Sample resumes and JDs
└── scripts/               # Setup and utility scripts
\`\`\`

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **Frontend**: Streamlit
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **ML/AI**: Sentence Transformers, OpenAI GPT, spaCy, NLTK
- **Document Processing**: PyMuPDF, python-docx, pdfplumber
- **Semantic Search**: ChromaDB, FAISS
- **Text Processing**: TF-IDF, BM25, Fuzzy Matching

## 📦 Installation

### Quick Start

1. **Clone the repository**
   \`\`\`bash
   git clone <repository-url>
   cd resume_relevance_system
   \`\`\`

2. **Run the setup script**
   \`\`\`bash
   chmod +x run.sh
   ./run.sh
   \`\`\`

3. **Set up environment variables** (optional)
   \`\`\`bash
   export OPENAI_API_KEY="your-openai-api-key"  # For LLM suggestions
   \`\`\`

### Manual Installation

1. **Create virtual environment**
   \`\`\`bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

2. **Install dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Download required models**
   \`\`\`bash
   python -m spacy download en_core_web_sm
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   \`\`\`

4. **Initialize database**
   \`\`\`bash
   python scripts/setup_database.py
   \`\`\`

## 🚀 Usage

### Starting the System

1. **Start the backend API**
   \`\`\`bash
   cd backend
   python main.py
   \`\`\`
   API will be available at: http://localhost:8000

2. **Start the frontend dashboard** (in another terminal)
   \`\`\`bash
   streamlit run frontend/app.py
   \`\`\`
   Dashboard will be available at: http://localhost:8501

### Using the Dashboard

1. **Create Job Descriptions**
   - Navigate to "Job Descriptions" tab
   - Paste job description text
   - System automatically extracts required/preferred skills

2. **Upload Resumes**
   - Go to "Resumes" tab
   - Upload PDF or DOCX files
   - View parsed candidate information

3. **Run Evaluations**
   - Select job description and resumes
   - Choose individual or batch evaluation
   - View detailed scoring and suggestions

4. **Analyze Results**
   - View candidate rankings
   - Analyze skills gaps
   - Export results for further processing

## 🔧 API Endpoints

### Job Descriptions
- `POST /api/job-descriptions/` - Create job description
- `GET /api/job-descriptions/` - List all job descriptions
- `GET /api/job-descriptions/{id}` - Get specific job description

### Resumes
- `POST /api/resumes/` - Upload and parse resume
- `GET /api/resumes/` - List all resumes
- `GET /api/resumes/{id}` - Get specific resume

### Evaluations
- `POST /api/evaluate/` - Evaluate single resume
- `POST /api/evaluate-batch/` - Batch evaluate resumes
- `GET /api/evaluations/jd/{id}` - Get evaluations for job description

## 📊 Scoring Algorithm

The system uses a hybrid scoring approach:

### Hard Matching (50% weight)
- **Skills Matching**: Fuzzy string matching for technical skills
- **Education Matching**: Degree level and field alignment
- **Experience Matching**: Years of experience comparison
- **Certifications**: Relevant certification identification

### Semantic Matching (50% weight)
- **Embedding Similarity**: Sentence transformer models
- **Contextual Understanding**: Beyond keyword matching
- **Semantic Relationships**: Related skills and concepts

### Final Score Calculation
\`\`\`
Relevance Score = (Hard Match × 0.5) + (Semantic Match × 0.5)

Fit Verdict:
- High: 75-100 points
- Medium: 50-74 points  
- Low: 0-49 points
\`\`\`

## 🤖 LLM Integration

The system supports multiple LLM providers for generating improvement suggestions:

- **OpenAI GPT**: Set `OPENAI_API_KEY` environment variable
- **Fallback Mode**: Rule-based suggestions when LLM unavailable
- **Customizable Prompts**: Modify suggestion generation logic

## 📈 Sample Data

The system includes sample data for testing:

- **Job Descriptions**: Senior Software Engineer, Data Scientist, Frontend Developer
- **Sample Resumes**: Matching candidate profiles with varying skill levels
- **Test Scenarios**: High, medium, and low fit examples

## 🔧 Configuration

### Environment Variables
\`\`\`bash
OPENAI_API_KEY=your-openai-api-key          # Optional: For LLM suggestions
DATABASE_URL=sqlite:///./resume_system.db   # Database connection
API_HOST=0.0.0.0                           # API host
API_PORT=8000                              # API port
\`\`\`

### Scoring Weights
Modify weights in `backend/services/scorer.py`:
\`\`\`python
self.weights = {
    'hard_match': 0.5,      # Hard matching weight
    'semantic_match': 0.5,   # Semantic matching weight
    'skills': 0.4,          # Skills importance
    'education': 0.2,       # Education importance
    'experience': 0.2,      # Experience importance
    'projects': 0.1,        # Projects importance
    'certifications': 0.1   # Certifications importance
}
\`\`\`

## 🧪 Testing

Run the test suite:
\`\`\`bash
# Test API endpoints
curl http://localhost:8000/health

# Test resume upload
curl -X POST -F "file=@sample_data/resumes/john_doe.pdf" http://localhost:8000/api/resumes/

# Test evaluation
curl -X POST -d "resume_id=1&jd_id=1" http://localhost:8000/api/evaluate/
\`\`\`

## 📝 Development

### Adding New Features

1. **New Parsing Logic**: Extend `backend/services/parser.py`
2. **Custom Scoring**: Modify `backend/services/scorer.py`
3. **Dashboard Components**: Add to `frontend/app.py`
4. **API Endpoints**: Create new routes in `backend/routes/`

### Database Schema Changes

1. Update `database/schema.sql`
2. Modify `backend/models.py`
3. Run migration script

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   \`\`\`bash
   export ENVIRONMENT=production
   export DATABASE_URL=postgresql://user:pass@host:port/db
   \`\`\`

2. **Docker Deployment**
   \`\`\`bash
   docker build -t resume-system .
   docker run -p 8000:8000 -p 8501:8501 resume-system
   \`\`\`

3. **Cloud Deployment**
   - Deploy backend to Heroku, AWS, or GCP
   - Use managed database (PostgreSQL)
   - Configure environment variables

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Open GitHub issues for bugs and feature requests
- **API Documentation**: Visit http://localhost:8000/docs when running

## 🎯 Roadmap

- [ ] Advanced NLP for better skill extraction
- [ ] Integration with ATS systems
- [ ] Multi-language support
- [ ] Advanced analytics and reporting
- [ ] Mobile-responsive dashboard
- [ ] Real-time collaboration features
- [ ] Integration with job boards
- [ ] Advanced ML model training interface

---

**Built for hackathons, ready for production!** 🚀
