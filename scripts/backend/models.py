"""
Database models for the Resume Relevance Check System
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'resume_system.db')

@dataclass
class JobDescription:
    id: Optional[int] = None
    title: str = ""
    company: str = ""
    description: str = ""
    required_skills: List[str] = None
    preferred_skills: List[str] = None
    qualifications: List[str] = None
    location: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.required_skills is None:
            self.required_skills = []
        if self.preferred_skills is None:
            self.preferred_skills = []
        if self.qualifications is None:
            self.qualifications = []

@dataclass
class Resume:
    id: Optional[int] = None
    filename: str = ""
    candidate_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    raw_text: str = ""
    skills: List[str] = None
    projects: List[Dict[str, str]] = None
    education: List[Dict[str, str]] = None
    certifications: List[str] = None
    experience_years: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.projects is None:
            self.projects = []
        if self.education is None:
            self.education = []
        if self.certifications is None:
            self.certifications = []

@dataclass
class Evaluation:
    id: Optional[int] = None
    resume_id: int = 0
    jd_id: int = 0
    relevance_score: float = 0.0
    fit_verdict: str = ""
    hard_match_score: float = 0.0
    semantic_match_score: float = 0.0
    missing_skills: List[str] = None
    missing_projects: List[str] = None
    missing_certifications: List[str] = None
    improvement_suggestions: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.missing_skills is None:
            self.missing_skills = []
        if self.missing_projects is None:
            self.missing_projects = []
        if self.missing_certifications is None:
            self.missing_certifications = []

class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Read and execute schema
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema = f.read()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema)
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # Job Description operations
    def save_job_description(self, jd: JobDescription) -> int:
        """Save job description to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO job_descriptions 
                (title, company, description, required_skills, preferred_skills, qualifications, location)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                jd.title, jd.company, jd.description,
                json.dumps(jd.required_skills),
                json.dumps(jd.preferred_skills),
                json.dumps(jd.qualifications),
                jd.location
            ))
            return cursor.lastrowid
    
    def get_job_description(self, jd_id: int) -> Optional[JobDescription]:
        """Get job description by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM job_descriptions WHERE id = ?", (jd_id,))
            row = cursor.fetchone()
            
            if row:
                return JobDescription(
                    id=row['id'],
                    title=row['title'],
                    company=row['company'],
                    description=row['description'],
                    required_skills=json.loads(row['required_skills'] or '[]'),
                    preferred_skills=json.loads(row['preferred_skills'] or '[]'),
                    qualifications=json.loads(row['qualifications'] or '[]'),
                    location=row['location'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        return None
    
    def get_all_job_descriptions(self) -> List[JobDescription]:
        """Get all job descriptions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM job_descriptions ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            return [JobDescription(
                id=row['id'],
                title=row['title'],
                company=row['company'],
                description=row['description'],
                required_skills=json.loads(row['required_skills'] or '[]'),
                preferred_skills=json.loads(row['preferred_skills'] or '[]'),
                qualifications=json.loads(row['qualifications'] or '[]'),
                location=row['location'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            ) for row in rows]
    
    def delete_job_description(self, jd_id: int) -> bool:
        """Delete job description by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM job_descriptions WHERE id = ?", (jd_id,))
            return cursor.rowcount > 0
    
    # Resume operations
    def save_resume(self, resume: Resume) -> int:
        """Save resume to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO resumes 
                (filename, candidate_name, email, phone, location, raw_text, 
                 skills, projects, education, certifications, experience_years)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resume.filename, resume.candidate_name, resume.email, resume.phone,
                resume.location, resume.raw_text,
                json.dumps(resume.skills),
                json.dumps(resume.projects),
                json.dumps(resume.education),
                json.dumps(resume.certifications),
                resume.experience_years
            ))
            return cursor.lastrowid
    
    def get_resume(self, resume_id: int) -> Optional[Resume]:
        """Get resume by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
            row = cursor.fetchone()
            
            if row:
                return Resume(
                    id=row['id'],
                    filename=row['filename'],
                    candidate_name=row['candidate_name'],
                    email=row['email'],
                    phone=row['phone'],
                    location=row['location'],
                    raw_text=row['raw_text'],
                    skills=json.loads(row['skills'] or '[]'),
                    projects=json.loads(row['projects'] or '[]'),
                    education=json.loads(row['education'] or '[]'),
                    certifications=json.loads(row['certifications'] or '[]'),
                    experience_years=row['experience_years'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        return None
    
    def get_all_resumes(self) -> List[Resume]:
        """Get all resumes"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resumes ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            return [Resume(
                id=row['id'],
                filename=row['filename'],
                candidate_name=row['candidate_name'],
                email=row['email'],
                phone=row['phone'],
                location=row['location'],
                raw_text=row['raw_text'],
                skills=json.loads(row['skills'] or '[]'),
                projects=json.loads(row['projects'] or '[]'),
                education=json.loads(row['education'] or '[]'),
                certifications=json.loads(row['certifications'] or '[]'),
                experience_years=row['experience_years'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            ) for row in rows]
    
    def delete_resume(self, resume_id: int) -> bool:
        """Delete resume by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
            return cursor.rowcount > 0
    
    # Evaluation operations
    def save_evaluation(self, evaluation: Evaluation) -> int:
        """Save evaluation to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO evaluations 
                (resume_id, jd_id, relevance_score, fit_verdict, hard_match_score, 
                 semantic_match_score, missing_skills, missing_projects, 
                 missing_certifications, improvement_suggestions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evaluation.resume_id, evaluation.jd_id, evaluation.relevance_score,
                evaluation.fit_verdict, evaluation.hard_match_score, evaluation.semantic_match_score,
                json.dumps(evaluation.missing_skills),
                json.dumps(evaluation.missing_projects),
                json.dumps(evaluation.missing_certifications),
                evaluation.improvement_suggestions
            ))
            return cursor.lastrowid
    
    def get_evaluations_by_jd(self, jd_id: int) -> List[Evaluation]:
        """Get all evaluations for a job description"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM evaluations 
                WHERE jd_id = ? 
                ORDER BY relevance_score DESC
            """, (jd_id,))
            rows = cursor.fetchall()
            
            return [Evaluation(
                id=row['id'],
                resume_id=row['resume_id'],
                jd_id=row['jd_id'],
                relevance_score=row['relevance_score'],
                fit_verdict=row['fit_verdict'],
                hard_match_score=row['hard_match_score'],
                semantic_match_score=row['semantic_match_score'],
                missing_skills=json.loads(row['missing_skills'] or '[]'),
                missing_projects=json.loads(row['missing_projects'] or '[]'),
                missing_certifications=json.loads(row['missing_certifications'] or '[]'),
                improvement_suggestions=row['improvement_suggestions'],
                created_at=row['created_at']
            ) for row in rows]
    
    def save_embedding(self, content_type: str, content_id: int, 
                      embedding: List[float], model_name: str):
        """Save embedding vector"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO embeddings (content_type, content_id, embedding_vector, model_name)
                VALUES (?, ?, ?, ?)
            """, (content_type, content_id, json.dumps(embedding), model_name))
    
    def get_embedding(self, content_type: str, content_id: int) -> Optional[List[float]]:
        """Get embedding vector"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT embedding_vector FROM embeddings 
                WHERE content_type = ? AND content_id = ?
                ORDER BY created_at DESC LIMIT 1
            """, (content_type, content_id))
            row = cursor.fetchone()
            
            if row:
                return json.loads(row['embedding_vector'])
        return None

# Global database instance
db = DatabaseManager()
