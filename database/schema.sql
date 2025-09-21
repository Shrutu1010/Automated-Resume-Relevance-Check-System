-- Resume Relevance Check System Database Schema

-- Table for storing job descriptions
CREATE TABLE IF NOT EXISTS job_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    description TEXT NOT NULL,
    required_skills TEXT, -- JSON array of required skills
    preferred_skills TEXT, -- JSON array of preferred skills
    qualifications TEXT, -- JSON array of qualifications
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing resumes
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    candidate_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255),
    raw_text TEXT NOT NULL,
    skills TEXT, -- JSON array of extracted skills
    projects TEXT, -- JSON array of projects
    education TEXT, -- JSON array of education
    certifications TEXT, -- JSON array of certifications
    experience_years INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing evaluation results
CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    jd_id INTEGER NOT NULL,
    relevance_score REAL NOT NULL, -- 0-100 score
    fit_verdict VARCHAR(20) NOT NULL, -- High/Medium/Low
    hard_match_score REAL NOT NULL,
    semantic_match_score REAL NOT NULL,
    missing_skills TEXT, -- JSON array of missing skills
    missing_projects TEXT, -- JSON array of missing project types
    missing_certifications TEXT, -- JSON array of missing certifications
    improvement_suggestions TEXT, -- LLM generated suggestions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id),
    FOREIGN KEY (jd_id) REFERENCES job_descriptions(id)
);

-- Table for storing embeddings (for semantic matching)
CREATE TABLE IF NOT EXISTS embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type VARCHAR(20) NOT NULL, -- 'resume' or 'jd'
    content_id INTEGER NOT NULL,
    embedding_vector TEXT NOT NULL, -- JSON array of embedding values
    model_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_evaluations_resume_id ON evaluations(resume_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_jd_id ON evaluations(jd_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_score ON evaluations(relevance_score);
CREATE INDEX IF NOT EXISTS idx_embeddings_content ON embeddings(content_type, content_id);
